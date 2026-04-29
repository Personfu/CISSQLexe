# Module 4: Retrieving Data from Two or More Tables

## JOIN Basics
- Combine data from two or more tables using JOINs
- INNER JOIN: Returns rows with matching values in both tables
- LEFT JOIN: Returns all rows from the left table, and matched rows from the right table
- RIGHT JOIN: Returns all rows from the right table, and matched rows from the left table

## Example: INNER JOIN
```sql
SELECT c.customer_id, c.first_name, o.order_id
FROM Customers c
INNER JOIN Orders o ON c.customer_id = o.customer_id;
```

## Example: LEFT JOIN
```sql
SELECT c.customer_id, c.first_name, o.order_id
FROM Customers c
LEFT JOIN Orders o ON c.customer_id = o.customer_id;
```

---

For more examples, see the built-in examples in this repository. ch04/`.
