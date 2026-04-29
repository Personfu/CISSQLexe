-- Module 5 submission: INSERT, UPDATE, DELETE
INSERT INTO Products (product_id, product_name, price, category)
VALUES (101, 'Acoustic Guitar', 499.99, 'Instruments'),
       (102, 'Electric Guitar', 899.99, 'Instruments'),
       (103, 'Guitar Case', 79.99, 'Accessories');

UPDATE Products
SET price = 529.99
WHERE product_id = 101;

UPDATE Products
SET product_name = 'Premium Electric Guitar'
WHERE product_id = 102;

DELETE FROM Products
WHERE product_id = 103;
