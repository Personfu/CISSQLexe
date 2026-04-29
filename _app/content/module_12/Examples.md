# Module 12 Examples

## Example 1: Create `customer_addresses`
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

## Example 2: Query `customer_addresses`
```sql
SELECT customer_id,
       last_name,
       first_name,
       bill_line1
FROM customer_addresses
ORDER BY last_name,
         first_name;
```

## Example 3: Update the view
```sql
UPDATE customer_addresses
SET ship_line1 = '1990 Westwood Blvd.'
WHERE customer_id = 8;
```

## Example 4: Create `order_item_products`
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
```

## Example 5: Create `product_summary`
```sql
DROP VIEW IF EXISTS product_summary;
CREATE VIEW product_summary AS
SELECT product_name,
       COUNT(*) AS order_count,
       SUM(item_total) AS order_total
FROM order_item_products
GROUP BY product_name;
```

## Example 6: Query top products
```sql
SELECT product_name,
       order_count,
       order_total
FROM product_summary
ORDER BY order_total DESC
LIMIT 5;
```
