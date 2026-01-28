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
- **ABAC**: Attribute-Based Access Control for fine-grained resource permissions.
- **ReBAC**: Relationship-Based Access Control for hierarchical data ownership.
- **Multi-tenant Visibility**: Banks can only see their own data and forms.

### 🚀 Performance & Scalability
- **Redis Cache**: High-performance caching for templates and user sessions.
- **Async Database**: Fully asynchronous PostgreSQL operations with SQLAlchemy.
- **Background Tasks**: Asynchronous processing for notifications and heavy operations.
- **Request Monitoring**: Comprehensive logging and performance tracking.

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM with async support
- **PostgreSQL**: Primary database for persistent storage
- **Redis**: Caching and session management
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
- Docker and Docker Compose (Recommended)
- Redis (Optional, for RQ)
- PostgreSQL (if not using Docker)

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
   This will start PostgreSQL (port 5434), Redis (port 6379), and the API (port 8001).

3. **Setup Python environment and run application**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Seed database with test data
   python seed_data.py
   python test_templates.py
   
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
   
   Create `.env` in the `backend/` directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/fastapi_db
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=fastapi_db
   SECRET_KEY=your-secret-key-change-in-production
   ```

5. **Initialize Database and Seed Data**
   ```bash
   # Create admin user (optional, seed_data.py includes this)
   python create_admin.py
   
   # Seed database with test data
   python seed_data.py
   python test_templates.py
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
   This runs PostgreSQL (port 5434), Redis (port 6379), and optionally the API container.

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

### Frontend

The project includes a Vanilla JavaScript frontend for form management and submission. The frontend files are located in the `frontend/` directory and are served statically by the FastAPI backend.

Key frontend features:
- User authentication and authorization
- Dynamic form rendering with conditional logic
- Admin panel for template management
- Role-based UI components

## Project Status

✅ **Completed Features:**
- Full RBAC/ABAC/ReBAC authorization system
- Multi-tenant bank support (BDO, Maya Bank, Security Bank)
- Dynamic form templates with conditional logic
- User management and authentication
- Database seeding with test data
- API documentation and health monitoring
- Redis caching and session management
- Comprehensive logging and error handling

✅ **Current Functionality:**
- Login system with role-based access
- Form template management
- User dashboard
- Admin panel for template creation
- Multi-bank form submissions
- Real-time form validation

🔧 **Recent Updates (Jan 2026):**
- Fixed form template serialization issues
- Updated version validation to accept float formats
- Improved database connection handling
- Enhanced error logging and debugging
- Updated Docker configuration for easier setup

## Testing

Run the test suite using pytest:

```bash
cd backend
source venv/bin/activate  # Ensure virtual environment is active
python -m pytest tests/ -v
```

For coverage report:

```bash
python -m pytest --cov=app tests/ --cov-report=html
```

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

4. **Form templates not loading**
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