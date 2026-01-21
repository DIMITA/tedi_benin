"""
Authentication utilities
"""
from functools import wraps
from flask import request, g
from flask_restx import abort
from app.models.auth import ApiKey


def require_api_key(required_scope=None):
    """
    Decorator to require API key authentication

    Args:
        required_scope: Optional scope required for the endpoint

    Returns:
        Decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key from header
            api_key = request.headers.get('X-API-KEY')

            if not api_key:
                abort(401, 'API key required. Include X-API-KEY header.')

            # Validate API key
            key_obj = ApiKey.query.filter_by(key=api_key).first()

            if not key_obj:
                abort(401, 'Invalid API key.')

            if not key_obj.is_valid():
                abort(401, 'API key is expired or inactive.')

            # Check scope if required
            if required_scope and not key_obj.has_scope(required_scope):
                abort(403, f'API key does not have required scope: {required_scope}')

            # Record usage
            key_obj.record_usage()

            # Add key object to request context and g for anti-scraping
            request.api_key = key_obj
            g.api_key_info = key_obj.to_dict(include_key=False)
            
            # Apply rate limiting
            try:
                from app.utils.anti_scraping import rate_limit_check
                rate_limit_check(g.api_key_info)
            except Exception:
                pass  # Don't fail if rate limiting unavailable

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_current_api_key():
    """
    Get current API key from request context

    Returns:
        ApiKey object or None
    """
    return getattr(request, 'api_key', None)
