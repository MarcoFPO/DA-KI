"""
Alpha Vantage data source plugin for fetching stock market data.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class AlphaVantagePlugin(DataSourcePlugin):
    """
    Alpha Vantage API plugin for fetching comprehensive stock market data.
    
    Provides access to:
    - OHLCV data (daily, intraday)
    - Technical indicators (RSI, MACD, SMA, etc.)
    - Fundamental data (earnings, company overview)
    - Real-time quotes
    """
    
    def __init__(self):
        """Initialize Alpha Vantage plugin."""
        self.name = "AlphaVantagePlugin"
        self.description = "Alpha Vantage stock market data provider"
        self.base_url = "https://www.alphavantage.co/query"
        self.api_key: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 12  # 5 calls per minute = 12 seconds between calls
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # API function mappings
        self.function_map = {
            "daily": "TIME_SERIES_DAILY_ADJUSTED",
            "intraday": "TIME_SERIES_INTRADAY",
            "weekly": "TIME_SERIES_WEEKLY_ADJUSTED",
            "monthly": "TIME_SERIES_MONTHLY_ADJUSTED"
        }
        
        self.indicator_map = {
            "RSI": "RSI",
            "MACD": "MACD",
            "SMA": "SMA",
            "EMA": "EMA",
            "BBANDS": "BBANDS",
            "STOCH": "STOCH",
            "ADX": "ADX",
            "WILLR": "%R",
            "ATR": "ATR",
            "ROC": "ROC"
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for Alpha Vantage plugin."""
        return {
            "api_key": {
                "type": "string",
                "description": "Alpha Vantage API key (get from alphavantage.co)",
                "default": "",
                "required": True,
                "sensitive": True
            },
            "rate_limit_delay": {
                "type": "integer",
                "description": "Delay between API calls in seconds (free tier: 5 calls/min)",
                "default": 12,
                "min": 1,
                "max": 60
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
            "enable_premium_features": {
                "type": "boolean",
                "description": "Enable premium features if you have a premium API key",
                "default": False
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.api_key = config.get("api_key")
            if not self.api_key:
                raise ValueError("Alpha Vantage API key is required")
            
            self.rate_limit_delay = config.get("rate_limit_delay", 12)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            logger.info(f"Alpha Vantage plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alpha Vantage plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited API request to Alpha Vantage."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)
        
        # Add API key to parameters
        params["apikey"] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Alpha Vantage API request (attempt {attempt + 1}): {params.get('function', 'unknown')}")
                
                async with self.session.get(self.base_url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API errors
                        if "Error Message" in data:
                            raise ValueError(f"Alpha Vantage API error: {data['Error Message']}")
                        
                        if "Note" in data:
                            # Rate limit exceeded
                            if "call frequency" in data["Note"].lower():
                                logger.warning("Alpha Vantage rate limit exceeded, waiting longer")
                                await asyncio.sleep(60)  # Wait 1 minute
                                continue
                            else:
                                logger.warning(f"Alpha Vantage note: {data['Note']}")
                        
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 30
                        logger.warning(f"Rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:
                        raise aiohttp.ClientError(f"HTTP {response.status}: {await response.text()}")
            
            except asyncio.TimeoutError:
                logger.warning(f"Alpha Vantage request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"Alpha Vantage request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"Alpha Vantage request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data from Alpha Vantage.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (daily, weekly, monthly, or time like 5min, 15min, etc.)
            
        Returns:
            List of OHLCV data dictionaries
        """
        try:
            # Determine API function based on interval
            if interval in ["1min", "5min", "15min", "30min", "60min"]:
                function = "TIME_SERIES_INTRADAY"
                params = {
                    "function": function,
                    "symbol": ticker.upper(),
                    "interval": interval,
                    "outputsize": "full"
                }
            else:
                function = self.function_map.get(interval, "TIME_SERIES_DAILY_ADJUSTED")
                params = {
                    "function": function,
                    "symbol": ticker.upper(),
                    "outputsize": "full"
                }
            
            data = await self._rate_limited_request(params)
            
            # Parse response based on function type
            time_series_key = None
            for key in data.keys():
                if "Time Series" in key:
                    time_series_key = key
                    break
            
            if not time_series_key:
                logger.warning(f"No time series data found for {ticker}")
                return []
            
            time_series = data[time_series_key]
            
            # Convert to standardized format
            ohlcv_data = []
            for date_str, values in time_series.items():
                try:
                    # Parse date
                    if " " in date_str:  # Intraday format: "2023-12-01 16:00:00"
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    else:  # Daily format: "2023-12-01"
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Filter by date range
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    if not (start_dt <= date_obj <= end_dt):
                        continue
                    
                    # Map Alpha Vantage keys to standard format
                    open_key = next((k for k in values.keys() if "open" in k.lower()), None)
                    high_key = next((k for k in values.keys() if "high" in k.lower()), None)
                    low_key = next((k for k in values.keys() if "low" in k.lower()), None)
                    close_key = next((k for k in values.keys() if "close" in k.lower()), None)
                    volume_key = next((k for k in values.keys() if "volume" in k.lower()), None)
                    
                    ohlcv_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "open": float(values[open_key]) if open_key else None,
                        "high": float(values[high_key]) if high_key else None,
                        "low": float(values[low_key]) if low_key else None,
                        "close": float(values[close_key]) if close_key else None,
                        "volume": int(values[volume_key]) if volume_key and values[volume_key] else 0,
                        "source": "alpha_vantage",
                        "ticker": ticker.upper()
                    }
                    
                    ohlcv_data.append(ohlcv_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing OHLCV data for {ticker} on {date_str}: {str(e)}")
                    continue
            
            # Sort by date
            ohlcv_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(ohlcv_data)} OHLCV records for {ticker} from Alpha Vantage")
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
        Fetch technical indicators from Alpha Vantage.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of indicator (RSI, MACD, SMA, etc.)
            params: Indicator-specific parameters
            
        Returns:
            List of indicator data dictionaries
        """
        try:
            function = self.indicator_map.get(indicator_type.upper())
            if not function:
                logger.warning(f"Unsupported indicator type: {indicator_type}")
                return []
            
            api_params = {
                "function": function,
                "symbol": ticker.upper(),
                "interval": params.get("interval", "daily"),
                "datatype": "json"
            }
            
            # Add indicator-specific parameters
            if indicator_type.upper() == "RSI":
                api_params["time_period"] = params.get("time_period", 14)
                api_params["series_type"] = params.get("series_type", "close")
            
            elif indicator_type.upper() == "MACD":
                api_params["series_type"] = params.get("series_type", "close")
                api_params["fastperiod"] = params.get("fastperiod", 12)
                api_params["slowperiod"] = params.get("slowperiod", 26)
                api_params["signalperiod"] = params.get("signalperiod", 9)
            
            elif indicator_type.upper() in ["SMA", "EMA"]:
                api_params["time_period"] = params.get("time_period", 20)
                api_params["series_type"] = params.get("series_type", "close")
            
            elif indicator_type.upper() == "BBANDS":
                api_params["time_period"] = params.get("time_period", 20)
                api_params["series_type"] = params.get("series_type", "close")
                api_params["nbdevup"] = params.get("nbdevup", 2)
                api_params["nbdevdn"] = params.get("nbdevdn", 2)
                api_params["matype"] = params.get("matype", 0)
            
            elif indicator_type.upper() == "STOCH":
                api_params["fastkperiod"] = params.get("fastkperiod", 14)
                api_params["slowkperiod"] = params.get("slowkperiod", 3)
                api_params["slowdperiod"] = params.get("slowdperiod", 3)
                api_params["slowkmatype"] = params.get("slowkmatype", 0)
                api_params["slowdmatype"] = params.get("slowdmatype", 0)
            
            data = await self._rate_limited_request(api_params)
            
            # Find technical analysis key
            technical_key = None
            for key in data.keys():
                if "Technical Analysis" in key:
                    technical_key = key
                    break
            
            if not technical_key:
                logger.warning(f"No technical analysis data found for {ticker} {indicator_type}")
                return []
            
            technical_data = data[technical_key]
            
            # Convert to standardized format
            indicator_data = []
            for date_str, values in technical_data.items():
                try:
                    indicator_record = {
                        "date": date_str,
                        "timestamp": datetime.strptime(date_str, "%Y-%m-%d").isoformat(),
                        "indicator_type": indicator_type.upper(),
                        "ticker": ticker.upper(),
                        "source": "alpha_vantage",
                        "values": {}
                    }
                    
                    # Parse indicator values
                    for key, value in values.items():
                        clean_key = key.lower().replace(f"{indicator_type.lower()}", "").strip(" -_")
                        if clean_key == "":
                            clean_key = indicator_type.lower()
                        indicator_record["values"][clean_key] = float(value)
                    
                    indicator_data.append(indicator_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing indicator data for {ticker} on {date_str}: {str(e)}")
                    continue
            
            # Sort by date
            indicator_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(indicator_data)} {indicator_type} records for {ticker}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching {indicator_type} data for {ticker}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch event data from Alpha Vantage.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of event (earnings, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of event data dictionaries
        """
        try:
            if event_type.lower() == "earnings":
                params = {
                    "function": "EARNINGS",
                    "symbol": ticker.upper()
                }
                
                data = await self._rate_limited_request(params)
                
                # Parse earnings data
                event_data = []
                
                # Check for quarterly earnings
                if "quarterlyEarnings" in data:
                    for earnings in data["quarterlyEarnings"]:
                        try:
                            fiscal_date = earnings.get("fiscalDateEnding", "")
                            reported_date = earnings.get("reportedDate", "")
                            
                            # Use reported date if available, otherwise fiscal date
                            event_date = reported_date if reported_date else fiscal_date
                            
                            if not event_date:
                                continue
                            
                            # Filter by date range
                            event_dt = datetime.strptime(event_date, "%Y-%m-%d")
                            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            
                            if not (start_dt <= event_dt <= end_dt):
                                continue
                            
                            event_record = {
                                "date": event_date,
                                "timestamp": event_dt.isoformat(),
                                "event_type": "earnings",
                                "ticker": ticker.upper(),
                                "source": "alpha_vantage",
                                "data": {
                                    "fiscal_date_ending": fiscal_date,
                                    "reported_date": reported_date,
                                    "reported_eps": earnings.get("reportedEPS"),
                                    "estimated_eps": earnings.get("estimatedEPS"),
                                    "surprise": earnings.get("surprise"),
                                    "surprise_percentage": earnings.get("surprisePercentage")
                                }
                            }
                            
                            event_data.append(event_record)
                        
                        except (ValueError, KeyError) as e:
                            logger.warning(f"Error parsing earnings data for {ticker}: {str(e)}")
                            continue
                
                logger.info(f"Fetched {len(event_data)} earnings events for {ticker}")
                return event_data
            
            else:
                logger.warning(f"Unsupported event type for Alpha Vantage: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching {event_type} events for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("Alpha Vantage plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing Alpha Vantage plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "api_key_configured": bool(self.api_key),
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "supported_intervals": ["1min", "5min", "15min", "30min", "60min", "daily", "weekly", "monthly"],
            "supported_indicators": list(self.indicator_map.keys()),
            "supported_events": ["earnings"]
        }