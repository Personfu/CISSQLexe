# Module 5: Insert, Update, and Delete Data

## INSERT Statement
- Add new rows to a table
```sql
INSERT INTO Products (product_id, product_name, price)
VALUES (1, 'Guitar', 499.99);
```

## UPDATE Statement
- Modify existing rows
```sql
UPDATE Products SET price = 599.99 WHERE product_id = 1;
```

## DELETE Statement
- Remove rows from a table
```sql
DELETE FROM Products WHERE product_id = 1;
```

---

For more examples, see the built-in examples in this repository. ch05/` and solutions in `the repository sample solutions and internal examples. /`.
