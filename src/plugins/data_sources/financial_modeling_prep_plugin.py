"""
Financial Modeling Prep data source plugin for comprehensive financial data.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class FinancialModelingPrepPlugin(DataSourcePlugin):
    """
    Financial Modeling Prep API plugin for comprehensive financial data.
    
    Provides access to:
    - Financial statements (income, balance sheet, cash flow)
    - Company profiles and metrics
    - Analyst estimates and ratings
    - Economic indicators
    - Market data and ratios
    """
    
    def __init__(self):
        """Initialize Financial Modeling Prep plugin."""
        self.name = "FinancialModelingPrepPlugin"
        self.description = "Financial Modeling Prep comprehensive financial data provider"
        self.base_url = "https://financialmodelingprep.com/api"
        
        self.api_key: Optional[str] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.2  # FMP allows good rate limits for paid plans
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # API version
        self.api_version = "v3"
        
        # Endpoint mappings
        self.endpoints = {
            "profile": f"{self.api_version}/profile",
            "financial_statements": f"{self.api_version}/income-statement",
            "balance_sheet": f"{self.api_version}/balance-sheet-statement",
            "cash_flow": f"{self.api_version}/cash-flow-statement",
            "key_metrics": f"{self.api_version}/key-metrics",
            "financial_ratios": f"{self.api_version}/ratios",
            "analyst_estimates": f"{self.api_version}/analyst-estimates",
            "price_target": f"{self.api_version}/price-target",
            "upgrades_downgrades": f"{self.api_version}/upgrades-downgrades",
            "earnings_calendar": f"{self.api_version}/earning_calendar",
            "economic_calendar": f"{self.api_version}/economic_calendar",
            "historical_price": f"{self.api_version}/historical-price-full",
            "real_time_price": f"{self.api_version}/quote",
            "market_cap": f"{self.api_version}/market-capitalization",
            "insider_trading": f"{self.api_version}/insider-trading",
            "institutional_holders": f"{self.api_version}/institutional-holder",
            "etf_holdings": f"{self.api_version}/etf-holder",
            "sec_filings": f"{self.api_version}/sec_filings"
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for Financial Modeling Prep plugin."""
        return {
            "api_key": {
                "type": "string",
                "description": "Financial Modeling Prep API key (get from financialmodelingprep.com)",
                "default": "",
                "required": True,
                "sensitive": True
            },
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
                raise ValueError("Financial Modeling Prep API key is required")
            
            self.rate_limit_delay = config.get("rate_limit_delay", 0.2)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            logger.info(f"Financial Modeling Prep plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize Financial Modeling Prep plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make rate-limited API request to Financial Modeling Prep."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        # Prepare parameters
        if params is None:
            params = {}
        
        # Add API key
        params["apikey"] = self.api_key
        
        url = f"{self.base_url}/{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"FMP API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Check for API errors
                        if isinstance(data, dict) and "Error Message" in data:
                            raise ValueError(f"FMP API error: {data['Error Message']}")
                        
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"FMP rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 401:
                        # Unauthorized - likely invalid API key
                        raise ValueError("FMP API unauthorized - check API key")
                    
                    elif response.status == 403:
                        # Forbidden - likely premium feature on free plan
                        raise ValueError("FMP API forbidden - premium feature or quota exceeded")
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"FMP request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"FMP request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"FMP request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data from Financial Modeling Prep.
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (daily supported)
            
        Returns:
            List of OHLCV data dictionaries
        """
        try:
            if interval != "daily":
                logger.warning(f"FMP only supports daily intervals, got: {interval}")
            
            # FMP historical price endpoint
            endpoint = f"{self.endpoints['historical_price']}/{ticker.upper()}"
            params = {
                "from": start_date,
                "to": end_date
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data or "historical" not in data:
                logger.warning(f"No historical data found for {ticker}")
                return []
            
            historical_data = data["historical"]
            
            # Convert to standardized format
            ohlcv_data = []
            for record in historical_data:
                try:
                    date_str = record.get("date")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    ohlcv_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "open": float(record.get("open", 0)),
                        "high": float(record.get("high", 0)),
                        "low": float(record.get("low", 0)),
                        "close": float(record.get("close", 0)),
                        "volume": int(record.get("volume", 0)),
                        "adj_close": float(record.get("adjClose", record.get("close", 0))),
                        "change": float(record.get("change", 0)),
                        "change_percent": float(record.get("changePercent", 0)),
                        "vwap": float(record.get("vwap", 0)),
                        "source": "financial_modeling_prep",
                        "ticker": ticker.upper()
                    }
                    
                    ohlcv_data.append(ohlcv_record)
                
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing OHLCV data for {ticker} on {date_str}: {str(e)}")
                    continue
            
            # Sort by date (newest first in FMP, we want oldest first)
            ohlcv_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(ohlcv_data)} OHLCV records for {ticker} from FMP")
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
        Fetch technical indicators from Financial Modeling Prep.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of indicator
            params: Indicator parameters
            
        Returns:
            List of indicator data
        """
        try:
            if indicator_type.lower() == "financial_ratios":
                return await self._fetch_financial_ratios(ticker, params)
            elif indicator_type.lower() == "key_metrics":
                return await self._fetch_key_metrics(ticker, params)
            else:
                logger.warning(f"FMP doesn't support technical indicator: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching {indicator_type} for {ticker}: {str(e)}")
            return []
    
    async def _fetch_financial_ratios(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch financial ratios for a company."""
        try:
            endpoint = f"{self.endpoints['financial_ratios']}/{ticker.upper()}"
            limit = params.get("limit", 5)
            
            data = await self._rate_limited_request(endpoint, {"limit": limit})
            
            if not data:
                return []
            
            ratio_data = []
            for record in data:
                try:
                    date_str = record.get("date", "")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    ratio_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "indicator_type": "FINANCIAL_RATIOS",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "values": {
                            "pe_ratio": record.get("priceEarningsRatio"),
                            "price_to_book": record.get("priceToBookRatio"),
                            "price_to_sales": record.get("priceToSalesRatio"),
                            "debt_to_equity": record.get("debtEquityRatio"),
                            "return_on_equity": record.get("returnOnEquity"),
                            "return_on_assets": record.get("returnOnAssets"),
                            "current_ratio": record.get("currentRatio"),
                            "quick_ratio": record.get("quickRatio"),
                            "gross_profit_margin": record.get("grossProfitMargin"),
                            "operating_profit_margin": record.get("operatingProfitMargin"),
                            "net_profit_margin": record.get("netProfitMargin")
                        }
                    }
                    
                    ratio_data.append(ratio_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing financial ratios for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(ratio_data)} financial ratio records for {ticker}")
            return ratio_data
        
        except Exception as e:
            logger.error(f"Error fetching financial ratios for {ticker}: {str(e)}")
            return []
    
    async def _fetch_key_metrics(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch key financial metrics for a company."""
        try:
            endpoint = f"{self.endpoints['key_metrics']}/{ticker.upper()}"
            limit = params.get("limit", 5)
            
            data = await self._rate_limited_request(endpoint, {"limit": limit})
            
            if not data:
                return []
            
            metrics_data = []
            for record in data:
                try:
                    date_str = record.get("date", "")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    metrics_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "indicator_type": "KEY_METRICS",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "values": {
                            "market_cap": record.get("marketCap"),
                            "enterprise_value": record.get("enterpriseValue"),
                            "revenue_per_share": record.get("revenuePerShare"),
                            "eps": record.get("netIncomePerShare"),
                            "book_value_per_share": record.get("bookValuePerShare"),
                            "operating_cash_flow_per_share": record.get("operatingCashFlowPerShare"),
                            "free_cash_flow_per_share": record.get("freeCashFlowPerShare"),
                            "debt_to_market_cap": record.get("debtToMarketCap"),
                            "earnings_yield": record.get("earningsYield"),
                            "dividend_yield": record.get("dividendYield")
                        }
                    }
                    
                    metrics_data.append(metrics_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing key metrics for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(metrics_data)} key metrics records for {ticker}")
            return metrics_data
        
        except Exception as e:
            logger.error(f"Error fetching key metrics for {ticker}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch event data from Financial Modeling Prep.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of event data dictionaries
        """
        try:
            if event_type.lower() == "earnings":
                return await self._fetch_earnings_events(ticker, start_date, end_date)
            elif event_type.lower() == "analyst_estimates":
                return await self._fetch_analyst_estimates(ticker)
            elif event_type.lower() == "upgrades_downgrades":
                return await self._fetch_upgrades_downgrades(ticker, start_date, end_date)
            elif event_type.lower() == "insider_trading":
                return await self._fetch_insider_trading(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported FMP event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching {event_type} events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_earnings_events(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch earnings calendar events."""
        try:
            endpoint = self.endpoints["earnings_calendar"]
            params = {
                "from": start_date,
                "to": end_date
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                return []
            
            # Filter for specific ticker
            ticker_events = [event for event in data if event.get("symbol", "").upper() == ticker.upper()]
            
            event_data = []
            for event in ticker_events:
                try:
                    date_str = event.get("date", "")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    event_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "event_type": "earnings",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "data": {
                            "eps_estimated": event.get("epsEstimated"),
                            "eps_actual": event.get("epsActual"),
                            "revenue_estimated": event.get("revenueEstimated"),
                            "revenue_actual": event.get("revenueActual"),
                            "time": event.get("time", ""),
                            "updated_from_date": event.get("updatedFromDate", "")
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing earnings event for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(event_data)} earnings events for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching earnings events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_analyst_estimates(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch analyst estimates."""
        try:
            endpoint = f"{self.endpoints['analyst_estimates']}/{ticker.upper()}"
            
            data = await self._rate_limited_request(endpoint)
            
            if not data:
                return []
            
            event_data = []
            for estimate in data:
                try:
                    date_str = estimate.get("date", "")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    event_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "event_type": "analyst_estimate",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "data": {
                            "estimated_revenue_low": estimate.get("estimatedRevenueLow"),
                            "estimated_revenue_high": estimate.get("estimatedRevenueHigh"),
                            "estimated_revenue_avg": estimate.get("estimatedRevenueAvg"),
                            "estimated_eps_avg": estimate.get("estimatedEpsAvg"),
                            "estimated_eps_high": estimate.get("estimatedEpsHigh"),
                            "estimated_eps_low": estimate.get("estimatedEpsLow"),
                            "number_analyst_estimated_revenue": estimate.get("numberAnalystEstimatedRevenue"),
                            "number_analyst_estimated_eps": estimate.get("numberAnalystEstimatedEps")
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing analyst estimate for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(event_data)} analyst estimates for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching analyst estimates for {ticker}: {str(e)}")
            return []
    
    async def _fetch_upgrades_downgrades(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch analyst upgrades and downgrades."""
        try:
            endpoint = f"{self.endpoints['upgrades_downgrades']}"
            params = {
                "symbol": ticker.upper()
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                return []
            
            # Filter by date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            event_data = []
            for event in data:
                try:
                    date_str = event.get("publishedDate", "")
                    if not date_str:
                        continue
                    
                    # Parse date (format may include time)
                    if "T" in date_str:
                        date_obj = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    else:
                        date_obj = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    
                    # Filter by date range
                    if not (start_dt <= date_obj <= end_dt):
                        continue
                    
                    event_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "event_type": "analyst_rating",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "data": {
                            "grade_current": event.get("gradeCurrent", ""),
                            "grade_previous": event.get("gradePrevious", ""),
                            "company": event.get("company", ""),
                            "price_target_current": event.get("priceTargetCurrent"),
                            "price_target_previous": event.get("priceTargetPrevious"),
                            "news_title": event.get("newsTitle", ""),
                            "news_publisher": event.get("newsPublisher", "")
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing upgrade/downgrade for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(event_data)} upgrade/downgrade events for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching upgrades/downgrades for {ticker}: {str(e)}")
            return []
    
    async def _fetch_insider_trading(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch insider trading events."""
        try:
            endpoint = f"{self.endpoints['insider_trading']}"
            params = {
                "symbol": ticker.upper(),
                "limit": 100
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                return []
            
            # Filter by date range
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            event_data = []
            for event in data:
                try:
                    date_str = event.get("transactionDate", "")
                    if not date_str:
                        continue
                    
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    
                    # Filter by date range
                    if not (start_dt <= date_obj <= end_dt):
                        continue
                    
                    event_record = {
                        "date": date_str,
                        "timestamp": date_obj.isoformat(),
                        "event_type": "insider_trading",
                        "ticker": ticker.upper(),
                        "source": "financial_modeling_prep",
                        "data": {
                            "filing_date": event.get("filingDate", ""),
                            "transaction_type": event.get("transactionType", ""),
                            "securities_owned": event.get("securitiesOwned", 0),
                            "securities_transacted": event.get("securitiesTransacted", 0),
                            "price": event.get("price", 0),
                            "reporting_name": event.get("reportingName", ""),
                            "type_of_owner": event.get("typeOfOwner", ""),
                            "acquisition_or_disposition": event.get("acquisitionOrDisposition", "")
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error parsing insider trading for {ticker}: {str(e)}")
                    continue
            
            logger.info(f"Fetched {len(event_data)} insider trading events for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching insider trading for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("Financial Modeling Prep plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing Financial Modeling Prep plugin: {str(e)}")
    
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
            "supported_intervals": ["daily"],
            "supported_indicators": ["financial_ratios", "key_metrics"],
            "supported_events": ["earnings", "analyst_estimates", "upgrades_downgrades", "insider_trading"],
            "api_version": self.api_version,
            "premium_features": True
        }