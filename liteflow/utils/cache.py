from flask import current_app
from flask_caching import Cache

# Initialize cache
cache = Cache()

# Keep track of cache keys by prefix
_cache_keys = {}

def init_cache(app):
    """Initialize the cache with the application"""
    cache.init_app(app)

def get_or_set_cache(key: str, value_func=None):
    """
    Get or set a cache value with explicit key.
    Returns a tuple (hit: bool, value: Any)
    
    Usage:
        # Try to get from cache
        hit, value = get_or_set_cache('github:repo:owner/name')
        if not hit:
            # Cache miss, compute value
            value = compute_expensive_value()
            # Store in cache
            _, value = get_or_set_cache('github:repo:owner/name', lambda: value)
    """
    # Extract prefix for tracking
    prefix = key.split(':')[0]
    if prefix not in _cache_keys:
        _cache_keys[prefix] = set()
    _cache_keys[prefix].add(key)
    
    # Try to get from cache
    value = cache.get(key)
    if value is not None:
        current_app.logger.info(f"Cache hit - Key: {key}")
        return value
        
    # If no value_func provided, return cache miss
    if value_func is None:
        current_app.logger.info(f"Cache miss - Key: {key}")
        return None
        
    # Compute and store value
    value = value_func()
    cache.set(key, value, timeout=current_app.config['CACHE_DEFAULT_TIMEOUT'])
    current_app.logger.info(f"Cache set - Key: {key}")
    return value

def clear_cache_by_prefix(prefix: str):
    """Clear all cache entries with given prefix"""
    if prefix in _cache_keys:
        for key in _cache_keys[prefix]:
            cache.delete(key)
            current_app.logger.info(f"Cache clear - Key: {key}")
        _cache_keys[prefix].clear()

def clear_github_cache():
    """Clear all GitHub API cache entries"""
    clear_cache_by_prefix('github')

def clear_s3_cache():
    """Clear all S3 listing cache entries"""
    clear_cache_by_prefix('s3')
