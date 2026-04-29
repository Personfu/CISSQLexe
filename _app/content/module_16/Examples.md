# Module 16 Examples

## Example 1: Discount validation trigger
```sql
DROP TRIGGER IF EXISTS products_before_update;
DELIMITER //
CREATE TRIGGER products_before_update
BEFORE UPDATE ON Products
FOR EACH ROW
BEGIN
  IF NEW.discount_percent < 0 OR NEW.discount_percent > 100 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Discount percent must be between 0 and 100';
  END IF;

  IF NEW.discount_percent > 0 AND NEW.discount_percent < 1 THEN
    SET NEW.discount_percent = NEW.discount_percent * 100;
  END IF;
END;//
DELIMITER ;
```

## Example 2: Insert trigger for default date
```sql
DROP TRIGGER IF EXISTS products_before_insert;
DELIMITER //
CREATE TRIGGER products_before_insert
BEFORE INSERT ON Products
FOR EACH ROW
BEGIN
  IF NEW.date_added IS NULL THEN
    SET NEW.date_added = CURRENT_DATE();
  END IF;
END;//
DELIMITER ;
```

## Example 3: Audit table and trigger
```sql
DROP TABLE IF EXISTS Products_Audit;
CREATE TABLE Products_Audit (
  audit_id INT AUTO_INCREMENT PRIMARY KEY,
  product_id INT NOT NULL,
  category_id INT NOT NULL,
  product_code VARCHAR(50) NOT NULL,
  product_name VARCHAR(255) NOT NULL,
  list_price DECIMAL(10,2) NOT NULL,
  discount_percent DECIMAL(5,2) NOT NULL,
  date_updated DATETIME NOT NULL
) ENGINE=InnoDB;

DROP TRIGGER IF EXISTS products_after_update;
DELIMITER //
CREATE TRIGGER products_after_update
AFTER UPDATE ON Products
FOR EACH ROW
BEGIN
  INSERT INTO Products_Audit (
    product_id,
    category_id,
    product_code,
    product_name,
    list_price,
    discount_percent,
    date_updated
  ) VALUES (
    OLD.product_id,
    OLD.category_id,
    OLD.product_code,
    OLD.product_name,
    OLD.list_price,
    OLD.discount_percent,
    NOW()
  );
END;//
DELIMITER ;
```

## Example 4: Event scheduler cleanup
```sql
SHOW VARIABLES LIKE 'event_scheduler';
SET GLOBAL event_scheduler = ON;

DROP EVENT IF EXISTS prune_products_audit;
CREATE EVENT prune_products_audit
ON SCHEDULE EVERY 1 DAY
DO
  DELETE FROM Products_Audit
  WHERE date_updated < NOW() - INTERVAL 7 DAY;

SHOW EVENTS LIKE 'prune_products_audit';
DROP EVENT IF EXISTS prune_products_audit;
```
