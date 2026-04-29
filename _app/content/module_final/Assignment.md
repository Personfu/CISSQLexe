# Final Project Assignment

## Final Project: Design and Implement a MySQL Database
This final project is a professional demonstration of your MySQL implementation skills. You will build a complete database schema, populate it with sample data, and validate constraint behavior.

## Deliverables
1. A folder named `LastnameFirstName-Final`
2. A submission package named `PersonFu-Final` can be used for this student deliverable.
2. SQL scripts that create the `my_web_db` database and required tables
3. Scripted sample data inserts for users, products, and downloads
4. A verified join query that returns downloads with user email and product name
5. ALTER statements to add `price` and `date_added` to `products`
6. ALTER statements to enforce `NOT NULL` and `VARCHAR(20)` on `users.first_name`
7. Demonstrated SQL statements that fail when constraints are violated
8. A short `README` or note file describing the sample schema and validation results

## Requirements
- Use `DROP DATABASE IF EXISTS` followed by `CREATE DATABASE`
- Specify `utf8mb4` character set and `InnoDB` engine for all tables
- Define `users`, `products`, and `downloads` tables with appropriate keys and foreign key relationships
- Add indexes on lookup or foreign key columns
- Insert at least 2 users, 2 products, and 3 download records
- Write a join query sorted by `email` descending and `product_name` ascending
- Use `NOW()` for `download_date` on the inserted download rows
- Alter the `products` table for price and date_added
- Alter the `users` table to enforce `NOT NULL` and length limits on `first_name`
- Attempt failing updates to prove the constraints are active

## Suggested project structure
- `create_my_web_db.sql` — database, tables, indexes, and sample data
- `alter_products_users.sql` — ALTER TABLE scripts and validation checks
- `query_downloads.sql` — join query and reporting examples
- `README.txt` — project summary and execution notes

## Grading focus
- Correct schema design and DDL (40%)
- Valid sample data and joins (20%)
- Constraint enforcement and validation (20%)
- Professional documentation and formatting (20%)
