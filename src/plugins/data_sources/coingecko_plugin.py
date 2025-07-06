"""
CoinGecko API plugin for cryptocurrency market data.
Free tier: 10,000 calls per month, no API key required.
"""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class CoinGeckoPlugin(DataSourcePlugin):
    """
    CoinGecko API plugin for cryptocurrency market data.
    
    Provides access to:
    - 10,000+ cryptocurrencies
    - Historical price data
    - Market data (market cap, volume, etc.)
    - DeFi protocol data
    - NFT floor prices
    - Exchange data
    - Global market statistics
    
    Free tier: 10,000 calls/month (no API key required)
    Pro tier: 50,000 calls/month with API key
    """
    
    def __init__(self):
        """Initialize CoinGecko plugin."""
        self.name = "CoinGeckoPlugin"
        self.description = "CoinGecko cryptocurrency market data (free tier available)"
        self.base_url = "https://api.coingecko.com/api/v3"
        
        self.api_key: Optional[str] = None  # Optional for pro tier
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 1.2  # Free tier: 50 calls/minute
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # API endpoints
        self.endpoints = {
            "ping": "/ping",
            "simple_price": "/simple/price",
            "coins_list": "/coins/list",
            "coins_markets": "/coins/markets",
            "coin_history": "/coins/{id}/history",
            "coin_market_chart": "/coins/{id}/market_chart",
            "coin_market_chart_range": "/coins/{id}/market_chart/range",
            "coin_ohlc": "/coins/{id}/ohlc",
            "exchanges": "/exchanges",
            "exchange_tickers": "/exchanges/{id}/tickers",
            "trending": "/search/trending",
            "global": "/global",
            "defi": "/global/decentralized_finance_defi",
            "nfts_list": "/nfts/list",
            "nft_collection": "/nfts/{id}"
        }
        
        # Common coin mappings
        self.coin_mappings = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "SOL": "solana",
            "TRX": "tron",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "SHIB": "shiba-inu",
            "AVAX": "avalanche-2",
            "UNI": "uniswap",
            "LINK": "chainlink",
            "ATOM": "cosmos"
        }
        
        # Supported currencies
        self.supported_currencies = [
            "usd", "eur", "jpy", "btc", "eth", "ltc", "bch", "bnb", "eos", "xrp", "xlm",
            "link", "dot", "yfi", "bits", "sats", "cny", "krw", "inr", "cad", "aud",
            "rub", "pln", "try", "zar", "hkd", "sgd", "nzd", "mxn", "chf", "nok", "sek"
        ]
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for CoinGecko plugin."""
        return {
            "api_key": {
                "type": "string",
                "description": "CoinGecko Pro API key (optional - enables higher rate limits)",
                "default": "",
                "required": False,
                "sensitive": True
            },
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds (free: 1.2s, pro: 0.12s)",
                "default": 1.2,
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
            "default_currency": {
                "type": "string",
                "description": "Default currency for price data",
                "default": "usd",
                "options": ["usd", "eur", "btc", "eth"]
            },
            "enable_pro_features": {
                "type": "boolean",
                "description": "Enable pro features if API key is provided",
                "default": False
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.api_key = config.get("api_key")
            self.rate_limit_delay = config.get("rate_limit_delay", 1.2)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            self.default_currency = config.get("default_currency", "usd")
            self.enable_pro_features = config.get("enable_pro_features", False)
            
            # Adjust rate limiting for pro accounts
            if self.api_key and self.enable_pro_features:
                self.rate_limit_delay = min(self.rate_limit_delay, 0.12)  # Pro: 500 calls/minute
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {"Accept": "application/json"}
            
            if self.api_key:
                headers["x-cg-pro-api-key"] = self.api_key
            
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
            
            logger.info(f"CoinGecko plugin initialized (Pro: {bool(self.api_key)}) with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize CoinGecko plugin: {str(e)}")
            raise
    
    def _get_coin_id(self, symbol: str) -> str:
        """Get CoinGecko coin ID from symbol."""
        symbol_upper = symbol.upper()
        return self.coin_mappings.get(symbol_upper, symbol.lower())
    
    async def _rate_limited_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Make rate-limited API request to CoinGecko."""
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
                logger.debug(f"CoinGecko API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 60  # CoinGecko suggests 1-minute wait
                        logger.warning(f"CoinGecko rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 404:
                        # Coin not found
                        logger.warning(f"Coin not found on CoinGecko: {params}")
                        return {}
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"CoinGecko request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"CoinGecko request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"CoinGecko request failed after {self.max_retries} attempts")
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV data from CoinGecko.
        
        Args:
            ticker: Cryptocurrency symbol (BTC, ETH, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval (daily supported by free tier)
            
        Returns:
            List of OHLCV data dictionaries
        """
        try:
            coin_id = self._get_coin_id(ticker)
            
            # Convert dates to timestamps
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            start_timestamp = int(start_dt.timestamp())
            end_timestamp = int(end_dt.timestamp())
            
            # Determine days for API call
            days_diff = (end_dt - start_dt).days
            
            if days_diff <= 1:
                # Use market_chart for recent data
                endpoint = self.endpoints["coin_market_chart"].format(id=coin_id)
                params = {
                    "vs_currency": self.default_currency,
                    "days": max(1, days_diff),
                    "interval": "daily" if days_diff > 1 else "hourly"
                }
            else:
                # Use market_chart/range for historical data
                endpoint = self.endpoints["coin_market_chart_range"].format(id=coin_id)
                params = {
                    "vs_currency": self.default_currency,
                    "from": start_timestamp,
                    "to": end_timestamp
                }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data:
                logger.warning(f"No data found for {ticker}")
                return []
            
            # Extract price data
            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            volumes = data.get("total_volumes", [])
            
            # Convert to OHLCV format
            ohlcv_data = []
            
            # Group by day for daily intervals
            daily_data = {}
            
            for i, price_point in enumerate(prices):
                try:
                    timestamp = price_point[0]
                    price = price_point[1]
                    
                    date_obj = datetime.fromtimestamp(timestamp / 1000)
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    # Get corresponding market cap and volume
                    market_cap = market_caps[i][1] if i < len(market_caps) else 0
                    volume = volumes[i][1] if i < len(volumes) else 0
                    
                    if date_str not in daily_data:
                        daily_data[date_str] = {
                            "date": date_str,
                            "timestamp": date_obj.strftime("%Y-%m-%d"),
                            "prices": [],
                            "market_cap": market_cap,
                            "volume": volume,
                            "date_obj": date_obj
                        }
                    
                    daily_data[date_str]["prices"].append(price)
                
                except (IndexError, ValueError, TypeError) as e:
                    logger.warning(f"Error parsing price data for {ticker}: {str(e)}")
                    continue
            
            # Create OHLCV records
            for date_str, day_data in daily_data.items():
                if not day_data["prices"]:
                    continue
                
                prices_list = day_data["prices"]
                
                ohlcv_record = {
                    "date": date_str,
                    "timestamp": day_data["date_obj"].isoformat(),
                    "open": prices_list[0],
                    "high": max(prices_list),
                    "low": min(prices_list),
                    "close": prices_list[-1],
                    "volume": day_data["volume"],
                    "market_cap": day_data["market_cap"],
                    "source": "coingecko",
                    "ticker": ticker.upper(),
                    "coin_id": coin_id,
                    "currency": self.default_currency
                }
                
                ohlcv_data.append(ohlcv_record)
            
            # Sort by date
            ohlcv_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(ohlcv_data)} OHLCV records for {ticker} from CoinGecko")
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
        Fetch market indicators from CoinGecko.
        
        Args:
            ticker: Cryptocurrency symbol
            indicator_type: Type of indicator
            params: Indicator parameters
            
        Returns:
            List of indicator data
        """
        try:
            if indicator_type.lower() == "market_metrics":
                return await self._fetch_market_metrics(ticker, params)
            elif indicator_type.lower() == "defi_metrics":
                return await self._fetch_defi_metrics()
            else:
                logger.warning(f"CoinGecko doesn't support technical indicator: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching {indicator_type} for {ticker}: {str(e)}")
            return []
    
    async def _fetch_market_metrics(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch market metrics for a cryptocurrency."""
        try:
            coin_id = self._get_coin_id(ticker)
            
            # Get current market data
            endpoint = self.endpoints["coins_markets"]
            api_params = {
                "vs_currency": self.default_currency,
                "ids": coin_id,
                "order": "market_cap_desc",
                "per_page": 1,
                "page": 1,
                "sparkline": False,
                "price_change_percentage": "1h,24h,7d,30d,1y"
            }
            
            data = await self._rate_limited_request(endpoint, api_params)
            
            if not data or len(data) == 0:
                return []
            
            coin_data = data[0]
            
            indicator_record = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "indicator_type": "MARKET_METRICS",
                "ticker": ticker.upper(),
                "source": "coingecko",
                "values": {
                    "market_cap": coin_data.get("market_cap"),
                    "market_cap_rank": coin_data.get("market_cap_rank"),
                    "fully_diluted_valuation": coin_data.get("fully_diluted_valuation"),
                    "total_volume": coin_data.get("total_volume"),
                    "high_24h": coin_data.get("high_24h"),
                    "low_24h": coin_data.get("low_24h"),
                    "price_change_24h": coin_data.get("price_change_24h"),
                    "price_change_percentage_24h": coin_data.get("price_change_percentage_24h"),
                    "price_change_percentage_7d": coin_data.get("price_change_percentage_7d_in_currency"),
                    "price_change_percentage_30d": coin_data.get("price_change_percentage_30d_in_currency"),
                    "price_change_percentage_1y": coin_data.get("price_change_percentage_1y_in_currency"),
                    "market_cap_change_24h": coin_data.get("market_cap_change_24h"),
                    "market_cap_change_percentage_24h": coin_data.get("market_cap_change_percentage_24h"),
                    "circulating_supply": coin_data.get("circulating_supply"),
                    "total_supply": coin_data.get("total_supply"),
                    "max_supply": coin_data.get("max_supply"),
                    "ath": coin_data.get("ath"),
                    "ath_change_percentage": coin_data.get("ath_change_percentage"),
                    "ath_date": coin_data.get("ath_date"),
                    "atl": coin_data.get("atl"),
                    "atl_change_percentage": coin_data.get("atl_change_percentage"),
                    "atl_date": coin_data.get("atl_date")
                }
            }
            
            logger.info(f"Fetched market metrics for {ticker}")
            return [indicator_record]
        
        except Exception as e:
            logger.error(f"Error fetching market metrics for {ticker}: {str(e)}")
            return []
    
    async def _fetch_defi_metrics(self) -> List[Dict[str, Any]]:
        """Fetch global DeFi metrics."""
        try:
            endpoint = self.endpoints["defi"]
            data = await self._rate_limited_request(endpoint)
            
            if not data:
                return []
            
            indicator_record = {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "timestamp": datetime.now().isoformat(),
                "indicator_type": "DEFI_METRICS",
                "ticker": "DEFI",
                "source": "coingecko",
                "values": {
                    "defi_market_cap": data.get("defi_market_cap"),
                    "eth_market_cap": data.get("eth_market_cap"),
                    "defi_to_eth_ratio": data.get("defi_to_eth_ratio"),
                    "trading_volume_24h": data.get("trading_volume_24h"),
                    "defi_dominance": data.get("defi_dominance"),
                    "top_coin_name": data.get("top_coin_name"),
                    "top_coin_defi_dominance": data.get("top_coin_defi_dominance")
                }
            }
            
            logger.info("Fetched global DeFi metrics")
            return [indicator_record]
        
        except Exception as e:
            logger.error(f"Error fetching DeFi metrics: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch crypto events from CoinGecko.
        
        Args:
            ticker: Cryptocurrency symbol
            event_type: Type of event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of event data dictionaries
        """
        try:
            if event_type.lower() == "trending":
                return await self._fetch_trending_coins()
            elif event_type.lower() == "market_updates":
                return await self._fetch_market_updates(ticker)
            else:
                logger.warning(f"Unsupported CoinGecko event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching CoinGecko events: {str(e)}")
            return []
    
    async def _fetch_trending_coins(self) -> List[Dict[str, Any]]:
        """Fetch trending cryptocurrencies."""
        try:
            endpoint = self.endpoints["trending"]
            data = await self._rate_limited_request(endpoint)
            
            if not data or "coins" not in data:
                return []
            
            event_data = []
            for coin in data["coins"]:
                coin_data = coin.get("item", {})
                
                event_record = {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "timestamp": datetime.now().isoformat(),
                    "event_type": "trending_coin",
                    "ticker": coin_data.get("symbol", "").upper(),
                    "source": "coingecko",
                    "data": {
                        "coin_id": coin_data.get("id"),
                        "name": coin_data.get("name"),
                        "symbol": coin_data.get("symbol"),
                        "market_cap_rank": coin_data.get("market_cap_rank"),
                        "thumb": coin_data.get("thumb"),
                        "small": coin_data.get("small"),
                        "large": coin_data.get("large"),
                        "slug": coin_data.get("slug"),
                        "price_btc": coin_data.get("price_btc"),
                        "score": coin_data.get("score")
                    }
                }
                
                event_data.append(event_record)
            
            logger.info(f"Fetched {len(event_data)} trending coins")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching trending coins: {str(e)}")
            return []
    
    async def _fetch_market_updates(self, ticker: str) -> List[Dict[str, Any]]:
        """Fetch market updates for a specific coin."""
        try:
            # Get recent price movements as market updates
            coin_id = self._get_coin_id(ticker)
            
            endpoint = self.endpoints["coin_market_chart"].format(id=coin_id)
            params = {
                "vs_currency": self.default_currency,
                "days": "1",
                "interval": "hourly"
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data or "prices" not in data:
                return []
            
            prices = data["prices"]
            if len(prices) < 2:
                return []
            
            # Calculate significant price movements (>5%)
            event_data = []
            for i in range(1, len(prices)):
                prev_price = prices[i-1][1]
                curr_price = prices[i][1]
                
                if prev_price > 0:
                    change_percent = ((curr_price - prev_price) / prev_price) * 100
                    
                    if abs(change_percent) > 5:  # Significant movement
                        timestamp = prices[i][0]
                        date_obj = datetime.fromtimestamp(timestamp / 1000)
                        
                        event_record = {
                            "date": date_obj.strftime("%Y-%m-%d"),
                            "timestamp": date_obj.isoformat(),
                            "event_type": "price_movement",
                            "ticker": ticker.upper(),
                            "source": "coingecko",
                            "data": {
                                "price_change": curr_price - prev_price,
                                "price_change_percent": change_percent,
                                "price_from": prev_price,
                                "price_to": curr_price,
                                "movement_type": "surge" if change_percent > 0 else "drop",
                                "significance": "major" if abs(change_percent) > 10 else "moderate"
                            }
                        }
                        
                        event_data.append(event_record)
            
            logger.info(f"Fetched {len(event_data)} market updates for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching market updates for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("CoinGecko plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing CoinGecko plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "api_key_configured": bool(self.api_key),
            "is_pro_account": bool(self.api_key and self.enable_pro_features),
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "supported_coins": len(self.coin_mappings),
            "supported_currencies": len(self.supported_currencies),
            "supported_indicators": ["market_metrics", "defi_metrics"],
            "supported_events": ["trending", "market_updates"],
            "cost": "FREE (10k calls/month) / PRO ($129/month)",
            "api_limits": {
                "free": "50 calls/minute, 10,000/month",
                "pro": "500 calls/minute, 50,000/month"
            }
        }