#!/usr/bin/env python3
"""
🔄 Yahoo Finance API Integration für DA-KI
Real-time Kursdaten mit Fallback-Mechanismus

Entwickelt mit Claude Code - Real-time Data Pipeline Implementation
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import time
import logging
from dataclasses import dataclass
from enum import Enum
import json
import random
import sys
import os

# Optional pandas import for historical data
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Add caching path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'caching'))

# Optional Redis caching
try:
    from redis_manager import SmartRedisManager, CacheStrategy
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    SmartRedisManager = None
    CacheStrategy = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIStatus(Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    DOWN = "down"
    FALLBACK = "fallback"

@dataclass
class StockData:
    """Standardisiertes Datenmodell für Aktieninformationen"""
    symbol: str
    name: str
    current_price: float
    previous_close: float
    change_amount: float
    change_percent: float
    volume: int
    market_cap: Optional[str] = None
    pe_ratio: Optional[float] = None
    high_52w: Optional[float] = None
    low_52w: Optional[float] = None
    timestamp: datetime = None
    source: str = "yahoo_finance"
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class YahooFinanceClient:
    """
    Enhanced Yahoo Finance API Client mit:
    - Rate Limiting (200 requests/hour)
    - Automatic Fallback zu Alpha Vantage
    - Error Handling & Retries
    - AsyncIO für parallele Requests
    """
    
    def __init__(self, enable_redis_cache: bool = True):
        self.base_url = "https://query1.finance.yahoo.com/v8/finance/chart"
        self.search_url = "https://query1.finance.yahoo.com/v1/finance/search"
        self.quote_url = "https://query1.finance.yahoo.com/v7/finance/quote"
        
        # Rate Limiting
        self.requests_per_hour = 200
        self.request_timestamps = []
        self.status = APIStatus.ACTIVE
        
        # Session für Connection Pooling
        self.session = None
        
        # Fallback API Keys (Alpha Vantage)
        self.alpha_vantage_key = "demo"  # Replace with actual key
        self.fallback_active = False
        
        # Smart Redis Caching
        self.enable_redis_cache = enable_redis_cache and HAS_REDIS
        self.redis_cache = None
        
        # Legacy cache für häufige Anfragen (fallback)
        self.cache = {}
        self.cache_duration = 60  # 1 Minute Cache
        
    async def __aenter__(self):
        """Async Context Manager Entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Initialize Redis Cache
        if self.enable_redis_cache:
            try:
                self.redis_cache = SmartRedisManager(namespace="yahoo_finance")
                await self.redis_cache.initialize()
                logger.info("✅ Redis caching enabled for Yahoo Finance")
            except Exception as e:
                logger.warning(f"⚠️  Redis cache initialization failed: {e}")
                self.redis_cache = None
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager Exit"""
        if self.session:
            await self.session.close()
        if self.redis_cache:
            await self.redis_cache.close()
    
    def _check_rate_limit(self) -> bool:
        """Prüfe Rate Limit (200 requests/hour)"""
        now = time.time()
        # Entferne Requests die älter als 1 Stunde sind
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if now - ts < 3600
        ]
        
        if len(self.request_timestamps) >= self.requests_per_hour:
            self.status = APIStatus.RATE_LIMITED
            return False
        
        self.request_timestamps.append(now)
        return True
    
    def _get_cache_key(self, symbol: str, data_type: str = "quote") -> str:
        """Generiere Cache-Schlüssel"""
        return f"{symbol}_{data_type}_{int(time.time() / self.cache_duration)}"
    
    async def _make_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Sichere HTTP-Anfrage mit Error Handling"""
        if not self._check_rate_limit():
            logger.warning("Rate limit erreicht, verwende Fallback")
            return None
            
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 429:
                    self.status = APIStatus.RATE_LIMITED
                    logger.warning(f"Rate limited by Yahoo Finance: {response.status}")
                else:
                    logger.error(f"Yahoo Finance API error: {response.status}")
                    
        except asyncio.TimeoutError:
            logger.error("Timeout bei Yahoo Finance Anfrage")
        except Exception as e:
            logger.error(f"Fehler bei Yahoo Finance Anfrage: {e}")
            
        return None
    
    async def get_stock_quote(self, symbol: str) -> Optional[StockData]:
        """
        Hole aktuelle Kursinformationen für eine Aktie mit Smart Caching
        """
        cache_key = f"quote:{symbol}"
        
        # Prüfe Redis Cache (L1 + L2)
        if self.redis_cache:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                logger.debug(f"Redis Cache HIT: {symbol}")
                return StockData(**cached_data)
        
        # Prüfe Legacy Cache (Fallback)
        legacy_cache_key = self._get_cache_key(symbol, "quote")
        if legacy_cache_key in self.cache:
            logger.debug(f"Legacy Cache HIT: {symbol}")
            return self.cache[legacy_cache_key]
        
        # Yahoo Finance Anfrage
        params = {
            'symbols': symbol,
            'fields': 'symbol,longName,regularMarketPrice,regularMarketPreviousClose,'
                     'regularMarketChange,regularMarketChangePercent,regularMarketVolume,'
                     'marketCap,trailingPE,fiftyTwoWeekHigh,fiftyTwoWeekLow'
        }
        
        data = await self._make_request(self.quote_url, params)
        
        if data and 'quoteResponse' in data:
            quotes = data['quoteResponse'].get('result', [])
            if quotes:
                quote = quotes[0]
                
                stock_data = StockData(
                    symbol=quote.get('symbol', symbol),
                    name=quote.get('longName', f'{symbol} Corp.'),
                    current_price=quote.get('regularMarketPrice', 0),
                    previous_close=quote.get('regularMarketPreviousClose', 0),
                    change_amount=quote.get('regularMarketChange', 0),
                    change_percent=quote.get('regularMarketChangePercent', 0),
                    volume=quote.get('regularMarketVolume', 0),
                    market_cap=self._format_market_cap(quote.get('marketCap')),
                    pe_ratio=quote.get('trailingPE'),
                    high_52w=quote.get('fiftyTwoWeekHigh'),
                    low_52w=quote.get('fiftyTwoWeekLow'),
                    source="yahoo_finance"
                )
                
                # Smart Cache speichern (Redis + Legacy)
                await self._cache_stock_data(cache_key, stock_data)
                return stock_data
        
        # Fallback zu simulierten Daten
        fallback_data = await self._fallback_stock_data(symbol)
        if fallback_data:
            await self._cache_stock_data(cache_key, fallback_data)
        return fallback_data
    
    async def _cache_stock_data(self, cache_key: str, stock_data: StockData):
        """Smart cache storage mit Redis + Legacy fallback"""
        try:
            # Redis Cache (L1 + L2) - 5 min TTL
            if self.redis_cache:
                # Convert StockData to dict for JSON serialization
                data_dict = {
                    'symbol': stock_data.symbol,
                    'name': stock_data.name,
                    'current_price': stock_data.current_price,
                    'previous_close': stock_data.previous_close,
                    'change_amount': stock_data.change_amount,
                    'change_percent': stock_data.change_percent,
                    'volume': stock_data.volume,
                    'market_cap': stock_data.market_cap,
                    'pe_ratio': stock_data.pe_ratio,
                    'high_52w': stock_data.high_52w,
                    'low_52w': stock_data.low_52w,
                    'timestamp': stock_data.timestamp.isoformat(),
                    'source': stock_data.source
                }
                
                await self.redis_cache.set(
                    cache_key, 
                    data_dict, 
                    ttl=300,  # 5 minutes
                    strategy=CacheStrategy.WRITE_THROUGH
                )
                logger.debug(f"Redis Cache SET: {cache_key}")
            
            # Legacy Cache fallback
            legacy_cache_key = self._get_cache_key(stock_data.symbol, "quote")
            self.cache[legacy_cache_key] = stock_data
            
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
            # Always fall back to legacy cache
            legacy_cache_key = self._get_cache_key(stock_data.symbol, "quote")
            self.cache[legacy_cache_key] = stock_data
    
    async def get_multiple_quotes(self, symbols: List[str]) -> Dict[str, StockData]:
        """
        Parallele Abfrage mehrerer Aktien mit Smart Caching
        Optimiert für 467 deutsche Aktien
        """
        logger.info(f"Lade Kursdaten für {len(symbols)} Aktien mit Smart Caching...")
        start_time = time.time()
        
        all_results = {}
        cache_hits = 0
        api_requests = 0
        
        # Phase 1: Cache Lookup für alle Symbole
        if self.redis_cache:
            cache_tasks = [
                self._get_cached_quote(symbol) for symbol in symbols
            ]
            cache_results = await asyncio.gather(*cache_tasks, return_exceptions=True)
            
            for symbol, cached_result in zip(symbols, cache_results):
                if isinstance(cached_result, StockData):
                    all_results[symbol] = cached_result
                    cache_hits += 1
                    logger.debug(f"Cache HIT: {symbol}")
        
        # Phase 2: API Requests für Cache Misses
        missing_symbols = [s for s in symbols if s not in all_results]
        
        if missing_symbols:
            logger.info(f"Cache misses: {len(missing_symbols)}, API requests needed")
            
            # Batch-Processing in Gruppen von 20 (Yahoo Finance Limit)
            batch_size = 20
            
            for i in range(0, len(missing_symbols), batch_size):
                batch = missing_symbols[i:i + batch_size]
                
                # Parallele Verarbeitung innerhalb der Gruppe
                tasks = [self._fetch_stock_quote(symbol) for symbol in batch]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Ergebnisse sammeln
                for symbol, result in zip(batch, results):
                    if isinstance(result, StockData):
                        all_results[symbol] = result
                        api_requests += 1
                    else:
                        logger.warning(f"Fehler bei {symbol}: {result}")
                        # Fallback für fehlgeschlagene Requests
                        fallback_data = await self._fallback_stock_data(symbol)
                        all_results[symbol] = fallback_data
                        await self._cache_stock_data(f"quote:{symbol}", fallback_data)
                
                # Rate Limiting: Kurze Pause zwischen Batches
                if i + batch_size < len(missing_symbols):
                    await asyncio.sleep(0.1)
                    
                # Progress Logging
                progress = min(i + batch_size, len(missing_symbols))
                logger.info(f"Fortschritt: {progress}/{len(missing_symbols)} API requests")
        
        duration = time.time() - start_time
        cache_hit_rate = (cache_hits / len(symbols)) * 100 if symbols else 0
        
        logger.info(f"✅ Erfolgreich {len(all_results)} Aktien geladen in {duration:.2f}s")
        logger.info(f"📊 Cache Hit Rate: {cache_hit_rate:.1f}% ({cache_hits} hits, {api_requests} API calls)")
        
        return all_results
    
    async def _get_cached_quote(self, symbol: str) -> Optional[StockData]:
        """Hole Quote aus Cache (Redis oder Legacy)"""
        cache_key = f"quote:{symbol}"
        
        # Redis Cache
        if self.redis_cache:
            cached_data = await self.redis_cache.get(cache_key)
            if cached_data:
                return StockData(**cached_data)
        
        # Legacy Cache
        legacy_cache_key = self._get_cache_key(symbol, "quote")
        if legacy_cache_key in self.cache:
            return self.cache[legacy_cache_key]
        
        return None
    
    async def _fetch_stock_quote(self, symbol: str) -> Optional[StockData]:
        """Hole Quote direkt von API (ohne Cache Check)"""
        cache_key = f"quote:{symbol}"
        
        # Yahoo Finance Anfrage
        params = {
            'symbols': symbol,
            'fields': 'symbol,longName,regularMarketPrice,regularMarketPreviousClose,'
                     'regularMarketChange,regularMarketChangePercent,regularMarketVolume,'
                     'marketCap,trailingPE,fiftyTwoWeekHigh,fiftyTwoWeekLow'
        }
        
        data = await self._make_request(self.quote_url, params)
        
        if data and 'quoteResponse' in data:
            quotes = data['quoteResponse'].get('result', [])
            if quotes:
                quote = quotes[0]
                
                stock_data = StockData(
                    symbol=quote.get('symbol', symbol),
                    name=quote.get('longName', f'{symbol} Corp.'),
                    current_price=quote.get('regularMarketPrice', 0),
                    previous_close=quote.get('regularMarketPreviousClose', 0),
                    change_amount=quote.get('regularMarketChange', 0),
                    change_percent=quote.get('regularMarketChangePercent', 0),
                    volume=quote.get('regularMarketVolume', 0),
                    market_cap=self._format_market_cap(quote.get('marketCap')),
                    pe_ratio=quote.get('trailingPE'),
                    high_52w=quote.get('fiftyTwoWeekHigh'),
                    low_52w=quote.get('fiftyTwoWeekLow'),
                    source="yahoo_finance"
                )
                
                # Cache speichern
                await self._cache_stock_data(cache_key, stock_data)
                return stock_data
        
        return None
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> Optional[Dict]:
        """
        Hole historische Kursdaten
        period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        """
        url = f"{self.base_url}/{symbol}"
        params = {
            'period1': int((datetime.now() - self._period_to_timedelta(period)).timestamp()),
            'period2': int(datetime.now().timestamp()),
            'interval': '1d',
            'includePrePost': 'false'
        }
        
        data = await self._make_request(url, params)
        
        if data and 'chart' in data:
            chart_data = data['chart']['result'][0]
            timestamps = chart_data['timestamp']
            quotes = chart_data['indicators']['quote'][0]
            
            if HAS_PANDAS:
                df = pd.DataFrame({
                    'date': [datetime.fromtimestamp(ts) for ts in timestamps],
                    'open': quotes['open'],
                    'high': quotes['high'],
                    'low': quotes['low'],
                    'close': quotes['close'],
                    'volume': quotes['volume']
                })
                return df.dropna()
            else:
                # Return as dict if pandas not available
                return {
                    'dates': [datetime.fromtimestamp(ts).isoformat() for ts in timestamps],
                    'opens': quotes['open'],
                    'highs': quotes['high'],
                    'lows': quotes['low'],
                    'closes': quotes['close'],
                    'volumes': quotes['volume']
                }
        
        return None
    
    def _period_to_timedelta(self, period: str) -> timedelta:
        """Konvertiere Periode zu timedelta"""
        period_map = {
            '1d': timedelta(days=1),
            '5d': timedelta(days=5),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730),
            '5y': timedelta(days=1825),
            '10y': timedelta(days=3650),
        }
        return period_map.get(period, timedelta(days=30))
    
    def _format_market_cap(self, market_cap: Optional[float]) -> Optional[str]:
        """Formatiere Marktkapitalisierung"""
        if market_cap is None:
            return None
            
        if market_cap >= 1e12:
            return f"{market_cap/1e12:.1f}T"
        elif market_cap >= 1e9:
            return f"{market_cap/1e9:.1f}B"
        elif market_cap >= 1e6:
            return f"{market_cap/1e6:.1f}M"
        else:
            return f"{market_cap:.0f}"
    
    async def _fallback_stock_data(self, symbol: str) -> StockData:
        """
        Fallback zu Alpha Vantage oder simulierten Daten
        """
        # Versuche Alpha Vantage falls verfügbar
        if not self.fallback_active and self.alpha_vantage_key != "demo":
            try:
                return await self._alpha_vantage_quote(symbol)
            except:
                self.fallback_active = True
        
        # Simulierte Daten als letzter Fallback
        return self._generate_mock_data(symbol)
    
    async def _alpha_vantage_quote(self, symbol: str) -> StockData:
        """Alpha Vantage Fallback API"""
        url = "https://www.alphavantage.co/query"
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key
        }
        
        data = await self._make_request(url, params)
        
        if data and 'Global Quote' in data:
            quote = data['Global Quote']
            
            current_price = float(quote.get('05. price', 0))
            previous_close = float(quote.get('08. previous close', 0))
            change_amount = current_price - previous_close
            change_percent = (change_amount / previous_close * 100) if previous_close > 0 else 0
            
            return StockData(
                symbol=quote.get('01. symbol', symbol),
                name=f"{symbol} Corp.",
                current_price=current_price,
                previous_close=previous_close,
                change_amount=change_amount,
                change_percent=change_percent,
                volume=int(quote.get('06. volume', 0)),
                source="alpha_vantage"
            )
        
        # Fallback zu Mock-Daten
        return self._generate_mock_data(symbol)
    
    def _generate_mock_data(self, symbol: str) -> StockData:
        """Generiere realistische Mock-Daten für Fallback"""
        # Basis-Preis zwischen 20-500€
        base_price = random.uniform(20, 500)
        
        # Realistische Tagesänderung (-5% bis +5%)
        change_percent = random.uniform(-5, 5)
        change_amount = base_price * (change_percent / 100)
        current_price = base_price + change_amount
        
        # Volume zwischen 100K und 10M
        volume = random.randint(100000, 10000000)
        
        return StockData(
            symbol=symbol,
            name=f"{symbol} Corp.",
            current_price=round(current_price, 2),
            previous_close=round(base_price, 2),
            change_amount=round(change_amount, 2),
            change_percent=round(change_percent, 2),
            volume=volume,
            market_cap=self._format_market_cap(current_price * random.randint(1000000, 100000000)),
            pe_ratio=round(random.uniform(10, 50), 1),
            source="mock_data"
        )
    
    def get_status(self) -> Dict[str, Any]:
        """API Status und Statistiken mit Cache Metrics"""
        status = {
            "status": self.status.value,
            "requests_last_hour": len(self.request_timestamps),
            "rate_limit": self.requests_per_hour,
            "legacy_cache_entries": len(self.cache),
            "fallback_active": self.fallback_active,
            "redis_cache_enabled": self.redis_cache is not None,
            "last_update": datetime.now().isoformat()
        }
        
        # Redis Cache Metrics
        if self.redis_cache:
            cache_metrics = self.redis_cache.get_metrics()
            status["redis_cache_metrics"] = cache_metrics
        
        return status

class RealTimeDataManager:
    """
    Real-time Data Manager für kontinuierliche Kursdatenaktualisierung
    """
    
    def __init__(self, symbols: List[str], update_interval: int = 60):
        self.symbols = symbols
        self.update_interval = update_interval  # Sekunden
        self.yahoo_client = YahooFinanceClient()
        self.is_running = False
        self.last_update = None
        self.data_cache = {}
        
    async def start_real_time_updates(self):
        """Starte kontinuierliche Updates"""
        self.is_running = True
        logger.info(f"🔄 Real-time Updates gestartet für {len(self.symbols)} Aktien")
        
        async with self.yahoo_client:
            while self.is_running:
                try:
                    start_time = time.time()
                    
                    # Aktualisiere alle Symbole
                    updated_data = await self.yahoo_client.get_multiple_quotes(self.symbols)
                    
                    # Cache aktualisieren
                    self.data_cache.update(updated_data)
                    self.last_update = datetime.now()
                    
                    # Performance Logging
                    duration = time.time() - start_time
                    logger.info(f"✅ Update abgeschlossen: {len(updated_data)} Aktien in {duration:.2f}s")
                    
                    # Warte bis zum nächsten Update
                    await asyncio.sleep(self.update_interval)
                    
                except Exception as e:
                    logger.error(f"Fehler bei Real-time Update: {e}")
                    await asyncio.sleep(30)  # Kürzere Pause bei Fehlern
    
    def stop_real_time_updates(self):
        """Stoppe Updates"""
        self.is_running = False
        logger.info("🔴 Real-time Updates gestoppt")
    
    def get_current_data(self, symbol: str = None) -> Union[StockData, Dict[str, StockData]]:
        """Hole aktuelle Daten aus Cache"""
        if symbol:
            return self.data_cache.get(symbol)
        return self.data_cache.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Status der Real-time Updates"""
        return {
            "is_running": self.is_running,
            "symbols_count": len(self.symbols),
            "cached_symbols": len(self.data_cache),
            "last_update": self.last_update.isoformat() if self.last_update else None,
            "update_interval": self.update_interval,
            "yahoo_api_status": self.yahoo_client.get_status()
        }

# Deutsche Aktien Symbole für Testing
GERMAN_STOCKS_SAMPLE = [
    "SAP.DE", "ASML.AS", "ADYEN.AS", "SIE.DE", "ALV.DE",
    "DTE.DE", "ADS.DE", "BMW.DE", "VOW3.DE", "BAS.DE",
    "BAYN.DE", "MBG.DE", "DBK.DE", "DAI.DE", "MUV2.DE",
    "RWE.DE", "LIN.DE", "HEI.DE", "DHL.DE", "CON.DE"
]

async def main():
    """Test und Demo Funktion"""
    print("🚀 Yahoo Finance API Integration Test")
    print("=" * 50)
    
    async with YahooFinanceClient() as client:
        # Einzelne Aktie testen
        print("\n1. Einzelaktie Test (SAP.DE)")
        sap_data = await client.get_stock_quote("SAP.DE")
        if sap_data:
            print(f"   Symbol: {sap_data.symbol}")
            print(f"   Name: {sap_data.name}")
            print(f"   Preis: €{sap_data.current_price}")
            print(f"   Änderung: {sap_data.change_percent:.2f}%")
            print(f"   Quelle: {sap_data.source}")
        
        # Multiple Aktien testen
        print(f"\n2. Batch Test ({len(GERMAN_STOCKS_SAMPLE)} Aktien)")
        start_time = time.time()
        
        batch_data = await client.get_multiple_quotes(GERMAN_STOCKS_SAMPLE)
        
        duration = time.time() - start_time
        print(f"   ✅ {len(batch_data)} Aktien in {duration:.2f}s geladen")
        print(f"   Durchschnitt: {duration/len(batch_data):.3f}s pro Aktie")
        
        # API Status
        print("\n3. API Status")
        status = client.get_status()
        for key, value in status.items():
            print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())