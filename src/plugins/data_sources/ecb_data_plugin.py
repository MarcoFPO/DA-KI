"""
European Central Bank (ECB) Statistical Data Warehouse plugin.
Completely free access to ECB economic and monetary data.
"""
import asyncio
import aiohttp
import logging
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class ECBDataPlugin(DataSourcePlugin):
    """
    European Central Bank Statistical Data Warehouse plugin.
    
    Provides completely free access to:
    - EUR exchange rates
    - ECB interest rates
    - Money market rates
    - Government bond yields
    - Monetary aggregates
    - Balance of payments
    - Banking statistics
    - Economic indicators
    
    Data source: https://sdw-wsrest.ecb.europa.eu/
    No API key required - completely free
    """
    
    def __init__(self):
        """Initialize ECB Data plugin."""
        self.name = "ECBDataPlugin"
        self.description = "European Central Bank statistical data - completely free"
        self.base_url = "https://sdw-wsrest.ecb.europa.eu/service"
        
        # No API key required
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.2  # ECB allows reasonable rate limits
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # ECB API endpoints
        self.endpoints = {
            "data": "/data",
            "dataflow": "/dataflow",
            "datastructure": "/datastructure",
            "codelist": "/codelist"
        }
        
        # Important ECB data flows
        self.dataflows = {
            # Exchange rates
            "ert": {
                "name": "Euro foreign exchange reference rates",
                "description": "Daily EUR exchange rates vs major currencies"
            },
            "exr": {
                "name": "Exchange Rates", 
                "description": "Historical EUR exchange rates"
            },
            
            # Interest rates
            "fm": {
                "name": "Financial markets",
                "description": "Money market rates, government bond yields"
            },
            "irt": {
                "name": "ECB interest rates",
                "description": "Official ECB interest rates"
            },
            "mir": {
                "name": "MFI interest rates",
                "description": "Monetary financial institution rates"
            },
            
            # Monetary policy
            "bsi": {
                "name": "Balance sheet items",
                "description": "Monetary aggregates, credit"
            },
            "mms": {
                "name": "Monetary market statistics",
                "description": "Money market survey data"
            },
            
            # Economic indicators
            "ei": {
                "name": "Economic indicators",
                "description": "Key economic statistics"
            },
            "bop": {
                "name": "Balance of payments",
                "description": "EU balance of payments"
            }
        }
        
        # Common currency codes
        self.currency_codes = {
            "USD": "US Dollar",
            "GBP": "British Pound",
            "JPY": "Japanese Yen",
            "CHF": "Swiss Franc",
            "CAD": "Canadian Dollar",
            "AUD": "Australian Dollar",
            "SEK": "Swedish Krona",
            "NOK": "Norwegian Krone",
            "DKK": "Danish Krone",
            "PLN": "Polish Zloty",
            "CZK": "Czech Koruna",
            "HUF": "Hungarian Forint",
            "RON": "Romanian Leu",
            "BGN": "Bulgarian Lev",
            "HRK": "Croatian Kuna",
            "RUB": "Russian Ruble",
            "CNY": "Chinese Yuan",
            "KRW": "South Korean Won",
            "INR": "Indian Rupee",
            "BRL": "Brazilian Real",
            "ZAR": "South African Rand",
            "TRY": "Turkish Lira"
        }
        
        # ECB interest rate series
        self.interest_rate_series = {
            "main_refinancing": "4F_N",  # Main refinancing operations
            "marginal_lending": "4F_N",   # Marginal lending facility
            "deposit_facility": "4F_N",   # Deposit facility
            "eonia": "EON_N",             # EONIA
            "euribor_1m": "RT_1M",        # 1-month EURIBOR
            "euribor_3m": "RT_3M",        # 3-month EURIBOR
            "euribor_6m": "RT_6M",        # 6-month EURIBOR
            "euribor_12m": "RT_12M"       # 12-month EURIBOR
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for ECB plugin."""
        return {
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds",
                "default": 0.2,
                "min": 0.1,
                "max": 2.0
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
            "default_format": {
                "type": "string",
                "description": "Default data format (json or xml)",
                "default": "json",
                "options": ["json", "xml"]
            },
            "detail_level": {
                "type": "string",
                "description": "Level of detail in API responses",
                "default": "dataonly",
                "options": ["full", "dataonly", "serieskeysonly", "nodata"]
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.rate_limit_delay = config.get("rate_limit_delay", 0.2)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            self.default_format = config.get("default_format", "json")
            self.detail_level = config.get("detail_level", "dataonly")
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {
                "Accept": f"application/vnd.sdmx.data+{self.default_format}; version=1.0.0",
                "User-Agent": "DA-KI Portfolio Manager"
            }
            
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
            
            logger.info(f"ECB Data plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize ECB Data plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make rate-limited API request to ECB."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"ECB API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        if self.default_format == "json":
                            data = await response.json()
                        else:
                            data = await response.text()
                        return data
                    
                    elif response.status == 404:
                        # Data not found
                        logger.warning(f"ECB data not found: {endpoint}")
                        return {}
                    
                    elif response.status == 413:
                        # Request too large
                        logger.warning(f"ECB request too large: {endpoint}")
                        return {}
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"ECB request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"ECB request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"ECB request failed after {self.max_retries} attempts")
    
    def _format_date_range(self, start_date: str, end_date: str) -> str:
        """Format date range for ECB API."""
        # ECB uses YYYY-MM-DD format
        return f"{start_date}/{end_date}"
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch economic data from ECB (not OHLCV, but economic time series).
        
        Args:
            ticker: Currency code or economic indicator
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data frequency
            
        Returns:
            List of economic data points in OHLCV-like format
        """
        try:
            # Map ticker to ECB data series
            if ticker.upper() in self.currency_codes:
                # Exchange rate data
                return await self._fetch_exchange_rates(ticker.upper(), start_date, end_date)
            elif ticker.lower().startswith("euribor"):
                # Interest rate data
                return await self._fetch_interest_rates(ticker.lower(), start_date, end_date)
            else:
                # Try as generic economic indicator
                return await self._fetch_economic_indicator(ticker, start_date, end_date)
        
        except Exception as e:
            logger.error(f"Error fetching ECB data for {ticker}: {str(e)}")
            return []
    
    async def _fetch_exchange_rates(self, currency: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch EUR exchange rates for a currency."""
        try:
            # Use EXR dataflow for exchange rates
            # Structure: EXR.FREQ.CURRENCY.EXR_TYPE.EXR_VAR.CURR_DENOMINATION
            endpoint = f"{self.endpoints['data']}/EXR/D.{currency}.EUR.SP00.A"
            
            params = {
                "startPeriod": start_date,
                "endPeriod": end_date,
                "detail": self.detail_level
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                logger.warning(f"No exchange rate data found for {currency}")
                return []
            
            # Parse JSON response
            economic_data = []
            
            if "dataSets" in data and len(data["dataSets"]) > 0:
                dataset = data["dataSets"][0]
                series = dataset.get("series", {})
                
                for series_key, series_data in series.items():
                    observations = series_data.get("observations", {})
                    
                    for obs_key, obs_value in observations.items():
                        try:
                            # Get observation value
                            value = float(obs_value[0]) if obs_value and obs_value[0] is not None else None
                            
                            if value is None:
                                continue
                            
                            # Get time period from structure
                            if "structure" in data and "dimensions" in data["structure"]:
                                time_dim = None
                                for dim in data["structure"]["dimensions"]["observation"]:
                                    if dim["id"] == "TIME_PERIOD":
                                        time_dim = dim
                                        break
                                
                                if time_dim and int(obs_key) < len(time_dim["values"]):
                                    time_period = time_dim["values"][int(obs_key)]["id"]
                                    
                                    # Parse date
                                    date_obj = datetime.strptime(time_period, "%Y-%m-%d")
                                    
                                    economic_record = {
                                        "date": time_period,
                                        "timestamp": date_obj.isoformat(),
                                        "open": value,  # Use exchange rate as price
                                        "high": value,
                                        "low": value,
                                        "close": value,
                                        "volume": 0,  # No volume for exchange rates
                                        "source": "ecb_data",
                                        "ticker": f"EUR{currency}",
                                        "currency_from": "EUR",
                                        "currency_to": currency,
                                        "exchange_rate": value,
                                        "data_type": "exchange_rate"
                                    }
                                    
                                    economic_data.append(economic_record)
                        
                        except (ValueError, KeyError, IndexError) as e:
                            logger.warning(f"Error parsing ECB exchange rate data: {str(e)}")
                            continue
            
            # Sort by date
            economic_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(economic_data)} exchange rate records for EUR/{currency}")
            return economic_data
        
        except Exception as e:
            logger.error(f"Error fetching exchange rates for {currency}: {str(e)}")
            return []
    
    async def _fetch_interest_rates(self, rate_type: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch ECB interest rates."""
        try:
            # Map rate type to ECB series
            if "euribor" in rate_type:
                if "1m" in rate_type:
                    series_code = "RT.MM.EUR.RT1M.BB.AC.A05"
                elif "3m" in rate_type:
                    series_code = "RT.MM.EUR.RT3M.BB.AC.A05"
                elif "6m" in rate_type:
                    series_code = "RT.MM.EUR.RT6M.BB.AC.A05"
                elif "12m" in rate_type:
                    series_code = "RT.MM.EUR.RT12M.BB.AC.A05"
                else:
                    series_code = "RT.MM.EUR.RT3M.BB.AC.A05"  # Default to 3M
                
                dataflow = "FM"
            else:
                # ECB policy rates
                series_code = "4F.M.U2.EUR.4F.BB.U2.2250"
                dataflow = "IRT"
            
            endpoint = f"{self.endpoints['data']}/{dataflow}/{series_code}"
            
            params = {
                "startPeriod": start_date,
                "endPeriod": end_date,
                "detail": self.detail_level
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                return []
            
            # Parse interest rate data (similar to exchange rates)
            economic_data = []
            
            if "dataSets" in data and len(data["dataSets"]) > 0:
                dataset = data["dataSets"][0]
                series = dataset.get("series", {})
                
                for series_key, series_data in series.items():
                    observations = series_data.get("observations", {})
                    
                    for obs_key, obs_value in observations.items():
                        try:
                            value = float(obs_value[0]) if obs_value and obs_value[0] is not None else None
                            
                            if value is None:
                                continue
                            
                            # Extract time period
                            if "structure" in data and "dimensions" in data["structure"]:
                                time_dim = None
                                for dim in data["structure"]["dimensions"]["observation"]:
                                    if dim["id"] == "TIME_PERIOD":
                                        time_dim = dim
                                        break
                                
                                if time_dim and int(obs_key) < len(time_dim["values"]):
                                    time_period = time_dim["values"][int(obs_key)]["id"]
                                    
                                    # Handle different date formats
                                    try:
                                        if len(time_period) == 7:  # YYYY-MM format
                                            date_obj = datetime.strptime(f"{time_period}-01", "%Y-%m-%d")
                                        else:  # YYYY-MM-DD format
                                            date_obj = datetime.strptime(time_period, "%Y-%m-%d")
                                    except ValueError:
                                        continue
                                    
                                    economic_record = {
                                        "date": date_obj.strftime("%Y-%m-%d"),
                                        "timestamp": date_obj.isoformat(),
                                        "open": value,
                                        "high": value,
                                        "low": value,
                                        "close": value,
                                        "volume": 0,
                                        "source": "ecb_data",
                                        "ticker": rate_type.upper(),
                                        "interest_rate": value,
                                        "rate_type": rate_type,
                                        "data_type": "interest_rate",
                                        "unit": "percent"
                                    }
                                    
                                    economic_data.append(economic_record)
                        
                        except (ValueError, KeyError, IndexError) as e:
                            logger.warning(f"Error parsing ECB interest rate data: {str(e)}")
                            continue
            
            economic_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(economic_data)} interest rate records for {rate_type}")
            return economic_data
        
        except Exception as e:
            logger.error(f"Error fetching interest rates for {rate_type}: {str(e)}")
            return []
    
    async def _fetch_economic_indicator(self, indicator: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch generic economic indicator."""
        try:
            # This is a simplified implementation
            # In production, you'd want a comprehensive mapping of indicators to ECB series
            logger.info(f"Generic economic indicator {indicator} not yet implemented")
            return []
        
        except Exception as e:
            logger.error(f"Error fetching economic indicator {indicator}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch economic indicators from ECB.
        
        Args:
            ticker: Currency or economic indicator
            indicator_type: Type of indicator
            params: Indicator parameters
            
        Returns:
            List of indicator data
        """
        try:
            if indicator_type.lower() == "monetary_policy":
                return await self._fetch_monetary_policy_indicators(params)
            elif indicator_type.lower() == "exchange_rate_volatility":
                return await self._fetch_exchange_rate_volatility(ticker, params)
            else:
                logger.warning(f"ECB doesn't support indicator type: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching ECB indicators: {str(e)}")
            return []
    
    async def _fetch_monetary_policy_indicators(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch monetary policy indicators."""
        try:
            # Fetch main ECB rates
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            start_date = params.get("start_date", (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"))
            
            rates_data = []
            
            # Fetch different rate types
            rate_types = ["euribor_3m", "euribor_12m"]
            
            for rate_type in rate_types:
                rate_data = await self._fetch_interest_rates(rate_type, start_date, end_date)
                rates_data.extend(rate_data)
            
            # Convert to indicator format
            indicator_data = []
            for record in rates_data:
                indicator_record = {
                    "date": record["date"],
                    "timestamp": record["timestamp"],
                    "indicator_type": "MONETARY_POLICY",
                    "ticker": "ECB",
                    "source": "ecb_data",
                    "values": {
                        record["rate_type"]: record["interest_rate"]
                    }
                }
                indicator_data.append(indicator_record)
            
            logger.info(f"Fetched {len(indicator_data)} monetary policy indicators")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching monetary policy indicators: {str(e)}")
            return []
    
    async def _fetch_exchange_rate_volatility(self, currency: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate exchange rate volatility."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            start_date = params.get("start_date", (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"))
            
            # Get exchange rate data
            fx_data = await self._fetch_exchange_rates(currency, start_date, end_date)
            
            if len(fx_data) < 2:
                return []
            
            # Calculate volatility (simplified)
            rates = [record["exchange_rate"] for record in fx_data]
            
            # Calculate daily returns
            returns = []
            for i in range(1, len(rates)):
                if rates[i-1] != 0:
                    daily_return = (rates[i] - rates[i-1]) / rates[i-1]
                    returns.append(daily_return)
            
            # Calculate rolling volatility
            window = 30  # 30-day window
            volatility_data = []
            
            for i in range(window, len(returns)):
                window_returns = returns[i-window:i]
                volatility = (sum(r**2 for r in window_returns) / len(window_returns)) ** 0.5
                
                date_index = i + 1  # Adjust for fx_data indexing
                if date_index < len(fx_data):
                    indicator_record = {
                        "date": fx_data[date_index]["date"],
                        "timestamp": fx_data[date_index]["timestamp"],
                        "indicator_type": "EXCHANGE_RATE_VOLATILITY",
                        "ticker": f"EUR{currency}",
                        "source": "ecb_data",
                        "values": {
                            "volatility": volatility,
                            "currency_pair": f"EUR/{currency}",
                            "window_days": window
                        }
                    }
                    volatility_data.append(indicator_record)
            
            logger.info(f"Calculated {len(volatility_data)} volatility records for EUR/{currency}")
            return volatility_data
        
        except Exception as e:
            logger.error(f"Error calculating exchange rate volatility: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch ECB events (limited - ECB doesn't provide event APIs).
        
        Args:
            ticker: Currency or indicator
            event_type: Type of event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of event data (limited functionality)
        """
        try:
            if event_type.lower() == "rate_changes":
                return await self._detect_rate_changes(ticker, start_date, end_date)
            else:
                logger.warning(f"ECB event type not supported: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching ECB events: {str(e)}")
            return []
    
    async def _detect_rate_changes(self, rate_type: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Detect significant interest rate changes."""
        try:
            # Get interest rate data
            rate_data = await self._fetch_interest_rates(rate_type, start_date, end_date)
            
            if len(rate_data) < 2:
                return []
            
            # Detect changes
            events = []
            threshold = 0.25  # 25 basis points
            
            for i in range(1, len(rate_data)):
                prev_rate = rate_data[i-1]["interest_rate"]
                curr_rate = rate_data[i]["interest_rate"]
                
                change = curr_rate - prev_rate
                
                if abs(change) >= threshold:
                    event_record = {
                        "date": rate_data[i]["date"],
                        "timestamp": rate_data[i]["timestamp"],
                        "event_type": "rate_change",
                        "ticker": rate_type.upper(),
                        "source": "ecb_data",
                        "data": {
                            "rate_from": prev_rate,
                            "rate_to": curr_rate,
                            "change": change,
                            "change_bps": change * 100,
                            "direction": "increase" if change > 0 else "decrease",
                            "significance": "major" if abs(change) >= 0.5 else "moderate"
                        }
                    }
                    events.append(event_record)
            
            logger.info(f"Detected {len(events)} rate change events for {rate_type}")
            return events
        
        except Exception as e:
            logger.error(f"Error detecting rate changes: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("ECB Data plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing ECB Data plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "supported_currencies": len(self.currency_codes),
            "supported_dataflows": len(self.dataflows),
            "supported_indicators": ["monetary_policy", "exchange_rate_volatility"],
            "supported_events": ["rate_changes"],
            "cost": "FREE",
            "api_key_required": False,
            "data_coverage": "European Central Bank statistical data warehouse"
        }