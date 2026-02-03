# Conditional Form Validator Backend Setup Guide

This guide provides step-by-step instructions to set up and run the Conditional Form Validator Backend project, including backend, frontend, database, and related tools.

## Prerequisites

- Ubuntu/Linux environment
- Python 3.9+
- Node.js (for frontend if needed, but here it's static)
- Docker and Docker Compose
- DBeaver (database GUI tool)

## Project Structure

```
conditional-form-validator-backend/
├── backend/          # FastAPI backend
├── frontend/         # Static HTML/JS frontend
├── requirements.txt  # Python dependencies
└── setup.md         # This file
```

## 1. Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python, pip, and virtualenv
sudo apt install -y python3 python3-pip python3-venv

# Install Docker
sudo apt install -y docker.io docker-compose

# Install DBeaver
sudo snap install dbeaver-ce

# Install Node.js (if needed for frontend development)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 2. Clone and Setup Project

```bash
# Navigate to project directory (assuming already cloned)
cd ~/conditional-form-validator-backend

# Make scripts executable
chmod +x backend/scripts/*.sh
```

## 3. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Deactivate when done (optional)
# deactivate
```

## 4. Setup Database with Docker

```bash
# From backend directory
cd backend

# Start PostgreSQL database
docker compose up -d db

# Check if database is running
docker compose ps

# View database logs
docker compose logs db

# Stop database
# docker compose down
```

## 5. Initialize Database

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Run database migrations
alembic upgrade head

# Seed initial data
python scripts/seed_database.py
python scripts/seed_form_templates.py
python scripts/seed_lookups.py
python scripts/seed_predefined_field_types.py

# Create admin user
python create_admin.py
```

## 6. Start Backend Server

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Start FastAPI server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Alternative: Run with Docker
# docker compose up api
```

## 7. Setup Frontend

```bash
# Navigate to frontend directory
cd ../frontend

# Serve static files (simple HTTP server)
python3 -m http.server 3000

# Or use Node.js if preferred
# npx serve . -p 3000

# For development with live reload (if using Node.js)
# npm install -g live-server
# live-server --port=3000
```

## 8. Access the Application

- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs (Swagger UI)
- Alternative Docs: http://localhost:8000/redoc
- Frontend: http://localhost:3000

## 9. Database Management with DBeaver

```bash
# Open DBeaver
dbeaver-ce

# In DBeaver:
# 1. Create new connection
# 2. Select PostgreSQL
# 3. Host: localhost
# 4. Port: 5434
# 5. Database: fastapi_db
# 6. Username: postgres
# 7. Password: postgres
```

## 10. Useful Terminal Commands

### Port Management

```bash
# Check what's running on port 8000
lsof -i :8000

# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Check all listening ports
netstat -tlnp | grep LISTEN
```

### Docker Management

```bash
# From backend directory
cd backend

# Start all services
docker compose up -d

# Start specific service
docker compose up -d db
docker compose up -d redis

# Stop all services
docker compose down

# View logs
docker compose logs
docker compose logs db

# Rebuild and restart
docker compose up -d --build
```

### Database Operations

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Downgrade
alembic downgrade -1

# Reset database
python recreate_db.py
```

### Testing

```bash
# From backend directory with venv activated
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_validator.py

# Run with coverage
pytest --cov=app --cov-report=html
```

### Development Scripts

```bash
# From backend/scripts directory
cd backend/scripts

# Grant permissions
./grant_abac_rebac_permissions.sql

# Quick fix permissions
./fix_permissions.sh

# Seed ABAC/ReBAC data
./run_seed_abac_rebac.sh
```

## 11. Environment Configuration

The application uses environment variables defined in `backend/.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/fastapi_db

# Security
SECRET_KEY=your-secret-key-change-in-production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Client IDs
CLIENT_IDS=web-client-v1,test-client
```

## 12. Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   lsof -ti:8000 | xargs kill -9
   ```

2. **Database connection refused**
   ```bash
   # Ensure database is running
   docker compose up -d db
   # Wait for health check
   docker compose ps
   ```

3. **Module not found**
   ```bash
   # Ensure you're in backend directory and venv is activated
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Permission denied**
   ```bash
   # Make scripts executable
   chmod +x backend/scripts/*.sh
   ```

### Logs

```bash
# Backend logs
tail -f backend/backend.log

# Docker logs
docker compose logs -f

# System logs
journalctl -u docker.service
```

## 13. Production Deployment

For production deployment:

```bash
# Build and run with Docker
cd backend
docker compose -f docker-compose.yml up -d --build

# Or use Docker Compose for all services
docker compose up -d
```

## 14. API Endpoints

Key API endpoints:

- `GET /api/v1/health` - Health check
- `POST /api/v1/auth/token` - Login
- `GET /api/v1/users` - List users
- `GET /api/v1/forms` - List forms
- `POST /api/v1/forms` - Create form

See full API documentation at http://localhost:8000/docs

## 15. Development Workflow

1. Start database: `docker compose up -d db`
2. Activate venv: `source venv/bin/activate`
3. Run migrations: `alembic upgrade head`
4. Start backend: `uvicorn app.main:app --reload`
5. Start frontend: `cd ../frontend && python3 -m http.server 3000`
6. Open browser: http://localhost:3000
7. Use DBeaver for database inspection

Happy coding! 🚀