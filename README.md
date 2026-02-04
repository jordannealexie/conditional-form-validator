# Dynamic Form Validation System

A comprehensive form management and validation platform built with FastAPI and Vanilla JavaScript.

## Key Features

### 🛠 Dynamic Form Engine
- **JSONSchema Validation**: Strict data typing and structure enforcement.
- **Nested Conditional Logic**: Advanced `show_if` rules (all/any/not) for complex business requirements.
- **Real-time Rendering**: Vanilla JS renderer that handles dynamic DOM updates and visibility.
- **Multi-bank Support**: BDO, Maya Bank, and Security Bank templates.

### 🔐 Unified Authorization
- **RBAC**: Role-Based Access Control for distinct user roles (Admin, Supervisor, Fieldman).
- **ABAC**: Attribute-Based Access Control for fine-grained resource permissions with sample policies.
- **ReBAC**: Relationship-Based Access Control for hierarchical data ownership with sample relationships.
- **Multi-tenant Visibility**: Banks can only see their own data and forms.
- **Sample Policies**: Pre-configured ABAC policies and ReBAC relationships for testing.

📖 **See [ABAC_REBAC_README.md](backend/ABAC_REBAC_README.md) for detailed documentation on ABAC and ReBAC features.**

### 🚀 Performance & Scalability
- **Redis Cache**: High-performance caching for templates and user sessions.
- **Async Database**: Fully asynchronous PostgreSQL operations with SQLAlchemy.
- **MinIO Storage**: S3-compatible object storage for scalable file uploads.
- **Background Tasks**: Asynchronous processing for notifications and heavy operations.
- **Request Monitoring**: Comprehensive logging and performance tracking.

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM with async support
- **PostgreSQL**: Primary database for persistent storage
- **Redis**: Caching and session management
- **MinIO**: S3-compatible object storage for file uploads
- **Pydantic**: Data validation using Python type annotations
- **Casbin**: Authorization library for RBAC/ABAC/ReBAC
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Bootstrap**: Responsive UI components
- **JSON Editor**: Dynamic form rendering and editing

## Architecture

The application follows a modular architecture with clear separation of concerns:

- **API Layer** (`app/api/`): FastAPI routers and endpoints
- **Services Layer** (`app/services/`): Business logic and data processing
- **Repositories Layer** (`app/repositories/`): Data access and database queries
- **Models Layer** (`app/models/`): SQLAlchemy database models
- **Schemas Layer** (`app/schemas/`): Pydantic request/response models
- **Core Layer** (`app/core/`): Configuration, security, and utilities
- **Dependencies** (`app/dependencies/`): Dependency injection functions
- **Middlewares** (`app/middlewares/`): Custom middleware for authentication and logging

## Getting Started

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (Recommended - includes PostgreSQL, Redis, and MinIO)
- Redis (Optional, for RQ - included in Docker setup)
- PostgreSQL (Optional - included in Docker setup)
- MinIO (Optional - included in Docker setup)

### Quick Start with Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/jordannealexie/conditional-form-validator-backend.git
   cd conditional-form-validator-backend/backend
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This will start PostgreSQL (port 5434), Redis (port 6379), MinIO (port 9000/9001), and the API (port 8001).

3. **Setup Python environment and run application**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Seed database with templates and lookup data (single seed entrypoint)
   cd backend
   python scripts/seed_all_templates.py
   
   # Start the application
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Manual Setup (Without Docker)

1. **Clone the repository**
   ```bash
   git clone https://github.com/jordannealexie/conditional-form-validator-backend.git
   cd conditional-form-validator-backend
   ```

2. **Create PostgreSQL Database**
   ```bash
   # Login to PostgreSQL
   psql -U postgres
   
   # Create database
   CREATE DATABASE fastapi_db;
   \q
   ```

3. **Setup Backend**
   ```bash
   cd backend
   python3 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   
   Copy `.env.example` to `.env` in the `backend/` directory and update with your values:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/fastapi_db
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=fastapi_db
   SECRET_KEY=your-secret-key-change-in-production
   
   # MinIO Configuration (for file storage)
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin
   MINIO_BUCKET=uploads
   MINIO_SECURE=false
   ```

5. **Initialize Database and Seed Data**
   ```bash
   # Create admin user (if needed)
   python create_admin.py

   # Seed database with templates, field types, and lookup data
   # This is the ONLY seed script teammates should run
   python scripts/seed_all_templates.py
   ```

6. **Run Application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Setup (Alternative)

For easier setup with all dependencies (PostgreSQL, Redis), use Docker Compose:

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```
   This runs PostgreSQL (port 5434), Redis (port 6379), MinIO (port 9000/9001), and optionally the API container.

3. **Follow steps 3-6 from Quick Start to run the Python application locally**

The application will be available at: **[http://localhost:8000](http://localhost:8000)**

### Accessing the Application

Open your browser and navigate to: **[http://localhost:8000](http://localhost:8000)**

**Default Login Credentials:**

| Role | Username | Password | Bank |
|------|----------|----------|------|
| Super Admin | `harrypotter` | `harrypotter` | N/A |
| Admin (BDO) | `bdo_admin_1` | `password123` | BDO |
| Supervisor (BDO) | `bdo_supervisor_1` | `password123` | BDO |
| Fieldman (BDO) | `bdo_fieldman_1` | `password123` | BDO |
| Admin (Maya) | `maya_admin_1` | `password123` | Maya Bank |
| Admin (SECB) | `secb_admin_1` | `password123` | Security Bank |

### API Documentation

- **Swagger UI**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **ReDoc**: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)
- **Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **Metrics**: [http://localhost:8000/api/v1/health/metrics](http://localhost:8000/api/v1/health/metrics)

### MinIO Object Storage

The application uses MinIO for scalable file storage. When running with Docker Compose, MinIO is automatically started.

- **MinIO Console**: [http://localhost:9001](http://localhost:9001)
  - **Username**: `minioadmin`
  - **Password**: `minioadmin`
- **API Endpoint**: `http://localhost:9000`
- **Default Bucket**: `uploads`

All file uploads are stored in the `uploads` bucket and can be accessed through the application's file endpoints.

### Frontend

The project includes a Vanilla JavaScript frontend for form management and submission. The frontend files are located in the `frontend/` directory and are served statically by the FastAPI backend.

Key frontend features:
- User authentication and authorization
- Dynamic form rendering with conditional logic
- Admin panel for template management
- Role-based UI components
- **ABAC Policy Management** (`/abac.html`): View, create, edit, and test attribute-based access policies
- **ReBAC Relationship Management** (`/rebac.html`): Manage relationships between users and resources

## Project Status

✅ **Completed Features:**
- Full RBAC/ABAC/ReBAC authorization system with sample policies
- Multi-tenant bank support (BDO, Maya Bank, Security Bank)
- Dynamic form templates with conditional logic
- User management and authentication
- Database seeding with test data (including ABAC/ReBAC)
- API documentation and health monitoring
- Redis caching and session management
- Comprehensive logging and error handling
- Frontend interfaces for ABAC and ReBAC management

✅ **Current Functionality:**
- Login system with role-based access
- Form template management
- User dashboard
- Admin panel for template creation
- Multi-bank form submissions
- Real-time form validation

🔧 **Recent Updates (Feb 2026):**
- Integrated MinIO object storage for scalable file uploads
- Updated Docker configuration with MinIO service
- Enhanced file storage with S3-compatible backend
- Improved environment configuration with .env.example

## Troubleshooting

### Common Issues

1. **Port 8000 already in use**
   ```bash
   # Kill existing processes
   lsof -ti:8000 | xargs kill -9
   # Or use a different port
   uvicorn app.main:app --reload --port 8001
   ```

2. **Database connection error**
   - Ensure PostgreSQL is running (Docker: `docker-compose ps`)
   - Check environment variables in `.env`
   - Verify database exists: `psql -U postgres -h localhost -p 5434 -d fastapi_db`

3. **Redis connection error**
   - Redis is optional for basic functionality
   - Start Redis: `docker-compose up redis -d`
   - Application will fallback to in-memory caching

4. **MinIO connection error**
   - Ensure MinIO is running: `docker-compose ps minio`
   - Check MinIO console: [http://localhost:9001](http://localhost:9001)
   - Verify bucket exists in MinIO console
   - Check MinIO environment variables in `.env`

5. **Form templates not loading**
   - Run seed script: `python seed_data.py`
   - Check API endpoint: `curl -H "X-Client-ID: web-client-v1" http://localhost:8000/api/v1/health`

### Development Tips

- Use `--reload` flag for auto-restart during development
- Check logs at `/api/v1/health/metrics` for performance monitoring
- API documentation available at `/api/v1/docs` for testing endpoints

## License
MIT

## Killing used port
sudo lsof -i :8000
sudo kill -9 PID