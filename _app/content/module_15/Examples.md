# Module 15 Examples

## Example 1: `insert_category`
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
CALL insert_category('Guitars');
```

## Example 2: `discount_price`
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

## Example 3: `item_total`
```sql
DROP FUNCTION IF EXISTS item_total;
DELIMITER //
CREATE FUNCTION item_total(p_item_id INT)
RETURNS DECIMAL(12,2)
DETERMINISTIC
BEGIN
  DECLARE price_after_discount DECIMAL(10,2);
  DECLARE qty INT;

  SELECT discount_price(p_item_id), quantity
  INTO price_after_discount, qty
  FROM Order_Items
  WHERE item_id = p_item_id;

  RETURN price_after_discount * qty;
END //
DELIMITER ;

SELECT item_total(1) AS item_total_value;
```

## Example 4: `insert_product` with validation
```sql
DROP PROCEDURE IF EXISTS insert_product;
DELIMITER //
CREATE PROCEDURE insert_product(
  IN p_category_id INT,
  IN p_product_code VARCHAR(50),
  IN p_product_name VARCHAR(255),
  IN p_list_price DECIMAL(10,2),
  IN p_discount_percent DECIMAL(5,2)
)
BEGIN
  IF p_list_price < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'list_price cannot be negative';
  END IF;
  IF p_discount_percent < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'discount_percent cannot be negative';
  END IF;

  INSERT INTO Products (category_id, product_code, product_name, list_price, discount_percent, description, date_added)
  VALUES (p_category_id, p_product_code, p_product_name, p_list_price, p_discount_percent, '', CURRENT_DATE());
END //
DELIMITER ;

CALL insert_product(1, 'GTR-100', 'New Guitar', 899.00, 10.0);
```

## Example 5: `update_product_discount`
```sql
DROP PROCEDURE IF EXISTS update_product_discount;
DELIMITER //
CREATE PROCEDURE update_product_discount(
  IN p_product_id INT,
  IN p_discount_percent DECIMAL(5,2)
)
BEGIN
  IF p_discount_percent < 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'discount_percent must be positive';
  END IF;

  UPDATE Products
  SET discount_percent = p_discount_percent
  WHERE product_id = p_product_id;
END //
DELIMITER ;

CALL update_product_discount(1, 15.0);
```
