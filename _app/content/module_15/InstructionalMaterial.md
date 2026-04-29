# Module 15: Procedures and Functions

## Creating Stored Procedures and Functions
This module teaches how to build stored procedures and functions that validate input, calculate values, and raise errors.

### Core concepts
- Stored procedure and function syntax
- Parameters, return values, and variable declarations
- Using `SIGNAL` to enforce input rules
- Building reusable computation logic in functions

## Example: `insert_category` procedure
```sql
DROP PROCEDURE IF EXISTS insert_category;
DELIMITER //
CREATE PROCEDURE insert_category(IN p_category_name VARCHAR(100))
BEGIN
  DECLARE sql_error INT DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET sql_error = 1;

  INSERT INTO Categories (category_name)
  VALUES (p_category_name);

  IF sql_error = 0 THEN
    SELECT '1 row was inserted.' AS message;
  ELSE
    SELECT 'Row was not inserted - duplicate entry.' AS message;
  END IF;
END //
DELIMITER ;

CALL insert_category('Guitars');
```

## Example: `discount_price` function
```sql
DROP FUNCTION IF EXISTS discount_price;
DELIMITER //
CREATE FUNCTION discount_price(p_item_id INT)
RETURNS DECIMAL(10,2)
DETERMINISTIC
BEGIN
  DECLARE result DECIMAL(10,2);
  SELECT item_price - discount_amount
  INTO result
  FROM Order_Items
  WHERE item_id = p_item_id;
  RETURN result;
END //
DELIMITER ;

SELECT discount_price(1) AS discounted_price;
```

---

### Reference materials
- Chapter 15 source exercises from `ch15.docx`
