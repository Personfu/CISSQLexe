# Module 16: Triggers and Events

## Creating Triggers and Events in MySQL
This module teaches trigger-based validation, audit logging, and event scheduler automation.

### Core concepts
- `BEFORE UPDATE` and `BEFORE INSERT` triggers for validation and default values
- `AFTER UPDATE` triggers to capture audit history
- Designing an audit table for product changes
- Using MySQL events to perform scheduled cleanup

## Example: Validation trigger for discount percent
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

## Example: Insert trigger for default date
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

---

### Reference materials
- Chapter 16 source exercises from `ch16.docx`
