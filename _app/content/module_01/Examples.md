# Module 1 Examples

## Example 1: Create a simple table
```sql
CREATE TABLE vendors (
    vendor_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_name VARCHAR(100) NOT NULL,
    contact_email VARCHAR(255)
);
```

## Example 2: Add a foreign key relationship
```sql
CREATE TABLE invoices (
    invoice_id INT PRIMARY KEY AUTO_INCREMENT,
    vendor_id INT NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    invoice_date DATE NOT NULL,
    invoice_total DECIMAL(9,2) NOT NULL,
    payment_total DECIMAL(9,2) DEFAULT 0,
    credit_total DECIMAL(9,2) DEFAULT 0,
    terms_id INT NOT NULL,
    invoice_due_date DATE NOT NULL,
    payment_date DATE,
    CONSTRAINT invoices_fk_vendors FOREIGN KEY (vendor_id)
        REFERENCES vendors (vendor_id)
);
```

## Example 3: Create and drop an index
```sql
CREATE INDEX invoices_vendor_id_index
ON invoices (vendor_id);

DROP INDEX invoices_vendor_id_index ON invoices;
```

---

These examples are drawn from the chapter 1 base scripts in `repository sample scripts/ch01/1-11.sql` and reflect real-world table creation and schema management practices.
