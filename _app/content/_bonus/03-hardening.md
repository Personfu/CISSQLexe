

## hardening_checklist.sql

```sql
-- ============================================================================
--  FLLC — Database Hardening Implementation
--  Production-ready security configurations.
--  FLLC 2026
-- ============================================================================

-- ============================================================================
--  1. CREATE LEAST-PRIVILEGE ROLES
-- ============================================================================

-- Application role: read/write to specific tables only
CREATE ROLE IF NOT EXISTS app_readwrite;
GRANT SELECT, INSERT, UPDATE ON mydb.users TO app_readwrite;
GRANT SELECT, INSERT, UPDATE ON mydb.orders TO app_readwrite;
GRANT SELECT ON mydb.products TO app_readwrite;
-- No DELETE, no DDL, no GRANT

-- Read-only analytics role
CREATE ROLE IF NOT EXISTS analytics_readonly;
GRANT SELECT ON mydb.* TO analytics_readonly;

-- Admin role (limited)
CREATE ROLE IF NOT EXISTS db_admin;
GRANT ALL PRIVILEGES ON mydb.* TO db_admin;
-- Still no SUPER, GRANT OPTION, or FILE privileges

-- ============================================================================
--  2. CREATE SERVICE ACCOUNTS (not root)
-- ============================================================================

CREATE USER IF NOT EXISTS 'app_service'@'10.0.%.%'
    IDENTIFIED BY 'CHANGE_ME_STRONG_PASSWORD_HERE'
    PASSWORD EXPIRE INTERVAL 90 DAY
    FAILED_LOGIN_ATTEMPTS 5
    PASSWORD_LOCK_TIME 2;

GRANT app_readwrite TO 'app_service'@'10.0.%.%';
SET DEFAULT ROLE app_readwrite FOR 'app_service'@'10.0.%.%';

-- ============================================================================
--  3. ENABLE AUDIT LOGGING
-- ============================================================================

-- MySQL Enterprise Audit (if available)
-- INSTALL PLUGIN audit_log SONAME 'audit_log.so';
-- SET GLOBAL audit_log_policy = 'ALL';

-- Manual audit table for tracking changes
CREATE TABLE IF NOT EXISTS audit_trail (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    operation ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_data JSON,
    new_data JSON,
    changed_by VARCHAR(100) DEFAULT CURRENT_USER(),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_ip VARCHAR(45)
) ENGINE=InnoDB;

-- Example trigger for users table
DELIMITER //
CREATE TRIGGER users_audit_update
AFTER UPDATE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (table_name, operation, old_data, new_data)
    VALUES (
        'users',
        'UPDATE',
        JSON_OBJECT('username', OLD.username, 'email', OLD.email, 'role', OLD.role),
        JSON_OBJECT('username', NEW.username, 'email', NEW.email, 'role', NEW.role)
    );
END//

CREATE TRIGGER users_audit_delete
AFTER DELETE ON users
FOR EACH ROW
BEGIN
    INSERT INTO audit_trail (table_name, operation, old_data)
    VALUES (
        'users',
        'DELETE',
        JSON_OBJECT('id', OLD.id, 'username', OLD.username, 'email', OLD.email)
    );
END//
DELIMITER ;

-- ============================================================================
--  4. ENCRYPTION AT REST
-- ============================================================================

-- Encrypt sensitive columns (application-level recommended)
-- For column-level encryption in MySQL:
ALTER TABLE users
    MODIFY password VARCHAR(255) NOT NULL COMMENT 'bcrypt hashed',
    MODIFY email VARCHAR(255) COMMENT 'AES encrypted at app layer';

-- Enable tablespace encryption (MySQL 8.0+)
-- ALTER TABLESPACE mydb_ts ENCRYPTION='Y';

-- ============================================================================
--  5. NETWORK SECURITY
-- ============================================================================

-- Restrict user connections by IP
-- Already done: 'app_service'@'10.0.%.%' limits to VPC range

-- Disable remote root login
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
FLUSH PRIVILEGES;

-- ============================================================================
--  6. BACKUP VERIFICATION
-- ============================================================================

-- Verify backup integrity (run after restore test)
SELECT
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_ROWS,
    DATA_LENGTH + INDEX_LENGTH AS total_bytes,
    ROUND((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024, 2) AS size_mb,
    UPDATE_TIME
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'mydb'
ORDER BY total_bytes DESC;

-- Compare row counts with expected values
-- SELECT COUNT(*) FROM users;        -- Expected: > 0
-- SELECT COUNT(*) FROM orders;       -- Expected: > 0
-- SELECT COUNT(*) FROM audit_trail;  -- Expected: > 0

```
