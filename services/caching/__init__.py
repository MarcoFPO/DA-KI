"""
🔄 Caching Package für DA-KI
Smart Multi-Level Caching System

Entwickelt mit Claude Code
"""

from .redis_manager import (
    SmartRedisManager, 
    CacheLevel, 
    CacheStrategy, 
    CacheEntry,
    cache_result,
    get_redis_manager
)

__all__ = [
    'SmartRedisManager',
    'CacheLevel',
    'CacheStrategy', 
    'CacheEntry',
    'cache_result',
    'get_redis_manager'
]