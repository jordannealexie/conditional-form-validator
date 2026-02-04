"""Celery application configuration for async task processing"""

from celery import Celery
from app.core.config import settings

# Initialize Celery with Redis as broker and backend
celery_app = Celery(
    "audit_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.audit_tasks"]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_connection_retry_on_startup=True,
    result_expires=86400,  # Results expire after 24 hours
    result_extended=True,  # Store additional task metadata
)

# Task routes (optional: for task routing to specific queues)
celery_app.conf.task_routes = {
    "app.tasks.audit_tasks.bulk_create_audit_logs": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.batch_delete_audit_logs": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.batch_export_audit_logs": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.batch_archive_audit_logs": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.get_audit_statistics": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.process_audit_batch_with_validation": {"queue": "audit_queue"},
    "app.tasks.audit_tasks.test_celery_connection": {"queue": "default"},
}
