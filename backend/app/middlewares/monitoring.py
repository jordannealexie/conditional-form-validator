"""
Request monitoring middleware for metrics and logging
Tracks all API requests with timing, status codes, and errors
"""
import time
import logging
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.core.metrics import track_request_metrics, http_requests_in_progress, track_error
from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor all HTTP requests
    - Tracks request duration
    - Logs requests with structured data
    - Records Prometheus metrics
    - Adds request ID for tracing
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Extract request info
        method = request.method
        path = request.url.path
        
        # Normalize endpoint path for metrics (remove IDs)
        endpoint = self._normalize_path(path)
        
        # Track in-progress requests
        if settings.METRICS_ENABLED:
            http_requests_in_progress.labels(method=method, endpoint=endpoint).inc()
        
        # Start timing
        start_time = time.time()
        
        # Log request start
        logger.info(
            f"Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "client_host": request.client.host if request.client else None,
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Track error
            if settings.METRICS_ENABLED:
                track_error(error_type=type(e).__name__, endpoint=endpoint)
            
            logger.error(
                f"Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(e),
                },
                exc_info=True
            )
            raise
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Track completed request
            if settings.METRICS_ENABLED:
                http_requests_in_progress.labels(method=method, endpoint=endpoint).dec()
            
        # Track metrics
        if settings.METRICS_ENABLED:
            track_request_metrics(method, endpoint, status_code, duration)
        
        # Log request completion
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration * 1000, 2),
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for metrics by removing IDs
        /api/v1/templates/123 -> /api/v1/templates/{id}
        """
        parts = path.split("/")
        normalized = []
        
        for part in parts:
            # Replace numeric IDs with placeholder
            if part.isdigit():
                normalized.append("{id}")
            # Replace UUIDs with placeholder
            elif len(part) == 36 and part.count("-") == 4:
                normalized.append("{uuid}")
            else:
                normalized.append(part)
        
        return "/".join(normalized)


class CacheHeaderMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add HTTP caching headers
    Improves performance for cacheable endpoints
    """
    
    # Endpoints that can be cached with their TTL in seconds
    CACHEABLE_ENDPOINTS = {
        "/api/v1/enums": 86400,  # 24 hours for enum data
        "/api/v1/banks": 3600,    # 1 hour for banks
        "/api/v1/field-types": 3600,  # 1 hour for field types
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Only add cache headers for GET requests
        if request.method != "GET":
            return response
        
        # Check if endpoint is cacheable
        path = request.url.path
        for endpoint, ttl in self.CACHEABLE_ENDPOINTS.items():
            if path.startswith(endpoint):
                # Add cache headers
                response.headers["Cache-Control"] = f"public, max-age={ttl}"
                response.headers["Vary"] = "Accept-Encoding"
                break
        else:
            # For authenticated endpoints, prevent caching
            if "Authorization" in request.headers:
                response.headers["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
        
        return response
