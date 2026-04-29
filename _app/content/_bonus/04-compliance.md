

## compliance_audit.sql

```sql
-- ============================================================================
-- FLLC COMPLIANCE AUDIT QUERIES
-- SOC 2 Type II | PCI-DSS 4.0 | NIST 800-53 r5 | CIS Controls v8
--
-- Run against production databases to verify compliance controls.
-- Each query maps to specific framework control IDs.
--
-- FLLC 2026 — FU PERSON
-- ============================================================================

-- ============================================================================
-- 1. ACCESS CONTROL REVIEW
-- NIST: AC-2, AC-3, AC-6 | PCI: 7.1, 7.2 | SOC2: CC6.1, CC6.3
-- CIS: 5.2, 5.4, 6.8
-- ============================================================================

-- 1a. List all database users and their privilege levels
-- Purpose: Verify least privilege principle
SELECT
    usename AS username,
    usesuper AS is_superuser,
    usecreatedb AS can_create_db,
    usecanlogin AS can_login,
    valuntil AS password_expiry
FROM pg_user
ORDER BY usesuper DESC, usename;

-- 1b. Identify accounts with excessive privileges (superuser or CREATE)
-- FINDING: Any non-DBA superuser = NIST AC-6 violation
SELECT
    usename AS username,
    'SUPERUSER' AS privilege_type,
    'CRITICAL - Review if role requires superuser' AS audit_note
FROM pg_user
WHERE usesuper = true
UNION ALL
SELECT
    usename,
    'CREATEDB',
    'HIGH - Review if role requires database creation'
FROM pg_user
WHERE usecreatedb = true AND usesuper = false;

-- 1c. Check for accounts without password expiry
-- NIST: IA-5 | PCI: 8.3.7 | CIS: 5.2
SELECT
    usename AS username,
    valuntil AS password_expiry,
    CASE
        WHEN valuntil IS NULL THEN 'NO EXPIRY SET - NONCOMPLIANT'
        WHEN valuntil < NOW() THEN 'EXPIRED - IMMEDIATE ACTION'
        WHEN valuntil < NOW() + INTERVAL '30 days' THEN 'EXPIRING SOON'
        ELSE 'COMPLIANT'
    END AS compliance_status
FROM pg_user
WHERE usecanlogin = true;

-- 1d. Identify dormant accounts (no recent activity)
-- SOC2: CC6.1 | NIST: AC-2(3)
SELECT
    usename AS username,
    valuntil AS last_known_expiry,
    'REVIEW - Check last login in application logs' AS audit_action
FROM pg_user
WHERE usecanlogin = true
ORDER BY usename;

-- ============================================================================
-- 2. ENCRYPTION VERIFICATION
-- NIST: SC-13, SC-28 | PCI: 3.5, 4.2 | SOC2: CC6.6
-- CIS: 3.10, 3.11
-- ============================================================================

-- 2a. Check if SSL/TLS is enforced
SELECT
    name,
    setting,
    CASE
        WHEN name = 'ssl' AND setting = 'on' THEN 'COMPLIANT'
        WHEN name = 'ssl' AND setting = 'off' THEN 'NONCOMPLIANT - Enable SSL'
        ELSE 'CHECK'
    END AS compliance_status
FROM pg_settings
WHERE name IN ('ssl', 'ssl_min_protocol_version', 'ssl_ciphers', 'password_encryption');

-- 2b. Verify password hashing algorithm
-- PCI-DSS 4.0 requires strong hashing (scram-sha-256 minimum)
SELECT
    name,
    setting,
    CASE
        WHEN setting = 'scram-sha-256' THEN 'COMPLIANT - Strong hash'
        WHEN setting = 'md5' THEN 'NONCOMPLIANT - Weak hash, migrate to scram-sha-256'
        ELSE 'REVIEW'
    END AS compliance_status
FROM pg_settings
WHERE name = 'password_encryption';

-- ============================================================================
-- 3. AUDIT LOGGING CONFIGURATION
-- NIST: AU-2, AU-3, AU-6, AU-12 | PCI: 10.2, 10.3 | SOC2: CC7.2
-- CIS: 8.2, 8.5, 8.11
-- ============================================================================

-- 3a. Verify audit logging is enabled and comprehensive
SELECT
    name,
    setting,
    CASE
        WHEN name = 'log_statement' AND setting = 'all' THEN 'COMPLIANT'
        WHEN name = 'log_statement' AND setting = 'none' THEN 'NONCOMPLIANT - Enable logging'
        WHEN name = 'log_connections' AND setting = 'on' THEN 'COMPLIANT'
        WHEN name = 'log_connections' AND setting = 'off' THEN 'NONCOMPLIANT'
        WHEN name = 'log_disconnections' AND setting = 'on' THEN 'COMPLIANT'
        WHEN name = 'log_disconnections' AND setting = 'off' THEN 'NONCOMPLIANT'
        ELSE setting
    END AS compliance_status
FROM pg_settings
WHERE name IN (
    'log_statement',
    'log_connections',
    'log_disconnections',
    'log_duration',
    'log_line_prefix',
    'log_min_duration_statement',
    'log_checkpoints',
    'log_lock_waits',
    'logging_collector'
);

-- 3b. Check log retention settings
-- PCI: 10.7 requires 1 year retention
SELECT
    name,
    setting,
    unit,
    CASE
        WHEN name = 'log_rotation_age' THEN 'Verify >= 365 days equivalent'
        WHEN name = 'log_rotation_size' THEN 'Verify adequate for retention period'
        ELSE 'REVIEW'
    END AS audit_note
FROM pg_settings
WHERE name LIKE 'log_rotation%' OR name = 'log_directory';

-- ============================================================================
-- 4. SEPARATION OF DUTIES
-- NIST: AC-5 | PCI: 7.1 | SOC2: CC6.1
-- ============================================================================

-- 4a. Check for role-based access control
SELECT
    r.rolname AS role_name,
    r.rolsuper AS is_superuser,
    r.rolcreaterole AS can_create_roles,
    r.rolcreatedb AS can_create_db,
    r.rolcanlogin AS can_login,
    ARRAY(
        SELECT b.rolname
        FROM pg_catalog.pg_auth_members m
        JOIN pg_catalog.pg_roles b ON (m.roleid = b.oid)
        WHERE m.member = r.oid
    ) AS member_of
FROM pg_catalog.pg_roles r
WHERE r.rolname NOT LIKE 'pg_%'
ORDER BY r.rolsuper DESC, r.rolname;

-- ============================================================================
-- 5. DATA PROTECTION
-- NIST: SC-28 | PCI: 3.5 | SOC2: CC6.6
-- ============================================================================

-- 5a. Identify tables that may contain sensitive data (PII/PCI)
-- Search for columns with names suggesting sensitive content
SELECT
    table_schema,
    table_name,
    column_name,
    data_type,
    CASE
        WHEN column_name ILIKE '%password%' THEN 'CREDENTIAL - Must be hashed'
        WHEN column_name ILIKE '%ssn%' OR column_name ILIKE '%social_security%' THEN 'PII - Must be encrypted'
        WHEN column_name ILIKE '%credit%' OR column_name ILIKE '%card%' THEN 'PCI - Must be encrypted/tokenized'
        WHEN column_name ILIKE '%email%' THEN 'PII - Review protection'
        WHEN column_name ILIKE '%phone%' THEN 'PII - Review protection'
        WHEN column_name ILIKE '%dob%' OR column_name ILIKE '%birth%' THEN 'PII - Review protection'
        ELSE 'REVIEW'
    END AS data_classification
FROM information_schema.columns
WHERE column_name ILIKE ANY(ARRAY[
    '%password%', '%secret%', '%token%', '%key%',
    '%ssn%', '%social_security%', '%credit%', '%card%',
    '%email%', '%phone%', '%dob%', '%birth%', '%address%'
])
AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;

-- ============================================================================
-- 6. NETWORK SECURITY
-- NIST: SC-7 | PCI: 1.3 | CIS: 9.2
-- ============================================================================

-- 6a. Check connection limits and listen addresses
SELECT
    name,
    setting,
    CASE
        WHEN name = 'listen_addresses' AND setting = '*' THEN 'WARNING - Listening on all interfaces'
        WHEN name = 'listen_addresses' AND setting = 'localhost' THEN 'COMPLIANT - Local only'
        WHEN name = 'max_connections' THEN 'Review if appropriate for workload'
        ELSE setting
    END AS audit_note
FROM pg_settings
WHERE name IN ('listen_addresses', 'max_connections', 'port');

-- ============================================================================
-- SUMMARY: Run this last for a quick compliance status
-- ============================================================================
SELECT
    'AUDIT COMPLETE' AS status,
    NOW() AS audit_timestamp,
    current_user AS auditor,
    current_database() AS database_name,
    version() AS db_version,
    'FLLC Compliance Audit v2026' AS tool;

```
