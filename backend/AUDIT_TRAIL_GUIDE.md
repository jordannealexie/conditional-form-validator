# Audit Trail Implementation Guide

## Overview

This document provides comprehensive guidance on implementing bulk audit trail logging with Celery task queue for asynchronous persistence.

## Architecture

### Components

1. **BulkAuditCollector**: Context manager for collecting audit entries in memory
2. **BulkAuditService**: Service for querying audit logs by page and row
3. **Celery Tasks**: Async task queue for bulk persistence
4. **Repository**: Database operations with bulk insert support
5. **API Endpoints**: Query endpoints for page-scoped and row-scoped audit logs

### Flow

```
API Endpoint
    ↓
Create BulkAuditCollector (context manager)
    ↓
Perform business logic (create/update/delete entities)
    ↓
For each entity: collector.add_entry(...)
    ↓
On context exit: Dispatch bulk task to Celery
    ↓
Celery Task: Bulk INSERT all entries in single transaction
    ↓
Database: Audit logs persisted
```

## Usage Examples

### Example 1: Bulk User Creation

```python
from fastapi import APIRouter, Depends, Request
from app.dependencies.audit import get_bulk_audit_service
from app.services.bulk_audit import BulkAuditService
from app.models.user import User

@router.post("/users/bulk")
async def bulk_create_users(
    users_data: List[UserCreate],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """Bulk create users with audit logging"""
    
    created_users = []
    
    # Use bulk audit collector
    async with bulk_audit_service.create_collector() as collector:
        for user_data in users_data:
            # Create user
            user = await user_service.create(user_data)
            created_users.append(user)
            
            # Add audit entry (collected in memory)
            collector.add_entry(
                action="created",
                entity_type="user",
                entity_id=user.id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                after_json={
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_active": user.is_active,
                },
                request=request
            )
    
    # At this point, all audit entries are dispatched to Celery
    # Business logic continues immediately
    
    return create_response(
        data=[UserResponse.model_validate(u) for u in created_users],
        message=f"Created {len(created_users)} users"
    )
```

### Example 2: Bulk User Update

```python
@router.put("/users/bulk")
async def bulk_update_users(
    updates: List[UserBulkUpdate],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """Bulk update users with audit logging"""
    
    updated_users = []
    
    async with bulk_audit_service.create_collector() as collector:
        for update_data in updates:
            # Get current state (before)
            user = await user_service.get(update_data.user_id)
            if not user:
                continue
            
            before_state = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
            }
            
            # Update user
            updated_user = await user_service.update(user.id, update_data.dict())
            updated_users.append(updated_user)
            
            after_state = {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "is_active": updated_user.is_active,
            }
            
            # Calculate changed fields
            edited_fields = [
                key for key in before_state.keys()
                if before_state[key] != after_state[key]
            ]
            
            # Add audit entry
            collector.add_entry(
                action="updated",
                entity_type="user",
                entity_id=updated_user.id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                before_json=before_state,
                after_json=after_state,
                edited_fields=edited_fields,
                request=request
            )
    
    return create_response(
        data=[UserResponse.model_validate(u) for u in updated_users],
        message=f"Updated {len(updated_users)} users"
    )
```

### Example 3: Bulk Delete

```python
@router.delete("/users/bulk")
async def bulk_delete_users(
    user_ids: List[int],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """Bulk delete users with audit logging"""
    
    deleted_count = 0
    
    async with bulk_audit_service.create_collector() as collector:
        for user_id in user_ids:
            # Get user before deletion
            user = await user_service.get(user_id)
            if not user:
                continue
            
            before_state = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
            }
            
            # Delete user
            await user_service.delete(user_id)
            deleted_count += 1
            
            # Add audit entry
            collector.add_entry(
                action="deleted",
                entity_type="user",
                entity_id=user_id,
                actor_user_id=current_user.id,
                actor_username=current_user.username,
                before_json=before_state,
                request=request
            )
    
    return create_response(
        message=f"Deleted {deleted_count} users"
    )
```

### Example 4: Using Helper Utilities

```python
from app.utils.audit_helpers import prepare_bulk_audit_entries, sanitize_for_audit

@router.post("/users/import")
async def import_users(
    users_data: List[UserCreate],
    request: Request,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
):
    """Import users from external source with audit logging"""
    
    created_users = []
    
    # Create all users first
    for user_data in users_data:
        user = await user_service.create(user_data)
        created_users.append(user)
    
    # Prepare bulk audit entries using helper
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    audit_entries = prepare_bulk_audit_entries(
        action="created",
        entity_type="user",
        entities=created_users,
        actor_user_id=current_user.id,
        actor_username=current_user.username,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # Dispatch to Celery
    from app.tasks.audit_tasks import bulk_create_audit_logs
    bulk_create_audit_logs.delay(audit_entries)
    
    return create_response(
        data=[UserResponse.model_validate(u) for u in created_users],
        message=f"Imported {len(created_users)} users"
    )
```

## Querying Audit Logs

### Get Audit Logs for a Page (Entity Type)

```
GET /api/v1/audit-trail/page/{entity_type}?page=1&page_size=50

Examples:
- /api/v1/audit-trail/page/user
- /api/v1/audit-trail/page/role
- /api/v1/audit-trail/page/form_template
```

### Get Audit Logs for a Row (Specific Entity)

```
GET /api/v1/audit-trail/row/{entity_type}/{entity_id}?page=1&page_size=50

Examples:
- /api/v1/audit-trail/row/user/123
- /api/v1/audit-trail/row/role/5
- /api/v1/audit-trail/row/form_template/42
```

### Get Audit Logs with Filters

```
GET /api/v1/audit-trail/entity/{entity_type}?entity_id=123&actor_user_id=5&page=1

Examples:
- /api/v1/audit-trail/entity/user?entity_id=123
- /api/v1/audit-trail/entity/user?actor_user_id=5
- /api/v1/audit-trail/entity/role?entity_id=10&actor_user_id=2
```

## Response Format

```json
{
  "success": true,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 50,
    "logs": [
      {
        "id": 1001,
        "action": "updated",
        "activity": "Updated User",
        "operator": "admin",
        "time": "2026-02-03T10:30:00Z",
        "num_fields_changed": 3,
        "before_json": {
          "username": "john_doe",
          "email": "john@example.com",
          "is_active": false
        },
        "after_json": {
          "username": "john_doe",
          "email": "john.doe@example.com",
          "is_active": true
        },
        "edited_fields": ["email", "is_active"],
        "entity_type": "user",
        "entity_id": "123"
      }
    ]
  }
}
```

## Performance Considerations

### Bulk Insert Performance

- **Single Transaction**: All audit entries are inserted in one transaction
- **Batch Size**: Recommended 50-100 entries per batch for optimal performance
- **Async Processing**: Celery handles persistence asynchronously, not blocking API response

### Database Considerations

- Ensure indexes on `resource_type`, `resource_id`, `user_id`, and `created_at`
- Consider partitioning audit_logs table by date for large datasets
- Use connection pooling for Celery workers

## Running Celery Worker

### Start Celery Worker

```bash
cd backend
celery -A app.core.celery_app worker --loglevel=info --concurrency=4 -Q audit_queue
```

### Monitor Celery

```bash
# Celery Flower (web-based monitoring)
celery -A app.core.celery_app flower --port=5555
```

## Testing

### Test Celery Connection

```python
from app.tasks.audit_tasks import test_celery_connection

# Test task
result = test_celery_connection.delay()
print(result.get(timeout=10))
```

### Test Bulk Audit Logging

```python
# In your test
async with bulk_audit_service.create_collector(async_mode=False) as collector:
    collector.add_entry(...)
    # Entries will be inserted directly (synchronous) for testing
```

## Best Practices

1. **Always use bulk collector** for operations affecting multiple entities
2. **Sanitize sensitive data** before adding to audit entries
3. **Include meaningful edited_fields** for updates
4. **Use before_json and after_json** for complete audit trail
5. **Never block on audit operations** - always use async mode in production
6. **Monitor Celery queue** to ensure tasks are processing
7. **Set appropriate TTL** for audit logs based on compliance requirements
8. **Test with async_mode=False** in unit tests for immediate verification

## Environment Variables

Add to `.env`:

```env
# Redis Configuration (used by Celery)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration (auto-constructed from Redis settings)
# Or override manually:
# CELERY_BROKER_URL=redis://localhost:6379/0
# CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Troubleshooting

### Issue: Audit logs not appearing

1. Check if Celery worker is running
2. Check Celery logs for errors
3. Verify Redis connection
4. Check database connection in Celery worker

### Issue: Performance degradation

1. Increase Celery worker concurrency
2. Optimize batch size
3. Add database indexes
4. Consider table partitioning

### Issue: Duplicate logs

1. Ensure idempotent task design
2. Check for retry configuration
3. Verify transaction boundaries
