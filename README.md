# Dynamic Form Validation System

A comprehensive form management and validation platform built with FastAPI and Vanilla JavaScript.

## Features

### 🛠 Dynamic Form Engine
- **JSONSchema Validation**: Strict data typing and structure enforcement.
- **Nested Conditional Logic**: Advanced `show_if` rules (all/any/not) for complex business requirements.
- **Real-time Rendering**: Vanilla JS renderer that handles dynamic DOM updates and visibility.

### 🔐 Unified Authorization
- **RBAC**: Role-Based Access Control for distinct user roles (Admin, Supervisor, Fieldman).
- **ABAC**: Attribute-Based Access Control for fine-grained resource permissions.
- **ReBAC**: Relationship-Based Access Control for hierarchical data ownership.
- **Multi-tenant Visibility**: Banks (BDO, Maya, Security Bank) can only see their own data.

### 🚀 Performance & Scalability
- **Redis Queue (RQ)**: Asynchronous processing for notifications and heavy tasks.
- **Background Fallback**: Automatic failover to FastAPI `BackgroundTasks` if Redis is offline.
- **Async DB**: Fully asynchronous database operations with SQLAlchemy and PostgreSQL.

## Getting Started

### Prerequisites
- Python 3.9+
- Redis (Optional, for RQ)
- PostgreSQL

### Installation

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
   CREATE DATABASE form_db;
   \q
   ```

3. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   
   # Activate virtual environment
   # On Windows: venv\Scripts\activate
   # On Linux/Mac:
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Configure Environment (Optional)**
   
   If you need custom settings, create `.env` in the `backend/` directory:
   ```env
   DATABASE_URL=postgresql://postgres:password@localhost:5432/form_db
   SECRET_KEY=your-secret-key-here
   ```

5. **Seed Database**
   ```bash
   # Run from backend/ directory with venv activated
   python -m scripts.seed_data
   ```

6. **Run Application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Accessing the Application

Open your browser and navigate to: **[http://localhost:8000](http://localhost:8000)**

**Default Login Credentials:**

| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |
| Supervisor (BDO) | `supervisor_bdo` | `password123` |
| Fieldman (BDO) | `user1` | `password123` |

### API Documentation

- Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- ReDoc: [http://localhost:8000/api/v1/redoc](http://localhost:8000/api/v1/redoc)

## Documentation
- [Implementation Plan](.gemini/antigravity/brain/07899d65-236f-49d5-b6b7-08fca3e9483a/implementation_plan.md)
- [Final Walkthrough](.gemini/antigravity/brain/07899d65-236f-49d5-b6b7-08fca3e9483a/walkthrough.md)

## License
MIT
