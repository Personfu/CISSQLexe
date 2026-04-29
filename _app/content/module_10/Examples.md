# Module 10 Examples

## Example 1: Scalar subquery
```sql
SELECT invoice_number, invoice_total
FROM invoices
WHERE invoice_total > (
    SELECT AVG(invoice_total)
    FROM invoices
);
```

## Example 2: `IN` and `ANY`
```sql
SELECT vendor_id, invoice_number, invoice_total
FROM invoices
WHERE invoice_total > ANY (
    SELECT invoice_total
    FROM invoices
    WHERE vendor_id = 95
);
```

## Example 3: Correlated subquery
```sql
SELECT v.vendor_name,
       i.invoice_number,
       i.invoice_total
FROM vendors v
JOIN invoices i ON i.vendor_id = v.vendor_id
WHERE i.payment_total < (
    SELECT AVG(payment_total)
    FROM invoices
    WHERE vendor_id = v.vendor_id
);
```

---

These examples follow patterns found in `repository sample scripts/ch07/7-01.sql` and related chapter 7 exercises.
