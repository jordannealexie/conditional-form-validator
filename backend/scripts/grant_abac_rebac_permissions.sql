-- SQL to grant ABAC and ReBAC permissions to specific roles
-- Run this script to grant permissions to roles that should manage ABAC/ReBAC

-- Option 1: Grant to Admin role (if you have one)
-- This assumes you have a 'p' table in Casbin that stores RBAC policies

-- Grant ABAC permissions to admin role
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'admin', 'abac', 'read'),
    ('p', 'admin', 'abac', 'write'),
    ('p', 'admin', 'abac', 'delete'),
    ('p', 'admin', 'rebac', 'read'),
    ('p', 'admin', 'rebac', 'write'),
    ('p', 'admin', 'rebac', 'delete')
ON CONFLICT DO NOTHING;

-- Option 2: Grant to specific users by username
-- Replace 'your_username' with actual username
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'your_username', 'abac', 'read'),
    ('p', 'your_username', 'abac', 'write'),
    ('p', 'your_username', 'abac', 'delete'),
    ('p', 'your_username', 'rebac', 'read'),
    ('p', 'your_username', 'rebac', 'write'),
    ('p', 'your_username', 'rebac', 'delete')
ON CONFLICT DO NOTHING;

-- Option 3: Grant to role then assign role to user
-- First, create the ABAC Admin role policies
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'abac_admin', 'abac', 'read'),
    ('p', 'abac_admin', 'abac', 'write'),
    ('p', 'abac_admin', 'abac', 'delete')
ON CONFLICT DO NOTHING;

-- Then assign user to that role
INSERT INTO casbin_rule (ptype, v0, v1) 
VALUES ('g', 'your_username', 'abac_admin')
ON CONFLICT DO NOTHING;

-- Create ReBAC Admin role
INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'rebac_admin', 'rebac', 'read'),
    ('p', 'rebac_admin', 'rebac', 'write'),
    ('p', 'rebac_admin', 'rebac', 'delete')
ON CONFLICT DO NOTHING;

-- Assign user to ReBAC admin role
INSERT INTO casbin_rule (ptype, v0, v1) 
VALUES ('g', 'your_username', 'rebac_admin')
ON CONFLICT DO NOTHING;

-- Verify the policies were added
SELECT * FROM casbin_rule WHERE v1 IN ('abac', 'rebac');
