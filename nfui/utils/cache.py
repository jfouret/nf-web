from functools import wraps
from flask import current_app
from flask_caching import Cache
import hashlib
import json

# Initialize cache
cache = Cache()

# Keep track of cache keys
_github_cache_keys = set()
_s3_cache_keys = set()

def init_cache(app):
    """Initialize the cache with the application"""
    cache.init_app(app)

def _make_cache_key(prefix, f, args, kwargs):
    """Helper function to create a cache key with a prefix"""
    key_parts = [
        prefix,
        f.__name__,
        *[str(arg) for arg in args],
        *[f"{k}:{v}" for k, v in sorted(kwargs.items())]
    ]
    return hashlib.sha256(json.dumps(key_parts).encode()).hexdigest()

def github_cache(f):
    """
    Decorator for caching GitHub API responses.
    Creates a unique key based on the function name and arguments.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        cache_key = _make_cache_key('github', f, args, kwargs)
        _github_cache_keys.add(cache_key)
        
        # Try to get from cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value

        # If not in cache, call the function
        value = f(*args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, value, timeout=current_app.config['CACHE_DEFAULT_TIMEOUT'])
        
        return value
    return decorated

def s3_cache(f):
    """
    Decorator for caching S3 listing responses.
    Creates a unique key based on the function name and arguments.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        cache_key = _make_cache_key('s3', f, args, kwargs)
        _s3_cache_keys.add(cache_key)
        
        # Try to get from cache first
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value

        # If not in cache, call the function
        value = f(*args, **kwargs)
        
        # Store in cache
        cache.set(cache_key, value, timeout=current_app.config['CACHE_DEFAULT_TIMEOUT'])
        
        return value
    return decorated

def clear_github_cache():
    """Clear all GitHub API cache entries"""
    global _github_cache_keys
    for key in _github_cache_keys:
        cache.delete(key)
    _github_cache_keys.clear()

def clear_s3_cache():
    """Clear all S3 listing cache entries"""
    global _s3_cache_keys
    for key in _s3_cache_keys:
        cache.delete(key)
    _s3_cache_keys.clear()
