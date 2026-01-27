"""
Prometheus metrics for monitoring and observability
Tracks API performance, database queries, and cache hits
"""
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for when prometheus_client is not available
    class Counter:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
    
    class Histogram:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def observe(self, *args, **kwargs):
            pass
        def time(self):
            return DummyTimer()
    
    class Gauge:
        def __init__(self, *args, **kwargs):
            pass
        def labels(self, *args, **kwargs):
            return self
        def inc(self, *args, **kwargs):
            pass
        def dec(self, *args, **kwargs):
            pass
        def set(self, *args, **kwargs):
            pass
    
    class DummyTimer:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            pass
    
    def generate_latest():
        return b"# Prometheus client not available"
    
    CONTENT_TYPE_LATEST = "text/plain"

from fastapi import Response
import time
from typing import Callable
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# API Metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "HTTP requests currently being processed",
    ["method", "endpoint"]
)

# Database Metrics
db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table"]
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query latency",
    ["operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

db_connections_active = Gauge(
    "db_connections_active",
    "Active database connections"
)

db_connections_pool_size = Gauge(
    "db_connections_pool_size",
    "Database connection pool size"
)

# Cache Metrics
cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_key_type"]
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_key_type"]
)

cache_operations_duration_seconds = Histogram(
    "cache_operations_duration_seconds",
    "Cache operation latency",
    ["operation"],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1]
)

# Validation Metrics
validation_total = Counter(
    "validation_total",
    "Total validations performed",
    ["template_id", "status"]
)

validation_duration_seconds = Histogram(
    "validation_duration_seconds",
    "Validation processing time",
    ["template_id"],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
)

# Error Metrics
errors_total = Counter(
    "errors_total",
    "Total errors",
    ["error_type", "endpoint"]
)


def track_request_metrics(method: str, endpoint: str, status_code: int, duration: float):
    """
    Track HTTP request metrics
    
    Args:
        method: HTTP method
        endpoint: API endpoint
        status_code: Response status code
        duration: Request duration in seconds
    """
    try:
        http_requests_total.labels(method=method, endpoint=endpoint, status=status_code).inc()
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to track request metrics: {e}")


def track_db_query(operation: str, table: str, duration: float):
    """
    Track database query metrics
    
    Args:
        operation: Database operation (select, insert, update, delete)
        table: Table name
        duration: Query duration in seconds
    """
    try:
        db_queries_total.labels(operation=operation, table=table).inc()
        db_query_duration_seconds.labels(operation=operation, table=table).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to track DB query metrics: {e}")


def track_cache_hit(cache_key_type: str):
    """Track cache hit"""
    try:
        cache_hits_total.labels(cache_key_type=cache_key_type).inc()
    except Exception as e:
        logger.warning(f"Failed to track cache hit: {e}")


def track_cache_miss(cache_key_type: str):
    """Track cache miss"""
    try:
        cache_misses_total.labels(cache_key_type=cache_key_type).inc()
    except Exception as e:
        logger.warning(f"Failed to track cache miss: {e}")


def track_cache_operation(operation: str, duration: float):
    """Track cache operation duration"""
    try:
        cache_operations_duration_seconds.labels(operation=operation).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to track cache operation: {e}")


def track_validation(template_id: int, status: str, duration: float):
    """
    Track validation metrics
    
    Args:
        template_id: Template ID
        status: Validation status (success, failure)
        duration: Validation duration in seconds
    """
    try:
        validation_total.labels(template_id=str(template_id), status=status).inc()
        validation_duration_seconds.labels(template_id=str(template_id)).observe(duration)
    except Exception as e:
        logger.warning(f"Failed to track validation metrics: {e}")


def track_error(error_type: str, endpoint: str):
    """Track error occurrence"""
    try:
        errors_total.labels(error_type=error_type, endpoint=endpoint).inc()
    except Exception as e:
        logger.warning(f"Failed to track error: {e}")


def get_metrics_response() -> Response:
    """
    Generate Prometheus metrics response
    
    Returns:
        FastAPI Response with metrics in Prometheus format
    """
    if PROMETHEUS_AVAILABLE:
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )
    else:
        return Response(
            content=b"# Prometheus client not available\n# Install prometheus_client to enable metrics",
            media_type="text/plain"
        )


# Decorator for automatic metric tracking
def track_time(metric_name: str = None):
    """
    Decorator to track function execution time
    
    Args:
        metric_name: Optional metric name (defaults to function name)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                name = metric_name or func.__name__
                logger.debug(f"{name} took {duration:.3f}s")
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                name = metric_name or func.__name__
                logger.debug(f"{name} took {duration:.3f}s")
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
