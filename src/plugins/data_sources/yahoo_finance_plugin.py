"""
Yahoo Finance data source plugin for fetching stock market data.
"""
import asyncio
import aiohttp
import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class YahooFinancePlugin(DataSourcePlugin):
    """
    Yahoo Finance plugin for fetching stock market data.
    
    Provides access to:
    - OHLCV data (daily, intraday)
    - Real-time quotes
    - Company information
    - News and events
    - Options data
    
    Note: This uses unofficial Yahoo Finance APIs which may change.
    """
    
    def __init__(self):
        """Initialize Yahoo Finance plugin."""
        self.name = "YahooFinancePlugin"
        self.description = "Yahoo Finance stock market data provider (free)"
        
        # Yahoo Finance endpoints
        self.base_url = "https://query1.finance.yahoo.com"
        self.chart_url = f"{self.base_url}/v8/finance/chart"
        self.quote_url = f"{self.base_url}/v7/finance/quote"
        self.news_url = f"{self.base_url}/v1/finance/search"
        self.options_url = f"{self.base_url}/v7/finance/options"
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.1  # Yahoo allows higher rate limits
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # User agent to avoid blocking
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        self.interval_map = {
            "1m": "1m",
            "2m": "2m", 
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "60m": "60m",
            "90m": "90m",
            "1h": "1h",
            "1d": "1d",
            "5d": "5d",
            "1wk": "1wk",
            "1mo": "1mo",
            "3mo": "3mo",
            "daily": "1d",
            "weekly": "1wk",
            "monthly": "1mo"
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for Yahoo Finance plugin."""
        return {
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds",
                "default": 0.1,
                "min": 0.01,
                "max": 5.0
            },
            "max_retries": {
                "type": "integer",
                "description": "Maximum number of retry attempts for failed requests",
                "default": 3,
                "min": 1,
                "max": 10
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "default": 30,
                "min": 5,
                "max": 120
            },
            "enable_news": {
                "type": "boolean",
                "description": "Enable news and sentiment data fetching",
                "default": True
            },
            "enable_options": {
                "type": "boolean",
                "description": "Enable options data fetching",
                "default": False
            },
            "user_agent": {
                "type": "string",
                "description": "Custom User-Agent string for requests",
                "default": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.rate_limit_delay = config.get("rate_limit_delay", 0.1)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            
            # Update headers with custom user agent
            custom_user_agent = config.get("user_agent")
            if custom_user_agent:
                self.headers["User-Agent"] = custom_user_agent
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
            
            logger.info(f"Yahoo Finance plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize Yahoo Finance plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, url: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make rate-limited request to Yahoo Finance."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Yahoo Finance request (attempt {attempt + 1}): {url}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 5
                        logger.warning(f"Yahoo Finance rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 404:
                        # Symbol not found
                        logger.warning(f"Symbol not found on Yahoo Finance: {params}")
                        return {}
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"Yahoo Finance request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
            
            except Exception as e:
                logger.error(f"Yahoo Finance request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 1)
        
        raise RuntimeError(f"Yahoo Finance request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval
            
        Returns:
            List of OHLCV data dictionaries
        """
        try:
            # Convert dates to timestamps
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            start_timestamp = int(start_dt.timestamp())
            end_timestamp = int(end_dt.timestamp())
            
            # Map interval
            yahoo_interval = self.interval_map.get(interval, "1d")
            
            # Build URL
            url = f"{self.chart_url}/{ticker.upper()}"
            params = {
                "period1": start_timestamp,
                "period2": end_timestamp,
                "interval": yahoo_interval,
                "includePrePost": "false",
                "events": "div,splits"
            }
            
            data = await self._rate_limited_request(url, params)
            
            if not data or "chart" not in data:
                logger.warning(f"No chart data found for {ticker}")
                return []
            
            chart_data = data["chart"]
            if not chart_data.get("result"):
                logger.warning(f"No chart results for {ticker}")
                return []
            
            result = chart_data["result"][0]
            timestamps = result.get("timestamp", [])
            indicators = result.get("indicators", {})
            
            if not indicators.get("quote"):
                logger.warning(f"No quote data in indicators for {ticker}")
                return []
            
            quote_data = indicators["quote"][0]
            
            # Extract OHLCV data
            ohlcv_data = []
            for i, timestamp in enumerate(timestamps):
                try:
                    date_obj = datetime.fromtimestamp(timestamp)
                    
                    # Skip if any required value is None
                    open_val = quote_data.get("open", [])[i] if i < len(quote_data.get("open", [])) else None
                    high_val = quote_data.get("high", [])[i] if i < len(quote_data.get("high", [])) else None
                    low_val = quote_data.get("low", [])[i] if i < len(quote_data.get("low", [])) else None
                    close_val = quote_data.get("close", [])[i] if i < len(quote_data.get("close", [])) else None
                    volume_val = quote_data.get("volume", [])[i] if i < len(quote_data.get("volume", [])) else None
                    
                    if any(val is None for val in [open_val, high_val, low_val, close_val]):
                        continue
                    
                    ohlcv_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "open": float(open_val),
                        "high": float(high_val),
                        "low": float(low_val),
                        "close": float(close_val),
                        "volume": int(volume_val) if volume_val is not None else 0,
                        "source": "yahoo_finance",
                        "ticker": ticker.upper()
                    }
                    
                    ohlcv_data.append(ohlcv_record)
                
                except (ValueError, IndexError, TypeError) as e:
                    logger.warning(f"Error parsing OHLCV data for {ticker} at index {i}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(ohlcv_data)} OHLCV records for {ticker} from Yahoo Finance")
            return ohlcv_data
        
        except Exception as e:
            logger.error(f"Error fetching OHLCV data for {ticker}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch technical indicators from Yahoo Finance.
        
        Note: Yahoo Finance doesn't provide technical indicators directly.
        This method fetches OHLCV data and calculates indicators locally.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of indicator
            params: Indicator parameters
            
        Returns:
            List of indicator data (empty for Yahoo Finance)
        """
        logger.info(f"Yahoo Finance doesn't provide technical indicators directly. Use local calculation for {indicator_type}")
        return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch event data from Yahoo Finance.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of event (news, earnings, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of event data dictionaries
        """
        try:
            if event_type.lower() == "news":
                return await self._fetch_news_data(ticker, start_date, end_date)
            elif event_type.lower() == "dividends":
                return await self._fetch_dividend_data(ticker, start_date, end_date)
            elif event_type.lower() == "splits":
                return await self._fetch_split_data(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported event type for Yahoo Finance: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching {event_type} events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_news_data(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch news data for a ticker."""
        try:
            # Yahoo Finance search for news
            url = f"{self.base_url}/v1/finance/search"
            params = {
                "q": ticker.upper(),
                "quotesCount": 0,
                "newsCount": 20
            }
            
            data = await self._rate_limited_request(url, params)
            
            if not data or "news" not in data:
                return []
            
            news_data = []
            for news_item in data["news"]:
                try:
                    # Parse publish time
                    publish_time = news_item.get("providerPublishTime")
                    if not publish_time:
                        continue
                    
                    date_obj = datetime.fromtimestamp(publish_time)
                    event_date = date_obj.strftime("%Y-%m-%d")
                    
                    # Filter by date range
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    if not (start_dt <= date_obj <= end_dt):
                        continue
                    
                    event_record = {
                        "date": event_date,
                        "timestamp": date_obj.isoformat(),
                        "event_type": "news",
                        "ticker": ticker.upper(),
                        "source": "yahoo_finance",
                        "data": {
                            "title": news_item.get("title", ""),
                            "summary": news_item.get("summary", ""),
                            "publisher": news_item.get("publisher", ""),
                            "link": news_item.get("link", ""),
                            "type": news_item.get("type", ""),
                            "uuid": news_item.get("uuid", "")
                        }
                    }
                    
                    news_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing news data: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(news_data)} news events for {ticker}")
            return news_data
        
        except Exception as e:
            logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return []
    
    async def _fetch_dividend_data(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch dividend data for a ticker."""
        try:
            # Get dividend data from chart API
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            url = f"{self.chart_url}/{ticker.upper()}"
            params = {
                "period1": int(start_dt.timestamp()),
                "period2": int(end_dt.timestamp()),
                "interval": "1d",
                "events": "div"
            }
            
            data = await self._rate_limited_request(url, params)
            
            dividend_data = []
            if data and "chart" in data and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                events = result.get("events", {})
                dividends = events.get("dividends", {})
                
                for timestamp, div_info in dividends.items():
                    date_obj = datetime.fromtimestamp(int(timestamp))
                    
                    event_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "event_type": "dividend",
                        "ticker": ticker.upper(),
                        "source": "yahoo_finance",
                        "data": {
                            "amount": div_info.get("amount", 0),
                            "date": date_obj.strftime("%Y-%m-%d")
                        }
                    }
                    
                    dividend_data.append(event_record)
            
            logger.info(f"Fetched {len(dividend_data)} dividend events for {ticker}")
            return dividend_data
        
        except Exception as e:
            logger.error(f"Error fetching dividends for {ticker}: {str(e)}")
            return []
    
    async def _fetch_split_data(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch stock split data for a ticker."""
        try:
            # Get split data from chart API
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            url = f"{self.chart_url}/{ticker.upper()}"
            params = {
                "period1": int(start_dt.timestamp()),
                "period2": int(end_dt.timestamp()),
                "interval": "1d",
                "events": "splits"
            }
            
            data = await self._rate_limited_request(url, params)
            
            split_data = []
            if data and "chart" in data and data["chart"]["result"]:
                result = data["chart"]["result"][0]
                events = result.get("events", {})
                splits = events.get("splits", {})
                
                for timestamp, split_info in splits.items():
                    date_obj = datetime.fromtimestamp(int(timestamp))
                    
                    event_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "event_type": "split",
                        "ticker": ticker.upper(),
                        "source": "yahoo_finance",
                        "data": {
                            "numerator": split_info.get("numerator", 1),
                            "denominator": split_info.get("denominator", 1),
                            "split_ratio": f"{split_info.get('numerator', 1)}:{split_info.get('denominator', 1)}",
                            "date": date_obj.strftime("%Y-%m-%d")
                        }
                    }
                    
                    split_data.append(event_record)
            
            logger.info(f"Fetched {len(split_data)} split events for {ticker}")
            return split_data
        
        except Exception as e:
            logger.error(f"Error fetching splits for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("Yahoo Finance plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing Yahoo Finance plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "supported_intervals": list(self.interval_map.keys()),
            "supported_indicators": [],  # Yahoo Finance doesn't provide indicators directly
            "supported_events": ["news", "dividends", "splits"],
            "free_tier": True,
            "api_key_required": False
        }