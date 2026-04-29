# Module 10: Subqueries and Correlated Queries

## Introduction to Subqueries
This module teaches subqueries as a powerful tool for filtering, scalar computation, and correlated row evaluation.

### Core concepts
- Subqueries in `SELECT`, `FROM`, and `WHERE`
- Scalar subqueries vs. table subqueries
- Correlated subqueries and the `EXISTS` predicate
- Set comparisons with `ALL`, `ANY`, and `IN`

## Example: Subquery in WHERE
```sql
SELECT invoice_number, invoice_total
FROM invoices
WHERE invoice_total > (
    SELECT AVG(invoice_total)
    FROM invoices
);
```

## Example: Correlated subquery
```sql
SELECT v.vendor_id, v.vendor_name
FROM vendors v
WHERE EXISTS (
    SELECT 1
    FROM invoices i
    WHERE i.vendor_id = v.vendor_id
      AND i.invoice_total > 10000
);
```

---

### Reference materials
- Source scripts: `repository sample scripts/ch07/7-01.sql`
- Example solutions: `repository sample solutions/ch07`
