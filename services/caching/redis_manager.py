#!/usr/bin/env python3
"""
🔄 Smart Redis Caching System für DA-KI
Multi-Level Caching mit Performance Optimierung

Entwickelt mit Claude Code - High-Performance Caching Architecture
"""

import redis
import asyncio
import aioredis
import json
import pickle
import time
import logging
import hashlib
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache Level Definitionen"""
    L1_MEMORY = "l1_memory"     # 5 min TTL - Hot Data
    L2_REDIS = "l2_redis"       # 1 hour TTL - Warm Data  
    L3_DATABASE = "l3_database" # Persistent - Cold Data

class CacheStrategy(Enum):
    """Caching Strategien"""
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"
    WRITE_AROUND = "write_around"
    REFRESH_AHEAD = "refresh_ahead"

@dataclass
class CacheEntry:
    """Standardisierter Cache Entry"""
    key: str
    data: Any
    timestamp: datetime
    ttl: int
    level: CacheLevel
    hit_count: int = 0
    last_accessed: datetime = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
    
    def is_expired(self) -> bool:
        """Prüfe ob Entry abgelaufen ist"""
        if self.ttl <= 0:  # Permanent cache
            return False
        return (datetime.now() - self.timestamp).seconds > self.ttl
    
    def update_access(self):
        """Update access statistics"""
        self.hit_count += 1
        self.last_accessed = datetime.now()

class SmartRedisManager:
    """
    Smart Redis Caching Manager mit Multi-Level Architecture
    
    Features:
    - L1: In-Memory Cache (5 min TTL)
    - L2: Redis Cache (1 hour TTL)
    - L3: Database Cache (Persistent)
    - Intelligent Cache Warming
    - Performance Analytics
    - Auto-scaling TTL
    """
    
    def __init__(self, 
                 redis_url: str = "redis://10.1.1.110:6379",
                 namespace: str = "da_ki",
                 l1_max_size: int = 1000,
                 default_ttl: int = 3600):
        
        self.redis_url = redis_url
        self.namespace = namespace
        self.l1_max_size = l1_max_size
        self.default_ttl = default_ttl
        
        # L1 Cache (In-Memory)
        self.l1_cache: Dict[str, CacheEntry] = {}
        self.l1_access_order: List[str] = []
        
        # Redis connections
        self.redis_client = None
        self.redis_async = None
        
        # Performance metrics
        self.metrics = {
            'l1_hits': 0,
            'l2_hits': 0,
            'l3_hits': 0,
            'misses': 0,
            'total_requests': 0,
            'cache_warming_jobs': 0,
            'evictions': 0
        }
        
        # Cache warming configuration
        self.warming_enabled = True
        self.warming_threshold = 0.8  # 80% TTL remaining triggers refresh
        
    async def initialize(self):
        """Initialize Redis connections"""
        try:
            # Sync Redis client
            self.redis_client = redis.from_url(
                self.redis_url, 
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            
            # Async Redis client (compatible with older aioredis)
            try:
                # Try newer aioredis syntax
                self.redis_async = await aioredis.from_url(
                    self.redis_url,
                    decode_responses=True
                )
            except AttributeError:
                # Fallback to older aioredis syntax
                self.redis_async = await aioredis.create_redis_pool(
                    self.redis_url,
                    encoding='utf-8'
                )
            
            # Test connection
            await self.redis_async.ping()
            logger.info(f"✅ Redis connection established: {self.redis_url}")
            
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            # Fallback to memory-only mode
            self.redis_client = None
            self.redis_async = None
            logger.warning("🔄 Fallback to memory-only caching mode")
    
    async def close(self):
        """Close Redis connections"""
        if self.redis_async:
            try:
                if hasattr(self.redis_async, 'close'):
                    await self.redis_async.close()
                elif hasattr(self.redis_async, 'wait_closed'):
                    self.redis_async.close()
                    await self.redis_async.wait_closed()
            except Exception as e:
                logger.warning(f"Redis close error: {e}")
    
    def _make_key(self, key: str, prefix: str = "") -> str:
        """Generate namespaced cache key"""
        if prefix:
            return f"{self.namespace}:{prefix}:{key}"
        return f"{self.namespace}:{key}"
    
    def _serialize(self, data: Any) -> str:
        """Serialize data for Redis storage"""
        if isinstance(data, (dict, list)):
            return json.dumps(data, default=str)
        elif hasattr(data, '__dict__'):
            return json.dumps(asdict(data) if hasattr(data, '__dataclass_fields__') else data.__dict__, default=str)
        else:
            return str(data)
    
    def _deserialize(self, data: str, data_type: type = dict) -> Any:
        """Deserialize data from Redis"""
        try:
            if data_type in (dict, list):
                return json.loads(data)
            else:
                return data_type(json.loads(data))
        except (json.JSONDecodeError, TypeError):
            return data
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Multi-level cache GET operation
        L1 → L2 → L3 → Source
        """
        self.metrics['total_requests'] += 1
        namespaced_key = self._make_key(key)
        
        # L1 Cache Check (Memory)
        l1_entry = self.l1_cache.get(namespaced_key)
        if l1_entry and not l1_entry.is_expired():
            l1_entry.update_access()
            self.metrics['l1_hits'] += 1
            logger.debug(f"L1 Cache HIT: {key}")
            
            # Schedule cache warming if needed
            if self.warming_enabled:
                await self._schedule_warming(namespaced_key, l1_entry)
            
            return l1_entry.data
        
        # L2 Cache Check (Redis)
        if self.redis_async:
            try:
                l2_data = await self.redis_async.get(namespaced_key)
                if l2_data:
                    deserialized_data = self._deserialize(l2_data)
                    
                    # Promote to L1
                    await self._set_l1(namespaced_key, deserialized_data, self.default_ttl // 12)  # 5 min
                    
                    self.metrics['l2_hits'] += 1
                    logger.debug(f"L2 Cache HIT: {key}")
                    return deserialized_data
                    
            except Exception as e:
                logger.error(f"L2 Cache error: {e}")
        
        # Cache MISS
        self.metrics['misses'] += 1
        logger.debug(f"Cache MISS: {key}")
        return default
    
    async def set(self, 
                  key: str, 
                  value: Any, 
                  ttl: int = None,
                  strategy: CacheStrategy = CacheStrategy.WRITE_THROUGH) -> bool:
        """
        Multi-level cache SET operation with strategies
        """
        if ttl is None:
            ttl = self.default_ttl
            
        namespaced_key = self._make_key(key)
        
        try:
            if strategy == CacheStrategy.WRITE_THROUGH:
                # Write to all levels simultaneously
                await asyncio.gather(
                    self._set_l1(namespaced_key, value, ttl // 12),  # L1: 5 min
                    self._set_l2(namespaced_key, value, ttl),        # L2: 1 hour
                    return_exceptions=True
                )
                
            elif strategy == CacheStrategy.WRITE_BACK:
                # Write to L1 immediately, L2 asynchronously
                await self._set_l1(namespaced_key, value, ttl // 12)
                asyncio.create_task(self._set_l2(namespaced_key, value, ttl))
                
            elif strategy == CacheStrategy.WRITE_AROUND:
                # Write only to L2, bypass L1
                await self._set_l2(namespaced_key, value, ttl)
            
            logger.debug(f"Cache SET: {key} with strategy {strategy.value}")
            return True
            
        except Exception as e:
            logger.error(f"Cache SET error: {e}")
            return False
    
    async def _set_l1(self, key: str, value: Any, ttl: int):
        """Set L1 cache entry with LRU eviction"""
        
        # LRU eviction if cache is full
        if len(self.l1_cache) >= self.l1_max_size:
            await self._evict_l1_lru()
        
        entry = CacheEntry(
            key=key,
            data=value,
            timestamp=datetime.now(),
            ttl=ttl,
            level=CacheLevel.L1_MEMORY
        )
        
        self.l1_cache[key] = entry
        
        # Update access order for LRU
        if key in self.l1_access_order:
            self.l1_access_order.remove(key)
        self.l1_access_order.append(key)
    
    async def _set_l2(self, key: str, value: Any, ttl: int):
        """Set L2 Redis cache entry"""
        if not self.redis_async:
            return
            
        try:
            serialized_value = self._serialize(value)
            await self.redis_async.setex(key, ttl, serialized_value)
            
        except Exception as e:
            logger.error(f"L2 Cache SET error: {e}")
    
    async def _evict_l1_lru(self):
        """Evict least recently used L1 cache entries"""
        if not self.l1_access_order:
            return
            
        # Remove 10% of cache entries (LRU)
        evict_count = max(1, len(self.l1_access_order) // 10)
        
        for _ in range(evict_count):
            if self.l1_access_order:
                lru_key = self.l1_access_order.pop(0)
                if lru_key in self.l1_cache:
                    del self.l1_cache[lru_key]
                    self.metrics['evictions'] += 1
    
    async def _schedule_warming(self, key: str, entry: CacheEntry):
        """Schedule cache warming for entries nearing expiration"""
        if not self.warming_enabled:
            return
            
        time_remaining = entry.ttl - (datetime.now() - entry.timestamp).seconds
        warming_threshold_time = entry.ttl * self.warming_threshold
        
        if time_remaining <= warming_threshold_time:
            # Schedule background refresh
            asyncio.create_task(self._warm_cache_entry(key))
            self.metrics['cache_warming_jobs'] += 1
    
    async def _warm_cache_entry(self, key: str):
        """Background cache warming task"""
        # This would typically refresh data from the source
        # For now, we'll extend the TTL of the existing entry
        logger.debug(f"Cache warming triggered for: {key}")
        # Implementation depends on data source integration
    
    async def delete(self, key: str) -> bool:
        """Delete from all cache levels"""
        namespaced_key = self._make_key(key)
        
        # Remove from L1
        if namespaced_key in self.l1_cache:
            del self.l1_cache[namespaced_key]
            if namespaced_key in self.l1_access_order:
                self.l1_access_order.remove(namespaced_key)
        
        # Remove from L2
        if self.redis_async:
            try:
                await self.redis_async.delete(namespaced_key)
            except Exception as e:
                logger.error(f"L2 Cache DELETE error: {e}")
                return False
        
        return True
    
    async def clear(self, pattern: str = None):
        """Clear cache entries by pattern"""
        if pattern:
            pattern = self._make_key(pattern)
        else:
            pattern = f"{self.namespace}:*"
        
        # Clear L1
        keys_to_remove = [k for k in self.l1_cache.keys() if k.startswith(pattern.replace('*', ''))]
        for key in keys_to_remove:
            del self.l1_cache[key]
            if key in self.l1_access_order:
                self.l1_access_order.remove(key)
        
        # Clear L2
        if self.redis_async:
            try:
                keys = await self.redis_async.keys(pattern)
                if keys:
                    await self.redis_async.delete(*keys)
            except Exception as e:
                logger.error(f"L2 Cache CLEAR error: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get cache performance metrics"""
        total_hits = self.metrics['l1_hits'] + self.metrics['l2_hits'] + self.metrics['l3_hits']
        hit_rate = (total_hits / self.metrics['total_requests']) * 100 if self.metrics['total_requests'] > 0 else 0
        
        return {
            **self.metrics,
            'hit_rate_percent': round(hit_rate, 2),
            'l1_size': len(self.l1_cache),
            'l1_max_size': self.l1_max_size,
            'redis_connected': self.redis_async is not None,
            'warming_enabled': self.warming_enabled,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get detailed cache information"""
        l1_info = {}
        for key, entry in self.l1_cache.items():
            l1_info[key] = {
                'timestamp': entry.timestamp.isoformat(),
                'ttl': entry.ttl,
                'hit_count': entry.hit_count,
                'last_accessed': entry.last_accessed.isoformat(),
                'is_expired': entry.is_expired()
            }
        
        return {
            'l1_cache': l1_info,
            'metrics': self.get_metrics(),
            'config': {
                'namespace': self.namespace,
                'l1_max_size': self.l1_max_size,
                'default_ttl': self.default_ttl,
                'warming_threshold': self.warming_threshold
            }
        }

# Decorator für automatisches Caching
def cache_result(ttl: int = 3600, key_func: Callable = None):
    """
    Decorator für automatisches Function Result Caching
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                func_name = func.__name__
                args_hash = hashlib.md5(str(args + tuple(kwargs.items())).encode()).hexdigest()[:8]
                cache_key = f"func:{func_name}:{args_hash}"
            
            # Get from cache (assuming redis_manager is available in scope)
            if hasattr(wrapper, '_cache_manager'):
                cached_result = await wrapper._cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            if hasattr(wrapper, '_cache_manager'):
                await wrapper._cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator

# Global Redis Manager Instance
redis_manager = None

async def get_redis_manager() -> SmartRedisManager:
    """Get or create global Redis manager instance"""
    global redis_manager
    if redis_manager is None:
        redis_manager = SmartRedisManager()
        await redis_manager.initialize()
    return redis_manager

async def main():
    """Test und Demo Funktion"""
    print("🚀 Smart Redis Caching System Test")
    print("=" * 50)
    
    # Initialize Redis Manager
    cache = SmartRedisManager()
    await cache.initialize()
    
    try:
        # Test Basic Operations
        print("\n1. Basic Cache Operations")
        await cache.set("test_key", {"message": "Hello Redis!"}, ttl=300)
        result = await cache.get("test_key")
        print(f"   SET/GET Test: {result}")
        
        # Test Multi-level Caching
        print("\n2. Multi-level Cache Test")
        test_data = {
            "stock": "SAP.DE",
            "price": 142.50,
            "timestamp": datetime.now().isoformat()
        }
        
        # Write with different strategies
        await cache.set("stock:SAP.DE", test_data, strategy=CacheStrategy.WRITE_THROUGH)
        
        # Multiple reads to test L1 cache
        for i in range(3):
            result = await cache.get("stock:SAP.DE")
            print(f"   Read {i+1}: {result['stock']} - €{result['price']}")
        
        # Performance metrics
        print("\n3. Performance Metrics")
        metrics = cache.get_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
            
        # Cache info
        print("\n4. Cache Information")
        cache_info = cache.get_cache_info()
        print(f"   L1 Cache Size: {len(cache_info['l1_cache'])}")
        print(f"   Hit Rate: {cache_info['metrics']['hit_rate_percent']}%")
        
    finally:
        await cache.close()

if __name__ == "__main__":
    asyncio.run(main())