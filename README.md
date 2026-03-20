<h1 align="center">Conditional Form Validator</h1>

<p align="center">
  <b>Dynamic Form Management, Validation & Authorization Platform</b>
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,postgres,redis,bootstrap,js,git,github,vscode,docker" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Enterprise%20Backend-purple?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Auth-RBAC%20%7C%20ABAC-success?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Validation-Dynamic%20Forms-blue?style=for-the-badge"/>
</p>

---

## Overview

**Conditional Form Validator Backend** is a scalable dynamic form management and validation system designed to support enterprise-grade workflows.

The platform enables **runtime form rendering, conditional validation logic, multi-tenant visibility, and fine-grained authorization policies**, making it suitable for complex business environments such as banking or field operations systems.

It combines asynchronous backend services, caching strategies, and modular architecture to deliver high performance and extensibility.

---

## Key Features

- **Dynamic Form Rendering Engine** — runtime DOM updates and conditional field visibility  
- **Conditional Validation Logic** — rule-based validation driven by JSON form schemas  
- **Unified Authorization System**  
  - RBAC (Role-Based Access Control)  
  - ABAC (Attribute-Based Access Control)  
- **Multi-tenant Data Isolation** — organization-specific form visibility  
- **High Performance Caching** — Redis-powered template and session caching  
- **Scalable File Upload Storage** — MinIO S3-compatible object storage  
- **Async Background Processing** — notifications and heavy task handling  
- **Request Monitoring & Logging** — performance tracking and diagnostics  

---

## Technology Stack

### Backend

- FastAPI  
- SQLAlchemy (Async ORM)  
- PostgreSQL  
- Redis  
- MinIO  
- Pydantic  
- Casbin  
- Uvicorn  

### Frontend (Admin / Renderer)

- Vanilla JavaScript  
- Bootstrap  
- JSON Editor  

### Tooling

- Git  
- GitHub  
- VS Code  
- Docker (optional deployment)

---

## System Architecture

The application follows a **layered modular architecture**:

```

app/
├── api/              → FastAPI routers and endpoints
├── services/         → Business logic layer
├── repositories/     → Database interaction layer
├── models/           → SQLAlchemy database models
├── schemas/          → Pydantic request / response schemas
├── core/             → Config, security utilities
├── dependencies/     → Dependency injection logic
└── middlewares/      → Authentication and logging middleware

````

---

## Getting Started

### Clone Repository

```bash
git clone https://github.com/jordannealexie/conditional-form-validator.git
cd conditional-form-validator-backend
````

---

### Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

### Run Development Server

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://localhost:8000
```

---

## Database Setup

* PostgreSQL is used as the primary datastore
* Import provided dump file if needed:

```
dump-fastapi_db-*.sql
```

---

## Authorization Model

### RBAC

* Admin
* Supervisor
* Fieldman

### ABAC

* Policy-driven fine-grained permissions
* Resource-level access control
* Attribute-based evaluation

---

## Performance & Scalability Components

| Component        | Purpose                            |
| ---------------- | ---------------------------------- |
| Redis            | Template caching & session storage |
| Async SQLAlchemy | Non-blocking DB operations         |
| MinIO            | Scalable file upload storage       |
| Background Tasks | Heavy workload offloading          |

---

## Project Structure

```
conditional-form-validator-backend/
├── backend/
├── frontend/
├── requirements.txt
├── setup.md
└── database_dump.sql
```

---

## Future Improvements

* Visual form builder UI
* Validation rule versioning
* Audit trail for policy changes
* Multi-region storage deployment
* Real-time collaborative form editing
* GraphQL API gateway

---

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub.
