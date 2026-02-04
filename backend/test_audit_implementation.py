"""
Test file for bulk audit logging functionality.

Run this to verify the audit trail implementation works correctly.
"""

import asyncio
from datetime import datetime


async def test_bulk_audit_imports():
    """Test that all audit modules import correctly"""
    print("Testing imports...")
    
    try:
        from app.core.celery_app import celery_app
        print("✓ Celery app imported")
        
        from app.tasks.audit_tasks import bulk_create_audit_logs
        print("✓ Audit tasks imported")
        
        from app.services.bulk_audit import BulkAuditService, BulkAuditCollector
        print("✓ Bulk audit service imported")
        
        from app.repositories.audit import AuditRepository
        print("✓ Audit repository imported")
        
        from app.schemas.audit_trail import AuditLogDetailResponse, AuditTrailPageResponse
        print("✓ Audit schemas imported")
        
        from app.utils.audit_helpers import calculate_edited_fields, sanitize_for_audit
        print("✓ Audit helpers imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_audit_helpers():
    """Test audit helper functions"""
    print("\nTesting audit helpers...")
    
    from app.utils.audit_helpers import calculate_edited_fields, sanitize_for_audit
    
    # Test calculate_edited_fields
    before = {"name": "John", "email": "john@example.com", "age": 25}
    after = {"name": "John", "email": "john.doe@example.com", "age": 26}
    
    edited = calculate_edited_fields(before, after)
    assert "email" in edited, "Email should be in edited fields"
    assert "age" in edited, "Age should be in edited fields"
    assert "name" not in edited, "Name should not be in edited fields"
    print(f"✓ calculate_edited_fields works: {edited}")
    
    # Test sanitize_for_audit
    sensitive_data = {
        "username": "john",
        "password": "secret123",
        "email": "john@example.com",
        "password_hash": "$2b$12$...",
    }
    
    sanitized = sanitize_for_audit(sensitive_data)
    assert sanitized["password"] == "***REDACTED***", "Password should be redacted"
    assert sanitized["password_hash"] == "***REDACTED***", "Password hash should be redacted"
    assert sanitized["username"] == "john", "Username should not be redacted"
    print(f"✓ sanitize_for_audit works: {sanitized}")
    
    print("✅ Audit helpers working correctly!")
    return True


async def test_bulk_collector_structure():
    """Test bulk collector data structure"""
    print("\nTesting bulk collector...")
    
    from app.services.bulk_audit import BulkAuditCollector
    
    # Create collector
    collector = BulkAuditCollector(async_mode=False)
    
    # Add some entries
    collector.add_entry(
        action="created",
        entity_type="user",
        entity_id=123,
        actor_user_id=1,
        actor_username="admin",
        after_json={"id": 123, "username": "john", "email": "john@example.com"},
    )
    
    collector.add_entry(
        action="updated",
        entity_type="user",
        entity_id=123,
        actor_user_id=1,
        actor_username="admin",
        before_json={"email": "john@example.com"},
        after_json={"email": "john.doe@example.com"},
        edited_fields=["email"],
    )
    
    # Check entries
    assert len(collector.entries) == 2, "Should have 2 entries"
    
    # Check first entry
    entry1 = collector.entries[0]
    assert entry1["action"] == "created"
    assert entry1["resource_type"] == "user"
    assert entry1["resource_id"] == "123"
    assert entry1["user_id"] == 1
    assert entry1["changes"]["after"]["username"] == "john"
    print(f"✓ Entry 1 structure correct: {entry1['action']} on {entry1['resource_type']}")
    
    # Check second entry
    entry2 = collector.entries[1]
    assert entry2["action"] == "updated"
    assert entry2["changes"]["before"]["email"] == "john@example.com"
    assert entry2["changes"]["after"]["email"] == "john.doe@example.com"
    assert "email" in entry2["changes"]["edited_fields"]
    print(f"✓ Entry 2 structure correct: {entry2['action']} with {len(entry2['changes']['edited_fields'])} fields changed")
    
    print("✅ Bulk collector working correctly!")
    return True


async def test_database_connection():
    """Test database connection for audit operations"""
    print("\nTesting database connection...")
    
    try:
        from app.db.session import get_db
        from app.repositories.audit import AuditRepository
        from app.models.audit import AuditLog
        
        # Get database session
        async for db in get_db():
            # Create repository
            repo = AuditRepository(db)
            
            # Try to query audit logs (just count)
            from sqlalchemy import select, func
            count_query = select(func.count()).select_from(AuditLog)
            result = await db.execute(count_query)
            count = result.scalar()
            
            print(f"✓ Database connection successful")
            print(f"✓ Current audit log count: {count}")
            
            break
        
        print("✅ Database connection working!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_celery_task_structure():
    """Test Celery task is properly structured"""
    print("\nTesting Celery task structure...")
    
    from app.tasks.audit_tasks import bulk_create_audit_logs
    from app.core.celery_app import celery_app
    
    # Check task is registered
    assert "app.tasks.audit_tasks.bulk_create_audit_logs" in celery_app.tasks
    print("✓ Bulk audit task is registered with Celery")
    
    # Check task properties
    task = celery_app.tasks["app.tasks.audit_tasks.bulk_create_audit_logs"]
    assert task.max_retries == 3
    print(f"✓ Task max_retries: {task.max_retries}")
    
    print("✅ Celery task structure correct!")
    return True


async def main():
    """Run all tests"""
    print("=" * 70)
    print("AUDIT TRAIL IMPLEMENTATION TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Test 1: Imports
    results.append(await test_bulk_audit_imports())
    
    # Test 2: Audit helpers
    if results[-1]:
        results.append(await test_audit_helpers())
    
    # Test 3: Bulk collector
    if results[-1]:
        results.append(await test_bulk_collector_structure())
    
    # Test 4: Database connection
    if results[-1]:
        results.append(await test_database_connection())
    
    # Test 5: Celery task
    if results[-1]:
        results.append(await test_celery_task_structure())
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print("\nNext steps:")
        print("1. Start Redis: sudo systemctl start redis")
        print("2. Start Celery worker: ./start_celery_worker.sh")
        print("3. Start FastAPI: uvicorn app.main:app --reload")
        print("4. Test endpoints:")
        print("   - GET /api/v1/audit-trail/page/user")
        print("   - GET /api/v1/audit-trail/row/user/1")
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print("Please check the errors above and fix them.")
    
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
