from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.api.v1.endpoints import users
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import rbac
from app.api.v1.endpoints import abac
from app.api.v1.endpoints import rebac
from app.api.v1.endpoints import authorization
from app.api.v1.endpoints import banks
from app.api.v1.endpoints import templates
from app.api.v1.endpoints import submissions
from app.api.v1.endpoints import roles
from app.api.v1.endpoints import files
from app.api.v1.endpoints import enums
from app.api.v1.endpoints import field_types
from app.api.v1.endpoints import lookups
from app.api.v1.endpoints import metadata
from app.api.v1.endpoints import audit_trail

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication (Optional)"])
api_router.include_router(rbac.router, prefix="/rbac", tags=["RBAC Management"])
api_router.include_router(abac.router, prefix="/abac", tags=["ABAC Management"])
api_router.include_router(rebac.router, prefix="/rebac", tags=["ReBAC Management"])
api_router.include_router(authorization.router, prefix="/authorization", tags=["Unified Authorization"])
api_router.include_router(banks.router, prefix="/banks", tags=["Form System - Banks"])
api_router.include_router(templates.router, prefix="/templates", tags=["Form System - Templates"])
api_router.include_router(submissions.router, prefix="/submissions", tags=["Form System - Submissions"])
api_router.include_router(enums.router, prefix="/enums", tags=["Form System - Enums"])
api_router.include_router(field_types.router, prefix="/field-types", tags=["Form System - Field Types"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(lookups.router, prefix="/lookups", tags=["Lookup Tables"])
api_router.include_router(metadata.router, prefix="/metadata", tags=["Form Metadata"])
api_router.include_router(audit_trail.router, prefix="/audit-trail", tags=["Audit Trail"])

# This is the main API router that includes all endpoint routers