from functools import wraps
from flask import current_app
from flask_caching import Cache
import hashlib
import json

# Initialize cache
cache = Cache()

def init_cache(app):
    """Initialize the cache with the application"""
    cache.init_app(app)

def github_cache(f):
    """
    Decorator for caching GitHub API responses.
    Creates a unique key based on the function name and arguments.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Create a unique key from function name and arguments
        key_parts = [
            f.__name__,
            *[str(arg) for arg in args],
            *[f"{k}:{v}" for k, v in sorted(kwargs.items())]
        ]
        cache_key = hashlib.sha256(json.dumps(key_parts).encode()).hexdigest()

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
    cache.clear()
