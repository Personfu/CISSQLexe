-- Module 4 submission: JOIN queries
SELECT o.order_id,
       c.first_name,
       c.last_name,
       o.order_date,
       o.total_amount
FROM Orders o
INNER JOIN Customers c ON o.customer_id = c.customer_id;

SELECT c.customer_id,
       c.first_name,
       c.last_name,
       o.order_id,
       o.total_amount
FROM Customers c
LEFT JOIN Orders o ON c.customer_id = o.customer_id;

SELECT o.order_id,
       c.first_name,
       c.last_name,
       p.product_name,
       i.quantity,
       i.item_price
FROM Orders o
JOIN Order_Items i ON o.order_id = i.order_id
JOIN Products p ON i.product_id = p.product_id
JOIN Customers c ON o.customer_id = c.customer_id;
