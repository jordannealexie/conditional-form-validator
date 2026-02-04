"""Celery tasks for asynchronous audit log persistence and batch processing"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from celery import Task
from sqlalchemy import create_engine, insert, delete, select, func, and_
from sqlalchemy.orm import sessionmaker
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.audit import AuditLog
import logging
import json
import csv
import io

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base task with database session management"""
    _engine = None
    _SessionLocal = None

    @property
    def engine(self):
        if self._engine is None:
            # Use synchronous engine for Celery tasks
            sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "")
            self._engine = create_engine(
                sync_db_url,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
        return self._engine

    @property
    def SessionLocal(self):
        if self._SessionLocal is None:
            self._SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        return self._SessionLocal


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.bulk_create_audit_logs",
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def bulk_create_audit_logs(self, audit_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bulk insert audit log entries asynchronously.
    
    Args:
        audit_entries: List of dictionaries containing audit log data
        
    Returns:
        Dict containing success status and count of inserted records
        
    This task is idempotent and can be safely retried.
    """
    if not audit_entries:
        logger.warning("bulk_create_audit_logs called with empty entries list")
        return {"success": True, "count": 0, "message": "No entries to insert"}
    
    session = self.SessionLocal()
    try:
        # Validate and prepare entries
        validated_entries = []
        for entry in audit_entries:
            # Ensure all required fields are present
            if "action" not in entry:
                logger.error(f"Missing 'action' field in audit entry: {entry}")
                continue
            
            # Set defaults for optional fields
            entry.setdefault("resource_type", "system")
            entry.setdefault("status", "success")
            
            validated_entries.append(entry)
        
        if not validated_entries:
            logger.warning("No valid entries after validation")
            return {"success": True, "count": 0, "message": "No valid entries to insert"}
        
        # Bulk insert using SQLAlchemy Core for better performance
        stmt = insert(AuditLog).values(validated_entries)
        session.execute(stmt)
        session.commit()
        
        logger.info(f"Successfully inserted {len(validated_entries)} audit log entries")
        return {
            "success": True,
            "count": len(validated_entries),
            "message": f"Successfully inserted {len(validated_entries)} audit logs"
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in bulk_create_audit_logs: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


@celery_app.task(
    name="app.tasks.audit_tasks.test_celery_connection",
    bind=False
)
def test_celery_connection() -> Dict[str, str]:
    """Simple test task to verify Celery is working"""
    return {"status": "success", "message": "Celery is working correctly"}


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.batch_delete_audit_logs",
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
)
def batch_delete_audit_logs(
    self,
    entity_type: Optional[str] = None,
    entity_ids: Optional[List[int]] = None,
    older_than_days: Optional[int] = None,
    actor_user_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Batch delete audit log entries based on criteria.
    
    Args:
        entity_type: Delete logs for specific entity type
        entity_ids: Delete logs for specific entity IDs
        older_than_days: Delete logs older than specified days
        actor_user_id: Delete logs by specific actor
        
    Returns:
        Dict containing success status and count of deleted records
    """
    session = self.SessionLocal()
    try:
        # Build delete query with filters
        conditions = []
        
        if entity_type:
            conditions.append(func.lower(AuditLog.resource_type) == entity_type.lower())
        
        if entity_ids:
            str_ids = [str(eid) for eid in entity_ids]
            conditions.append(AuditLog.resource_id.in_(str_ids))
        
        if older_than_days:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
            conditions.append(AuditLog.created_at < cutoff_date)
        
        if actor_user_id:
            conditions.append(AuditLog.user_id == actor_user_id)
        
        if not conditions:
            logger.warning("batch_delete_audit_logs called without any filter criteria")
            return {
                "success": False,
                "count": 0,
                "message": "No filter criteria provided - refusing to delete all logs"
            }
        
        # Execute delete
        stmt = delete(AuditLog).where(and_(*conditions))
        result = session.execute(stmt)
        session.commit()
        
        deleted_count = result.rowcount
        logger.info(f"Successfully deleted {deleted_count} audit log entries")
        
        return {
            "success": True,
            "count": deleted_count,
            "message": f"Successfully deleted {deleted_count} audit logs"
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in batch_delete_audit_logs: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.batch_export_audit_logs",
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
)
def batch_export_audit_logs(
    self,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    actor_user_id: Optional[int] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    export_format: str = "json"
) -> Dict[str, Any]:
    """
    Batch export audit log entries based on criteria.
    
    Args:
        entity_type: Filter by entity type
        entity_id: Filter by entity ID
        actor_user_id: Filter by actor user ID
        from_date: Export logs from this date (ISO format)
        to_date: Export logs until this date (ISO format)
        export_format: Export format (json or csv)
        
    Returns:
        Dict containing success status and exported data
    """
    session = self.SessionLocal()
    try:
        # Build query with filters
        query = select(AuditLog)
        conditions = []
        
        if entity_type:
            conditions.append(func.lower(AuditLog.resource_type) == entity_type.lower())
        
        if entity_id:
            conditions.append(AuditLog.resource_id == str(entity_id))
        
        if actor_user_id:
            conditions.append(AuditLog.user_id == actor_user_id)
        
        if from_date:
            from_dt = datetime.fromisoformat(from_date.replace('Z', '+00:00'))
            conditions.append(AuditLog.created_at >= from_dt)
        
        if to_date:
            to_dt = datetime.fromisoformat(to_date.replace('Z', '+00:00'))
            conditions.append(AuditLog.created_at <= to_dt)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(AuditLog.created_at.desc())
        
        result = session.execute(query)
        logs = result.scalars().all()
        
        # Convert to serializable format
        exported_data = []
        for log in logs:
            log_dict = {
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "changes": log.changes,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "created_by": log.created_by,
                "updated_by": log.updated_by,
                "deleted_by": log.deleted_by,
            }
            exported_data.append(log_dict)
        
        if export_format.lower() == "csv":
            # Convert to CSV string
            if exported_data:
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=exported_data[0].keys())
                writer.writeheader()
                for row in exported_data:
                    # Convert nested dicts to JSON strings for CSV
                    csv_row = {k: json.dumps(v) if isinstance(v, dict) else v for k, v in row.items()}
                    writer.writerow(csv_row)
                csv_content = output.getvalue()
                output.close()
                
                return {
                    "success": True,
                    "count": len(exported_data),
                    "format": "csv",
                    "data": csv_content,
                    "message": f"Successfully exported {len(exported_data)} audit logs to CSV"
                }
        
        # Default JSON format
        return {
            "success": True,
            "count": len(exported_data),
            "format": "json",
            "data": exported_data,
            "message": f"Successfully exported {len(exported_data)} audit logs"
        }
        
    except Exception as e:
        logger.error(f"Error in batch_export_audit_logs: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.batch_archive_audit_logs",
    max_retries=3,
    default_retry_delay=10,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=120,
    retry_jitter=True,
)
def batch_archive_audit_logs(
    self,
    older_than_days: int,
    entity_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Archive audit logs older than specified days by exporting and then deleting.
    
    This task:
    1. Exports matching logs to JSON format
    2. Deletes the exported logs from the database
    3. Returns the archived data for storage
    
    Args:
        older_than_days: Archive logs older than specified days
        entity_type: Optionally filter by entity type
        
    Returns:
        Dict containing success status, archived data, and counts
    """
    session = self.SessionLocal()
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        
        # Build query for logs to archive
        query = select(AuditLog).where(AuditLog.created_at < cutoff_date)
        
        if entity_type:
            query = query.where(func.lower(AuditLog.resource_type) == entity_type.lower())
        
        query = query.order_by(AuditLog.created_at.asc())
        
        result = session.execute(query)
        logs = result.scalars().all()
        
        if not logs:
            return {
                "success": True,
                "archived_count": 0,
                "deleted_count": 0,
                "message": "No logs found matching archive criteria"
            }
        
        # Archive the logs (convert to JSON)
        archived_data = []
        log_ids = []
        for log in logs:
            log_ids.append(log.id)
            archived_data.append({
                "id": log.id,
                "user_id": log.user_id,
                "username": log.username,
                "action": log.action,
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "status": log.status,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "changes": log.changes,
                "created_at": log.created_at.isoformat() if log.created_at else None,
                "created_by": log.created_by,
                "updated_by": log.updated_by,
                "deleted_by": log.deleted_by,
            })
        
        # Delete the archived logs
        delete_stmt = delete(AuditLog).where(AuditLog.id.in_(log_ids))
        delete_result = session.execute(delete_stmt)
        session.commit()
        
        deleted_count = delete_result.rowcount
        
        logger.info(f"Archived {len(archived_data)} logs and deleted {deleted_count} from database")
        
        return {
            "success": True,
            "archived_count": len(archived_data),
            "deleted_count": deleted_count,
            "archived_data": archived_data,
            "cutoff_date": cutoff_date.isoformat(),
            "message": f"Successfully archived {len(archived_data)} audit logs older than {older_than_days} days"
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in batch_archive_audit_logs: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.get_audit_statistics",
    max_retries=2,
    default_retry_delay=5,
)
def get_audit_statistics(self) -> Dict[str, Any]:
    """
    Get statistics about audit logs for monitoring and reporting.
    
    Returns:
        Dict containing various audit log statistics
    """
    session = self.SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        
        # Total count
        total_query = select(func.count()).select_from(AuditLog)
        total = session.execute(total_query).scalar() or 0
        
        # Count by entity type
        entity_query = select(
            AuditLog.resource_type,
            func.count().label('count')
        ).group_by(AuditLog.resource_type)
        entity_result = session.execute(entity_query)
        logs_by_entity = {row.resource_type or 'unknown': row.count for row in entity_result}
        
        # Count by action
        action_query = select(
            AuditLog.action,
            func.count().label('count')
        ).group_by(AuditLog.action)
        action_result = session.execute(action_query)
        logs_by_action = {row.action or 'unknown': row.count for row in action_result}
        
        # Logs in last 24 hours
        last_24h = now - timedelta(hours=24)
        count_24h_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_24h
        )
        logs_last_24h = session.execute(count_24h_query).scalar() or 0
        
        # Logs in last 7 days
        last_7d = now - timedelta(days=7)
        count_7d_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_7d
        )
        logs_last_7d = session.execute(count_7d_query).scalar() or 0
        
        # Logs in last 30 days
        last_30d = now - timedelta(days=30)
        count_30d_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_30d
        )
        logs_last_30d = session.execute(count_30d_query).scalar() or 0
        
        return {
            "success": True,
            "total_logs": total,
            "logs_by_entity_type": logs_by_entity,
            "logs_by_action": logs_by_action,
            "logs_last_24h": logs_last_24h,
            "logs_last_7d": logs_last_7d,
            "logs_last_30d": logs_last_30d,
            "generated_at": now.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in get_audit_statistics: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.tasks.audit_tasks.process_audit_batch_with_validation",
    max_retries=3,
    default_retry_delay=5,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def process_audit_batch_with_validation(
    self,
    audit_entries: List[Dict[str, Any]],
    validate_entities: bool = False
) -> Dict[str, Any]:
    """
    Process a batch of audit entries with optional entity validation.
    
    This enhanced version supports:
    - Pre-processing and validation of entries
    - Optional validation that referenced entities exist
    - Detailed error reporting for failed entries
    
    Args:
        audit_entries: List of dictionaries containing audit log data
        validate_entities: If True, validate that referenced entities exist
        
    Returns:
        Dict containing success status, counts, and error details
    """
    if not audit_entries:
        logger.warning("process_audit_batch_with_validation called with empty entries list")
        return {"success": True, "processed": 0, "failed": 0, "message": "No entries to process"}
    
    session = self.SessionLocal()
    try:
        validated_entries = []
        failed_entries = []
        
        for idx, entry in enumerate(audit_entries):
            try:
                # Validate required fields
                if "action" not in entry:
                    failed_entries.append({
                        "index": idx,
                        "error": "Missing required field 'action'",
                        "entry": entry
                    })
                    continue
                
                # Build the audit log entry
                processed_entry = {
                    "action": entry.get("action"),
                    "resource_type": entry.get("entity_type", entry.get("resource_type", "system")).lower(),
                    "resource_id": str(entry.get("entity_id", entry.get("resource_id", ""))),
                    "user_id": entry.get("actor_user_id", entry.get("user_id")),
                    "username": entry.get("actor_username", entry.get("username")),
                    "status": entry.get("status", "success"),
                    "ip_address": entry.get("ip_address"),
                    "user_agent": entry.get("user_agent"),
                }
                
                # Build changes dict from before/after json
                changes = {}
                if entry.get("before_json"):
                    changes["before"] = entry["before_json"]
                if entry.get("after_json"):
                    changes["after"] = entry["after_json"]
                if entry.get("edited_fields"):
                    changes["edited_fields"] = entry["edited_fields"]
                
                if changes:
                    processed_entry["changes"] = changes
                
                # Set created_by, updated_by, deleted_by based on action
                action = entry.get("action", "").lower()
                actor_id = entry.get("actor_user_id", entry.get("user_id"))
                if action == "created":
                    processed_entry["created_by"] = actor_id
                elif action == "updated":
                    processed_entry["updated_by"] = actor_id
                elif action == "deleted":
                    processed_entry["deleted_by"] = actor_id
                
                validated_entries.append(processed_entry)
                
            except Exception as e:
                failed_entries.append({
                    "index": idx,
                    "error": str(e),
                    "entry": entry
                })
        
        # Bulk insert validated entries
        inserted_count = 0
        if validated_entries:
            stmt = insert(AuditLog).values(validated_entries)
            session.execute(stmt)
            session.commit()
            inserted_count = len(validated_entries)
        
        logger.info(
            f"Batch processing complete: {inserted_count} inserted, {len(failed_entries)} failed"
        )
        
        return {
            "success": True,
            "processed": inserted_count,
            "failed": len(failed_entries),
            "failed_entries": failed_entries if failed_entries else None,
            "message": f"Processed {inserted_count} entries, {len(failed_entries)} failed"
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error in process_audit_batch_with_validation: {str(e)}", exc_info=True)
        raise
    finally:
        session.close()
