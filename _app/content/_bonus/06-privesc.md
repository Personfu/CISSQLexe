

## privilege_escalation.sql

```sql
-- ═══════════════════════════════════════════════════════════════
-- FLLC Lab 06: Database Privilege Escalation Patterns
-- Educational reference — test environments only
-- ═══════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════
-- 6.1  ENUMERATING CURRENT PRIVILEGES
-- ═══════════════════════════════════════════════════════════════

-- PostgreSQL: Current user and role memberships
SELECT current_user, current_database();
SELECT r.rolname, r.rolsuper, r.rolcreatedb, r.rolcreaterole, r.rolcanlogin
FROM pg_roles r WHERE r.rolname = current_user;

-- PostgreSQL: All grants on all tables
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.role_table_grants
WHERE grantee = current_user;

-- MySQL: Current privileges
-- SHOW GRANTS FOR CURRENT_USER();

-- SQL Server: Effective permissions
-- SELECT * FROM fn_my_permissions(NULL, 'SERVER');
-- SELECT * FROM fn_my_permissions(NULL, 'DATABASE');

-- ═══════════════════════════════════════════════════════════════
-- 6.2  DANGEROUS MISCONFIGURATIONS
-- ═══════════════════════════════════════════════════════════════

-- Check for public schema write access (PostgreSQL)
SELECT nspname, nspacl FROM pg_namespace WHERE nspname = 'public';

-- Check for overly permissive roles
SELECT r.rolname, r.rolsuper, r.rolcreatedb, r.rolcreaterole,
       r.rolreplication, r.rolbypassrls
FROM pg_roles r WHERE r.rolsuper = true OR r.rolcreatedb = true;

-- Check for SECURITY DEFINER functions (run as owner, not caller)
SELECT n.nspname, p.proname, p.prosecdef, r.rolname as owner
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
JOIN pg_roles r ON p.proowner = r.oid
WHERE p.prosecdef = true;

-- ═══════════════════════════════════════════════════════════════
-- 6.3  ESCALATION VIA FUNCTION ABUSE
-- ═══════════════════════════════════════════════════════════════

-- If a SECURITY DEFINER function owned by superuser exists:
-- CREATE OR REPLACE FUNCTION admin_func() RETURNS void AS $$
-- BEGIN
--   EXECUTE 'ALTER ROLE attacker WITH SUPERUSER';
-- END;
-- $$ LANGUAGE plpgsql SECURITY DEFINER;
-- 
-- Calling admin_func() as any user grants superuser

-- DEFENSE:
-- 1. Audit all SECURITY DEFINER functions
-- 2. Set search_path explicitly in functions
-- 3. Revoke EXECUTE from PUBLIC on sensitive functions

-- ═══════════════════════════════════════════════════════════════
-- 6.4  ESCALATION VIA COPY / LOAD DATA
-- ═══════════════════════════════════════════════════════════════

-- PostgreSQL: COPY reads server-side files (requires superuser or pg_read_server_files)
-- COPY (SELECT '') TO '/tmp/test.txt';
-- COPY sensitive_data FROM '/etc/passwd' WITH (FORMAT text);

-- MySQL: LOAD DATA reads server-side files
-- LOAD DATA INFILE '/etc/passwd' INTO TABLE exfil_table;

-- DEFENSE: Revoke file-read roles, set secure_file_priv, disable local_infile

-- ═══════════════════════════════════════════════════════════════
-- 6.5  DEFENSE: LEAST PRIVILEGE HARDENING
-- ═══════════════════════════════════════════════════════════════

-- Create read-only application role
-- CREATE ROLE app_readonly;
-- GRANT CONNECT ON DATABASE production TO app_readonly;
-- GRANT USAGE ON SCHEMA public TO app_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO app_readonly;

-- Create write-limited application role
-- CREATE ROLE app_writer;
-- GRANT app_readonly TO app_writer;
-- GRANT INSERT, UPDATE ON orders, sessions TO app_writer;
-- Explicitly deny DELETE and TRUNCATE

-- Row-Level Security (PostgreSQL)
-- ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY user_orders ON orders FOR ALL
--   USING (user_id = current_setting('app.current_user_id')::int);

-- ═══════════════════════════════════════════════════════════════
-- 6.6  AUDIT: DETECT ESCALATION ATTEMPTS
-- ═══════════════════════════════════════════════════════════════

-- PostgreSQL: Enable pgAudit
-- ALTER SYSTEM SET shared_preload_libraries = 'pgaudit';
-- ALTER SYSTEM SET pgaudit.log = 'ddl, role, misc_set';

-- Query audit log for suspicious role changes:
-- SELECT * FROM pgaudit.log
-- WHERE command_tag IN ('ALTER ROLE', 'GRANT', 'CREATE ROLE')
-- AND timestamp > NOW() - INTERVAL '24 hours'
-- ORDER BY timestamp DESC;

-- NIST 800-53 Mapping:
-- AC-2  Account Management (role auditing)
-- AC-6  Least Privilege (role restrictions)
-- AU-2  Audit Events (DDL logging)
-- AU-12 Audit Generation (pgaudit config)

```
