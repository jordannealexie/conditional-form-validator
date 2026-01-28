# ReBAC Relationship Graph Structure

## Visual Representation of Seeded Relationships

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         REBAC RELATIONSHIP GRAPH                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   User 138   │
└──────┬───────┘
       │
       ├─(owner)────────────────────┐
       │                            ▼
       │                      ┌──────────────┐
       ├─(editor)────────────▶│  Template 1  │
       │                      │   (BDO)      │
       ├─(viewer)────────────▶└──────┬───────┘
       │                             │
       │                             ├─(parent)─────┐
       │                             │              ▼
       ├─(member)────────────┐       │        ┌──────────────┐
       │                     ▼       │        │  Template 2  │
       │              ┌────────────┐ │        │   (Maya)     │
       │              │   Role 28  │ │        └──────────────┘
       │              │  (Admin)   │ │
       │              └────────────┘ │
       │                             │
       └─(delegate)──────────────────┼───┐
                                     │   │
                                     │   ▼
                  ┌──────────────────┘  ┌──────────────┐
                  │                     │   User 139   │
                  │                     └──────┬───────┘
                  │                            │
                  │                            ├─(owner)──────────┐
                  │                            │                  ▼
                  │                            │            ┌──────────────┐
                  │                            ├─(editor)──▶│  Template 2  │
                  │                            │            │   (Maya)     │
                  │                            └─(viewer)──▶└──────────────┘
                  │
                  ▼
            ┌──────────────┐
            │ Submission 1 │
            │  (Form Data) │
            └──────┬───────┘
                   │
                   ├─(owner)────────User 138
                   │
                   ├─(reviewer)─────User 139
                   │
                   └─(depends_on)──┐
                                   ▼
                            ┌──────────────┐
                            │ Submission 2 │
                            │  (Form Data) │
                            └──────┬───────┘
                                   │
                                   ├─(owner)────User 139
                                   │
                                   └─(reviewer)──User 140

┌──────────────┐
│   User 140   │
└──────┬───────┘
       │
       ├─(reports_to)──────────▶User 138
       │
       ├─(owner)────────────────┐
       │                        ▼
       │                  ┌──────────────┐
       ├─(editor)────────▶│  Template 3  │
       │                  │   (SecBank)  │
       └─(viewer)────────▶└──────────────┘
```

## Relationship Type Legend

| Symbol | Relationship Type | Description |
|--------|------------------|-------------|
| `─(owner)──▶` | Owner | User owns the resource |
| `─(editor)──▶` | Editor | User can edit the resource |
| `─(viewer)──▶` | Viewer | User can view the resource |
| `─(reviewer)──▶` | Reviewer | User can review submissions |
| `─(manager)──▶` | Manager | Role can manage the resource |
| `─(member)──▶` | Member | User is member of role |
| `─(parent)──▶` | Parent | Template hierarchy |
| `─(depends_on)──▶` | Depends On | Submission workflow dependency |
| `─(delegate)──▶` | Delegate | Authority delegation |
| `─(reports_to)──▶` | Reports To | Organizational reporting |

## Graph Traversal Examples

### Example 1: Check if User 138 can access Template 1
```
Path: User 138 ─(owner)─▶ Template 1
Result: ✅ Direct ownership
```

### Example 2: Check if User 139 can review Submission 1
```
Path: User 139 ─(reviewer)─▶ Submission 1
Result: ✅ Direct reviewer relationship
```

### Example 3: Check if User 140 has access through delegation
```
Path: User 140 ─(reports_to)─▶ User 138 ─(owner)─▶ Template 1
Result: ✅ Access through organizational hierarchy
```

### Example 4: Check template hierarchy
```
Path: Template 1 ─(parent)─▶ Template 2
Result: ✅ Child template relationship established
```

### Example 5: Check submission workflow
```
Path: Submission 1 ─(depends_on)─▶ Submission 2
Result: ✅ Approval workflow dependency
```

### Example 6: Check role-based access
```
Path: User 138 ─(member)─▶ Role 28 (Admin) ─(manager)─▶ Template 1
Result: ✅ Access through role membership
```

## Database Query Examples

### Get all resources owned by User 138
```sql
SELECT resource_type, resource_id 
FROM resource_relationships 
WHERE subject_type = 'user' 
  AND subject_id = '138' 
  AND relationship_type = 'owner';
```

### Get all users who can view Template 1
```sql
SELECT subject_id, relationship_type 
FROM resource_relationships 
WHERE resource_type = 'template' 
  AND resource_id = '1' 
  AND subject_type = 'user';
```

### Get relationship chain for Submission 1
```sql
-- Direct relationships
SELECT * FROM resource_relationships 
WHERE resource_type = 'submission' AND resource_id = '1';

-- Parent template relationships
SELECT rr2.* FROM resource_relationships rr1
JOIN resource_relationships rr2 ON rr1.parent_resource_id = rr2.resource_id
WHERE rr1.resource_type = 'submission' 
  AND rr1.resource_id = '1'
  AND rr2.resource_type = 'template';
```

### Get all delegated authorities from User 138
```sql
SELECT resource_id as delegated_to_user
FROM resource_relationships
WHERE subject_type = 'user'
  AND subject_id = '138'
  AND relationship_type = 'delegate'
  AND resource_type = 'user';
```

## API Usage for Graph Traversal

### Frontend: Get Relationship Graph for Visualization
```javascript
// Get all relationships
const response = await fetch('/api/v1/rebac/relationships', {
  headers: {
    'X-Client-ID': 'web-app-123',
    'Authorization': `Bearer ${token}`
  }
});
const { data: relationships } = await response.json();

// Build graph data structure
const nodes = new Set();
const edges = [];

relationships.forEach(rel => {
  nodes.add(`${rel.subject_type}:${rel.subject_id}`);
  nodes.add(`${rel.resource_type}:${rel.resource_id}`);
  
  edges.push({
    source: `${rel.subject_type}:${rel.subject_id}`,
    target: `${rel.resource_type}:${rel.resource_id}`,
    label: rel.relationship_type
  });
});

// Render with D3.js, vis.js, or Cytoscape.js
renderGraph(Array.from(nodes), edges);
```

### Backend: Check Access via Relationship Chain
```python
# In rebac_service.py
async def check_access_path(
    self,
    username: str,
    resource: str,
    action: str
) -> tuple[bool, Optional[List[str]]]:
    """
    Check if user has access via relationship chain
    Returns: (has_permission, relationship_path)
    """
    # This method already exists in the service
    # Example usage:
    has_access, path = await rebac_service.check_access_path(
        username="user138",
        resource="template:1",
        action="edit"
    )
    
    if has_access:
        print(f"Access granted via path: {' → '.join(path)}")
    else:
        print("Access denied")
```

## Relationship Statistics

From the seed script execution:
- **Total Relationships**: 23
- **User → Template**: 9 relationships (3 owners, 3 editors, 3 viewers)
- **User → Submission**: 4 relationships (2 owners, 2 reviewers)
- **Role → Template**: 2 relationships (admin + manager)
- **User → Role**: 3 relationships (role membership)
- **Template → Template**: 1 relationship (hierarchy)
- **Submission → Submission**: 1 relationship (dependency)
- **User → User**: 2 relationships (delegation + reporting)

## Next Steps for Graph Functionality

1. **Frontend Visualization**:
   - Install graph library (D3.js, vis.js, or Cytoscape.js)
   - Create graph visualization component
   - Add interactive node/edge exploration
   - Implement zoom, pan, and search

2. **Advanced Queries**:
   - Implement shortest path algorithm
   - Add relationship strength scoring
   - Support multi-hop traversal
   - Cache common paths for performance

3. **UI Enhancements**:
   - Add "View Graph" button on ReBAC page
   - Show relationship preview on hover
   - Highlight active paths in graph
   - Filter graph by relationship type

4. **Performance Optimization**:
   - Add database indexes on subject_id, resource_id
   - Implement relationship caching in Redis
   - Use graph database (Neo4j) for complex queries
   - Add pagination for large relationship sets
