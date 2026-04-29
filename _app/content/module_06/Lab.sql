-- Module 6 submission: user management and system variables
CREATE USER IF NOT EXISTS 'report_user'@'localhost' IDENTIFIED BY 'SecurePass123!';
GRANT SELECT, INSERT ON test_db.* TO 'report_user'@'localhost';
REVOKE INSERT ON test_db.* FROM 'report_user'@'localhost';

SELECT @@global.time_zone AS global_time_zone,
       @@global.max_connections AS global_max_connections;

SET GLOBAL time_zone = '+00:00';
SET GLOBAL max_connections = 500;
