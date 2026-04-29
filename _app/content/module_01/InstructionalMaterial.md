# Module 1: Introduction to Relational Databases

## What is a Relational Database?
A relational database organizes data into tables (relations) consisting of rows and columns. Each table represents an entity, and relationships between tables are established using keys.

### Key Concepts
- **Table**: A collection of related data entries
- **Row**: A single record in a table
- **Column**: A data field in a table
- **Primary Key**: Uniquely identifies each row
- **Foreign Key**: Links rows in one table to rows in another

## Why SQL?
SQL (Structured Query Language) is the standard language for interacting with relational databases. It allows you to create, read, update, and delete data efficiently.

## Example
```sql
CREATE TABLE Customers (
    customer_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email_address VARCHAR(100)
);
```

---

For more examples, see the built-in examples in this repository. ch01/`.
