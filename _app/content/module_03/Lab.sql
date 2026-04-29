-- Module 3 submission: SELECT queries
SELECT * FROM Products;

SELECT * FROM Products
WHERE price > 100;

SELECT product_name, price
FROM Products
ORDER BY price DESC;

SELECT product_name AS Product, price AS Cost
FROM Products;
