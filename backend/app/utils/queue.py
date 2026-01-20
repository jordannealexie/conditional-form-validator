import logging
from typing import Callable, Any, Optional
from fastapi import BackgroundTasks
from redis import Redis
from rq import Queue
from app.core.config import settings

logger = logging.getLogger(__name__)

class QueueService:
    """
    Unified Queue Service that uses RQ if Redis is available, 
    otherwise falls back to FastAPI's BackgroundTasks.
    """
    _redis_conn: Optional[Redis] = None
    _rq_queue: Optional[Queue] = None

    @classmethod
    def _get_rq_queue(cls) -> Optional[Queue]:
        if cls._rq_queue:
            return cls._rq_queue
        
        try:
            # Try to connect to Redis
            # In development, settings.REDIS_URL should be set
            # fallback to localhost if not set
            redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")
            cls._redis_conn = Redis.from_url(redis_url, socket_connect_timeout=1)
            cls._redis_conn.ping() # Test connection
            cls._rq_queue = Queue("default", connection=cls._redis_conn)
            logger.info("✅ Connected to Redis for RQ")
            return cls._rq_queue
        except Exception as e:
            logger.warning(f"⚠️ Redis not available, falling back to BackgroundTasks: {e}")
            return None

    @classmethod
    def enqueue(cls, func: Callable, *args, background_tasks: Optional[BackgroundTasks] = None, **kwargs) -> Any:
        """
        Enqueue a task.
        If background_tasks is provided and Redis is not available, uses it.
        Otherwise attempts to use RQ.
        """
        queue = cls._get_rq_queue()
        
        if queue:
            try:
                job = queue.enqueue(func, *args, **kwargs)
                logger.info(f"🚀 Enqueued task {func.__name__} to RQ (Job ID: {job.id})")
                return job
            except Exception as e:
                logger.error(f"❌ Failed to enqueue to RQ: {e}")

        # Fallback to BackgroundTasks
        if background_tasks:
            background_tasks.add_task(func, *args, **kwargs)
            logger.info(f"🕒 Task {func.__name__} added to FastAPI BackgroundTasks")
            return None
        
        # Immediate execution if no queue and no background_tasks (not ideal but safe)
        logger.warning(f"⚠️ No queue or background_tasks available, executing {func.__name__} synchronously")
        return func(*args, **kwargs)

# Task definitions (examples)

def send_submission_notification(submission_id: int):
    """Notify supervisor of new submission"""
    logger.info(f"📧 Notification for submission {submission_id} processed")
    # Real implementation would send email/SMS

def process_file_upload(file_token: str):
    """Simulate file processing (anti-virus, thumbnail, etc.)"""
    logger.info(f"🛡️ File {file_token} processed for security")
    # Real implementation would scan file

def log_audit_event(user_id: int, action: str, details: str):
    """Log audit event asynchronously"""
    logger.info(f"📝 Audit: User {user_id} performed {action}")
    # Real implementation would save to audit_logs table
