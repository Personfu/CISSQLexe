# Module 1 Assignment: Exploring Relational Databases

**Course:** SQL Essentials for the Real World
**Module:** 1 – Introduction to Relational Databases
**Learning Outcomes:**
- Define and identify tables, rows, columns, primary keys, and foreign keys (CLO 1, 2)
- Explain the purpose of relationships in a database (CLO 2)

---

## Assignment Instructions

### Exercise 1: Identify Database Components
Given the following table definition:

```sql
CREATE TABLE Orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2)
);
```

1. List the table name, all column names, and identify the primary key.
2. Explain what type of data each column would store.

### Exercise 2: Create Your Own Table
Write a SQL statement to create a table named `Products` with the following columns:
- product_id (integer, primary key)
- product_name (string, up to 100 characters)
- price (decimal, up to 2 decimal places)
- category (string, up to 50 characters)

### Exercise 3: Establish a Relationship
Write a SQL statement to add a foreign key to the `Orders` table that references the `customer_id` in a `Customers` table.

### Exercise 4: Reflection
In your own words, explain why primary keys and foreign keys are important in relational databases.

---

## Submission Instructions
- Save your SQL scripts and written answers in a folder named `LastnameFirstnameModule1` (replace with your name)
- Zip the folder and submit it as `LastnameFirstnameModule1.zip`

---

**Rubric:**
- Correct SQL syntax and structure (40%)
- Accurate identification and explanation of database components (30%)
- Clear, thoughtful reflection (20%)
- Proper submission format (10%)

---

**Instructor:** Personfu
**Support:** See docs/Support.md for help.