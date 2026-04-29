-- Module 1 submission: relational database concepts
-- Exercise 1 answers:
-- Table: Orders
-- Columns: order_id, customer_id, order_date, total_amount
-- Primary key: order_id
-- Data types: INT, INT, DATE, DECIMAL(10,2)

-- Exercise 2: Create Products table
CREATE TABLE IF NOT EXISTS Products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    price DECIMAL(10,2),
    category VARCHAR(50)
);

-- Exercise 3: Add foreign key relationship
ALTER TABLE Orders
    ADD CONSTRAINT fk_orders_customers
    FOREIGN KEY (customer_id)
    REFERENCES Customers(customer_id);
