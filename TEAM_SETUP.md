# Team Setup Guide

This document explains how any teammate can clone, set up, and run the project so that all backend + frontend features (including the audit trail) work the same.

## 1. Clone the Repository

```bash
git clone https://github.com/jordannealexie/conditional-form-validator-backend.git
cd conditional-form-validator-backend
```

If you are working from a fork, replace the URL with your fork URL.

## 2. Backend Environment Setup

From the `backend` folder:

```bash
cd backend

# (Recommended) Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2.1 Environment Variables (.env)

Create a `.env` file inside the `backend` directory with at least:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5434/fastapi_db
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db
SECRET_KEY=your-secret-key-change-in-production
REDIS_URL=redis://localhost:6379/0
```

Adjust values if your local PostgreSQL/Redis are different.

## 3. Start Infrastructure with Docker (Postgres + Redis)

From the `backend` directory:

```bash
cd backend

# Start Postgres and Redis (and optional API container)
docker-compose up -d
```

This will expose:
- PostgreSQL on `localhost:5434`
- Redis on `localhost:6379`

## 4. Initialize and Seed the Database

Still inside `backend` (and with the virtualenv activated):

```bash
# (Optional) Create an admin user
python create_admin.py

# Seed database with templates, field types, and lookup data
# This is the ONLY seed script your team should run
python scripts/seed_all_templates.py
```

Legacy seed scripts (`seed_data.py`, `seed_form_templates.py`,
`seed_sample_templates.py`, etc.) are kept only for reference and
should not be used in normal team workflows.

## 5. Run Database Migrations (Alembic)

```bash
cd backend
source venv/bin/activate

alembic upgrade head
```

This ensures your DB schema matches the latest code changes.

## 6. Run the Backend API Locally

From `backend` with the virtualenv active:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open Swagger at:
- http://localhost:8000/api/v1/docs

## 7. Frontend Usage

The frontend lives under `frontend/` and is served statically by the backend. After the backend is running, open:

- http://localhost:8000

Key pages:
- User Management: `/users.html`
- Roles & Permissions: `/roles.html`
- Template Builder (Form templates): `/admin-templates.html`

## 8. Keeping Everyone in Sync

### 8.1 Pulling Latest Changes

Each teammate should regularly pull from the main branch:

```bash
# From the project root
git pull origin main  # or the branch you all use
```

After pulling:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt      # in case dependencies changed
alembic upgrade head                 # in case migrations were added
```

### 8.2 Pushing Changes So Others See Them

After you make and test changes:

```bash
# From project root
git status         # check modified files
git add .          # or add specific files
git commit -m "Describe your change"
git push origin main   # or your feature branch
```

Your teammates then run:

```bash
git pull
cd backend
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

This ensures they have the same code, dependencies, and DB schema (including all audit trail features).

## 9. Running Tests

From `backend` with the virtualenv active:

```bash
python -m pytest tests/ -v
```

Use this to confirm everything passes before pushing changes that teammates will pull.
