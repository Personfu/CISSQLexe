-- Module 2 submission: MySQL Workbench setup and sample database
CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;
CREATE TABLE IF NOT EXISTS test_table (
    id INT PRIMARY KEY,
    name VARCHAR(50)
);

-- Exercise 4: Example SQL that would be executed in Workbench
INSERT INTO test_table (id, name) VALUES (1, 'Example');
