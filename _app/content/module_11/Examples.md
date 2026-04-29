# Module 11 Examples

## Example 1: Character and string types
```sql
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    first_name VARCHAR(20) NOT NULL,
    last_name VARCHAR(30) NOT NULL
);
```

## Example 2: Decimal and integer types
```sql
CREATE TABLE products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(6,2) NOT NULL DEFAULT 9.99,
    quantity SMALLINT UNSIGNED NOT NULL
);
```

## Example 3: Date and time types
```sql
CREATE TABLE downloads (
    download_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    download_date DATETIME NOT NULL,
    expire_date DATE
);
```

---

These examples support the data type principles covered in chapter 8 and in `repository sample scripts/ch08/8-08.sql`.
