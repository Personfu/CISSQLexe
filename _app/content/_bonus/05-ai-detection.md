

## ai_anomaly_detection.sql

```sql
-- ============================================================================
-- FLLC AI ANOMALY DETECTION — Pure SQL
-- Detect suspicious patterns using statistical methods and behavioral baselines.
--
-- Use Cases:
--   - Brute force login detection
--   - Data exfiltration anomalies
--   - Bot traffic identification
--   - Insider threat indicators
--   - AI-generated attack pattern detection
--   - Privilege escalation chains
--
-- Note: These queries assume a standard audit/event log table structure.
--       Adapt table/column names to your specific schema.
--
-- FLLC 2026 — FU PERSON
-- ============================================================================

-- ============================================================================
-- SETUP: Create sample audit table (if testing)
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_events (
    event_id SERIAL PRIMARY KEY,
    event_time TIMESTAMP DEFAULT NOW(),
    event_type VARCHAR(50),        -- 'LOGIN', 'QUERY', 'DATA_ACCESS', 'ADMIN', 'API_CALL'
    username VARCHAR(100),
    source_ip VARCHAR(45),
    user_agent TEXT,
    target_resource VARCHAR(200),
    action VARCHAR(50),            -- 'SUCCESS', 'FAILURE', 'DENIED'
    data_volume_bytes BIGINT DEFAULT 0,
    response_time_ms INTEGER DEFAULT 0,
    session_id VARCHAR(100),
    metadata JSONB
);

-- ============================================================================
-- 1. BRUTE FORCE LOGIN DETECTION
-- Flag IPs with > 10 failed logins in 5 minutes
-- ============================================================================

SELECT
    source_ip,
    username,
    COUNT(*) AS failed_attempts,
    MIN(event_time) AS first_attempt,
    MAX(event_time) AS last_attempt,
    EXTRACT(EPOCH FROM (MAX(event_time) - MIN(event_time))) AS duration_seconds,
    'BRUTE_FORCE' AS detection_type,
    CASE
        WHEN COUNT(*) > 50 THEN 'CRITICAL'
        WHEN COUNT(*) > 20 THEN 'HIGH'
        WHEN COUNT(*) > 10 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS severity
FROM audit_events
WHERE event_type = 'LOGIN'
  AND action = 'FAILURE'
  AND event_time > NOW() - INTERVAL '5 minutes'
GROUP BY source_ip, username
HAVING COUNT(*) > 10
ORDER BY failed_attempts DESC;

-- ============================================================================
-- 2. DATA EXFILTRATION ANOMALY
-- Detect users downloading significantly more data than their baseline
-- Uses Z-score: values > 3 standard deviations from mean are anomalous
-- ============================================================================

WITH user_daily_volume AS (
    SELECT
        username,
        DATE(event_time) AS event_date,
        SUM(data_volume_bytes) AS daily_bytes
    FROM audit_events
    WHERE event_type = 'DATA_ACCESS'
      AND event_time > NOW() - INTERVAL '30 days'
    GROUP BY username, DATE(event_time)
),
user_baseline AS (
    SELECT
        username,
        AVG(daily_bytes) AS avg_bytes,
        STDDEV(daily_bytes) AS stddev_bytes,
        COUNT(*) AS sample_days
    FROM user_daily_volume
    GROUP BY username
    HAVING COUNT(*) >= 7  -- need at least 7 days for baseline
),
today_volume AS (
    SELECT
        username,
        SUM(data_volume_bytes) AS today_bytes
    FROM audit_events
    WHERE event_type = 'DATA_ACCESS'
      AND DATE(event_time) = CURRENT_DATE
    GROUP BY username
)
SELECT
    t.username,
    t.today_bytes,
    b.avg_bytes AS baseline_avg,
    b.stddev_bytes AS baseline_stddev,
    CASE
        WHEN b.stddev_bytes > 0
        THEN ROUND((t.today_bytes - b.avg_bytes) / b.stddev_bytes, 2)
        ELSE 0
    END AS z_score,
    'DATA_EXFILTRATION' AS detection_type,
    CASE
        WHEN b.stddev_bytes > 0 AND (t.today_bytes - b.avg_bytes) / b.stddev_bytes > 5 THEN 'CRITICAL'
        WHEN b.stddev_bytes > 0 AND (t.today_bytes - b.avg_bytes) / b.stddev_bytes > 3 THEN 'HIGH'
        ELSE 'MEDIUM'
    END AS severity
FROM today_volume t
JOIN user_baseline b ON t.username = b.username
WHERE b.stddev_bytes > 0
  AND (t.today_bytes - b.avg_bytes) / b.stddev_bytes > 3
ORDER BY z_score DESC;

-- ============================================================================
-- 3. BOT TRAFFIC DETECTION (AI-Generated Requests)
-- Identifies patterns consistent with automated/AI-generated traffic:
--   - Unnaturally consistent response times
--   - High request rates from single IP
--   - Missing or identical user agents
--   - Perfect request spacing (low timing jitter)
-- ============================================================================

WITH ip_stats AS (
    SELECT
        source_ip,
        COUNT(*) AS total_requests,
        COUNT(DISTINCT user_agent) AS unique_agents,
        AVG(response_time_ms) AS avg_response_ms,
        STDDEV(response_time_ms) AS stddev_response_ms,
        -- Coefficient of variation: low = suspiciously consistent
        CASE
            WHEN AVG(response_time_ms) > 0
            THEN STDDEV(response_time_ms) / AVG(response_time_ms)
            ELSE 0
        END AS timing_cv,
        -- Request rate per minute
        COUNT(*) / GREATEST(EXTRACT(EPOCH FROM (MAX(event_time) - MIN(event_time))) / 60, 1) AS requests_per_min,
        MIN(event_time) AS first_seen,
        MAX(event_time) AS last_seen
    FROM audit_events
    WHERE event_time > NOW() - INTERVAL '1 hour'
    GROUP BY source_ip
    HAVING COUNT(*) > 20
)
SELECT
    source_ip,
    total_requests,
    unique_agents,
    ROUND(avg_response_ms::numeric, 1) AS avg_response_ms,
    ROUND(timing_cv::numeric, 4) AS timing_coefficient,
    ROUND(requests_per_min::numeric, 1) AS req_per_min,
    'BOT_TRAFFIC' AS detection_type,
    -- Score: higher = more likely bot
    ROUND((
        CASE WHEN timing_cv < 0.1 THEN 3 ELSE 0 END +  -- Consistent timing
        CASE WHEN unique_agents <= 1 THEN 2 ELSE 0 END + -- Single user agent
        CASE WHEN requests_per_min > 60 THEN 3 ELSE 0 END + -- High rate
        CASE WHEN total_requests > 500 THEN 2 ELSE 0 END   -- Volume
    )::numeric, 0) AS bot_score,
    CASE
        WHEN (CASE WHEN timing_cv < 0.1 THEN 3 ELSE 0 END +
              CASE WHEN unique_agents <= 1 THEN 2 ELSE 0 END +
              CASE WHEN requests_per_min > 60 THEN 3 ELSE 0 END) >= 6 THEN 'HIGH'
        WHEN (CASE WHEN timing_cv < 0.1 THEN 3 ELSE 0 END +
              CASE WHEN unique_agents <= 1 THEN 2 ELSE 0 END +
              CASE WHEN requests_per_min > 60 THEN 3 ELSE 0 END) >= 3 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS severity
FROM ip_stats
ORDER BY bot_score DESC;

-- ============================================================================
-- 4. INSIDER THREAT — UNUSUAL ACCESS PATTERNS
-- Detects users accessing resources outside their normal pattern
-- ============================================================================

WITH user_normal_resources AS (
    SELECT
        username,
        target_resource,
        COUNT(*) AS access_count
    FROM audit_events
    WHERE event_type = 'DATA_ACCESS'
      AND event_time BETWEEN NOW() - INTERVAL '30 days' AND NOW() - INTERVAL '1 day'
    GROUP BY username, target_resource
    HAVING COUNT(*) >= 3  -- Resource is "normal" if accessed 3+ times
),
today_access AS (
    SELECT DISTINCT
        username,
        target_resource
    FROM audit_events
    WHERE event_type = 'DATA_ACCESS'
      AND DATE(event_time) = CURRENT_DATE
)
SELECT
    t.username,
    t.target_resource AS new_resource_accessed,
    'INSIDER_THREAT' AS detection_type,
    'MEDIUM' AS severity,
    'User accessed resource not in their 30-day baseline' AS description
FROM today_access t
LEFT JOIN user_normal_resources n
    ON t.username = n.username AND t.target_resource = n.target_resource
WHERE n.target_resource IS NULL
ORDER BY t.username;

-- ============================================================================
-- 5. PRIVILEGE ESCALATION CHAIN DETECTION
-- Identifies sequences: normal user -> admin action within short time
-- ============================================================================

WITH admin_actions AS (
    SELECT
        username,
        event_time,
        target_resource,
        action,
        LAG(event_type) OVER (PARTITION BY username ORDER BY event_time) AS prev_event_type,
        LAG(event_time) OVER (PARTITION BY username ORDER BY event_time) AS prev_event_time
    FROM audit_events
    WHERE event_time > NOW() - INTERVAL '24 hours'
      AND (event_type = 'ADMIN' OR event_type = 'LOGIN')
)
SELECT
    username,
    prev_event_type AS preceding_event,
    prev_event_time AS preceding_time,
    event_time AS admin_action_time,
    EXTRACT(EPOCH FROM (event_time - prev_event_time)) AS seconds_between,
    target_resource,
    'PRIVESC_CHAIN' AS detection_type,
    'HIGH' AS severity
FROM admin_actions
WHERE prev_event_type = 'LOGIN'
  AND EXTRACT(EPOCH FROM (event_time - prev_event_time)) < 30  -- Admin action within 30s of login
ORDER BY event_time DESC;

-- ============================================================================
-- 6. ANOMALOUS QUERY PATTERNS (SQL Injection Indicators)
-- Searches for suspicious query characteristics in logged statements
-- ============================================================================

SELECT
    username,
    source_ip,
    event_time,
    target_resource AS query_target,
    'SQLI_INDICATOR' AS detection_type,
    CASE
        WHEN metadata::text ILIKE '%UNION%SELECT%' THEN 'UNION-based injection'
        WHEN metadata::text ILIKE '%OR%1=1%' THEN 'Boolean-based injection'
        WHEN metadata::text ILIKE '%WAITFOR%DELAY%' THEN 'Time-based blind injection'
        WHEN metadata::text ILIKE '%xp_cmdshell%' THEN 'Command injection via xp_cmdshell'
        WHEN metadata::text ILIKE '%DROP%TABLE%' THEN 'Destructive injection'
        WHEN metadata::text ILIKE '%INTO%OUTFILE%' THEN 'File write injection'
        WHEN metadata::text ILIKE '%LOAD_FILE%' THEN 'File read injection'
        WHEN metadata::text ILIKE '%INFORMATION_SCHEMA%' THEN 'Schema enumeration'
        ELSE 'Pattern match'
    END AS injection_type,
    'CRITICAL' AS severity
FROM audit_events
WHERE event_type = 'QUERY'
  AND event_time > NOW() - INTERVAL '24 hours'
  AND (
    metadata::text ILIKE '%UNION%SELECT%'
    OR metadata::text ILIKE '%OR%1=1%'
    OR metadata::text ILIKE '%WAITFOR%DELAY%'
    OR metadata::text ILIKE '%xp_cmdshell%'
    OR metadata::text ILIKE '%DROP%TABLE%'
    OR metadata::text ILIKE '%INTO%OUTFILE%'
    OR metadata::text ILIKE '%LOAD_FILE%'
    OR metadata::text ILIKE '%INFORMATION_SCHEMA%'
  )
ORDER BY event_time DESC;

-- ============================================================================
-- DETECTION SUMMARY
-- ============================================================================
SELECT
    'AI ANOMALY DETECTION COMPLETE' AS status,
    NOW() AS run_timestamp,
    current_database() AS database_name,
    'FLLC v2026' AS engine;

```
