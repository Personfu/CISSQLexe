# Module 14 Examples

## Example 1: Transactional delete procedure
```sql
DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE sql_error INT DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET sql_error = 1;

  START TRANSACTION;
  DELETE FROM Addresses WHERE customer_id = 8;
  DELETE FROM Customers WHERE customer_id = 8;

  IF sql_error = 0 THEN
    COMMIT;
  ELSE
    ROLLBACK;
  END IF;
END //
DELIMITER ;

CALL test();
```

## Example 2: Transaction with `LAST_INSERT_ID()`
```sql
DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE sql_error INT DEFAULT 0;
  DECLARE order_id INT DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET sql_error = 1;

  START TRANSACTION;
  INSERT INTO Orders VALUES (DEFAULT, 3, NOW(), '10.00', '0.00', NULL, 4, 'American Express', '378282246310005', '04/2016', 4);
  SET order_id = LAST_INSERT_ID();
  INSERT INTO Order_Items VALUES (DEFAULT, order_id, 6, '415.00', '161.85', 1);
  INSERT INTO Order_Items VALUES (DEFAULT, order_id, 1, '699.00', '209.70', 1);

  IF sql_error = 0 THEN
    COMMIT;
  ELSE
    ROLLBACK;
  END IF;
END //
DELIMITER ;

CALL test();
```

## Example 3: Locked row merge procedure
```sql
DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE sql_error INT DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET sql_error = 1;

  START TRANSACTION;
  SELECT * FROM Customers WHERE customer_id = 6 FOR UPDATE NOWAIT;
  UPDATE Orders SET customer_id = 3 WHERE customer_id = 6;
  UPDATE Addresses SET customer_id = 3 WHERE customer_id = 6;
  DELETE FROM Customers WHERE customer_id = 6;

  IF sql_error = 0 THEN
    COMMIT;
  ELSE
    ROLLBACK;
  END IF;
END //
DELIMITER ;

CALL test();
```
