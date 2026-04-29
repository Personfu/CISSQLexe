-- PersonFuExercise12.sql
-- CIS276DA MySQL Database Module 15 / Chapter 13 stored procedure exercises

DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE product_count INT DEFAULT 0;

  SELECT COUNT(*) INTO product_count
  FROM Products;

  IF product_count >= 7 THEN
    SELECT 'The number of products is greater than or equal to 7' AS message;
  ELSE
    SELECT 'The number of products is less than 7' AS message;
  END IF;
END //
DELIMITER ;

CALL test();


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


DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE result_text TEXT DEFAULT '';

  WHILE i <= 10 DO
    IF 10 % i = 0 AND 20 % i = 0 THEN
      SET result_text = CONCAT(result_text, i, ' ');
    END IF;
    SET i = i + 1;
  END WHILE;

  SELECT CONCAT('Common factors of 10 and 20: ', TRIM(result_text)) AS message;
END //
DELIMITER ;

CALL test();


DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE product_name VARCHAR(255);
  DECLARE list_price DECIMAL(10,2);
  DECLARE output_text TEXT DEFAULT '';
  DECLARE cur CURSOR FOR
    SELECT product_name, list_price
    FROM Products
    WHERE list_price > 700
    ORDER BY list_price DESC;
  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN cur;
  read_loop: LOOP
    FETCH cur INTO product_name, list_price;
    IF done THEN
      LEAVE read_loop;
    END IF;
    SET output_text = CONCAT(output_text,
                             '"', product_name, '","', FORMAT(list_price, 2), '"|');
  END LOOP;
  CLOSE cur;

  SELECT output_text AS product_list;
END //
DELIMITER ;

CALL test();


DROP PROCEDURE IF EXISTS test;
DELIMITER //
CREATE PROCEDURE test()
BEGIN
  DECLARE sql_error INT DEFAULT 0;
  DECLARE CONTINUE HANDLER FOR SQLEXCEPTION SET sql_error = 1;

  INSERT INTO Categories (category_name)
  VALUES ('Guitars');

  IF sql_error = 0 THEN
    SELECT '1 row was inserted.' AS message;
  ELSE
    SELECT 'Row was not inserted - duplicate entry.' AS message;
  END IF;
END //
DELIMITER ;

CALL test();
