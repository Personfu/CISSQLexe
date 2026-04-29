

## forensic_queries.sql

```sql
-- ============================================================================
--  FLLC — SQL Forensic Analysis Queries
--  Real-world incident response and threat hunting queries.
--  Compatible with: MySQL, PostgreSQL, SQL Server, SQLite
--  FLLC 2026
-- ============================================================================

-- ============================================================================
--  1. AUTHENTICATION ANOMALIES
-- ============================================================================

-- Failed login attempts by IP (brute force detection)
SELECT
    source_ip,
    COUNT(*) AS failed_attempts,
    MIN(event_time) AS first_attempt,
    MAX(event_time) AS last_attempt,
    TIMESTAMPDIFF(MINUTE, MIN(event_time), MAX(event_time)) AS duration_minutes
FROM auth_logs
WHERE event_type = 'LOGIN_FAILED'
  AND event_time >= NOW() - INTERVAL 24 HOUR
GROUP BY source_ip
HAVING COUNT(*) > 10
ORDER BY failed_attempts DESC;

-- Successful logins after multiple failures (credential stuffing success)
SELECT
    a.username,
    a.source_ip,
    a.event_time AS successful_login,
    f.failed_count,
    f.first_failure
FROM auth_logs a
JOIN (
    SELECT
        username,
        source_ip,
        COUNT(*) AS failed_count,
        MIN(event_time) AS first_failure,
        MAX(event_time) AS last_failure
    FROM auth_logs
    WHERE event_type = 'LOGIN_FAILED'
    GROUP BY username, source_ip
    HAVING COUNT(*) >= 5
) f ON a.username = f.username AND a.source_ip = f.source_ip
WHERE a.event_type = 'LOGIN_SUCCESS'
  AND a.event_time > f.last_failure
ORDER BY a.event_time DESC;

-- Logins from unusual locations (geo-anomaly)
SELECT
    u.username,
    a.source_ip,
    a.geo_country,
    a.event_time,
    u.usual_country
FROM auth_logs a
JOIN users u ON a.username = u.username
WHERE a.event_type = 'LOGIN_SUCCESS'
  AND a.geo_country != u.usual_country
  AND a.event_time >= NOW() - INTERVAL 7 DAY
ORDER BY a.event_time DESC;

-- ============================================================================
--  2. PRIVILEGE ESCALATION DETECTION
-- ============================================================================

-- Recent privilege changes
SELECT
    modified_by,
    target_user,
    old_role,
    new_role,
    change_time,
    source_ip
FROM role_change_log
WHERE change_time >= NOW() - INTERVAL 48 HOUR
  AND new_role IN ('admin', 'superadmin', 'root')
ORDER BY change_time DESC;

-- Users who granted themselves elevated privileges
SELECT
    modified_by,
    target_user,
    new_role,
    change_time
FROM role_change_log
WHERE modified_by = target_user
  AND new_role IN ('admin', 'superadmin')
ORDER BY change_time DESC;

-- ============================================================================
--  3. DATA EXFILTRATION INDICATORS
-- ============================================================================

-- Large query result sets (potential data dump)
SELECT
    username,
    query_text,
    rows_returned,
    execution_time_ms,
    event_time,
    source_ip
FROM query_log
WHERE rows_returned > 10000
  AND event_time >= NOW() - INTERVAL 24 HOUR
ORDER BY rows_returned DESC
LIMIT 50;

-- Unusual table access patterns
SELECT
    username,
    table_accessed,
    COUNT(*) AS access_count,
    SUM(rows_returned) AS total_rows
FROM query_log
WHERE table_accessed IN ('users', 'credentials', 'payment_info', 'ssn_data')
  AND event_time >= NOW() - INTERVAL 7 DAY
GROUP BY username, table_accessed
HAVING COUNT(*) > 100
ORDER BY total_rows DESC;

-- ============================================================================
--  4. INJECTION ATTEMPT DETECTION
-- ============================================================================

-- Queries containing SQL injection patterns
SELECT
    username,
    source_ip,
    query_text,
    event_time,
    CASE
        WHEN query_text LIKE '%UNION%SELECT%' THEN 'UNION injection'
        WHEN query_text LIKE '%OR 1=1%' THEN 'Boolean bypass'
        WHEN query_text LIKE '%SLEEP(%' THEN 'Time-based blind'
        WHEN query_text LIKE '%WAITFOR%DELAY%' THEN 'Time-based blind (MSSQL)'
        WHEN query_text LIKE '%INTO OUTFILE%' THEN 'File write attempt'
        WHEN query_text LIKE '%LOAD_FILE%' THEN 'File read attempt'
        WHEN query_text LIKE "%--%'" THEN 'Comment bypass'
        WHEN query_text LIKE '%DROP TABLE%' THEN 'Destructive injection'
        ELSE 'Other'
    END AS injection_type
FROM query_log
WHERE (
    query_text LIKE '%UNION%SELECT%'
    OR query_text LIKE '%OR 1=1%'
    OR query_text LIKE '%SLEEP(%'
    OR query_text LIKE '%WAITFOR%DELAY%'
    OR query_text LIKE '%INTO OUTFILE%'
    OR query_text LIKE '%LOAD_FILE%'
    OR query_text LIKE '%DROP TABLE%'
    OR query_text LIKE '%xp_cmdshell%'
)
AND event_time >= NOW() - INTERVAL 30 DAY
ORDER BY event_time DESC;

-- ============================================================================
--  5. ACCOUNT TAKEOVER TIMELINE
-- ============================================================================

-- Build timeline for a compromised account
SELECT
    event_type,
    source_ip,
    user_agent,
    event_time,
    details
FROM (
    SELECT 'AUTH' AS event_type, source_ip, user_agent, event_time,
           CONCAT('Login: ', event_type) AS details
    FROM auth_logs WHERE username = 'TARGET_USER'

    UNION ALL

    SELECT 'QUERY' AS event_type, source_ip, NULL, event_time,
           LEFT(query_text, 200) AS details
    FROM query_log WHERE username = 'TARGET_USER'

    UNION ALL

    SELECT 'ROLE_CHANGE' AS event_type, source_ip, NULL, change_time,
           CONCAT(old_role, ' -> ', new_role) AS details
    FROM role_change_log WHERE target_user = 'TARGET_USER'
) combined
WHERE event_time >= NOW() - INTERVAL 30 DAY
ORDER BY event_time ASC;

-- ============================================================================
--  6. DATABASE HARDENING AUDIT
-- ============================================================================

-- Check for default/weak passwords
SELECT
    username,
    CASE
        WHEN password_hash = MD5('password') THEN 'CRITICAL: password = "password"'
        WHEN password_hash = MD5('admin') THEN 'CRITICAL: password = "admin"'
        WHEN password_hash = MD5('123456') THEN 'CRITICAL: password = "123456"'
        WHEN password_hash = MD5(username) THEN 'HIGH: password = username'
        ELSE 'OK'
    END AS password_status
FROM users
WHERE password_hash IN (
    MD5('password'), MD5('admin'), MD5('123456'), MD5('root'),
    MD5('test'), MD5('guest'), MD5(''), MD5(username)
);

-- Check user privileges (MySQL)
SELECT
    user,
    host,
    Super_priv,
    Grant_priv,
    File_priv,
    Process_priv,
    Shutdown_priv
FROM mysql.user
WHERE Super_priv = 'Y'
   OR Grant_priv = 'Y'
   OR File_priv = 'Y';

-- Tables without primary keys (data integrity risk)
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_ROWS
FROM information_schema.TABLES t
WHERE TABLE_TYPE = 'BASE TABLE'
  AND TABLE_SCHEMA NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys')
  AND NOT EXISTS (
      SELECT 1 FROM information_schema.TABLE_CONSTRAINTS tc
      WHERE tc.TABLE_SCHEMA = t.TABLE_SCHEMA
        AND tc.TABLE_NAME = t.TABLE_NAME
        AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
  )
ORDER BY TABLE_ROWS DESC;

```
