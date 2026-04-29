# Module 4 Examples

## Example 1: INNER JOIN
```sql
SELECT c.customer_id, c.first_name, o.order_id
FROM Customers c
INNER JOIN Orders o ON c.customer_id = o.customer_id;
```

## Example 2: LEFT JOIN
```sql
SELECT c.customer_id, c.first_name, o.order_id
FROM Customers c
LEFT JOIN Orders o ON c.customer_id = o.customer_id;
```

## Example 3: Multi-table JOIN
```sql
SELECT o.order_id, c.first_name, p.product_name
FROM Orders o
JOIN Customers c ON o.customer_id = c.customer_id
JOIN Order_Items oi ON o.order_id = oi.order_id
JOIN Products p ON oi.product_id = p.product_id;
```

---

For more examples, see the built-in examples in this repository. ch04/`.