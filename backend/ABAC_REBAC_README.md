# ABAC & ReBAC Policy Management

## Overview

This project now includes comprehensive Attribute-Based Access Control (ABAC) and Relationship-Based Access Control (ReBAC) implementations with sample policies and frontend interfaces.

## Features

### ABAC (Attribute-Based Access Control)
- Define policies based on user and resource attributes
- Flexible rule engine supporting multiple conditions
- Sample policies for common scenarios:
  - Department-based access control
  - Seniority level access
  - Clearance-based access for confidential resources
  - Working hours restrictions
  - Role-based delete permissions
  - Regional access policies

### ReBAC (Relationship-Based Access Control)
- Define relationships between users and resources
- Hierarchical resource organization
- Sample relationships:
  - Organization membership
  - Team management
  - Resource ownership
  - View permissions

## Sample Policies Seeded

### ABAC Policies

1. **Department Access Policy**
   - Users can access resources from their own department
   - Rule: `user.department == resource.department`

2. **Senior Staff Override**
   - Senior staff (level >= 5) can access all resources
   - Rule: `user.level >= 5`

3. **Confidential Access Policy**
   - Only users with clearance can access confidential resources
   - Rule: `user.clearance == "confidential" AND resource.classification == "confidential"`

4. **Working Hours Policy**
   - Access restricted to working hours (9 AM - 5 PM)
   - Rule: `9 <= time.hour <= 17`

5. **Manager Delete Access**
   - Only managers can delete resources
   - Rule: `user.position == "manager" AND action == "delete"`

6. **Regional Access Policy**
   - Users can only access resources from their region (unless global)
   - Rule: `user.region == resource.region OR user.is_global == true`

### ReBAC Relationships

Sample relationships created:
- **Organization membership**: Users belong to organizations
- **Team management**: Users manage or are members of teams
- **Resource ownership**: Users own specific templates
- **View permissions**: Users can view specific resources

## Seeding Data

### Run ABAC/ReBAC Seeding Only

```bash
cd backend
python3 scripts/seed_abac_rebac.py
```

### Run Complete Seeding (Including ABAC/ReBAC)

```bash
cd backend
python3 scripts/seed_data.py
```

This will automatically seed:
- 6 ABAC policies
- User attributes for existing users (department, level, position, clearance, region)
- Resource attributes for templates and submissions
- 8+ ReBAC relationships showing hierarchical organization

## API Endpoints

### ABAC Endpoints

- `GET /api/v1/abac/policies` - List all ABAC policies
- `POST /api/v1/abac/policies` - Create new ABAC policy
- `GET /api/v1/abac/policies/{id}` - Get specific policy
- `DELETE /api/v1/abac/policies/{id}` - Delete policy
- `POST /api/v1/abac/check` - Check if access is allowed based on policies
- `POST /api/v1/abac/attributes/user` - Set user attribute
- `GET /api/v1/abac/attributes/user/{user_id}` - Get user attributes
- `POST /api/v1/abac/attributes/resource` - Set resource attribute
- `GET /api/v1/abac/attributes/resource/{type}/{id}` - Get resource attributes

### ReBAC Endpoints

- `GET /api/v1/rebac/relationships` - List all relationships
- `POST /api/v1/rebac/relationships` - Create new relationship
- `GET /api/v1/rebac/relationships/{id}` - Get specific relationship
- `PUT /api/v1/rebac/relationships/{id}` - Update relationship
- `DELETE /api/v1/rebac/relationships/{id}` - Delete relationship
- `POST /api/v1/rebac/check` - Check if access is allowed based on relationships
- `GET /api/v1/rebac/relationships/resource/{type}/{id}` - Get relationships for a resource

## Frontend Pages

### ABAC Management (`/abac.html`)

Features:
- View all ABAC policies in a table
- Create new policies with custom rules
- Edit existing policies
- Delete policies
- Test policy evaluation

### ReBAC Management (`/rebac.html`)

Features:
- View all relationships in a table
- Create new relationships (subject → resource)
- Edit existing relationships
- Delete relationships
- Filter relationships by type

## Sample User Attributes

The seeding script creates the following sample attributes:

**User 1** (Department Manager):
- department: engineering
- level: 7
- position: manager
- clearance: confidential
- region: north
- is_global: false

**User 2** (Junior Staff):
- department: engineering
- level: 3
- position: developer
- clearance: public
- region: north
- is_global: false

**User 3** (Sales Team):
- department: sales
- level: 5
- position: sales_rep
- clearance: public
- region: south
- is_global: false

**User 4** (Global Admin):
- department: operations
- level: 9
- position: director
- clearance: top_secret
- region: north
- is_global: true

## Sample Resource Attributes

**Template 1** (Engineering):
- department: engineering
- classification: confidential
- region: north

**Template 2** (Sales):
- department: sales
- classification: public
- region: south

**Template 3** (HR):
- department: hr
- classification: confidential
- region: north

## Testing the Policies

1. **Access the frontend**:
   - Navigate to `/abac.html` for ABAC management
   - Navigate to `/rebac.html` for ReBAC management

2. **View existing policies**:
   - Policies are automatically loaded when you access the pages
   - All seeded policies will be visible in the tables

3. **Create a new policy**:
   - Click "Add New Policy" button
   - Fill in the policy details
   - Define the rule conditions
   - Submit to create

4. **Test policy evaluation**:
   - Use the "Test" button on any policy
   - Provide sample user and resource attributes
   - See if access would be granted

## Architecture

### Models

- **ABACPolicy**: Stores policy definitions and rules
- **UserAttribute**: Key-value pairs for user attributes
- **ResourceAttribute**: Key-value pairs for resource attributes
- **ResourceRelationship**: Defines subject-resource relationships

### Services

- **ABACService**: Handles ABAC policy management and evaluation
- **REBACService**: Handles relationship management and access checks

### Frontend Components

- **abac.js**: Frontend logic for ABAC management
- **rebac.js**: Frontend logic for ReBAC management
- **api.js**: API integration layer

## Database Schema

### ABAC Tables
- `abac_policies`: Policy definitions
- `user_attributes`: User attribute storage
- `resource_attributes`: Resource attribute storage

### ReBAC Tables
- `resource_relationships`: Relationship definitions

## Configuration

The Casbin models are located in:
- `/backend/app/casbin/abac_model.conf`
- `/backend/app/casbin/rebac_model.conf`

## Best Practices

1. **ABAC Policies**:
   - Keep rules simple and easy to understand
   - Use meaningful attribute names
   - Document policy purposes clearly
   - Test policies thoroughly before deploying

2. **ReBAC Relationships**:
   - Establish clear hierarchy structures
   - Use consistent relationship types
   - Document parent-child relationships
   - Regularly audit relationship chains

3. **Security**:
   - Only superusers should manage policies
   - Regular policy audits are recommended
   - Monitor policy evaluation logs
   - Keep attribute definitions consistent

## Troubleshooting

### Policies Not Showing

1. Verify seeding completed successfully:
   ```bash
   python3 scripts/seed_abac_rebac.py
   ```

2. Check database connection:
   ```bash
   docker-compose ps
   ```

3. Verify API endpoints are accessible:
   ```bash
   curl http://localhost:8000/api/v1/abac/policies
   ```

### Frontend Not Loading Data

1. Check browser console for errors
2. Verify authentication token is valid
3. Check API response in Network tab
4. Ensure user has superuser permissions

## Future Enhancements

- [ ] Policy versioning and history
- [ ] Advanced policy testing framework
- [ ] Policy conflict detection
- [ ] Relationship graph visualization
- [ ] Policy simulation mode
- [ ] Bulk policy import/export
- [ ] Policy impact analysis

## References

- [ABAC Wikipedia](https://en.wikipedia.org/wiki/Attribute-based_access_control)
- [ReBAC Explanation](https://www.osohq.com/academy/relationship-based-access-control-rebac)
- [Casbin Documentation](https://casbin.org/docs/overview)
