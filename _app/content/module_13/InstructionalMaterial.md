# Module 13: Stored Programs and Procedures

## Language Skills for Writing Stored Programs
This module teaches stored procedures, variables, control flow, cursors, and error handling in MySQL.

### Core concepts
- Using `DELIMITER`, `CREATE PROCEDURE`, and `BEGIN...END`
- Declaring variables and storing query results
- Conditional logic with `IF` and loops
- Cursor-based row processing
- Handling SQL exceptions in stored procedures

## Example: Conditional procedure
```sql
DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE product_count INT DEFAULT 0;
  SELECT COUNT(*) INTO product_count FROM Products;

  IF product_count >= 7 THEN
    SELECT 'The number of products is greater than or equal to 7' AS message;
  ELSE
    SELECT 'The number of products is less than 7' AS message;
  END IF;
END //
DELIMITER ;

CALL test();
```

## Example: Procedure with average price
```sql
DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE product_count INT DEFAULT 0;
  DECLARE average_price DECIMAL(10,2) DEFAULT 0.00;

  SELECT COUNT(*), AVG(list_price)
  INTO product_count, average_price
  FROM Products;

  IF product_count >= 7 THEN
    SELECT product_count AS product_count,
           average_price AS average_price;
  ELSE
    SELECT 'The number of products is less than 7' AS message;
  END IF;
END //
DELIMITER ;

CALL test();
```

---

### Reference materials
- Chapter 13 source exercises from `ch13.docx`
