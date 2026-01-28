import uvicorn
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.core.casbin_enforcer import casbin_enforcer
from app.core.cache import cache
from app.core.logging_config import setup_logging
from app.middlewares.monitoring import RequestMonitoringMiddleware, CacheHeaderMiddleware
from app.api.v1.api import api_router
from app.db.session import engine
from app.db.base_class import Base
from app.exceptions.handlers import add_exception_handlers
from app.utils.docs import setup_swagger_documentation

port = int(os.getenv("PORT", "8000"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("🚀 Starting application...")
    
    # Setup structured logging
    setup_logging()
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Redis cache
    if settings.CACHE_ENABLED:
        try:
            await cache.connect()
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️ Redis cache connection failed: {e}. Operating without cache.")
    
    # Initialize Casbin enforcers
    await casbin_enforcer.initialize()
    
    print("✅ Application started successfully!")
    print(f"📚 API Documentation: http://localhost:{port}{settings.API_V1_STR}/docs")
    print(f"📊 Metrics endpoint: http://localhost:{port}{settings.API_V1_STR}/health/metrics")
    
    yield
    
    # Shutdown
    if settings.CACHE_ENABLED:
        await cache.disconnect()
        print("✅ Redis cache disconnected")
    
    await engine.dispose()
    print("👋 Application shutdown complete")


# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)


def custom_openapi():
    """Custom OpenAPI schema with security definitions"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="FastAPI project with RBAC, ABAC, and ReBAC authorization using Casbin and PostgreSQL",
        routes=app.routes,
    )
    
    # Add Bearer authentication (JWT)
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token"
        }
    }
    
    # Apply security globally
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Set custom OpenAPI schema (Optional - FastAPI handles this via dependencies)
# app.openapi = custom_openapi

# Configure CORS with explicit settings for Swagger UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add monitoring and performance middlewares
if settings.METRICS_ENABLED:
    app.add_middleware(RequestMonitoringMiddleware)
    app.add_middleware(CacheHeaderMiddleware)

# Register exception handlers
add_exception_handlers(app)

# Include API router (includes all endpoint routers)
app.include_router(api_router, prefix=settings.API_V1_STR)

# Setup custom Swagger documentation with X-Client-ID header
setup_swagger_documentation(app, settings.API_V1_STR)

# Construct path to frontend relative to this file
# backend/app/main.py -> backend/app -> backend -> root -> frontend
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")

if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print(f"⚠️ Frontend directory not found at {frontend_path}")

# Root endpoint replaced by StaticFiles
# @app.get("/")
# async def root():
#     """Root endpoint"""
#     return {
#         "message": "Welcome to FastAPI RBAC/ABAC/ReBAC API",
#         "docs": f"{settings.API_V1_STR}/docs",
#         "version": "1.0.0"
#     }


# @app.get("/health")
# async def health_check(request: Request):
#     """Health check endpoint"""
#     origin = request.headers.get('origin', 'No origin')
#     print(f"Root health check from origin: {origin}")
#     return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )