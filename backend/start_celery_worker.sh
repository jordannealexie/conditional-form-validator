#!/bin/bash

# Celery Worker Startup Script
# This script starts the Celery worker for processing audit log tasks

set -e

echo "Starting Celery worker for audit tasks..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker
celery -A app.core.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --queues=audit_queue \
    --hostname=audit_worker@%h \
    --max-tasks-per-child=1000 \
    --time-limit=300 \
    --soft-time-limit=240

echo "Celery worker stopped."
