# Module 12: Views in MySQL

## How to Create Views in MySQL
This module teaches students how to create and use views to simplify query logic, centralize business rules, and enable view-based data access.

### Core concepts
- Views are named SELECT queries that behave like virtual tables
- Views simplify repeated joins and reporting queries
- Views can support updates when they are simple and non-aggregated
- Summary views provide aggregated reporting for business metrics

## Example: Create a customer addresses view
```sql
DROP VIEW IF EXISTS customer_addresses;
CREATE VIEW customer_addresses AS
SELECT c.customer_id,
       c.email_address,
       c.last_name,
       c.first_name,
       a.bill_line1,
       a.bill_line2,
       a.bill_city,
       a.bill_state,
       a.bill_zip,
       a.ship_line1,
       a.ship_line2,
       a.ship_city,
       a.ship_state,
       a.ship_zip
FROM Customers c
JOIN Addresses a ON c.customer_id = a.customer_id;
```

## Example: Query a view like a table
```sql
SELECT customer_id,
       last_name,
       first_name,
       bill_line1
FROM customer_addresses
ORDER BY last_name,
         first_name;
```

## Example: Update through a view
```sql
UPDATE customer_addresses
SET ship_line1 = '1990 Westwood Blvd.'
WHERE customer_id = 8;
```

## Example: Create a summary view
```sql
DROP VIEW IF EXISTS order_item_products;
CREATE VIEW order_item_products AS
SELECT o.order_id,
       o.order_date,
       o.tax_amount,
       o.ship_date,
       p.product_name,
       i.item_price,
       i.discount_amount,
       i.item_price - i.discount_amount AS final_price,
       i.quantity,
       (i.item_price - i.discount_amount) * i.quantity AS item_total
FROM Orders o
JOIN Order_Items i ON o.order_id = i.order_id
JOIN Products p ON i.product_id = p.product_id;

DROP VIEW IF EXISTS product_summary;
CREATE VIEW product_summary AS
SELECT product_name,
       COUNT(*) AS order_count,
       SUM(item_total) AS order_total
FROM order_item_products
GROUP BY product_name;
```

---

### Reference materials
- Chapter 12 source exercises from `ch12.docx`
