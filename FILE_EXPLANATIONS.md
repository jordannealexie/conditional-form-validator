# File Explanations for conditional-form-validator-backend

This document provides brief explanations for each file in the conditional-form-validator-backend project, organized by directory structure.

## Root Directory

### README.md
Comprehensive project documentation providing an overview of the Dynamic Form Validation System built with FastAPI and Vanilla JavaScript. It details the system's features including dynamic form engines with conditional logic, unified authorization models (RBAC/ABAC/ReBAC), and performance optimizations. The file includes complete setup instructions, architecture diagrams, API documentation links, and default login credentials for different user roles.

### TEAMMATE_FIX_INSTRUCTIONS.md
Urgent troubleshooting guide for fixing corrupted role permissions in the database. This document explains how permissions were reset using the ensure_permissions.py script and provides step-by-step instructions for teammates to log out, clear browser cache, and re-authenticate. It includes verification steps, prevention measures, and fallback procedures if issues persist, ensuring proper access control restoration.

### migrate_phone_patterns.py
Database migration script that updates existing form templates containing outdated phone validation patterns. The script searches for templates using the old international phone pattern and replaces them with the new Philippines-specific format (09 or +639 followed by 9 digits). It connects to the PostgreSQL database asynchronously, processes all templates, and provides detailed logging of the migration progress and results.

### requirements.txt
Python dependency manifest listing all required packages for the project. It includes core web framework libraries like FastAPI and Uvicorn, database drivers such as asyncpg and SQLAlchemy, security packages like bcrypt and python-jose, testing frameworks like pytest, and utility libraries for caching (Redis), validation (Pydantic), and more. The file ensures consistent package versions across development environments.

### test_validation.py
Comprehensive test script for validating the enhanced field validation functionality in the FormValidator class. It tests various field types including email, phone, currency, percentage, and text with length constraints, as well as conditional field validation and select option validation. The script provides detailed pass/fail feedback for each test case and ensures the validation system correctly handles both valid and invalid input scenarios.

### .gitignore
Git ignore configuration file that excludes temporary files, build artifacts, and sensitive data from version control. It prevents Python bytecode files, virtual environments, database files, logs, IDE configurations, environment variables, and uploaded files from being committed to the repository, maintaining a clean and secure codebase.

## .github/

### clean-code.md
Guidelines for maintaining clean, readable code in the project.

### code-quality.md
Standards and practices for code quality assurance.

### commit-message-instructions.md
Instructions for writing proper commit messages.

### copilot-instructions.md
Detailed instructions for GitHub Copilot on coding standards, folder structure, and best practices for this FastAPI project.

### database.md
Documentation on database design, models, and relationships.

### python.md
Python-specific guidelines and conventions used in the project.

## backend/

### main.py
Backwards compatibility entry point for running the FastAPI backend server. This file imports the main application from app.main and uses Uvicorn to start the server. It accepts an optional command-line argument for the port number (defaulting to 8000) and enables auto-reload for development. This wrapper ensures existing scripts or deployment configurations that reference backend/main.py continue to work without changes.

### requirements.txt
Backend-specific Python dependencies.

### Dockerfile
Docker configuration for containerizing the backend application.

### docker-compose.yml
Docker Compose setup for running the backend with PostgreSQL and Redis.

### pytest.ini
Configuration for pytest testing framework.

### CODE_OF_CONDUCT.md
Code of conduct for contributors and maintainers.

### LICENSE
Project license file.

### OPTIMIZATIONS_SUMMARY.md
Summary of performance optimizations implemented in the backend.

### .env
Environment variables file (should be gitignored).

### .env.example
Example environment variables file for setup.

### add_fields_column.py
Script to add fields column to database tables.

### audit_db.py
Script for auditing database operations and logs.

### benchmark_optimizations.py
Script to benchmark and measure performance optimizations.

### create_admin.py
Script to create an admin user in the system.

### recreate_db.py
Script to recreate the database schema.

### seed_data.py
Script to seed initial data into the database.

### seed_error.log
Log file for seeding errors.

### verify_delete.py
Script to verify deletion operations.

### verify_permission_sync.py
Script to verify permission synchronization.

### verify_validation.py
Script to verify form validation logic.

### alembic.ini
Alembic configuration for database migrations.

### alembic/
#### env.py
Alembic environment configuration for migrations.

#### script.py.mako
Alembic migration script template.

#### versions/
##### 20260121_143018_add_is_superuser_to_users.py
Migration to add is_superuser field to users table.

##### 20260126_053222_add_missing_audit_fields_clean.py
Migration to add missing audit fields.

##### 20260126_063802_add_audit_columns_to_user_roles.py
Migration to add audit columns to user_roles table.

##### 20260126_add_audit_columns.py
Migration to add audit columns.

##### 20260126_add_field_types.py
Migration to add field types.

##### perf_indexes_001.py
Migration to add performance indexes.

### app/
#### __init__.py
Package initialization for the app module.

#### main.py
Main FastAPI application setup file that configures the core web framework. It defines an async lifespan context manager that handles application startup and shutdown events, including database table creation, Redis cache initialization, and Casbin enforcer setup. The file configures CORS middleware for cross-origin requests, mounts static file directories, adds custom monitoring and caching middlewares, includes the main API router, and sets up custom exception handlers. It also customizes the OpenAPI schema with project-specific metadata and provides the entry point for running the server with Uvicorn.

#### api/
##### __init__.py
API package initialization.

##### v1/
###### __init__.py
Version 1 API package initialization.

###### api.py
Main API router that includes all endpoint routers.

###### endpoints/
####### __init__.py
Endpoints package initialization.

####### abac.py
API endpoints for Attribute-Based Access Control (ABAC) management.

####### authorization.py
Endpoints for general authorization operations.

####### auth.py
FastAPI router containing authentication endpoints for user management. Includes user registration with email validation and password hashing, login with OAuth2 password flow that returns JWT access and refresh tokens, token refresh functionality to extend sessions, logout to invalidate refresh tokens, and a /me endpoint to retrieve current user information. Implements rate limiting, audit logging for security events, and proper error handling for authentication failures.

####### banks.py
Endpoints for managing bank entities.

####### enums.py
Endpoints for retrieving enumeration values.

####### field_types.py
Endpoints for managing form field types.

####### files.py
Endpoints for file upload and management.

####### health.py
Health check endpoints for monitoring.

####### rbac.py
Endpoints for Role-Based Access Control (RBAC) management.

####### rebac.py
Endpoints for Relationship-Based Access Control (ReBAC) management.

####### roles.py
Endpoints for role management.

####### submissions.py
Endpoints for form submission management.

####### templates.py
Endpoints for form template management.

####### users.py
Endpoints for user management.

#### casbin/
##### __init__.py
Casbin package initialization.

##### abac_model.conf
Casbin model configuration for Attribute-Based Access Control.

##### rbac_model.conf
Casbin model configuration for Role-Based Access Control.

##### rebac_model.conf
Casbin model configuration for Relationship-Based Access Control.

#### core/
##### __init__.py
Core package initialization.

##### cache.py
Redis caching implementation.

##### casbin_enforcer.py
Casbin enforcer setup and management.

##### config.py
Application configuration using Pydantic settings.

##### json_schema_validator.py
JSON Schema validation utilities.

##### logging_config.py
Structured logging configuration.

##### metrics.py
Application metrics and monitoring.

##### security.py
Security utilities including password hashing and JWT handling.

##### validator.py
Form validation logic and rules.

#### db/
##### __init__.py
Database package initialization.

##### base.py
Database base configuration and model imports.

##### base_class.py
Base SQLAlchemy model class with common fields.

##### session.py
Database session management and connection setup.

#### dependencies/
##### __init__.py
Dependencies package initialization.

##### audit.py
Audit logging dependency injection.

##### auth.py
Authentication dependency injection.

##### pagination.py
Pagination dependency injection.

##### permissions.py
Permission checking dependency injection.

##### services.py
Service layer dependency injection.

#### dtos/
##### custom_response_dto.py
Custom response data transfer objects.

#### exceptions/
##### __init__.py
Exceptions package initialization.

##### handlers.py
Global exception handlers for FastAPI.

##### http_exceptions.py
Custom HTTP exception classes.

#### middlewares/
##### __init__.py
Middlewares package initialization.

##### auth_middleware.py
Authentication middleware.

##### clientid.py
Client ID validation middleware.

##### cors.py
CORS middleware configuration.

##### logging.py
Request logging middleware.

##### monitoring.py
Request monitoring and metrics middleware.

##### setup.py
Middleware setup and configuration.

#### models/
##### __init__.py
Models package initialization.

##### abac.py
SQLAlchemy models for Attribute-Based Access Control.

##### audit.py
Audit logging models.

##### field_types.py
Models for form field types.

##### forms.py
Models for forms, templates, and submissions.

##### user.py
User and role models.

#### repositories/
##### __init__.py
Repositories package initialization.

##### audit.py
Data access layer for audit logs.

##### base.py
Base repository class with common CRUD operations.

##### field_types.py
Repository for field types data access.

##### forms.py
Repository for forms and templates data access.

##### user.py
Repository for user data access.

#### schemas/
##### __init__.py
Schemas package initialization.

##### abac.py
Pydantic schemas for ABAC operations.

##### authorization.py
Schemas for authorization requests/responses.

##### auth.py
Authentication schemas (login, tokens).

##### common.py
Common schemas used across the application.

##### field_types.py
Schemas for field types.

##### forms.py
Schemas for forms, templates, and submissions.

##### rbac.py
Schemas for Role-Based Access Control.

##### user.py
Schemas for user management.

#### services/
##### __init__.py
Services package initialization.

##### abac_service.py
Business logic for Attribute-Based Access Control.

##### audit.py
Audit logging service.

##### authorization_service.py
General authorization service.

##### field_types.py
Field types management service.

##### form_validation.py
Form validation service.

##### rebac_service.py
Relationship-Based Access Control service.

##### user_service.py
User management business logic.

#### utils/
##### __init__.py
Utils package initialization.

##### common.py
Common utility functions.

##### docs.py
Documentation utilities.

##### json_schema_builder.py
Utilities for building JSON schemas.

##### queue.py
Queue management utilities (Redis RQ).

##### rate_limit.py
Rate limiting utilities.

##### response.py
Response formatting utilities.

##### validators.py
Additional validation utilities.

### scripts/
#### check_user_access.py
Script to check user access permissions.

#### ensure_permissions.py
Script to ensure correct role permissions are set.

#### example_field_types_usage.py
Example script showing field types usage.

#### fix_null_superuser.py
Script to fix null superuser fields.

#### fix_permissions.sh
Shell script to fix permissions.

#### fix_role_permissions.py
Script to fix role permissions.

#### init_db.py
Database initialization script.

#### quick_fix_for_teammates.sh
Quick fix shell script for teammates.

#### run_seed.sh
Shell script to run database seeding.

#### seed_database.py
Script to seed the database with initial data.

#### seed_data.py (legacy)
Legacy data seeding script (drops/recreates form tables and seeds
sample data). Replaced in normal workflows by
`backend/scripts/seed_all_templates.py` which is non-destructive.

#### seed_field_types.py (legacy)
Legacy script to seed field types. Its logic is now orchestrated by
`backend/scripts/seed_all_templates.py`.

#### seed_form_templates.py (legacy)
Legacy script to seed form templates (JSON-schema based). It is now
invoked via `backend/scripts/seed_all_templates.py`.

#### seed_predefined_field_types.py (legacy)
Legacy script to seed predefined field types. It is now invoked via
`backend/scripts/seed_all_templates.py`.

#### seed_sample_templates.py (legacy)
Legacy script to seed sample templates. It is now invoked via
`backend/scripts/seed_all_templates.py`.

#### setup.sh
Setup shell script for the project.

#### sync_user_roles.py
Script to synchronize user roles.

#### test_bank_restrictions.py
Script to test bank restrictions.

#### test_permissions_endpoint.py
Script to test permissions endpoints.

#### test_permissions.py
Script to test permissions.

#### verify_policies.py
Script to verify authorization policies.

### tests/
#### __init__.py
Tests package initialization.

#### conftest.py
Pytest configuration and fixtures.

#### test_validator.py
Unit tests for the validator module.

#### docs/
##### functional_testing.md
Documentation for functional testing.

##### integration_testing.md
Documentation for integration testing.

##### README.md
Testing documentation overview.

##### unit_testing.md
Documentation for unit testing.

#### functional/
##### __init__.py
Functional tests package initialization.

##### test_app.py
Functional tests for the application.

##### test_middleware_functional.py
Functional tests for middleware.

##### test_user_endpoints.py
Functional tests for user endpoints.

##### test_user_login.py
Functional tests for user login.

##### test_user_register.py
Functional tests for user registration.

#### integration/
##### __init__.py
Integration tests package initialization.

##### test_repository.py
Integration tests for repositories.

##### test_services.py
Integration tests for services.

##### test_user_repository.py
Integration tests for user repository.

#### unit/
##### __init__.py
Unit tests package initialization.

##### test_schemas.py
Unit tests for Pydantic schemas.

##### test_security.py
Unit tests for security utilities.

##### test_user_service.py
Unit tests for user service.

##### test_utils.py
Unit tests for utility functions.

### uploads/
#### file_*.jfif
Uploaded image files from form submissions.

## frontend/

### *.html
HTML pages for the frontend interface:
- abac.html: Attribute-Based Access Control page
- admin-templates.html: Admin template management page
- dashboard.html: Main dashboard page
- form-fill.html: Form filling page
- index.html: Main index page
- index-debug.html: Debug version of index page
- index-nojs.html: No-JavaScript fallback page
- profile.html: User profile page
- rebac.html: Relationship-Based Access Control page
- register.html: User registration page
- roles.html: Role management page
- simple-test.html: Simple test page
- submissions.html: Form submissions page
- test.html: Test page
- users.html: User management page

### css/
#### custom.css
Custom CSS styles for the frontend.

#### index.css
Main CSS styles for the index page.

#### .gitkeep
Placeholder file to keep the directory in git.

### images/
#### favicon.ico
Favicon icon file.

#### favicon.png
Favicon PNG file.

### js/
#### .gitkeep
Placeholder file to keep the directory in git.

#### abac.js
JavaScript for ABAC functionality.

#### admin-templates.js
JavaScript for admin template management.

#### api.js
API client utilities for frontend.

#### auth.js
Authentication JavaScript functions.

#### dashboard.js
Dashboard page JavaScript.

#### form-fill.js
Form filling JavaScript logic.

#### FormRenderer.js
Main form rendering engine with conditional logic.

#### profile.js
Profile page JavaScript.

#### rbac.js
Role-Based Access Control JavaScript.

#### rebac.js
Relationship-Based Access Control JavaScript.

#### roles.js
Role management JavaScript.

#### submissions.js
Submissions page JavaScript.

#### users.js
User management JavaScript.

#### utils.js
Common utility functions for frontend.