"""
Anti-Scraping Protection Module for TEDI API

Implements multiple layers of protection:
1. Rate Limiting (per IP and per API key)
2. Behavioral Detection (suspicious patterns)
3. Data Noise Injection (for non-admin users)
4. Request Fingerprinting
5. Honeypot Detection
"""

import hashlib
import random
import time
import json
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any, Tuple

from flask import request, g, current_app, abort
import redis

# Redis connection for rate limiting
_redis_client = None


def get_redis_client():
    """Get or create Redis client for rate limiting"""
    global _redis_client
    if _redis_client is None:
        redis_url = current_app.config.get('REDIS_URL', 'redis://localhost:6379/0')
        _redis_client = redis.from_url(redis_url, decode_responses=True)
    return _redis_client


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    Sliding window rate limiter using Redis
    Tracks requests per IP and per API key
    """
    
    # Default limits
    DEFAULT_RATE_LIMIT_PER_MINUTE = 60
    DEFAULT_RATE_LIMIT_PER_HOUR = 1000
    DEFAULT_RATE_LIMIT_PER_DAY = 10000
    
    # Stricter limits for unauthenticated requests
    ANON_RATE_LIMIT_PER_MINUTE = 20
    ANON_RATE_LIMIT_PER_HOUR = 200
    ANON_RATE_LIMIT_PER_DAY = 1000
    
    @staticmethod
    def get_client_identifier() -> Tuple[str, str]:
        """
        Get unique client identifier (IP + optional API key)
        Returns: (ip_address, api_key or 'anon')
        """
        # Get real IP (considering proxies)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip and ',' in ip:
            ip = ip.split(',')[0].strip()
        
        api_key = request.headers.get('X-API-KEY', 'anon')
        
        return ip, api_key
    
    @staticmethod
    def check_rate_limit(api_key_info: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limits
        
        Args:
            api_key_info: API key details from database (optional)
            
        Returns:
            (allowed: bool, info: dict with remaining limits)
        """
        try:
            redis_client = get_redis_client()
        except Exception:
            # If Redis is unavailable, allow request but log
            return True, {'error': 'rate_limiter_unavailable'}
        
        ip, api_key = RateLimiter.get_client_identifier()
        now = int(time.time())
        
        # Determine limits based on authentication
        if api_key_info:
            limit_minute = api_key_info.get('rate_limit_per_hour', 1000) // 60
            limit_hour = api_key_info.get('rate_limit_per_hour', 1000)
            limit_day = api_key_info.get('rate_limit_per_day', 10000)
            key_prefix = f"rate:{api_key[:16]}"
        else:
            limit_minute = RateLimiter.ANON_RATE_LIMIT_PER_MINUTE
            limit_hour = RateLimiter.ANON_RATE_LIMIT_PER_HOUR
            limit_day = RateLimiter.ANON_RATE_LIMIT_PER_DAY
            key_prefix = f"rate:ip:{hashlib.md5(ip.encode()).hexdigest()[:16]}"
        
        # Check each time window
        windows = [
            ('minute', 60, limit_minute),
            ('hour', 3600, limit_hour),
            ('day', 86400, limit_day),
        ]
        
        info = {
            'ip': ip,
            'authenticated': api_key_info is not None,
        }
        
        for window_name, window_seconds, limit in windows:
            key = f"{key_prefix}:{window_name}:{now // window_seconds}"
            
            try:
                current = redis_client.incr(key)
                if current == 1:
                    redis_client.expire(key, window_seconds)
                
                info[f'{window_name}_remaining'] = max(0, limit - current)
                info[f'{window_name}_limit'] = limit
                
                if current > limit:
                    info['blocked_by'] = window_name
                    info['retry_after'] = window_seconds - (now % window_seconds)
                    return False, info
                    
            except Exception:
                continue
        
        return True, info
    
    @staticmethod
    def record_suspicious_activity(reason: str, severity: int = 1):
        """
        Record suspicious activity for an IP/key
        
        Args:
            reason: Why this is suspicious
            severity: 1-5 scale (5 = most severe)
        """
        try:
            redis_client = get_redis_client()
            ip, api_key = RateLimiter.get_client_identifier()
            
            # Create suspicion score key
            key = f"suspicious:{hashlib.md5(ip.encode()).hexdigest()[:16]}"
            
            # Increment suspicion score
            score = redis_client.incr(key)
            if score == 1:
                redis_client.expire(key, 3600)  # Expire after 1 hour
            
            # Add severity multiplier
            redis_client.incrby(key, severity - 1)
            
            # Log the event
            log_key = f"suspicious_log:{ip}:{int(time.time())}"
            redis_client.setex(log_key, 86400, json.dumps({
                'reason': reason,
                'severity': severity,
                'api_key': api_key[:8] + '...' if api_key != 'anon' else 'anon',
                'timestamp': datetime.utcnow().isoformat(),
                'path': request.path,
                'method': request.method,
            }))
            
        except Exception:
            pass
    
    @staticmethod
    def is_blocked() -> Tuple[bool, Optional[str]]:
        """
        Check if IP is temporarily blocked due to suspicious activity
        
        Returns:
            (is_blocked: bool, reason: str or None)
        """
        try:
            redis_client = get_redis_client()
            ip, _ = RateLimiter.get_client_identifier()
            
            key = f"suspicious:{hashlib.md5(ip.encode()).hexdigest()[:16]}"
            score = redis_client.get(key)
            
            # Raised threshold to 50 to reduce false positives
            if score and int(score) >= 50:
                return True, "Too many suspicious requests detected"
            
            # Check for hard blocks (honeypot triggers)
            block_key = f"blocked:{hashlib.md5(ip.encode()).hexdigest()[:16]}"
            if redis_client.exists(block_key):
                return True, "IP temporarily blocked"
                
        except Exception:
            pass
        
        return False, None


# ============================================================================
# BEHAVIORAL DETECTION
# ============================================================================

class BehaviorAnalyzer:
    """
    Detect suspicious request patterns that indicate scraping
    """
    
    # Suspicious patterns
    PATTERNS = {
        'rapid_fire': 30,           # Requests per second threshold (raised from 10)
        'sequential_pages': 10,      # Sequential page accesses (raised from 5)
        'missing_referer': False,    # Disabled - many legitimate clients don't send referer
        'suspicious_user_agent': False,  # Disabled - too many false positives
        'pagination_sweep': True,    # Iterating through all pages
    }
    
    # Known bot user agents (partial matches) - only aggressive scrapers
    BOT_USER_AGENTS = [
        'scrapy', 'python-urllib',
        'go-http-client', 'apache-httpclient',
    ]
    
    # Legitimate browser/client patterns (expanded)
    BROWSER_PATTERNS = ['mozilla', 'chrome', 'safari', 'firefox', 'edge', 'axios', 'fetch', 'postman', 'insomnia', 'curl']
    
    @staticmethod
    def analyze_request() -> Tuple[bool, list]:
        """
        Analyze current request for suspicious patterns
        
        Returns:
            (is_suspicious: bool, reasons: list)
        """
        reasons = []
        
        # 1. Check User-Agent - only for clearly malicious bots
        user_agent = request.headers.get('User-Agent', '').lower()
        
        if user_agent:
            # Only flag known aggressive scraper agents
            for bot in BehaviorAnalyzer.BOT_USER_AGENTS:
                if bot in user_agent:
                    reasons.append(f'bot_user_agent:{bot}')
                    break
        
        # 2. Check for rapid-fire requests (only very aggressive patterns)
        try:
            redis_client = get_redis_client()
            ip, _ = RateLimiter.get_client_identifier()
            
            rapid_key = f"rapid:{hashlib.md5(ip.encode()).hexdigest()[:16]}:{int(time.time())}"
            count = redis_client.incr(rapid_key)
            if count == 1:
                redis_client.expire(rapid_key, 1)
            
            if count > BehaviorAnalyzer.PATTERNS['rapid_fire']:
                reasons.append(f'rapid_fire:{count}_per_second')
                
        except Exception:
            pass
        
        # 3. Check for pagination sweep (someone iterating all pages)
        if 'page' in request.args:
            try:
                page = int(request.args.get('page', 1))
                redis_client = get_redis_client()
                ip, _ = RateLimiter.get_client_identifier()
                
                page_key = f"pages:{hashlib.md5(ip.encode()).hexdigest()[:16]}:{request.path}"
                
                # Store accessed pages in a sorted set
                redis_client.zadd(page_key, {str(page): time.time()})
                redis_client.expire(page_key, 300)  # 5 min window
                
                # Check if accessing pages sequentially
                pages = redis_client.zrange(page_key, 0, -1)
                if len(pages) >= 5:
                    page_nums = sorted([int(p) for p in pages])
                    # Check for sequential access
                    sequential = sum(1 for i in range(len(page_nums)-1) 
                                   if page_nums[i+1] - page_nums[i] == 1)
                    if sequential >= 4:
                        reasons.append('pagination_sweep')
                        
            except Exception:
                pass
        
        # 4. Check request headers fingerprint
        suspicious_headers = BehaviorAnalyzer._check_headers()
        reasons.extend(suspicious_headers)
        
        return len(reasons) > 0, reasons
    
    @staticmethod
    def _check_headers() -> list:
        """Check for suspicious header patterns"""
        reasons = []
        
        # Missing common browser headers
        expected_headers = ['Accept', 'Accept-Language', 'Accept-Encoding']
        missing = [h for h in expected_headers if h not in request.headers]
        
        if len(missing) >= 2:
            reasons.append('missing_browser_headers')
        
        # Check for Accept header (browsers send specific patterns)
        accept = request.headers.get('Accept', '')
        if accept and accept == '*/*':
            # Generic accept header, typical of scripts
            reasons.append('generic_accept_header')
        
        return reasons


# ============================================================================
# DATA NOISE INJECTION
# ============================================================================

class DataNoiseInjector:
    """
    Add slight noise to numerical data for non-admin users
    This prevents exact data extraction while maintaining statistical validity
    """
    
    # Noise levels by data sensitivity
    NOISE_LEVELS = {
        'low': 0.001,      # 0.1% noise
        'medium': 0.005,   # 0.5% noise  
        'high': 0.01,      # 1% noise
    }
    
    # Fields to apply noise to (by sector)
    NOISY_FIELDS = {
        'agriculture': [
            'production_tonnes', 'yield_tonnes_per_ha', 'area_harvested_ha', 'price_per_kg'
        ],
        'realestate': [
            'price_per_sqm', 'median_price', 'num_transactions', 'rental_yield'
        ],
        'employment': [
            'total_employed', 'unemployment_rate', 'median_salary', 'informal_rate'
        ],
        'business': [
            'num_businesses', 'business_density_index', 'total_revenue', 'total_employees'
        ],
    }
    
    @staticmethod
    def should_apply_noise(api_key_info: Optional[Dict] = None) -> bool:
        """
        Determine if noise should be applied to response
        
        Admin users and users with can_api_direct get clean data
        """
        if not api_key_info:
            return True
        
        if api_key_info.get('is_admin'):
            return False
        
        if api_key_info.get('can_api_direct'):
            return False
        
        return True
    
    @staticmethod
    def add_noise(value: Any, noise_level: str = 'low', field_name: str = '') -> Any:
        """
        Add noise to a numerical value
        
        Args:
            value: Original value
            noise_level: 'low', 'medium', or 'high'
            field_name: Name of the field (for logging)
            
        Returns:
            Value with noise applied
        """
        if value is None:
            return value
        
        if not isinstance(value, (int, float)):
            return value
        
        if value == 0:
            return value
        
        noise_pct = DataNoiseInjector.NOISE_LEVELS.get(noise_level, 0.005)
        
        # Apply gaussian noise
        noise = random.gauss(0, abs(value) * noise_pct)
        noisy_value = value + noise
        
        # Keep same type
        if isinstance(value, int):
            return int(round(noisy_value))
        
        return round(noisy_value, 4)
    
    @staticmethod
    def apply_to_response(data: Any, sector: str = '', api_key_info: Optional[Dict] = None) -> Any:
        """
        Apply noise to API response data
        
        Args:
            data: Response data (dict, list, or value)
            sector: Data sector for field matching
            api_key_info: API key details
            
        Returns:
            Data with noise applied if appropriate
        """
        if not DataNoiseInjector.should_apply_noise(api_key_info):
            return data
        
        noisy_fields = DataNoiseInjector.NOISY_FIELDS.get(sector, [])
        
        if isinstance(data, dict):
            return {
                k: DataNoiseInjector.apply_to_response(v, sector, api_key_info)
                if k not in noisy_fields
                else DataNoiseInjector.add_noise(v, 'low', k)
                for k, v in data.items()
            }
        
        elif isinstance(data, list):
            return [
                DataNoiseInjector.apply_to_response(item, sector, api_key_info)
                for item in data
            ]
        
        return data


# ============================================================================
# HONEYPOT DETECTION
# ============================================================================

class HoneypotDetector:
    """
    Detect bots by including hidden endpoints that only bots would access
    """
    
    # Hidden endpoints that should never be accessed by real users
    HONEYPOT_PATHS = [
        '/api/v1/admin/users',
        '/api/v1/admin/dump',
        '/api/v1/export/all',
        '/api/v1/data/bulk',
        '/api/v1/.env',
        '/api/v1/config.json',
        '/api/v1/backup',
    ]
    
    @staticmethod
    def is_honeypot_request() -> bool:
        """Check if request is to a honeypot endpoint"""
        return request.path in HoneypotDetector.HONEYPOT_PATHS
    
    @staticmethod
    def handle_honeypot():
        """Handle honeypot access - block and log"""
        try:
            redis_client = get_redis_client()
            ip, api_key = RateLimiter.get_client_identifier()
            
            # Immediately block this IP
            block_key = f"blocked:{hashlib.md5(ip.encode()).hexdigest()[:16]}"
            redis_client.setex(block_key, 3600, 'honeypot_triggered')
            
            # Log the event
            RateLimiter.record_suspicious_activity(
                f'honeypot_access:{request.path}', 
                severity=5
            )
            
        except Exception:
            pass


# ============================================================================
# MIDDLEWARE / DECORATORS
# ============================================================================

def anti_scraping_middleware():
    """
    Flask before_request middleware for anti-scraping protection
    Call this in your app factory
    """
    # 1. Check if IP is blocked
    is_blocked, reason = RateLimiter.is_blocked()
    if is_blocked:
        abort(429, description=reason or "Too many requests")
    
    # 2. Check honeypots
    if HoneypotDetector.is_honeypot_request():
        HoneypotDetector.handle_honeypot()
        abort(404, description="Not found")
    
    # 3. Analyze behavior
    is_suspicious, reasons = BehaviorAnalyzer.analyze_request()
    if is_suspicious:
        for reason in reasons:
            severity = 2 if 'bot' in reason or 'sweep' in reason else 1
            RateLimiter.record_suspicious_activity(reason, severity)
    
    # Store for use in response processing
    g.anti_scraping_suspicious = is_suspicious
    g.anti_scraping_reasons = reasons


def rate_limit_check(api_key_info: Optional[Dict] = None):
    """
    Check rate limits for current request
    
    Args:
        api_key_info: API key details from database
        
    Returns:
        True if allowed, aborts with 429 if blocked
    """
    allowed, info = RateLimiter.check_rate_limit(api_key_info)
    
    # Store rate limit info for response headers
    g.rate_limit_info = info
    
    if not allowed:
        retry_after = info.get('retry_after', 60)
        abort(429, description=f"Rate limit exceeded. Retry after {retry_after} seconds")
    
    return True


def add_security_headers(response):
    """
    Add security headers to response
    Call this in after_request
    """
    # Anti-scraping headers
    response.headers['X-Robots-Tag'] = 'noindex, nofollow'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Cache-Control'] = 'no-store, max-age=0'
    
    # Rate limit headers
    if hasattr(g, 'rate_limit_info'):
        info = g.rate_limit_info
        response.headers['X-RateLimit-Limit'] = str(info.get('hour_limit', 1000))
        response.headers['X-RateLimit-Remaining'] = str(info.get('hour_remaining', 1000))
        if 'retry_after' in info:
            response.headers['Retry-After'] = str(info['retry_after'])
    
    return response


def protected_endpoint(sector: str = ''):
    """
    Decorator for API endpoints that need anti-scraping protection
    
    Args:
        sector: Data sector name for noise injection
    
    Usage:
        @protected_endpoint(sector='agriculture')
        def get_data():
            return {...}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get API key info from g (set by auth middleware)
            api_key_info = getattr(g, 'api_key_info', None)
            
            # Check rate limit
            rate_limit_check(api_key_info)
            
            # Call the original function
            result = f(*args, **kwargs)
            
            # Apply noise if needed (for non-admin users)
            if sector and isinstance(result, (dict, list, tuple)):
                if isinstance(result, tuple):
                    data, status = result[0], result[1] if len(result) > 1 else 200
                    noisy_data = DataNoiseInjector.apply_to_response(
                        data, sector, api_key_info
                    )
                    return noisy_data, status
                else:
                    return DataNoiseInjector.apply_to_response(
                        result, sector, api_key_info
                    )
            
            return result
        
        return decorated_function
    return decorator


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_request_fingerprint() -> str:
    """
    Generate a fingerprint for the current request
    Used for tracking and identifying repeat visitors
    """
    components = [
        request.headers.get('User-Agent', ''),
        request.headers.get('Accept-Language', ''),
        request.headers.get('Accept-Encoding', ''),
        request.headers.get('Accept', ''),
    ]
    
    fingerprint = hashlib.md5('|'.join(components).encode()).hexdigest()
    return fingerprint


def log_api_access(api_key_info: Optional[Dict] = None, response_size: int = 0):
    """
    Log API access for analytics and abuse detection
    """
    try:
        redis_client = get_redis_client()
        ip, api_key = RateLimiter.get_client_identifier()
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'ip': ip,
            'api_key': api_key[:8] + '...' if api_key != 'anon' else 'anon',
            'path': request.path,
            'method': request.method,
            'fingerprint': get_request_fingerprint(),
            'response_size': response_size,
            'suspicious': getattr(g, 'anti_scraping_suspicious', False),
        }
        
        # Store in a time-series list
        key = f"access_log:{datetime.utcnow().strftime('%Y-%m-%d-%H')}"
        redis_client.lpush(key, json.dumps(log_data))
        redis_client.expire(key, 86400 * 7)  # Keep for 7 days
        
    except Exception:
        pass
