-- Final Project SQL script for my_web_db

DROP DATABASE IF EXISTS my_web_db;
CREATE DATABASE my_web_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE my_web_db;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(30) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE downloads (
    download_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    download_date DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;

CREATE INDEX idx_downloads_user_id ON downloads(user_id);
CREATE INDEX idx_downloads_product_id ON downloads(product_id);
CREATE INDEX idx_users_email ON users(email);

INSERT INTO users (email, first_name, last_name)
VALUES
  ('cassandra@example.com', 'Cassandra', 'Lee'),
  ('andrew@example.com', 'Andrew', 'Scott');

INSERT INTO products (product_name)
VALUES
  ('Business Intelligence Guide'),
  ('Advanced SQL Video Course');

INSERT INTO downloads (user_id, product_id, filename)
VALUES
  (1, 2, 'advanced_sql_video.mp4'),
  (2, 1, 'business_intelligence_guide.pdf'),
  (2, 2, 'advanced_sql_video.mp4');

SELECT u.email,
       p.product_name,
       d.filename,
       d.download_date
FROM downloads d
JOIN users u ON d.user_id = u.user_id
JOIN products p ON d.product_id = p.product_id
ORDER BY u.email DESC, p.product_name ASC;

-- Demonstrate the required ALTER TABLE changes
ALTER TABLE products
  ADD COLUMN price DECIMAL(6,2) NOT NULL DEFAULT 9.99,
  ADD COLUMN date_added DATETIME NOT NULL DEFAULT NOW();

ALTER TABLE users
  MODIFY COLUMN first_name VARCHAR(20) NOT NULL;

-- These updates should fail due to enforced constraints
UPDATE users
SET first_name = NULL
WHERE user_id = 1;

UPDATE users
SET first_name = 'ANameLongerThanTwentyCharacters'
WHERE user_id = 1;


-- ALTERS --

-- Final Project ALTER table validation script

USE my_web_db;

-- Add the required columns to products
ALTER TABLE products
  ADD COLUMN price DECIMAL(6,2) NOT NULL DEFAULT 9.99,
  ADD COLUMN date_added DATETIME NOT NULL DEFAULT NOW();

-- Enforce users.first_name length and NOT NULL
ALTER TABLE users
  MODIFY COLUMN first_name VARCHAR(20) NOT NULL;

-- Validation checks
SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, CHARACTER_MAXIMUM_LENGTH
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'my_web_db'
  AND TABLE_NAME IN ('users', 'products');

-- Demonstrate constraint failure: NULL first name
UPDATE users
SET first_name = NULL
WHERE user_id = 1;

-- Demonstrate constraint failure: overly long first name
UPDATE users
SET first_name = 'ThisFirstNameIsLongerThanTwentyCharacters'
WHERE user_id = 1;


-- REPORTING --

-- Final Project reporting query

USE my_web_db;

SELECT u.email,
       p.product_name,
       d.filename,
       d.download_date
FROM downloads d
JOIN users u ON d.user_id = u.user_id
JOIN products p ON d.product_id = p.product_id
ORDER BY u.email DESC,
         p.product_name ASC;
