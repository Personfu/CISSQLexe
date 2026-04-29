# Final Project Package

This folder contains the final MySQL database implementation for the course.

## Files included
- `create_my_web_db.sql`: Creates the `my_web_db` database, tables, indexes, sample data, and validates constraints.
- `alter_products_users.sql`: Contains ALTER TABLE statements for the required schema changes and validation tests.
- `query_downloads.sql`: Contains the join query that returns downloads with user email and product name, ordered as required.

## Instructions
1. Execute `create_my_web_db.sql` in MySQL Workbench or the MySQL command line.
2. Execute `alter_products_users.sql` to apply schema changes and verify constraint behavior.
3. Execute `query_downloads.sql` to review the final reporting query.

## Notes
- The database uses `utf8mb4` and `InnoDB`.
- The schema enforces referential integrity between `users`, `products`, and `downloads`.
- The project demonstrates both database creation and schema maintenance through ALTER statements.


Submission package: `PersonFu-Final` contains the final SQL scripts, documentation, and project notes for grading.
