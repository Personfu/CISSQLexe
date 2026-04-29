# Final Project Examples

## Example 1: Create the database and tables
```sql
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
    product_name VARCHAR(100) NOT NULL,
    price DECIMAL(6,2) NOT NULL DEFAULT 9.99,
    date_added DATETIME NOT NULL DEFAULT NOW()
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
```

## Example 2: Sample data insert
```sql
INSERT INTO users (email, first_name, last_name)
VALUES ('alisa@example.com', 'Alisa', 'Reed'),
       ('derek@example.com', 'Derek', 'Chan');

INSERT INTO products (product_name)
VALUES ('SQL Performance Guide'),
       ('Reporting Automation Workbook');
```

## Example 3: Join query and sorting
```sql
SELECT u.email,
       p.product_name,
       d.filename,
       d.download_date
FROM downloads d
JOIN users u ON d.user_id = u.user_id
JOIN products p ON d.product_id = p.product_id
ORDER BY u.email DESC, p.product_name ASC;
```
