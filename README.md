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
2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Database Setup**
   Ensure your `DATABASE_URL` is set in environment variables or `app/core/config.py`.
   ```bash
   python seed_data.py
   ```
4. **Run Application**
   ```bash
   uvicorn app.main:app --reload
   ```

### Accessing the Frontend

The frontend is built with vanilla JavaScript and is served directly by the FastAPI backend.

- **URL**: [http://localhost:8000](http://localhost:8000)
- **Directory**: All frontend files are located in the `/frontend` directory.

Once the backend server is running, you can open your browser and navigate to the URL above to access the dashboard and form submission system.

## Documentation
- [Implementation Plan](.gemini/antigravity/brain/07899d65-236f-49d5-b6b7-08fca3e9483a/implementation_plan.md)
- [Final Walkthrough](.gemini/antigravity/brain/07899d65-236f-49d5-b6b7-08fca3e9483a/walkthrough.md)

## License
MIT
