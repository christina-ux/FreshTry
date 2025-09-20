import functools
import time
import hashlib
import json
import os
import pickle
from typing import Any, Callable, Dict, Optional, Tuple, TypeVar, Union, cast

T = TypeVar('T')

class Cache:
    """Efficient caching system with multiple cache backends"""
    
    def __init__(self, cache_dir: str = "/tmp/policyedgeai_cache", max_memory_items: int = 1000):
        self.cache_dir = cache_dir
        self.memory_cache: Dict[str, Tuple[float, Any]] = {}
        self.max_memory_items = max_memory_items
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_key(self, prefix: str, args: Tuple, kwargs: Dict) -> str:
        """Generate a cache key from function arguments"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return f"{prefix}_{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _get_disk_path(self, key: str) -> str:
        """Get the path to the disk cache file"""
        return os.path.join(self.cache_dir, f"{key}.pickle")
    
    def get(self, key: str, max_age: Optional[float] = None) -> Tuple[bool, Any]:
        """Get a value from the cache"""
        # Try memory cache first
        if key in self.memory_cache:
            timestamp, value = self.memory_cache[key]
            if max_age is None or time.time() - timestamp < max_age:
                return True, value
        
        # Try disk cache
        disk_path = self._get_disk_path(key)
        if os.path.exists(disk_path):
            try:
                with open(disk_path, "rb") as f:
                    timestamp, value = pickle.load(f)
                    
                if max_age is None or time.time() - timestamp < max_age:
                    # Also update memory cache
                    self.memory_cache[key] = (timestamp, value)
                    return True, value
            except Exception:
                pass
        
        return False, None
    
    def set(self, key: str, value: Any) -> None:
        """Set a value in the cache"""
        timestamp = time.time()
        
        # Set in memory cache
        self.memory_cache[key] = (timestamp, value)
        
        # Manage memory cache size
        if len(self.memory_cache) > self.max_memory_items:
            # Remove oldest 10% of items
            items_to_remove = int(self.max_memory_items * 0.1)
            oldest_keys = sorted(self.memory_cache.keys(), 
                                key=lambda k: self.memory_cache[k][0])[:items_to_remove]
            for k in oldest_keys:
                del self.memory_cache[k]
        
        # Set in disk cache
        disk_path = self._get_disk_path(key)
        try:
            with open(disk_path, "wb") as f:
                pickle.dump((timestamp, value), f)
        except Exception:
            pass
    
    def invalidate(self, key: str) -> None:
        """Remove a key from the cache"""
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        disk_path = self._get_disk_path(key)
        if os.path.exists(disk_path):
            try:
                os.remove(disk_path)
            except Exception:
                pass
    
    def clear(self) -> None:
        """Clear all cache"""
        self.memory_cache.clear()
        
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".pickle"):
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception:
            pass

# Create a global cache instance
cache = Cache()

def cached(prefix: str, max_age: Optional[float] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if we should skip the cache
            skip_cache = kwargs.pop("skip_cache", False)
            if skip_cache:
                return func(*args, **kwargs)
            
            # Generate cache key
            key = cache._get_key(prefix, args, kwargs)
            
            # Try to get from cache
            found, value = cache.get(key, max_age)
            if found:
                return value
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache.set(key, result)
            return result
        
        return cast(Callable, wrapper)
    
    return decorator