-- Migration: Add audit trail columns to audit_logs table
-- Date: 2026-02-02

-- Add changes column for before/after tracking
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS changes JSON;
COMMENT ON COLUMN audit_logs.changes IS 'Before and after values in JSON format';

-- Add created_by, updated_by, deleted_by columns
ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS created_by INTEGER;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_created_by FOREIGN KEY (created_by) REFERENCES users(id);
COMMENT ON COLUMN audit_logs.created_by IS 'User ID who created this record';

ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS updated_by INTEGER;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_updated_by FOREIGN KEY (updated_by) REFERENCES users(id);
COMMENT ON COLUMN audit_logs.updated_by IS 'User ID who updated this record';

ALTER TABLE audit_logs ADD COLUMN IF NOT EXISTS deleted_by INTEGER;
ALTER TABLE audit_logs ADD CONSTRAINT fk_audit_logs_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(id);
COMMENT ON COLUMN audit_logs.deleted_by IS 'User ID who deleted this record';
