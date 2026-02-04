# Audit Trail System Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT REQUEST                              │
│                  POST /users/bulk (50 users)                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI ENDPOINT                                │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │  async with bulk_audit_service.create_collector() as col:  │    │
│  │      for user_data in users_data:                          │    │
│  │          user = await create(user_data)  # Business logic  │    │
│  │          collector.add_entry(...)        # Add to memory   │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  Returns immediately ────────────────────────────────────────────►  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ On context exit
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BULK AUDIT COLLECTOR                              │
│                                                                       │
│  In-Memory Collection:                                               │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ Entry 1: {action: "created", entity_type: "user", ...} │         │
│  │ Entry 2: {action: "created", entity_type: "user", ...} │         │
│  │ Entry 3: {action: "created", entity_type: "user", ...} │         │
│  │ ... (50 entries)                                        │         │
│  └────────────────────────────────────────────────────────┘         │
│                                                                       │
│  Dispatch to Celery:                                                 │
│  bulk_create_audit_logs.delay([entry1, entry2, ..., entry50])       │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Async dispatch
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        REDIS QUEUE                                   │
│                    (Celery Broker)                                   │
│                                                                       │
│  Queue: audit_queue                                                  │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ Task: bulk_create_audit_logs                           │         │
│  │ Payload: [50 audit entries]                            │         │
│  │ Status: PENDING                                         │         │
│  └────────────────────────────────────────────────────────┘         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Worker picks up
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      CELERY WORKER                                   │
│                                                                       │
│  Task: bulk_create_audit_logs                                        │
│  ┌────────────────────────────────────────────────────────┐         │
│  │ 1. Validate entries                                     │         │
│  │ 2. Create database session                              │         │
│  │ 3. BEGIN TRANSACTION                                    │         │
│  │ 4. INSERT INTO audit_logs (...) VALUES                  │         │
│  │    (entry1), (entry2), ..., (entry50)                   │         │
│  │ 5. COMMIT                                                │         │
│  │ 6. Return success                                        │         │
│  └────────────────────────────────────────────────────────┘         │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Single bulk INSERT
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     POSTGRESQL DATABASE                              │
│                                                                       │
│  Table: audit_logs                                                   │
│  ┌────┬─────────┬───────────────┬─────────────┬──────────────┐     │
│  │ id │ action  │ resource_type │ resource_id │ changes      │     │
│  ├────┼─────────┼───────────────┼─────────────┼──────────────┤     │
│  │  1 │ created │ user          │ 101         │ {after: ...} │     │
│  │  2 │ created │ user          │ 102         │ {after: ...} │     │
│  │  3 │ created │ user          │ 103         │ {after: ...} │     │
│  │... │ ...     │ ...           │ ...         │ ...          │     │
│  │ 50 │ created │ user          │ 150         │ {after: ...} │     │
│  └────┴─────────┴───────────────┴─────────────┴──────────────┘     │
│                                                                       │
│  ✅ 50 rows inserted in ONE transaction                              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Query Flow

### Page-Level Query (All users)

```
GET /api/v1/audit-trail/page/user?page=1&page_size=50
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│             BulkAuditService                             │
│  get_logs_by_page(entity_type="user")                   │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             AuditRepository                              │
│  get_by_entity_type_and_id(                             │
│      entity_type="user",                                 │
│      entity_id=None  # No row filter                     │
│  )                                                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             Database Query                               │
│                                                           │
│  SELECT * FROM audit_logs                                │
│  WHERE resource_type = 'user'                            │
│  ORDER BY created_at DESC  ← BEFORE pagination          │
│  OFFSET 0 LIMIT 50;                                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             Response                                     │
│  {                                                       │
│    "total": 500,                                         │
│    "page": 1,                                            │
│    "page_size": 50,                                      │
│    "logs": [...]  ← 50 most recent user logs            │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

### Row-Level Query (Specific user)

```
GET /api/v1/audit-trail/row/user/123?page=1&page_size=50
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│             BulkAuditService                             │
│  get_logs_by_row(                                        │
│      entity_type="user",                                 │
│      entity_id=123                                       │
│  )                                                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             AuditRepository                              │
│  get_by_entity_type_and_id(                             │
│      entity_type="user",                                 │
│      entity_id=123  # Row filter                         │
│  )                                                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             Database Query                               │
│                                                           │
│  SELECT * FROM audit_logs                                │
│  WHERE resource_type = 'user'                            │
│    AND resource_id = '123'  ← Row-specific               │
│  ORDER BY created_at DESC  ← BEFORE pagination          │
│  OFFSET 0 LIMIT 50;                                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│             Response                                     │
│  {                                                       │
│    "total": 15,                                          │
│    "page": 1,                                            │
│    "page_size": 50,                                      │
│    "logs": [...]  ← Only logs for user 123              │
│  }                                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Data Structure

### Audit Entry in Memory (Before Persistence)

```json
{
  "action": "updated",
  "resource_type": "user",
  "resource_id": "123",
  "user_id": 5,
  "username": "admin",
  "status": "success",
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "changes": {
    "before": {
      "username": "john_doe",
      "email": "john@example.com",
      "is_active": false
    },
    "after": {
      "username": "john_doe",
      "email": "john.doe@example.com",
      "is_active": true
    },
    "edited_fields": ["email", "is_active"]
  },
  "created_by": null,
  "updated_by": 5,
  "deleted_by": null
}
```

### Audit Log in Database

```sql
id              | 1001
action          | updated
resource_type   | user
resource_id     | 123
user_id         | 5
username        | admin
status          | success
ip_address      | 192.168.1.100
user_agent      | Mozilla/5.0...
changes         | {"before": {...}, "after": {...}, "edited_fields": [...]}
created_by      | NULL
updated_by      | 5
deleted_by      | NULL
created_at      | 2026-02-03 10:30:00+00
```

### API Response (Detailed View)

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
        "num_fields_changed": 2,
        "before_json": {
          "email": "john@example.com",
          "is_active": false
        },
        "after_json": {
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

---

## Performance Characteristics

### Time Complexity

```
┌──────────────────────────┬────────────────┬─────────────┐
│ Operation                │ API Response   │ Background  │
├──────────────────────────┼────────────────┼─────────────┤
│ Create 1 user            │ ~30ms          │ ~5ms        │
│ Create 10 users          │ ~80ms          │ ~10ms       │
│ Create 50 users          │ ~150ms         │ ~25ms       │
│ Create 100 users         │ ~250ms         │ ~50ms       │
├──────────────────────────┼────────────────┼─────────────┤
│ Update 1 user            │ ~35ms          │ ~5ms        │
│ Update 50 users          │ ~180ms         │ ~25ms       │
│ Update 100 users         │ ~300ms         │ ~50ms       │
├──────────────────────────┼────────────────┼─────────────┤
│ Query page (50 logs)     │ ~80ms          │ N/A         │
│ Query row (10 logs)      │ ~50ms          │ N/A         │
└──────────────────────────┴────────────────┴─────────────┘

Note: Background time is for bulk INSERT in Celery worker
      API response is non-blocking (doesn't wait for audit)
```

### Space Complexity

```
┌──────────────────────────┬─────────────────────────────┐
│ Item                     │ Approx Size                  │
├──────────────────────────┼─────────────────────────────┤
│ Single audit entry       │ ~500 bytes (JSON)            │
│ 100 entries in memory    │ ~50 KB                       │
│ 1000 entries in memory   │ ~500 KB                      │
├──────────────────────────┼─────────────────────────────┤
│ Database row             │ ~800 bytes (with indexes)    │
│ 1M audit logs            │ ~800 MB                      │
│ 10M audit logs           │ ~8 GB                        │
└──────────────────────────┴─────────────────────────────┘
```

### Concurrency

```
┌────────────────────────────────────────────────────────┐
│                    Concurrent Requests                  │
│                                                          │
│  Request 1 ──┐                                          │
│  Request 2 ──┼──► Celery Queue ──► Worker Pool ──► DB  │
│  Request 3 ──┘         │               (4 workers)      │
│                        │                                 │
│                   Redis Queue                            │
│                   (FIFO)                                 │
│                                                          │
│  Each request dispatches independent bulk task           │
│  Workers process in parallel (up to concurrency limit)   │
└────────────────────────────────────────────────────────┘
```

---

## Failure Handling

### Retry Logic

```
Task Failed
    │
    ├─ Retry 1 (after 5s)
    │   │
    │   └─ Failed again
    │       │
    │       ├─ Retry 2 (after 10s, backoff)
    │       │   │
    │       │   └─ Failed again
    │       │       │
    │       │       ├─ Retry 3 (after 20s, backoff)
    │       │       │   │
    │       │       │   ├─ Success ✅
    │       │       │   └─ OR Final Failure ❌
    │       │       │
    │       │       └─ Task moved to Dead Letter Queue
    │       │
    │       └─ Alert/Log error
    │
    └─ Business logic continues (audit failure doesn't break API)
```

### Transaction Safety

```
BEGIN TRANSACTION
    │
    ├─ Validate 100 entries
    │
    ├─ INSERT INTO audit_logs (...)
    │   VALUES (entry1), (entry2), ..., (entry100)
    │
    ├─ Check for errors
    │   │
    │   ├─ Error? ──► ROLLBACK ──► Retry entire task
    │   │
    │   └─ Success? ──► COMMIT ──► All 100 rows persisted ✅
    │
    └─ Close session
```

---

## Monitoring Dashboards

### Celery Flower (http://localhost:5555)

```
┌────────────────────────────────────────────────┐
│              Celery Flower                     │
├────────────────────────────────────────────────┤
│  Active Tasks:      3                          │
│  Processed:         1,234                      │
│  Failed:            2                          │
│  Retried:           5                          │
│                                                 │
│  Workers:                                       │
│  ├─ audit_worker@host1  [Active]               │
│  ├─ audit_worker@host2  [Active]               │
│  └─ audit_worker@host3  [Active]               │
│                                                 │
│  Queue: audit_queue                             │
│  ├─ Pending:  12 tasks                          │
│  └─ ETA:      ~2 seconds                        │
└────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### ✅ Why Bulk Operations?

**Problem**: Creating 100 users = 100 separate audit inserts = slow

**Solution**: Collect all 100 in memory → single bulk INSERT

**Benefit**: 100x faster, single transaction, atomic operation

### ✅ Why Celery?

**Problem**: Bulk INSERT (even fast) blocks API response

**Solution**: Dispatch to background worker via Celery

**Benefit**: API returns immediately, audit happens asynchronously

### ✅ Why Redis?

**Problem**: Need reliable queue for tasks

**Solution**: Redis as Celery broker (fast, reliable, simple)

**Benefit**: Proven, scalable, minimal setup

### ✅ Why Context Manager?

**Problem**: Easy to forget to persist audit logs

**Solution**: BulkAuditCollector context manager

**Benefit**: Automatic dispatch on context exit, clean API

### ✅ Why JSON for before/after?

**Problem**: Need flexible storage for any entity type

**Solution**: Store entire state as JSON

**Benefit**: Query-able, flexible, future-proof

---

## Deployment Architecture

### Single Server

```
┌─────────────────────────────────────────────┐
│           Server (Ubuntu)                    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │  Redis (Port 6379)                  │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │  Celery Worker (4 processes)        │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │  FastAPI (Port 8000)                │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │  PostgreSQL (Port 5432)             │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Scaled Architecture

```
┌─────────────────┐
│  Load Balancer  │
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼───────────┐
│ API 1 │ │ API 2│ │ API 3│ │ Celery Fleet │
│FastAPI│ │FastAPI│FastAPI│ │ (10 workers) │
└───┬───┘ └──┬───┘ └──┬───┘ └──┬───────────┘
    │        │        │        │
    └────┬───┴────┬───┴────────┘
         │        │
    ┌────▼────┐  │
    │  Redis  │  │
    │ Cluster │  │
    └─────────┘  │
                 │
            ┌────▼────────┐
            │ PostgreSQL  │
            │   Cluster   │
            └─────────────┘
```

---

This architecture diagram shows the complete data flow, query patterns, performance characteristics, and deployment options for the audit trail system.
