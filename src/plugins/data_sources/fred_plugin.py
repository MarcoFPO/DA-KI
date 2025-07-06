"""
FRED (Federal Reserve Economic Data) plugin for fetching macroeconomic data.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class FREDPlugin(DataSourcePlugin):
    """
    FRED (Federal Reserve Economic Data) plugin for macroeconomic data.
    
    Provides access to:
    - Interest rates (Federal Funds Rate, Treasury yields)
    - Economic indicators (GDP, unemployment, inflation)
    - Market indicators (VIX, yield curves)
    - International data
    """
    
    def __init__(self):
        """Initialize FRED plugin."""
        self.name = "FREDPlugin"
        self.description = "Federal Reserve Economic Data (FRED) macroeconomic data provider"
        self.base_url = "https://api.stlouisfed.org/fred"
        
        self.api_key: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.5  # FRED allows reasonable rate limits
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # Common FRED series IDs for financial markets
        self.series_map = {
            # Interest Rates
            "federal_funds_rate": "FEDFUNDS",
            "10_year_treasury": "GS10",
            "2_year_treasury": "GS2",
            "3_month_treasury": "GS3M",
            "30_year_treasury": "GS30",
            "real_10_year_rate": "DFII10",
            
            # Economic Indicators
            "gdp": "GDP",
            "unemployment_rate": "UNRATE",
            "inflation_rate": "CPIAUCSL",
            "core_inflation": "CPILFESL",
            "pce_inflation": "PCEPI",
            "ism_manufacturing": "NAPM",
            "ism_services": "NAPMEI",
            "consumer_confidence": "UMCSENT",
            "retail_sales": "RSAFS",
            "industrial_production": "INDPRO",
            "housing_starts": "HOUST",
            "nonfarm_payrolls": "PAYEMS",
            
            # Market Indicators
            "vix": "VIXCLS",
            "dollar_index": "DTWEXBGS",
            "sp500": "SP500",
            "yield_curve_10y2y": "T10Y2Y",
            "yield_curve_10y3m": "T10Y3M",
            "high_yield_spread": "BAMLH0A0HYM2",
            "investment_grade_spread": "BAMLC0A0CM",
            
            # Money Supply
            "m1_money_supply": "M1SL",
            "m2_money_supply": "M2SL",
            
            # International
            "crude_oil": "DCOILWTICO",
            "gold_price": "GOLDAMGBD228NLBM",
            "copper_price": "PCOPPUSDM"
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for FRED plugin."""
        return {
            "api_key": {
                "type": "string",
                "description": "FRED API key (get from research.stlouisfed.org/useraccount/apikey)",
                "default": "",
                "required": True,
                "sensitive": True
            },
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds",
                "default": 0.5,
                "min": 0.1,
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
            "default_frequency": {
                "type": "string",
                "description": "Default data frequency (d=daily, w=weekly, m=monthly, q=quarterly, a=annual)",
                "default": "d",
                "options": ["d", "w", "m", "q", "a"]
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.api_key = config.get("api_key")
            if not self.api_key:
                raise ValueError("FRED API key is required")
            
            self.rate_limit_delay = config.get("rate_limit_delay", 0.5)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            self.default_frequency = config.get("default_frequency", "d")
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            logger.info(f"FRED plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize FRED plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited API request to FRED."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        # Add API key and format
        params["api_key"] = self.api_key
        params["file_type"] = "json"
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"FRED API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for FRED API errors
                        if "error_code" in data:
                            error_msg = data.get("error_message", "Unknown FRED API error")
                            raise ValueError(f"FRED API error {data['error_code']}: {error_msg}")
                        
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"FRED rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 400:
                        # Bad request - likely invalid parameters
                        text = await response.text()
                        raise ValueError(f"FRED API bad request: {text}")
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"FRED request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"FRED request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"FRED request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch economic data series from FRED.
        
        Note: FRED doesn't provide OHLCV data, but economic time series.
        The 'ticker' parameter should be a FRED series ID or mapped name.
        
        Args:
            ticker: FRED series ID or mapped economic indicator name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data frequency (daily, weekly, monthly, etc.)
            
        Returns:
            List of economic data points in OHLCV-like format
        """
        try:
            # Map ticker to FRED series ID if it's a known indicator
            series_id = self.series_map.get(ticker.lower(), ticker.upper())
            
            # Map interval to FRED frequency
            frequency_map = {
                "daily": "d",
                "weekly": "w", 
                "monthly": "m",
                "quarterly": "q",
                "annual": "a"
            }
            frequency = frequency_map.get(interval, self.default_frequency)
            
            params = {
                "series_id": series_id,
                "observation_start": start_date,
                "observation_end": end_date,
                "frequency": frequency,
                "aggregation_method": "avg",
                "sort_order": "asc"
            }
            
            data = await self._rate_limited_request("series/observations", params)
            
            if "observations" not in data:
                logger.warning(f"No observations found for FRED series {series_id}")
                return []
            
            observations = data["observations"]
            
            # Convert to OHLCV-like format (using value as close, others as same)
            economic_data = []
            for obs in observations:
                try:
                    date_str = obs.get("date")
                    value_str = obs.get("value")
                    
                    if not date_str or not value_str or value_str == ".":
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    value = float(value_str)
                    
                    # Format as OHLCV (all values same for economic data)
                    economic_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "open": value,
                        "high": value,
                        "low": value,
                        "close": value,
                        "volume": 0,  # No volume for economic data
                        "value": value,  # Keep original value
                        "series_id": series_id,
                        "source": "fred",
                        "ticker": ticker,
                        "realtime_start": obs.get("realtime_start"),
                        "realtime_end": obs.get("realtime_end")
                    }
                    
                    economic_data.append(economic_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing FRED observation for {series_id}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(economic_data)} FRED observations for {series_id}")
            return economic_data
        
        except Exception as e:
            logger.error(f"Error fetching FRED data for {ticker}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch economic indicators from FRED.
        
        Args:
            ticker: FRED series ID or mapped name
            indicator_type: Type of economic indicator
            params: Parameters for the indicator
            
        Returns:
            List of indicator data
        """
        try:
            # For FRED, technical indicators are actually economic series
            # Map indicator types to FRED series
            indicator_series_map = {
                "interest_rate": "FEDFUNDS",
                "inflation": "CPIAUCSL",
                "unemployment": "UNRATE",
                "gdp_growth": "GDP",
                "yield_curve": "T10Y2Y",
                "vix": "VIXCLS",
                "dollar_strength": "DTWEXBGS"
            }
            
            series_id = indicator_series_map.get(indicator_type.lower())
            if not series_id:
                logger.warning(f"Unknown FRED indicator type: {indicator_type}")
                return []
            
            # Use start/end dates from params or default range
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            start_date = params.get("start_date", (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
            
            # Get the data using the OHLCV method
            data = await self.fetch_ohlcv_data(series_id, start_date, end_date, "monthly")
            
            # Convert to indicator format
            indicator_data = []
            for record in data:
                indicator_record = {
                    "date": record["date"],
                    "timestamp": record["timestamp"],
                    "indicator_type": indicator_type.upper(),
                    "ticker": ticker,
                    "source": "fred",
                    "values": {
                        indicator_type.lower(): record["value"],
                        "series_id": record["series_id"]
                    }
                }
                indicator_data.append(indicator_record)
            
            logger.info(f"Fetched {len(indicator_data)} FRED indicator records for {indicator_type}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching FRED indicator {indicator_type}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch economic events from FRED.
        
        Args:
            ticker: FRED series ID or category
            event_type: Type of economic event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of economic event data
        """
        try:
            if event_type.lower() == "fed_releases":
                return await self._fetch_fed_releases(start_date, end_date)
            elif event_type.lower() == "economic_releases":
                return await self._fetch_economic_releases(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported FRED event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching FRED events: {str(e)}")
            return []
    
    async def _fetch_fed_releases(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch Federal Reserve data releases."""
        try:
            params = {
                "realtime_start": start_date,
                "realtime_end": end_date,
                "limit": 100,
                "order_by": "realtime_start"
            }
            
            data = await self._rate_limited_request("releases", params)
            
            if "releases" not in data:
                return []
            
            event_data = []
            for release in data["releases"]:
                try:
                    release_date = release.get("realtime_start", "")
                    if not release_date:
                        continue
                    
                    date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                    
                    event_record = {
                        "date": release_date,
                        "timestamp": date_obj.isoformat(),
                        "event_type": "fed_release",
                        "ticker": "FED",
                        "source": "fred",
                        "data": {
                            "release_id": release.get("id"),
                            "name": release.get("name", ""),
                            "press_release": release.get("press_release", False),
                            "link": release.get("link", ""),
                            "notes": release.get("notes", "")
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing Fed release: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(event_data)} Fed releases")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching Fed releases: {str(e)}")
            return []
    
    async def _fetch_economic_releases(self, category: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch economic data releases for a category."""
        try:
            # This is a simplified implementation
            # In practice, you would need to map categories to specific release IDs
            params = {
                "realtime_start": start_date,
                "realtime_end": end_date,
                "limit": 50
            }
            
            data = await self._rate_limited_request("releases", params)
            
            event_data = []
            if "releases" in data:
                for release in data["releases"][:10]:  # Limit results
                    try:
                        release_date = release.get("realtime_start", "")
                        if not release_date:
                            continue
                        
                        date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                        
                        event_record = {
                            "date": release_date,
                            "timestamp": date_obj.isoformat(),
                            "event_type": "economic_release",
                            "ticker": category.upper(),
                            "source": "fred",
                            "data": {
                                "release_id": release.get("id"),
                                "name": release.get("name", ""),
                                "category": category
                            }
                        }
                        
                        event_data.append(event_record)
                    
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Error parsing economic release: {str(e)}")
                        continue
            
            logger.info(f"Fetched {len(event_data)} economic releases for {category}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching economic releases for {category}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("FRED plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing FRED plugin: {str(e)}")
    
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
            "supported_series": list(self.series_map.keys()),
            "supported_frequencies": ["daily", "weekly", "monthly", "quarterly", "annual"],
            "supported_events": ["fed_releases", "economic_releases"],
            "total_series_available": len(self.series_map)
        }