"""
Reddit sentiment analysis plugin for social media sentiment data.
"""
import asyncio
import aiohttp
import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from .data_source_plugin import DataSourcePlugin

logger = logging.getLogger(__name__)


class RedditSentimentPlugin(DataSourcePlugin):
    """
    Reddit sentiment analysis plugin for social media sentiment data.
    
    Provides access to:
    - Reddit posts and comments sentiment
    - Subreddit activity metrics
    - Trending stocks mentions
    - Social sentiment scores
    
    Uses Reddit API and sentiment analysis libraries.
    """
    
    def __init__(self):
        """Initialize Reddit sentiment plugin."""
        self.name = "RedditSentimentPlugin"
        self.description = "Reddit social sentiment analysis for stock discussions"
        
        # Reddit API endpoints
        self.base_url = "https://www.reddit.com"
        self.oauth_url = "https://oauth.reddit.com"
        
        self.client_id: Optional[str] = None
        self.client_secret: Optional[str] = None
        self.user_agent: str = "DA-KI:v1.0 (by /u/your_username)"
        
        self.session: Optional[aiohttp.ClientSession] = None
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
        
        self.rate_limit_delay = 1.0  # Reddit requires respectful rate limiting
        self.last_call_time = 0
        self.max_retries = 3
        self.timeout = 30
        
        # Target subreddits for stock discussions
        self.stock_subreddits = [
            "stocks",
            "investing", 
            "SecurityAnalysis",
            "ValueInvesting",
            "StockMarket",
            "wallstreetbets",
            "pennystocks",
            "Daytrading",
            "financialindependence",
            "SecurityAnalysis"
        ]
        
        # Sentiment keywords for basic analysis
        self.positive_keywords = [
            "bullish", "buy", "long", "moon", "rocket", "pump", "gains", 
            "profit", "diamond hands", "hold", "strong", "good", "great",
            "excellent", "amazing", "love", "like", "positive", "up", "rise"
        ]
        
        self.negative_keywords = [
            "bearish", "sell", "short", "dump", "loss", "losses", "crash",
            "drop", "fall", "bad", "terrible", "awful", "hate", "dislike",
            "negative", "down", "decline", "weak", "paper hands"
        ]
    
    def get_name(self) -> str:
        """Get plugin name."""
        return self.name
    
    def get_description(self) -> str:
        """Get plugin description."""
        return self.description
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Get configuration schema for Reddit sentiment plugin."""
        return {
            "client_id": {
                "type": "string",
                "description": "Reddit API client ID (create app at reddit.com/prefs/apps)",
                "default": "",
                "required": True,
                "sensitive": True
            },
            "client_secret": {
                "type": "string",
                "description": "Reddit API client secret",
                "default": "",
                "required": True,
                "sensitive": True
            },
            "user_agent": {
                "type": "string",
                "description": "User agent string for Reddit API requests",
                "default": "DA-KI:v1.0 (by /u/your_username)",
                "required": True
            },
            "rate_limit_delay": {
                "type": "number",
                "description": "Delay between API calls in seconds (Reddit guidelines: max 60 requests/minute)",
                "default": 1.0,
                "min": 0.5,
                "max": 10.0
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
            "target_subreddits": {
                "type": "array",
                "description": "List of subreddits to monitor for stock discussions",
                "default": ["stocks", "investing", "SecurityAnalysis"],
                "items": {"type": "string"}
            },
            "enable_sentiment_analysis": {
                "type": "boolean",
                "description": "Enable advanced sentiment analysis (requires additional libraries)",
                "default": True
            },
            "min_post_score": {
                "type": "integer",
                "description": "Minimum post score to include in analysis",
                "default": 10,
                "min": 0
            }
        }
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize plugin with configuration."""
        try:
            self.client_id = config.get("client_id")
            self.client_secret = config.get("client_secret")
            
            if not self.client_id or not self.client_secret:
                raise ValueError("Reddit API client ID and secret are required")
            
            self.user_agent = config.get("user_agent", self.user_agent)
            self.rate_limit_delay = config.get("rate_limit_delay", 1.0)
            self.max_retries = config.get("max_retries", 3)
            self.timeout = config.get("timeout", 30)
            
            # Update target subreddits if provided
            target_subreddits = config.get("target_subreddits")
            if target_subreddits:
                self.stock_subreddits = target_subreddits
            
            self.min_post_score = config.get("min_post_score", 10)
            
            # Create aiohttp session
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            headers = {"User-Agent": self.user_agent}
            self.session = aiohttp.ClientSession(timeout=timeout, headers=headers)
            
            logger.info(f"Reddit sentiment plugin initialized with rate limit: {self.rate_limit_delay}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit sentiment plugin: {str(e)}")
            raise
    
    async def _get_access_token(self) -> str:
        """Get OAuth access token for Reddit API."""
        if self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at:
            return self.access_token
        
        try:
            auth = aiohttp.BasicAuth(self.client_id, self.client_secret)
            data = {
                "grant_type": "client_credentials"
            }
            
            async with self.session.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=auth,
                data=data
            ) as response:
                if response.status == 200:
                    token_data = await response.json()
                    self.access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
                    
                    logger.info("Successfully obtained Reddit access token")
                    return self.access_token
                else:
                    text = await response.text()
                    raise aiohttp.ClientError(f"Failed to get Reddit token: {response.status} {text}")
        
        except Exception as e:
            logger.error(f"Error getting Reddit access token: {str(e)}")
            raise
    
    async def _rate_limited_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make rate-limited API request to Reddit."""
        if not self.session:
            raise RuntimeError("Plugin not initialized")
        
        # Get access token
        token = await self._get_access_token()
        
        # Rate limiting
        current_time = asyncio.get_event_loop().time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last_call
            await asyncio.sleep(sleep_time)
        
        # Prepare headers
        headers = {
            "Authorization": f"bearer {token}",
            "User-Agent": self.user_agent
        }
        
        url = f"{self.oauth_url}{endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Reddit API request (attempt {attempt + 1}): {endpoint}")
                
                async with self.session.get(url, params=params, headers=headers) as response:
                    self.last_call_time = asyncio.get_event_loop().time()
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    
                    elif response.status == 429:
                        # Rate limit exceeded
                        wait_time = (attempt + 1) * 30
                        logger.warning(f"Reddit rate limit exceeded, waiting {wait_time} seconds")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status == 401:
                        # Token expired, refresh and retry
                        self.access_token = None
                        if attempt < self.max_retries - 1:
                            token = await self._get_access_token()
                            headers["Authorization"] = f"bearer {token}"
                            continue
                        else:
                            raise ValueError("Reddit API unauthorized")
                    
                    else:
                        text = await response.text()
                        raise aiohttp.ClientError(f"HTTP {response.status}: {text[:200]}")
            
            except asyncio.TimeoutError:
                logger.warning(f"Reddit request timeout (attempt {attempt + 1})")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 5)
            
            except Exception as e:
                logger.error(f"Reddit request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep((attempt + 1) * 2)
        
        raise RuntimeError(f"Reddit request failed after {self.max_retries} attempts")
    
    def _calculate_basic_sentiment(self, text: str) -> Dict[str, Any]:
        """Calculate basic sentiment score using keyword analysis."""
        text_lower = text.lower()
        
        positive_count = sum(1 for keyword in self.positive_keywords if keyword in text_lower)
        negative_count = sum(1 for keyword in self.negative_keywords if keyword in text_lower)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            sentiment_score = 0.0
            sentiment_label = "neutral"
        else:
            sentiment_score = (positive_count - negative_count) / total_sentiment_words
            if sentiment_score > 0.2:
                sentiment_label = "positive"
            elif sentiment_score < -0.2:
                sentiment_label = "negative"
            else:
                sentiment_label = "neutral"
        
        return {
            "score": sentiment_score,
            "label": sentiment_label,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "confidence": min(total_sentiment_words / 10, 1.0)  # Confidence based on number of sentiment words
        }
    
    def _extract_ticker_mentions(self, text: str) -> List[str]:
        """Extract stock ticker mentions from text."""
        # Pattern for stock tickers (1-5 uppercase letters, often preceded by $)
        ticker_pattern = r'\$?([A-Z]{1,5})(?=\s|$|[^\w])'
        
        matches = re.findall(ticker_pattern, text.upper())
        
        # Filter out common words that might match the pattern
        common_words = {
            "THE", "AND", "OR", "BUT", "FOR", "NOT", "TO", "OF", "IN", "ON", "AT", "BY",
            "UP", "DOWN", "OUT", "ALL", "ANY", "SO", "IF", "IT", "IS", "AM", "ARE", "WAS",
            "WERE", "BE", "BEEN", "HAVE", "HAS", "HAD", "DO", "DOES", "DID", "WILL", "WOULD",
            "COULD", "SHOULD", "MAY", "MIGHT", "CAN", "MUST", "GET", "GOT", "GO", "GOES",
            "WENT", "COME", "CAME", "SEE", "SAW", "TAKE", "TOOK", "GIVE", "GAVE", "MAKE",
            "MADE", "THINK", "THOUGHT", "KNOW", "KNEW", "WANT", "LIKE", "LOVE", "HATE",
            "GOOD", "BAD", "BIG", "SMALL", "NEW", "OLD", "LONG", "SHORT", "HIGH", "LOW",
            "BEST", "WORST", "MORE", "MOST", "LESS", "LEAST", "VERY", "TOO", "NOW", "THEN",
            "HERE", "THERE", "THIS", "THAT", "THESE", "THOSE", "WHO", "WHAT", "WHEN",
            "WHERE", "WHY", "HOW", "YES", "NO", "OK", "LOL", "OMG", "WTF", "FUD", "HODL",
            "BUY", "SELL", "PUMP", "DUMP", "MOON", "YOLO", "DD"
        }
        
        # Filter out common words and return unique tickers
        valid_tickers = [ticker for ticker in matches if ticker not in common_words and len(ticker) >= 2]
        return list(set(valid_tickers))
    
    async def fetch_ohlcv_data(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        interval: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Reddit doesn't provide OHLCV data, but sentiment time series.
        
        Args:
            ticker: Stock ticker symbol to search for
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Aggregation interval
            
        Returns:
            List of sentiment data in OHLCV-like format
        """
        try:
            sentiment_data = []
            
            # Search for posts mentioning the ticker across target subreddits
            for subreddit in self.stock_subreddits:
                posts = await self._search_subreddit_posts(subreddit, ticker, start_date, end_date)
                
                for post in posts:
                    sentiment_data.append({
                        "date": post["date"],
                        "timestamp": post["timestamp"],
                        "open": post["sentiment_score"],  # Use sentiment as price proxy
                        "high": post["sentiment_score"],
                        "low": post["sentiment_score"],
                        "close": post["sentiment_score"],
                        "volume": post["engagement_score"],  # Use engagement as volume proxy
                        "source": "reddit_sentiment",
                        "ticker": ticker.upper(),
                        "subreddit": subreddit,
                        "sentiment_label": post["sentiment_label"],
                        "post_id": post["post_id"],
                        "title": post["title"][:100]  # Truncated title
                    })
            
            # Sort by timestamp
            sentiment_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(sentiment_data)} Reddit sentiment records for {ticker}")
            return sentiment_data
        
        except Exception as e:
            logger.error(f"Error fetching Reddit sentiment data for {ticker}: {str(e)}")
            return []
    
    async def _search_subreddit_posts(self, subreddit: str, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Search for posts mentioning a ticker in a specific subreddit."""
        try:
            # Reddit search endpoint
            endpoint = f"/r/{subreddit}/search"
            params = {
                "q": f"${ticker} OR {ticker}",
                "restrict_sr": "true",
                "sort": "new",
                "limit": 25,
                "type": "link"
            }
            
            data = await self._rate_limited_request(endpoint, params)
            
            if not data or "data" not in data or "children" not in data["data"]:
                return []
            
            posts = []
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            
            for child in data["data"]["children"]:
                try:
                    post_data = child["data"]
                    
                    # Parse post creation time
                    created_utc = post_data.get("created_utc", 0)
                    post_date = datetime.fromtimestamp(created_utc)
                    
                    # Filter by date range
                    if not (start_dt <= post_date <= end_dt):
                        continue
                    
                    # Check if post score meets minimum threshold
                    score = post_data.get("score", 0)
                    if score < self.min_post_score:
                        continue
                    
                    # Extract text for sentiment analysis
                    title = post_data.get("title", "")\n                    selftext = post_data.get("selftext", "")
                    full_text = f"{title} {selftext}"
                    
                    # Check if ticker is actually mentioned
                    mentioned_tickers = self._extract_ticker_mentions(full_text)
                    if ticker.upper() not in mentioned_tickers:
                        continue
                    
                    # Calculate sentiment
                    sentiment = self._calculate_basic_sentiment(full_text)
                    
                    # Calculate engagement score (combination of score, comments, etc.)
                    num_comments = post_data.get("num_comments", 0)
                    upvote_ratio = post_data.get("upvote_ratio", 0.5)
                    engagement_score = score * upvote_ratio + num_comments * 0.5
                    
                    post_record = {
                        "date": post_date.strftime("%Y-%m-%d"),
                        "timestamp": post_date.isoformat(),
                        "post_id": post_data.get("id", ""),
                        "title": title,
                        "author": post_data.get("author", ""),
                        "score": score,
                        "num_comments": num_comments,
                        "upvote_ratio": upvote_ratio,
                        "engagement_score": engagement_score,
                        "sentiment_score": sentiment["score"],
                        "sentiment_label": sentiment["label"],
                        "sentiment_confidence": sentiment["confidence"],
                        "mentioned_tickers": mentioned_tickers,
                        "url": post_data.get("url", ""),
                        "permalink": f"https://reddit.com{post_data.get('permalink', '')}"
                    }
                    
                    posts.append(post_record)
                
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Error parsing Reddit post: {str(e)}")
                    continue
            
            return posts
        
        except Exception as e:
            logger.error(f"Error searching subreddit {subreddit} for {ticker}: {str(e)}")
            return []
    
    async def fetch_technical_indicators(
        self,
        ticker: str,
        indicator_type: str,
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Fetch sentiment-based indicators.
        
        Args:
            ticker: Stock ticker symbol
            indicator_type: Type of sentiment indicator
            params: Parameters for the indicator
            
        Returns:
            List of sentiment indicator data
        """
        try:
            if indicator_type.lower() == "sentiment_trend":
                return await self._fetch_sentiment_trend(ticker, params)
            elif indicator_type.lower() == "mention_volume":
                return await self._fetch_mention_volume(ticker, params)
            else:
                logger.warning(f"Unsupported Reddit indicator type: {indicator_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching Reddit indicator {indicator_type} for {ticker}: {str(e)}")
            return []
    
    async def _fetch_sentiment_trend(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch sentiment trend over time."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            days_back = params.get("days_back", 30)
            start_date = params.get("start_date", (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"))
            
            # Get sentiment data
            sentiment_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Aggregate by day
            daily_sentiment = {}
            for record in sentiment_data:
                date = record["date"]
                if date not in daily_sentiment:
                    daily_sentiment[date] = {
                        "total_sentiment": 0,
                        "count": 0,
                        "total_engagement": 0
                    }
                
                daily_sentiment[date]["total_sentiment"] += record["close"]
                daily_sentiment[date]["count"] += 1
                daily_sentiment[date]["total_engagement"] += record["volume"]
            
            # Calculate averages
            indicator_data = []
            for date, data in daily_sentiment.items():
                avg_sentiment = data["total_sentiment"] / data["count"] if data["count"] > 0 else 0
                avg_engagement = data["total_engagement"] / data["count"] if data["count"] > 0 else 0
                
                indicator_record = {
                    "date": date,
                    "timestamp": datetime.strptime(date, "%Y-%m-%d").isoformat(),
                    "indicator_type": "SENTIMENT_TREND",
                    "ticker": ticker.upper(),
                    "source": "reddit_sentiment",
                    "values": {
                        "avg_sentiment": avg_sentiment,
                        "avg_engagement": avg_engagement,
                        "post_count": data["count"],
                        "total_engagement": data["total_engagement"]
                    }
                }
                
                indicator_data.append(indicator_record)
            
            # Sort by date
            indicator_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(indicator_data)} sentiment trend records for {ticker}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching sentiment trend for {ticker}: {str(e)}")
            return []
    
    async def _fetch_mention_volume(self, ticker: str, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fetch mention volume over time."""
        try:
            end_date = params.get("end_date", datetime.now().strftime("%Y-%m-%d"))
            days_back = params.get("days_back", 30)
            start_date = params.get("start_date", (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d"))
            
            # Get sentiment data
            sentiment_data = await self.fetch_ohlcv_data(ticker, start_date, end_date)
            
            # Count mentions by day
            daily_mentions = {}
            for record in sentiment_data:
                date = record["date"]
                daily_mentions[date] = daily_mentions.get(date, 0) + 1
            
            # Create indicator records
            indicator_data = []
            for date, count in daily_mentions.items():
                indicator_record = {
                    "date": date,
                    "timestamp": datetime.strptime(date, "%Y-%m-%d").isoformat(),
                    "indicator_type": "MENTION_VOLUME",
                    "ticker": ticker.upper(),
                    "source": "reddit_sentiment",
                    "values": {
                        "mention_count": count,
                        "subreddit_count": len(self.stock_subreddits)
                    }
                }
                
                indicator_data.append(indicator_record)
            
            # Sort by date
            indicator_data.sort(key=lambda x: x["timestamp"])
            
            logger.info(f"Fetched {len(indicator_data)} mention volume records for {ticker}")
            return indicator_data
        
        except Exception as e:
            logger.error(f"Error fetching mention volume for {ticker}: {str(e)}")
            return []
    
    async def fetch_event_data(
        self,
        ticker: str,
        event_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch social media events from Reddit.
        
        Args:
            ticker: Stock ticker symbol
            event_type: Type of social event
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of social event data
        """
        try:
            if event_type.lower() == "viral_posts":
                return await self._fetch_viral_posts(ticker, start_date, end_date)
            elif event_type.lower() == "dd_posts":
                return await self._fetch_dd_posts(ticker, start_date, end_date)
            else:
                logger.warning(f"Unsupported Reddit event type: {event_type}")
                return []
        
        except Exception as e:
            logger.error(f"Error fetching Reddit events for {ticker}: {str(e)}")
            return []
    
    async def _fetch_viral_posts(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch viral posts about the ticker."""
        try:
            event_data = []
            
            for subreddit in self.stock_subreddits:
                posts = await self._search_subreddit_posts(subreddit, ticker, start_date, end_date)
                
                # Filter for viral posts (high engagement)
                viral_threshold = 100  # Minimum score for viral posts
                viral_posts = [post for post in posts if post["engagement_score"] > viral_threshold]
                
                for post in viral_posts:
                    event_record = {
                        "date": post["date"],
                        "timestamp": post["timestamp"],
                        "event_type": "viral_post",
                        "ticker": ticker.upper(),
                        "source": "reddit_sentiment",
                        "data": {
                            "post_id": post["post_id"],
                            "title": post["title"],
                            "subreddit": subreddit,
                            "score": post["score"],
                            "engagement_score": post["engagement_score"],
                            "sentiment_score": post["sentiment_score"],
                            "sentiment_label": post["sentiment_label"],
                            "permalink": post["permalink"]
                        }
                    }
                    
                    event_data.append(event_record)
            
            # Sort by engagement score
            event_data.sort(key=lambda x: x["data"]["engagement_score"], reverse=True)
            
            logger.info(f"Fetched {len(event_data)} viral posts for {ticker}")
            return event_data
        
        except Exception as e:
            logger.error(f"Error fetching viral posts for {ticker}: {str(e)}")
            return []
    
    async def _fetch_dd_posts(self, ticker: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch due diligence (DD) posts about the ticker."""
        try:
            event_data = []
            
            # Search for DD posts specifically
            dd_keywords = ["DD", "due diligence", "analysis", "research", "deep dive"]
            
            for subreddit in self.stock_subreddits:
                for keyword in dd_keywords:
                    endpoint = f"/r/{subreddit}/search"
                    params = {
                        "q": f"{keyword} {ticker}",
                        "restrict_sr": "true",
                        "sort": "relevance",
                        "limit": 10,
                        "type": "link"
                    }
                    
                    try:
                        data = await self._rate_limited_request(endpoint, params)
                        
                        if not data or "data" not in data:
                            continue
                        
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                        
                        for child in data["data"]["children"]:
                            post_data = child["data"]
                            
                            created_utc = post_data.get("created_utc", 0)
                            post_date = datetime.fromtimestamp(created_utc)
                            
                            if not (start_dt <= post_date <= end_dt):
                                continue
                            
                            title = post_data.get("title", "").lower()
                            if any(kw.lower() in title for kw in dd_keywords):
                                event_record = {
                                    "date": post_date.strftime("%Y-%m-%d"),
                                    "timestamp": post_date.isoformat(),
                                    "event_type": "dd_post",
                                    "ticker": ticker.upper(),
                                    "source": "reddit_sentiment",
                                    "data": {
                                        "post_id": post_data.get("id", ""),
                                        "title": post_data.get("title", ""),
                                        "subreddit": subreddit,
                                        "score": post_data.get("score", 0),
                                        "num_comments": post_data.get("num_comments", 0),
                                        "author": post_data.get("author", ""),
                                        "permalink": f"https://reddit.com{post_data.get('permalink', '')}"
                                    }
                                }
                                
                                event_data.append(event_record)
                    
                    except Exception as e:
                        logger.warning(f"Error searching for DD posts in {subreddit}: {str(e)}")
                        continue
            
            # Remove duplicates and sort by score
            seen_ids = set()
            unique_events = []
            for event in event_data:
                post_id = event["data"]["post_id"]
                if post_id not in seen_ids:
                    seen_ids.add(post_id)
                    unique_events.append(event)
            
            unique_events.sort(key=lambda x: x["data"]["score"], reverse=True)
            
            logger.info(f"Fetched {len(unique_events)} DD posts for {ticker}")
            return unique_events
        
        except Exception as e:
            logger.error(f"Error fetching DD posts for {ticker}: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Close the plugin and cleanup resources."""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            logger.info("Reddit sentiment plugin closed successfully")
        except Exception as e:
            logger.error(f"Error closing Reddit sentiment plugin: {str(e)}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current plugin status."""
        return {
            "name": self.name,
            "status": "active" if self.session and not self.session.closed else "inactive",
            "client_id_configured": bool(self.client_id),
            "access_token_valid": bool(self.access_token and self.token_expires_at and datetime.now() < self.token_expires_at),
            "rate_limit_delay": self.rate_limit_delay,
            "last_call_time": self.last_call_time,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            "target_subreddits": self.stock_subreddits,
            "supported_indicators": ["sentiment_trend", "mention_volume"],
            "supported_events": ["viral_posts", "dd_posts"],
            "min_post_score": self.min_post_score
        }