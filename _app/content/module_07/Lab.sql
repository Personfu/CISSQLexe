-- Module 7 submission: security best practices
CREATE USER IF NOT EXISTS 'secure_user'@'localhost' IDENTIFIED BY 'StrongPass!23';
GRANT SELECT, INSERT ON secure_db.* TO 'secure_user'@'localhost';
REVOKE INSERT ON secure_db.* FROM 'secure_user'@'localhost';

-- Security best practice examples:
-- 1. Use least privilege for database users.
-- 2. Disable remote root login where possible.
-- 3. Enable encryption for data at rest and in transit.
