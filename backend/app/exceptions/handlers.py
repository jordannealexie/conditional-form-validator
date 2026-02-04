from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.exceptions.http_exceptions import BaseCustomError
from app.utils.response import create_response
from fastapi import status
from starlette.exceptions import HTTPException as StarletteHTTPException  # Import Starlette's HTTPException
import traceback

def add_exception_handlers(app: FastAPI) -> None:
    """Add exception handlers to the FastAPI application."""
    
    # Add handler for Starlette's HTTPException (handles non-existent routes)
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions including 404 Not Found for routes"""
        return create_response(
            success=False,
            message=str(exc.detail),
            errors=[str(exc.detail)],
            error_code="NOT_FOUND" if exc.status_code == status.HTTP_404_NOT_FOUND else f"HTTP_ERROR_{exc.status_code}",
            status_code=exc.status_code
        )
    
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle database integrity errors"""
        error_msg = str(exc.orig) if hasattr(exc, 'orig') else str(exc)
        
        # Parse common integrity errors
        if "unique constraint" in error_msg.lower():
            # Extract constraint name for more specific error messages
            constraint_name = ""
            if "uq_" in error_msg.lower() or "_key" in error_msg.lower():
                # Try to extract the constraint name
                import re
                match = re.search(r'(?:constraint\s+["\']?)(\w+)', error_msg.lower())
                if match:
                    constraint_name = match.group(1)
            
            # Provide more specific error messages based on constraint
            if "storage_path" in error_msg.lower():
                detail = "A file with this storage path already exists. Please try again."
            elif "token" in error_msg.lower():
                detail = "A file token conflict occurred. Please try uploading again."
            elif "email" in error_msg.lower():
                detail = "This email address is already registered."
            elif "username" in error_msg.lower():
                detail = "This username is already taken."
            else:
                detail = "A record with this value already exists"
            
            status_code_val = status.HTTP_409_CONFLICT
            error_code = "DUPLICATE_ENTRY"
        elif "foreign key constraint" in error_msg.lower():
            detail = "Cannot perform this operation due to related records"
            status_code_val = status.HTTP_400_BAD_REQUEST
            error_code = "FOREIGN_KEY_VIOLATION"
        elif (
            "not null constraint" in error_msg.lower()
            or "not-null constraint" in error_msg.lower()
            or "null value in column" in error_msg.lower()
        ):
            detail = "Required field is missing"
            status_code_val = status.HTTP_400_BAD_REQUEST
            error_code = "MISSING_REQUIRED_FIELD"
        else:
            detail = "Database integrity error"
            status_code_val = status.HTTP_400_BAD_REQUEST
            error_code = "INTEGRITY_ERROR"
        
        print(f"Database integrity error: {error_msg}")
        
        return create_response(
            success=False,
            message=detail,
            errors=[detail],
            error_code=error_code,
            status_code=status_code_val
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle SQLAlchemy errors"""
        error_msg = str(exc)
        print(f"Database error: {error_msg}")
        print(traceback.format_exc())
        
        return create_response(
            success=False,
            message="Database operation failed",
            errors=["Database operation failed"],
            error_code="DATABASE_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors"""
        errors = [f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()]
        return create_response(
            success=False,
            message="Validation error",
            errors=errors,
            error_code="VALIDATION_ERROR",  # Custom error code for validation errors
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle FastAPI request validation errors"""
        errors = [
            f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
            for err in exc.errors()
        ]
        return create_response(
            success=False,
            message="Validation error",
            errors=errors,
            error_code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY  # This is FastAPI's default for validation
        )
    
    @app.exception_handler(BaseCustomError)  # Handle all custom errors with one handler
    async def custom_exception_handler(request: Request, exc: BaseCustomError):
        """Handle all custom exceptions"""
        response = create_response(
            success=False,
            message=exc.detail,
            errors=[exc.detail],
            error_code=getattr(exc, 'error_code', None),
            status_code=exc.status_code
        )
        
        # Add headers if they exist (for UnauthorizedError)
        if hasattr(exc, 'headers') and exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
                
        return response
        
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Handle unhandled exceptions"""
        error_msg = str(exc)
        print(f"Unhandled exception: {error_msg}")
        print(traceback.format_exc())
        
        return create_response(
            success=False,
            message="Internal server error",
            errors=["An unexpected error occurred. Please contact support."],
            error_code="INTERNAL_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )