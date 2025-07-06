"""
SEC EDGAR Filings plugin for US company financial data.
Completely free access to all SEC filings.
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


class SECFilingsPlugin(DataSourcePlugin):
    """
    SEC EDGAR Filings plugin for US company financial data.
    
    Provides completely free access to:
    - 10-K Annual Reports
    - 10-Q Quarterly Reports
    - 8-K Current Reports
    - Proxy Statements
    - Insider Trading (Form 4)
    - Company Facts (XBRL)
    - Real-time filings feed
    
    Data source: https://data.sec.gov/
    No API key required - completely free
    """
    
    def __init__(self):
        """Initialize SEC Filings plugin."""
        self.name = "SECFilingsPlugin"
        self.description = "SEC EDGAR filings - completely free US company data"
        self.base_url = "https://data.sec.gov"
        
        # No API key required
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.1  # SEC requests respectful rate limiting
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # Required headers for SEC API
        self.headers = {
            "User-Agent": "DA-KI Portfolio Manager contact@da-ki.example.com",
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov"
        }
        
        # SEC API endpoints
        self.endpoints = {
            "company_facts": "/api/xbrl/companyfacts/CIK{cik}.json",
            "submissions": "/api/xbrl/submissions/CIK{cik}.json",
            "company_tickers": "/api/xbrl/companyfacts.zip",
            "frames": "/api/xbrl/frames/us-gaap/{tag}/{unit}/{year}Q{quarter}.json",
            "filings": "/api/xbrl/filings",
            "mutual_fund_prospectus": "/api/xbrl/mutual-fund"
        }
        
        # Common GAAP tags for financial data
        self.gaap_tags = {
            "revenue": "Revenues",
            "net_income": "NetIncomeLoss", 
            "total_assets": "Assets",
            "total_liabilities": "Liabilities",
            "stockholders_equity": "StockholdersEquity",
            "cash": "CashAndCashEquivalentsAtCarryingValue",
            "debt": "LongTermDebt",
            "shares_outstanding": "CommonStockSharesOutstanding",
            "eps": "EarningsPerShareBasic",
            "operating_income": "OperatingIncomeLoss"
        }
        
        # Form types
        self.form_types = {
            "10-K": "Annual report",
            "10-Q": "Quarterly report", 
            "8-K": "Current report",
            "DEF 14A": "Proxy statement",
            "4": "Insider trading",
            "3": "Initial insider ownership",
            "5": "Annual insider ownership",
            "13F-HR": "Institutional holdings",
            "SC 13G": "Beneficial ownership",
            "424B": "Prospectus"
        }
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for SEC plugin."""
        return {
            "user_agent": {
                "type": "string",
                "description": "User-Agent for SEC API requests (required by SEC)",
                "default": "DA-KI Portfolio Manager contact@da-ki.example.com",
                "required": True
            },
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds (SEC recommends respectful usage)",
                "default": 0.1,
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
            "include_amendments": {
                "type": "boolean",
                "description": "Include amended filings in results",
                "default": False
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            # Update user agent if provided
            user_agent = config.get("user_agent")
            if user_agent:
                self.headers["User-Agent"] = user_agent
            
            self.rate_limit_delay = config.get("rate_limit_delay", 0.1)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            self.include_amendments = config.get("include_amendments", False)
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
            
            logger.info(f"SEC Filings plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize SEC Filings plugin: {str(e)}")
            raise
    
    def _get_cik_from_ticker(self, ticker: str) -> Optional[str]:
        """Get CIK number from ticker symbol."""
        # This is a simplified mapping - in production, you'd want to maintain
        # a comprehensive ticker-to-CIK mapping or use SEC's company tickers endpoint
        ticker_to_cik = {
            "AAPL": "0000320193",
            "MSFT": "0000789019", 
            "GOOGL": "0001652044",
            "AMZN": "0001018724",
            "TSLA": "0001318605",
            "META": "0001326801",
            "NVDA": "0001045810",
            "JPM": "0000019617",
            "JNJ": "0000200406",
            "PG": "0000080424"
        }
        
        return ticker_to_cik.get(ticker.upper())
    
    async def _rate_limited_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make rate-limited API request to SEC."""
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
                logger.debug(f"SEC API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"SEC rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 404:
                        # Not found
                        logger.warning(f"SEC data not found: {endpoint}")
                        return {}
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"SEC request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"SEC request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"SEC request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "quarterly"
    ) -> List[Dict[str, Any]]:
        """
        Fetch financial data from SEC filings (not OHLCV, but financial metrics).
        
        Args:
            ticker: Stock ticker symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (quarterly, annual)
            
        Returns:
            List of financial data points in OHLCV-like format
        """
        try:
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                logger.warning(f"CIK not found for ticker {ticker}")
                return []
            
            # Get company facts
            endpoint = self.endpoints["company_facts"].format(cik=cik)
            data = await self._rate_limited_request(endpoint)
            
            if not data or "facts" not in data:
                logger.warning(f"No company facts found for {ticker}")
                return []
            
            # Extract US-GAAP facts
            us_gaap = data["facts"].get("us-gaap", {})
            
            financial_data = []
            
            # Process key financial metrics
            for metric_name, gaap_tag in self.gaap_tags.items():
                if gaap_tag in us_gaap:
                    metric_data = us_gaap[gaap_tag]
                    units = metric_data.get("units", {})
                    
                    # Process USD values
                    usd_data = units.get("USD", [])
                    for entry in usd_data:
                        try:
                            end_period = entry.get("end")
                            if not end_period:
                                continue
                            
                            date_obj = datetime.strptime(end_period, "%Y-%m-%d")
                            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            
                            # Filter by date range
                            if not (start_dt <= date_obj <= end_dt):
                                continue
                            
                            value = entry.get("val", 0)
                            form = entry.get("form", "")
                            
                            # Create financial record in OHLCV-like format
                            financial_record = {
                                "date": end_period,
                                "timestamp": date_obj.isoformat(),
                                "open": value,  # Use value as price proxy
                                "high": value,
                                "low": value,
                                "close": value,
                                "volume": 0,  # No volume for financial data
                                "source": "sec_filings",
                                "ticker": ticker.upper(),
                                "metric": metric_name,
                                "gaap_tag": gaap_tag,
                                "form_type": form,
                                "filing_date": entry.get("filed", ""),
                                "period": entry.get("fp", ""),
                                "fiscal_year": entry.get("fy", ""),
                                "quarter": entry.get("fp", "").replace("FY", "").replace("Q", "") if entry.get("fp") else ""
                            }
                            
                            financial_data.append(financial_record)
                        
                        except (ValueError, KeyError, TypeError) as e:
                            logger.warning(f"Error parsing SEC data for {ticker}: {str(e)}")
                            continue
            
            # Sort by date
            financial_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(financial_data)} SEC financial records for {ticker}")
            return financial_data
        
        except Exception as e:
            logger.error(f"Error fetching SEC data for {ticker}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch financial ratios and metrics from SEC data.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of financial indicator
            params: Parameters for the indicator
            
        Returns:
            List of financial indicator data
        """
        try:
            if indicator_type.lower() == "financial_ratios":
                return await self._fetch_financial_ratios(ticker, params)
            elif indicator_type.lower() == "key_metrics":
                return await self._fetch_key_metrics(ticker, params)
            else:
                logger.warning(f"SEC doesn't support indicator type: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching SEC indicators for {ticker}: {str(e)}")
            return []
    
    async def _fetch_financial_ratios(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate financial ratios from SEC data."""
        try:
            # Get raw financial data
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            start_date = params.get("start_date", (datetime.now() - timedelta(days=1095)).strftime("%Y-%m-%d"))  # 3 years
            
            financial_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Group by reporting period
            periods = {}
            for record in financial_data:
                period_key = f"{record['fiscal_year']}-{record['quarter']}"
                if period_key not in periods:
                    periods[period_key] = {
                        "date": record["date"],
                        "timestamp": record["timestamp"],
                        "fiscal_year": record["fiscal_year"],
                        "quarter": record["quarter"]
                    }
                
                periods[period_key][record["metric"]] = record["close"]
            
            # Calculate ratios
            ratio_data = []
            for period_key, period_data in periods.items():
                try:
                    # Basic ratios calculation
                    ratios = {}
                    
                    # ROE = Net Income / Stockholders Equity
                    if "net_income" in period_data and "stockholders_equity" in period_data:
                        if period_data["stockholders_equity"] != 0:
                            ratios["roe"] = period_data["net_income"] / period_data["stockholders_equity"]
                    
                    # ROA = Net Income / Total Assets
                    if "net_income" in period_data and "total_assets" in period_data:
                        if period_data["total_assets"] != 0:
                            ratios["roa"] = period_data["net_income"] / period_data["total_assets"]
                    
                    # Debt to Equity = Total Debt / Stockholders Equity
                    if "debt" in period_data and "stockholders_equity" in period_data:
                        if period_data["stockholders_equity"] != 0:
                            ratios["debt_to_equity"] = period_data["debt"] / period_data["stockholders_equity"]
                    
                    if ratios:
                        ratio_record = {
                            "date": period_data["date"],
                            "timestamp": period_data["timestamp"],
                            "indicator_type": "FINANCIAL_RATIOS",
                            "ticker": ticker.upper(),
                            "source": "sec_filings",
                            "values": ratios
                        }
                        ratio_data.append(ratio_record)
                
                except (ZeroDivisionError, KeyError) as e:
                    logger.warning(f"Error calculating ratios for {ticker} period {period_key}: {str(e)}")
                    continue
            
            logger.info(f"Calculated {len(ratio_data)} financial ratio records for {ticker}")
            return ratio_data
        
        except Exception as e:
            logger.error(f"Error calculating financial ratios for {ticker}: {str(e)}")
            return []
    
    async def _fetch_key_metrics(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key financial metrics from SEC data."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            start_date = params.get("start_date", (datetime.now() - timedelta(days=1095)).strftime("%Y-%m-%d"))
            
            financial_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Group by period and extract metrics
            periods = {}
            for record in financial_data:
                period_key = f"{record['fiscal_year']}-{record['quarter']}"
                if period_key not in periods:
                    periods[period_key] = {
                        "date": record["date"],
                        "timestamp": record["timestamp"]
                    }
                periods[period_key][record["metric"]] = record["close"]
            
            # Format as key metrics
            metrics_data = []
            for period_key, period_data in periods.items():
                metrics_record = {
                    "date": period_data["date"],
                    "timestamp": period_data["timestamp"],
                    "indicator_type": "KEY_METRICS",
                    "ticker": ticker.upper(),
                    "source": "sec_filings",
                    "values": {
                        "total_revenue": period_data.get("revenue", 0),
                        "net_income": period_data.get("net_income", 0),
                        "total_assets": period_data.get("total_assets", 0),
                        "total_liabilities": period_data.get("total_liabilities", 0),
                        "stockholders_equity": period_data.get("stockholders_equity", 0),
                        "cash_and_equivalents": period_data.get("cash", 0),
                        "long_term_debt": period_data.get("debt", 0),
                        "shares_outstanding": period_data.get("shares_outstanding", 0),
                        "earnings_per_share": period_data.get("eps", 0)
                    }
                }
                metrics_data.append(metrics_record)
            
            logger.info(f"Extracted {len(metrics_data)} key metrics records for {ticker}")
            return metrics_data
        
        except Exception as e:
            logger.error(f"Error extracting key metrics for {ticker}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch SEC filing events.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of SEC event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of SEC filing event data
        """
        try:
            if event_type.lower() == "filings":
                return await self._fetch_filings(ticker, start_date, end_date)
            elif event_type.lower() == "insider_trading":
                return await self._fetch_insider_trading(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported SEC event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching SEC events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_filings(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch SEC filings for a company."""
        try:
            cik = self._get_cik_from_ticker(ticker)
            if not cik:
                logger.warning(f"CIK not found for ticker {ticker}")
                return []
            
            # Get company submissions
            endpoint = self.endpoints["submissions"].format(cik=cik)
            data = await self._rate_limited_request(endpoint)
            
            if not data or "filings" not in data:
                return []
            
            filings = data["filings"]
            recent_filings = filings.get("recent", {})
            
            event_data = []
            filing_count = len(recent_filings.get("form", []))
            
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            for i in range(filing_count):
                try:
                    filing_date = recent_filings.get("filingDate", [])[i]
                    if not filing_date:
                        continue
                    
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d")
                    
                    # Filter by date range
                    if not (start_dt <= filing_dt <= end_dt):
                        continue
                    
                    form_type = recent_filings.get("form", [])[i]
                    
                    # Filter amendments if configured
                    if not self.include_amendments and "/A" in form_type:
                        continue
                    
                    event_record = {
                        "date": filing_date,
                        "timestamp": filing_dt.isoformat(),
                        "event_type": "sec_filing",
                        "ticker": ticker.upper(),
                        "source": "sec_filings",
                        "data": {
                            "form_type": form_type,
                            "form_description": self.form_types.get(form_type.replace("/A", ""), "Unknown form"),
                            "accession_number": recent_filings.get("accessionNumber", [])[i],
                            "filing_date": filing_date,
                            "report_date": recent_filings.get("reportDate", [])[i],
                            "acceptance_date": recent_filings.get("acceptanceDateTime", [])[i],
                            "is_amendment": "/A" in form_type,
                            "size": recent_filings.get("size", [])[i],
                            "primary_document": recent_filings.get("primaryDocument", [])[i]
                        }
                    }
                    
                    event_data.append(event_record)
                
                except (IndexError, ValueError) as e:
                    logger.warning(f"Error parsing SEC filing for {ticker}: {str(e)}")
                    continue
            
            # Sort by date
            event_data.sort(key=lambda x: x["timestamp"], reverse=True)
            
            logger.info(f"Fetched {len(event_data)} SEC filings for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching SEC filings for {ticker}: {str(e)}")
            return []
    
    async def _fetch_insider_trading(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch insider trading events (Form 4 filings)."""
        try:
            # Get all filings first
            filings = await self._fetch_filings(ticker, start_date, end_date)
            
            # Filter for Form 4 (insider trading)
            insider_filings = [
                filing for filing in filings 
                if filing["data"]["form_type"].startswith("4")
            ]
            
            # Convert to insider trading events
            insider_events = []
            for filing in insider_filings:
                event_record = {
                    "date": filing["date"],
                    "timestamp": filing["timestamp"],
                    "event_type": "insider_trading",
                    "ticker": ticker.upper(),
                    "source": "sec_filings",
                    "data": {
                        "form_type": filing["data"]["form_type"],
                        "filing_date": filing["data"]["filing_date"],
                        "accession_number": filing["data"]["accession_number"],
                        "is_amendment": filing["data"]["is_amendment"],
                        "document_url": f"https://www.sec.gov/Archives/edgar/data/{self._get_cik_from_ticker(ticker)}/{filing['data']['accession_number'].replace('-', '')}/{filing['data']['primary_document']}"
                    }
                }
                insider_events.append(event_record)
            
            logger.info(f"Fetched {len(insider_events)} insider trading events for {ticker}")
            return insider_events
        
        except Exception as e:
            logger.error(f"Error fetching insider trading for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("SEC Filings plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing SEC Filings plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "supported_data_types": ["financial_statements", "filings", "insider_trading"],
            "supported_forms": list(self.form_types.keys()),
            "supported_metrics": list(self.gaap_tags.keys()),
            "cost": "FREE",
            "api_key_required": False,
            "rate_limits": "Respectful usage requested by SEC"
        }