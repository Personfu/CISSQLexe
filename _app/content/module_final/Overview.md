# Final Project Overview

## Project Description
This final project demonstrates a complete MySQL database implementation from requirements to execution. You will design a download-tracking schema, create the database and tables, add indexes, populate sample data, and validate constraints.

## Learning Outcomes
- Build a production-ready MySQL schema
- Apply `utf8mb4` and `InnoDB`
- Enforce referential integrity with foreign keys
- Validate schema behavior with sample data and edge-case updates

## What to submit
- SQL script files for schema creation and data insertion
- A final ZIP package containing the completed project folder


---

# Final Project: MySQL Database Implementation

## Project Overview
This final project demonstrates your ability to design, implement, and test a MySQL database from requirements to working SQL scripts.

### Learning outcomes
- Design tables, keys, relationships, and indexes
- Create databases with `utf8mb4` and `InnoDB`
- Insert sample data and join related tables
- Apply constraints, alter table definitions, and demonstrate validation failures

## Requirements
1. Create the `my_web_db` database using `utf8mb4` and `InnoDB`
2. Create `users`, `products`, and `downloads` tables with the required columns
3. Add indexing to improve query performance
4. Insert sample rows to demonstrate the data model
5. Write a join query sorted by email descending and product ascending
6. Add new columns to `products` for price and date added
7. Modify `users.first_name` to be `NOT NULL` and `VARCHAR(20)`
8. Demonstrate failed updates for NULL and overly long first name values

## Submission instructions
- Create a folder named `LastnameFirstname-Final`
- Add your SQL scripts and sample data files to the folder
- Zip the folder and submit it

## Included sample scripts
See `final_project/create_my_web_db.sql` for the complete database implementation sample.
Also review `final_project/alter_products_users.sql` for the required ALTER TABLE validation and `final_project/query_downloads.sql` for the final reporting join query.
