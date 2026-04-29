# Module 11: Working with Data Types

## Working with Data Types in MySQL
This module explains how to choose and use MySQL data types for text, numeric, date/time, and binary data.

### Core concepts
- Data type categories: numeric, date/time, string, and binary
- Character sets and collations
- Choosing fixed-length vs. variable-length types
- Date/time storage and formatting

## Example: Character types
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    email VARCHAR(255) UNIQUE
);
```

## Example: Numeric types
```sql
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(6,2) NOT NULL DEFAULT 9.99,
    quantity SMALLINT UNSIGNED NOT NULL
);
```

## Example: Date and time types
```sql
CREATE TABLE downloads (
    download_id INT AUTO_INCREMENT PRIMARY KEY,
    download_date DATETIME NOT NULL,
    expire_date DATE
);
```

---

### Reference materials
- Source scripts: `repository sample scripts/ch08/8-08.sql`, `8-09.sql`
- Example solutions: `repository sample solutions/ch08`
