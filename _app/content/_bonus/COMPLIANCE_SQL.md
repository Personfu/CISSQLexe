# FLLC Compliance SQL Cheatsheet

> SQL queries mapped to NIST 800-53, PCI-DSS 4.0, SOC 2, and CIS Controls.
> FLLC 2026

---

## Access Control Queries

### AC-2: Account Management (NIST) / 7.1: Need-to-Know (PCI)
```sql
-- List all users and privileges
SELECT usename, usesuper, usecreatedb, valuntil FROM pg_user;

-- Find users without password expiry
SELECT usename FROM pg_user WHERE valuntil IS NULL AND usecanlogin;
```

### AC-6: Least Privilege (NIST) / CC6.3 (SOC2)
```sql
-- Identify superuser accounts (should be minimal)
SELECT usename FROM pg_user WHERE usesuper = true;

-- Check table-level grants
SELECT grantee, table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee NOT IN ('postgres', 'PUBLIC')
ORDER BY grantee;
```

---

## Encryption Checks

### SC-13: Cryptographic Protection (NIST) / 3.5: Key Management (PCI)
```sql
-- Verify SSL is enabled
SELECT name, setting FROM pg_settings WHERE name = 'ssl';

-- Check password hash algorithm
SELECT name, setting FROM pg_settings WHERE name = 'password_encryption';
-- Expected: scram-sha-256

-- Verify minimum TLS version
SELECT name, setting FROM pg_settings WHERE name = 'ssl_min_protocol_version';
-- Expected: TLSv1.2 or TLSv1.3
```

---

## Audit Logging

### AU-2: Audit Events (NIST) / 10.2: Log Events (PCI) / CC7.2 (SOC2)
```sql
-- Check logging configuration
SELECT name, setting FROM pg_settings
WHERE name IN ('log_statement', 'log_connections', 'log_disconnections',
               'logging_collector', 'log_min_duration_statement');

-- Verify log format includes required fields
SELECT name, setting FROM pg_settings WHERE name = 'log_line_prefix';
-- Should include: %t (time), %u (user), %d (database), %h (host)
```

---

## Anomaly Detection

### SI-4: System Monitoring (NIST) / 11.5.1 (PCI)
```sql
-- Failed logins in last hour (brute force indicator)
SELECT source_ip, COUNT(*) AS failures
FROM audit_events
WHERE event_type = 'LOGIN' AND action = 'FAILURE'
  AND event_time > NOW() - INTERVAL '1 hour'
GROUP BY source_ip HAVING COUNT(*) > 5;

-- Data volume anomaly (Z-score)
-- See ai_anomaly_detection.sql for full implementation
```

---

## Quick Compliance Check

```sql
-- One-query compliance snapshot
SELECT
    (SELECT setting FROM pg_settings WHERE name='ssl') AS ssl_enabled,
    (SELECT setting FROM pg_settings WHERE name='password_encryption') AS pw_hash,
    (SELECT setting FROM pg_settings WHERE name='log_statement') AS log_level,
    (SELECT setting FROM pg_settings WHERE name='log_connections') AS log_conn,
    (SELECT COUNT(*) FROM pg_user WHERE usesuper) AS superuser_count,
    (SELECT COUNT(*) FROM pg_user WHERE valuntil IS NULL AND usecanlogin) AS no_pw_expiry;
```

---

**FLLC 2026** — FU PERSON by PERSON FU
