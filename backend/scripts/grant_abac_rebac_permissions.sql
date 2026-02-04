

INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'admin', 'abac', 'read'),
    ('p', 'admin', 'abac', 'write'),
    ('p', 'admin', 'abac', 'delete'),
ON CONFLICT DO NOTHING;

INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'your_username', 'abac', 'read'),
    ('p', 'your_username', 'abac', 'write'),
    ('p', 'your_username', 'abac', 'delete'),
ON CONFLICT DO NOTHING;

INSERT INTO casbin_rule (ptype, v0, v1, v2) 
VALUES 
    ('p', 'abac_admin', 'abac', 'read'),
    ('p', 'abac_admin', 'abac', 'write'),
    ('p', 'abac_admin', 'abac', 'delete')
ON CONFLICT DO NOTHING;

INSERT INTO casbin_rule (ptype, v0, v1) 
VALUES ('g', 'your_username', 'abac_admin')
ON CONFLICT DO NOTHING;



SELECT * FROM casbin_rule WHERE v1 IN ('abac');
