"""
News sentiment analysis plugin for financial news sentiment data.
"""
import asyncio
import aiohttp
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from urllib.parse import urlencode

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class NewsSentimentPlugin(DataSourcePlugin):
    """
    News sentiment analysis plugin for financial news sentiment data.
    
    Provides access to:
    - Financial news articles and sentiment
    - Company-specific news analysis
    - Market news sentiment trends
    - Event-driven news analysis
    
    Uses multiple news APIs and sentiment analysis.
    """
    
    def __init__(self):
        """Initialize News sentiment plugin."""
        self.name = "NewsSentimentPlugin"
        self.description = "Financial news sentiment analysis from multiple sources"
        
        # News API endpoints
        self.newsapi_base = "https://newsapi.org/v2"
        self.finnhub_base = "https://finnhub.io/api/v1"
        self.marketaux_base = "https://api.marketaux.com/v1"
        
        # API keys
        self.newsapi_key: Optional[str] = None
        self.finnhub_key: Optional[str] = None
        self.marketaux_key: Optional[str] = None
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limit_delay = 0.5  # Conservative rate limiting
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # Financial news sources
        self.financial_sources = [
            "reuters.com",
            "bloomberg.com",
            "wsj.com",
            "cnbc.com",
            "marketwatch.com",
            "seekingalpha.com",
            "fool.com",
            "investing.com",
            "benzinga.com",
            "finviz.com",
            "yahoo.com"
        ]
        
        # Sentiment keywords for basic analysis
        self.positive_keywords = [
            "profit", "growth", "gain", "rise", "increase", "boost", "strong", "positive",
            "upgrade", "beat", "exceed", "outperform", "buy", "bullish", "optimistic",
            "revenue", "earnings", "success", "expansion", "acquisition", "merger",
            "dividend", "breakthrough", "innovation", "partnership", "agreement"
        ]
        
        self.negative_keywords = [
            "loss", "decline", "fall", "decrease", "drop", "weak", "negative", "downgrade",
            "miss", "underperform", "sell", "bearish", "pessimistic", "warning", "concern",
            "risk", "lawsuit", "investigation", "scandal", "bankruptcy", "layoffs",
            "recession", "crash", "volatile", "uncertainty", "challenge"
        ]
        
        # Market impact keywords
        self.high_impact_keywords = [
            "earnings", "guidance", "forecast", "merger", "acquisition", "lawsuit",
            "fda approval", "clinical trial", "partnership", "contract", "deal",
            "ceo", "management", "resignation", "appointment", "investigation",
            "sec", "regulatory", "patent", "product launch", "recall"
        ]
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for News sentiment plugin."""
        return {
            "newsapi_key": {
                "type": "string",
                "description": "NewsAPI.org API key (get from newsapi.org)",
                "default": "",
                "required": False,
                "sensitive": True
            },
            "finnhub_key": {
                "type": "string",
                "description": "Finnhub API key (get from finnhub.io)",
                "default": "",
                "required": False,
                "sensitive": True
            },
            "marketaux_key": {
                "type": "string",
                "description": "MarketAux API key (get from marketaux.com)",
                "default": "",
                "required": False,
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
            "preferred_sources": {
                "type": "array",
                "description": "Preferred news sources for analysis",
                "default": ["reuters.com", "bloomberg.com", "wsj.com", "cnbc.com"],
                "items": {"type": "string"}
            },
            "enable_sentiment_analysis": {
                "type": "boolean",
                "description": "Enable sentiment analysis of news content",
                "default": True
            },
            "min_relevance_score": {
                "type": "number",
                "description": "Minimum relevance score for including news articles",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.newsapi_key = config.get("newsapi_key")
            self.finnhub_key = config.get("finnhub_key")
            self.marketaux_key = config.get("marketaux_key")
            
            if not any([self.newsapi_key, self.finnhub_key, self.marketaux_key]):
                logger.warning("No news API keys provided. Limited functionality available.")
            
            self.rate_limit_delay = config.get("rate_limit_delay", 0.5)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            self.min_relevance_score = config.get("min_relevance_score", 0.5)
            
            # Update preferred sources if provided
            preferred_sources = config.get("preferred_sources")
            if preferred_sources:
                self.financial_sources = preferred_sources
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            logger.info(f"News sentiment plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize News sentiment plugin: {str(e)}")
            raise
    
    async def _rate_limited_request(self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> Any:
        """Make rate-limited API request."""
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
                logger.debug(f"News API request (attempt {attempt + 1}): {url}")
                
                async with self.session.get(url, params=params, headers=headers) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        
                        if 'application/json' in content_type:
                            data = await response.json()
                        elif 'xml' in content_type:
                            text = await response.text()
                            data = self._parse_xml_to_dict(text)
                        else:
                            data = await response.text()
                        
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 10
                        logger.warning(f"News API rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 401:
                        # Unauthorized - likely invalid API key
                        raise ValueError("News API unauthorized - check API key")
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"News API request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"News API request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"News API request failed after {self.max_retries} attempts")
    
    def _parse_xml_to_dict(self, xml_text: str) -> Dict[str, Any]:
        """Parse XML response to dictionary (for RSS feeds)."""
        try:
            root = ET.fromstring(xml_text)
            
            # Handle RSS feed format
            if root.tag == "rss" or "rss" in xml_text.lower():
                items = []
                for item in root.findall(".//item"):
                    item_dict = {}
                    for child in item:
                        item_dict[child.tag] = child.text
                    items.append(item_dict)
                return {"articles": items}
            
            # Handle other XML formats
            return {"content": xml_text}
        
        except ET.ParseError as e:
            logger.warning(f"XML parsing error: {str(e)}")
            return {"content": xml_text}
    
    def _calculate_sentiment_score(self, text: str) -> Dict[str, Any]:
        """Calculate sentiment score using keyword analysis."""
        if not text:
            return {"score": 0.0, "label": "neutral", "confidence": 0.0}
        
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        high_impact_count = sum(1 for keyword in self.high_impact_keywords if keyword in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            
            # Adjust for high impact keywords
            if high_impact_count > 0:
                sentiment_score *= 1.5  # Amplify sentiment for high impact news
            
            if sentiment_score > 0.3:
                sentiment_label = "positive"
            elif sentiment_score < -0.3:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        # Calculate confidence based on number of sentiment words and text length
        confidence = min((total_sentiment_words + high_impact_count) / 10, 1.0)
        
        return {
            "score": max(-1.0, min(1.0, sentiment_score)),  # Clamp to [-1, 1]
            "label": sentiment_label,
            "confidence": confidence,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "high_impact_count": high_impact_count
        }
    
    def _calculate_relevance_score(self, article: Dict[str, Any], ticker: str) -> float:
        """Calculate how relevant an article is to the given ticker."""
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        content = article.get("content", "").lower()
        
        full_text = f"{title} {description} {content}"
        
        # Check for exact ticker mention
        ticker_mentions = len(re.findall(rf'\b{ticker.lower()}\b', full_text))
        
        # Check for company name patterns (simplified)
        company_patterns = [
            rf'\b{ticker.lower()}\s+(corp|corporation|inc|company|ltd)\b',
            rf'\b{ticker.lower()}\s+stock\b',
            rf'\b{ticker.lower()}\s+shares\b'
        ]
        
        company_mentions = sum(len(re.findall(pattern, full_text)) for pattern in company_patterns)
        
        # Base relevance score
        relevance = min((ticker_mentions * 2 + company_mentions) / 10, 1.0)
        
        # Boost for title mentions
        if ticker.lower() in title:
            relevance += 0.3
        
        # Boost for financial context
        financial_keywords = ["earnings", "revenue", "profit", "stock", "shares", "market", "trading"]
        financial_score = sum(1 for keyword in financial_keywords if keyword in full_text) / len(financial_keywords)
        relevance += financial_score * 0.2
        
        return min(relevance, 1.0)
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Fetch news sentiment data in OHLCV-like format.
        
        Args:
            ticker: Stock ticker symbol to search for
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Aggregation interval
            
        Returns:
            List of news sentiment data in OHLCV-like format
        """
        try:
            sentiment_data = []
            
            # Fetch from multiple sources
            if self.newsapi_key:
                newsapi_data = await self._fetch_newsapi_articles(ticker, start_date, end_date)
                sentiment_data.extend(newsapi_data)
            
            if self.finnhub_key:
                finnhub_data = await self._fetch_finnhub_news(ticker, start_date, end_date)
                sentiment_data.extend(finnhub_data)
            
            if self.marketaux_key:
                marketaux_data = await self._fetch_marketaux_news(ticker, start_date, end_date)
                sentiment_data.extend(marketaux_data)
            
            # If no API keys, try free sources
            if not sentiment_data:
                free_data = await self._fetch_free_news_sources(ticker, start_date, end_date)
                sentiment_data.extend(free_data)
            
            # Sort by timestamp
            sentiment_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(sentiment_data)} news sentiment records for {ticker}")
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching news sentiment data for {ticker}: {str(e)}")
            return []
    
    async def _fetch_newsapi_articles(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch articles from NewsAPI."""
        try:
            url = f"{self.newsapi_base}/everything"
            params = {
                "q": f'"{ticker}" OR "{ticker} stock" OR "{ticker} shares"',
                "from": start_date,
                "to": end_date,
                "domains": ",".join(self.financial_sources),
                "sortBy": "relevancy",
                "pageSize": 50,
                "apiKey": self.newsapi_key
            }
            
            data = await self._rate_limited_request(url, params)
            
            if not data or "articles" not in data:
                return []
            
            sentiment_data = []
            for article in data["articles"]:
                try:
                    # Calculate relevance
                    relevance = self._calculate_relevance_score(article, ticker)
                    if relevance < self.min_relevance_score:
                        continue
                    
                    # Parse date
                    published_at = article.get("publishedAt", "")
                    if published_at:
                        date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    else:
                        continue
                    
                    # Calculate sentiment
                    title = article.get("title", "")
                    description = article.get("description", "")
                    content = f"{title} {description}"
                    
                    sentiment = self._calculate_sentiment_score(content)
                    
                    sentiment_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "open": sentiment["score"],
                        "high": sentiment["score"],
                        "low": sentiment["score"],
                        "close": sentiment["score"],
                        "volume": int(relevance * 100),  # Use relevance as volume proxy
                        "source": "newsapi",
                        "ticker": ticker.upper(),
                        "sentiment_label": sentiment["label"],
                        "sentiment_confidence": sentiment["confidence"],
                        "relevance_score": relevance,
                        "title": title[:100],  # Truncated
                        "source_name": article.get("source", {}).get("name", ""),
                        "url": article.get("url", "")
                    }
                    
                    sentiment_data.append(sentiment_record)
                
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing NewsAPI article: {str(e)}")
                    continue
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching NewsAPI articles for {ticker}: {str(e)}")
            return []
    
    async def _fetch_finnhub_news(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch news from Finnhub."""
        try:
            url = f"{self.finnhub_base}/company-news"
            
            # Convert dates to YYYY-MM-DD format for Finnhub
            params = {
                "symbol": ticker.upper(),
                "from": start_date,
                "to": end_date,
                "token": self.finnhub_key
            }
            
            data = await self._rate_limited_request(url, params)
            
            if not data or not isinstance(data, list):
                return []
            
            sentiment_data = []
            for article in data:
                try:
                    # Parse date
                    datetime_timestamp = article.get("datetime", 0)
                    if datetime_timestamp:
                        date_obj = datetime.fromtimestamp(datetime_timestamp)
                    else:
                        continue
                    
                    # Calculate sentiment
                    headline = article.get("headline", "")
                    summary = article.get("summary", "")
                    content = f"{headline} {summary}"
                    
                    sentiment = self._calculate_sentiment_score(content)
                    relevance = self._calculate_relevance_score({"title": headline, "description": summary}, ticker)
                    
                    if relevance < self.min_relevance_score:
                        continue
                    
                    sentiment_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "open": sentiment["score"],
                        "high": sentiment["score"],
                        "low": sentiment["score"],
                        "close": sentiment["score"],
                        "volume": int(relevance * 100),
                        "source": "finnhub",
                        "ticker": ticker.upper(),
                        "sentiment_label": sentiment["label"],
                        "sentiment_confidence": sentiment["confidence"],
                        "relevance_score": relevance,
                        "title": headline[:100],
                        "source_name": article.get("source", ""),
                        "url": article.get("url", "")
                    }
                    
                    sentiment_data.append(sentiment_record)
                
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing Finnhub article: {str(e)}")
                    continue
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching Finnhub news for {ticker}: {str(e)}")
            return []
    
    async def _fetch_marketaux_news(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch news from MarketAux."""
        try:
            url = f"{self.marketaux_base}/news/all"
            params = {
                "symbols": ticker.upper(),
                "filter_entities": "true",
                "published_after": f"{start_date}T00:00:00",
                "published_before": f"{end_date}T23:59:59",
                "limit": 50,
                "api_token": self.marketaux_key
            }
            
            data = await self._rate_limited_request(url, params)
            
            if not data or "data" not in data:
                return []
            
            sentiment_data = []
            for article in data["data"]:
                try:
                    # Parse date
                    published_at = article.get("published_at", "")
                    if published_at:
                        date_obj = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                    else:
                        continue
                    
                    # Calculate sentiment
                    title = article.get("title", "")
                    description = article.get("description", "")
                    content = f"{title} {description}"
                    
                    sentiment = self._calculate_sentiment_score(content)
                    relevance = self._calculate_relevance_score({"title": title, "description": description}, ticker)
                    
                    if relevance < self.min_relevance_score:
                        continue
                    
                    sentiment_record = {
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "timestamp": date_obj.isoformat(),
                        "open": sentiment["score"],
                        "high": sentiment["score"],
                        "low": sentiment["score"],
                        "close": sentiment["score"],
                        "volume": int(relevance * 100),
                        "source": "marketaux",
                        "ticker": ticker.upper(),
                        "sentiment_label": sentiment["label"],
                        "sentiment_confidence": sentiment["confidence"],
                        "relevance_score": relevance,
                        "title": title[:100],
                        "source_name": article.get("source", ""),
                        "url": article.get("url", "")
                    }
                    
                    sentiment_data.append(sentiment_record)
                
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing MarketAux article: {str(e)}")
                    continue
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching MarketAux news for {ticker}: {str(e)}")
            return []
    
    async def _fetch_free_news_sources(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch news from free sources (RSS feeds, etc.)."""
        try:
            # This is a simplified implementation
            # In practice, you would implement RSS feed parsing for various sources
            sentiment_data = []
            
            # Example: Yahoo Finance RSS (simplified)
            try:
                url = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker.upper()}&region=US&lang=en-US"
                data = await self._rate_limited_request(url)
                
                if isinstance(data, dict) and "articles" in data:
                    for article in data["articles"][:10]:  # Limit to 10 articles
                        try:
                            title = article.get("title", "")
                            description = article.get("description", "")
                            pub_date = article.get("pubDate", "")
                            
                            if not title:
                                continue
                            
                            # Simple date parsing (would need improvement for production)
                            try:
                                date_obj = datetime.now()  # Fallback to current time
                            except:
                                continue
                            
                            sentiment = self._calculate_sentiment_score(f"{title} {description}")
                            relevance = self._calculate_relevance_score({"title": title, "description": description}, ticker)
                            
                            if relevance < self.min_relevance_score:
                                continue
                            
                            sentiment_record = {
                                "date": date_obj.strftime("%Y-%m-%d"),
                                "timestamp": date_obj.isoformat(),
                                "open": sentiment["score"],
                                "high": sentiment["score"],
                                "low": sentiment["score"],
                                "close": sentiment["score"],
                                "volume": int(relevance * 100),
                                "source": "yahoo_rss",
                                "ticker": ticker.upper(),
                                "sentiment_label": sentiment["label"],
                                "sentiment_confidence": sentiment["confidence"],
                                "relevance_score": relevance,
                                "title": title[:100],
                                "source_name": "Yahoo Finance",
                                "url": article.get("link", "")
                            }
                            
                            sentiment_data.append(sentiment_record)
                        
                        except Exception as e:
                            logger.warning(f"Error parsing RSS article: {str(e)}")
                            continue
            
            except Exception as e:
                logger.warning(f"Error fetching RSS feed: {str(e)}")
            
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching free news sources for {ticker}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch news-based technical indicators.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of news indicator
            params: Parameters for the indicator
            
        Returns:
            List of news indicator data
        """
        try:
            if indicator_type.lower() == "news_sentiment_trend":
                return await self._fetch_sentiment_trend(ticker, params)
            elif indicator_type.lower() == "news_volume":
                return await self._fetch_news_volume(ticker, params)
            else:
                logger.warning(f"Unsupported news indicator type: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching news indicator {indicator_type} for {ticker}: {str(e)}")
            return []
    
    async def _fetch_sentiment_trend(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch news sentiment trend over time."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            days_back = params.get("days_back", 30)
            start_date = params.get("start_date", (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"))
            
            # Get news sentiment data
            sentiment_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Aggregate by day
            daily_sentiment = {}
            for record in sentiment_data:
                date = record["date"]
                if date not in daily_sentiment:
                    daily_sentiment[date] = {
                        "total_sentiment": 0,
                        "count": 0,
                        "total_relevance": 0
                    }
                
                daily_sentiment[date]["total_sentiment"] += record["close"]
                daily_sentiment[date]["count"] += 1
                daily_sentiment[date]["total_relevance"] += record.get("relevance_score", 0.5)
            
            # Calculate averages
            indicator_data = []
            for date, data in daily_sentiment.items():
                avg_sentiment = data["total_sentiment"] / data["count"] if data["count"] > 0 else 0
                avg_relevance = data["total_relevance"] / data["count"] if data["count"] > 0 else 0
                
                indicator_record = {
                    "date": date,
                    "timestamp": datetime.strptime(date, "%Y-%m-%d").isoformat(),
                    "indicator_type": "NEWS_SENTIMENT_TREND",
                    "ticker": ticker.upper(),
                    "source": "news_sentiment",
                    "values": {
                        "avg_sentiment": avg_sentiment,
                        "avg_relevance": avg_relevance,
                        "article_count": data["count"],
                        "total_sentiment": data["total_sentiment"]
                    }
                }
                
                indicator_data.append(indicator_record)
            
            # Sort by date
            indicator_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(indicator_data)} news sentiment trend records for {ticker}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching news sentiment trend for {ticker}: {str(e)}")
            return []
    
    async def _fetch_news_volume(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch news volume over time."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            days_back = params.get("days_back", 30)
            start_date = params.get("start_date", (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"))
            
            # Get news data
            news_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Count articles by day
            daily_volume = {}
            for record in news_data:
                date = record["date"]
                daily_volume[date] = daily_volume.get(date, 0) + 1
            
            # Create indicator records
            indicator_data = []
            for date, count in daily_volume.items():
                indicator_record = {
                    "date": date,
                    "timestamp": datetime.strptime(date, "%Y-%m-%d").isoformat(),
                    "indicator_type": "NEWS_VOLUME",
                    "ticker": ticker.upper(),
                    "source": "news_sentiment",
                    "values": {
                        "article_count": count,
                        "sources_count": len(set(r.get("source_name", "") for r in news_data if r["date"] == date))
                    }
                }
                
                indicator_data.append(indicator_record)
            
            # Sort by date
            indicator_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(indicator_data)} news volume records for {ticker}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching news volume for {ticker}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch news events.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of news event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of news event data
        """
        try:
            if event_type.lower() == "breaking_news":
                return await self._fetch_breaking_news(ticker, start_date, end_date)
            elif event_type.lower() == "high_impact_news":
                return await self._fetch_high_impact_news(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported news event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching news events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_breaking_news(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch breaking news events."""
        try:
            # Get recent news data
            news_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Filter for high-impact, recent news (breaking news characteristics)
            breaking_threshold = 0.7  # High relevance threshold
            recent_hours = 24  # Consider news from last 24 hours as potentially breaking
            
            current_time = datetime.now()
            event_data = []
            
            for record in news_data:
                try:
                    record_time = datetime.fromisoformat(record["timestamp"].replace("Z", "+00:00"))
                    hours_old = (current_time - record_time).total_seconds() / 3600
                    
                    # Check if it qualifies as breaking news
                    relevance = record.get("relevance_score", 0)
                    high_impact = record.get("high_impact_count", 0) > 0
                    
                    if (relevance > breaking_threshold or high_impact) and hours_old <= recent_hours:
                        event_record = {
                            "date": record["date"],
                            "timestamp": record["timestamp"],
                            "event_type": "breaking_news",
                            "ticker": ticker.upper(),
                            "source": "news_sentiment",
                            "data": {
                                "title": record.get("title", ""),
                                "sentiment_score": record["close"],
                                "sentiment_label": record.get("sentiment_label", ""),
                                "relevance_score": relevance,
                                "source_name": record.get("source_name", ""),
                                "url": record.get("url", ""),
                                "hours_old": hours_old
                            }
                        }
                        
                        event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing breaking news record: {str(e)}")
                    continue
            
            # Sort by relevance and recency
            event_data.sort(key=lambda x: (x["data"]["relevance_score"], -x["data"]["hours_old"]), reverse=True)
            
            logger.info(f"Fetched {len(event_data)} breaking news events for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching breaking news for {ticker}: {str(e)}")
            return []
    
    async def _fetch_high_impact_news(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch high-impact news events."""
        try:
            # Get news data
            news_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            event_data = []
            for record in news_data:
                try:
                    # Check for high-impact indicators
                    high_impact_count = record.get("high_impact_count", 0)
                    sentiment_confidence = record.get("sentiment_confidence", 0)
                    relevance = record.get("relevance_score", 0)
                    
                    # High impact criteria
                    if high_impact_count > 0 and (sentiment_confidence > 0.6 or relevance > 0.8):
                        event_record = {
                            "date": record["date"],
                            "timestamp": record["timestamp"],
                            "event_type": "high_impact_news",
                            "ticker": ticker.upper(),
                            "source": "news_sentiment",
                            "data": {
                                "title": record.get("title", ""),
                                "sentiment_score": record["close"],
                                "sentiment_label": record.get("sentiment_label", ""),
                                "relevance_score": relevance,
                                "high_impact_count": high_impact_count,
                                "sentiment_confidence": sentiment_confidence,
                                "source_name": record.get("source_name", ""),
                                "url": record.get("url", "")
                            }
                        }
                        
                        event_data.append(event_record)
                
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing high-impact news record: {str(e)}")
                    continue
            
            # Sort by impact score
            event_data.sort(key=lambda x: x["data"]["high_impact_count"] * x["data"]["relevance_score"], reverse=True)
            
            logger.info(f"Fetched {len(event_data)} high-impact news events for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching high-impact news for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("News sentiment plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing News sentiment plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "newsapi_key_configured": bool(self.newsapi_key),
            "finnhub_key_configured": bool(self.finnhub_key),
            "marketaux_key_configured": bool(self.marketaux_key),
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "financial_sources": len(self.financial_sources),
            "supported_indicators": ["news_sentiment_trend", "news_volume"],
            "supported_events": ["breaking_news", "high_impact_news"],
            "min_relevance_score": self.min_relevance_score
        }