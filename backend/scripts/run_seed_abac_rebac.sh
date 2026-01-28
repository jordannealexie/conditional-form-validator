#!/bin/bash
# Wrapper script to run ABAC/ReBAC seeding with correct database URL

cd "$(dirname "$0")/.."

DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/fastapi_db" \
python scripts/seed_abac_rebac_new.py
