from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time

from app.db.session import get_db
from app.core.cache import cache
from app.core.metrics import get_metrics_response
from app.utils.common import log_error
from app.utils.response import create_response

router = APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Simple health check endpoint to verify the API is running",
)
async def health_check(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.

    This endpoint checks the health of the service and its dependencies.
    It verifies database connectivity and returns status information.

    Args:
        request: FastAPI request object
        db: Database session dependency

    Returns:
        Success response with health status
    """
    origin = request.headers.get('origin', 'No origin')
    log_error(f"Health check performed from origin: {origin}")
    
    # Try to connect to the database
    try:
        # test database connectivity using SQLAlchemy text()
        result = await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    data = {
        "status": "ok",
        "message": "Service is healthy",
        "database": db_status,
        "version": "0.1.0"
    }

    return create_response(
        data=data,
        message="Health check successful"
    )


@router.get(
    "/detailed",
    status_code=status.HTTP_200_OK,
    summary="Detailed health check",
    description="Comprehensive health check with all dependencies",
)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """
    Detailed health check for all system dependencies
    
    Checks:
    - Database connectivity and response time
    - Redis cache connectivity
    - System health
    
    Returns:
        Detailed health status of all components
    """
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Check database
    try:
        start = time.time()
        await db.execute(text("SELECT 1"))
        db_latency = round((time.time() - start) * 1000, 2)
        health_data["checks"]["database"] = {
            "status": "up",
            "latency_ms": db_latency
        }
    except Exception as e:
        health_data["status"] = "unhealthy"
        health_data["checks"]["database"] = {
            "status": "down",
            "error": str(e)
        }
    
    # Check Redis cache
    try:
        if cache.is_connected():
            start = time.time()
            await cache.set("health_check", {"test": True}, ttl=10)
            await cache.get("health_check")
            cache_latency = round((time.time() - start) * 1000, 2)
            health_data["checks"]["cache"] = {
                "status": "up",
                "latency_ms": cache_latency
            }
        else:
            health_data["checks"]["cache"] = {
                "status": "disconnected",
                "note": "Operating without cache"
            }
    except Exception as e:
        health_data["checks"]["cache"] = {
            "status": "error",
            "error": str(e)
        }
    
    return create_response(
        data=health_data,
        message="Detailed health check completed"
    )


@router.get(
    "/metrics",
    summary="Prometheus metrics endpoint",
    description="Expose Prometheus metrics for monitoring",
)
async def metrics():
    """
    Prometheus metrics endpoint
    
    Exposes application metrics in Prometheus format:
    - HTTP request metrics
    - Database query metrics
    - Cache hit/miss rates
    - Error rates
    """
    return get_metrics_response()


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness probe",
    description="Kubernetes readiness probe - checks if app can serve traffic",
)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """
    Readiness probe for Kubernetes
    
    Returns 200 if app is ready to serve traffic
    Returns 503 if not ready (database down)
    """
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return create_response(
            data={"status": "not ready"},
            message="Service not ready",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@router.get(
    "/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness probe",
    description="Kubernetes liveness probe - checks if app is alive",
)
async def liveness_check():
    """
    Liveness probe for Kubernetes
    
    Simple check that the application is running
    Always returns 200 unless the process is dead
    """
    return {"status": "alive"}