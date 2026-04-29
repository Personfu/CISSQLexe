# Module 9 Examples

## Example 1: Aggregate revenue by vendor
```sql
SELECT vendor_id,
       COUNT(*) AS invoice_count,
       SUM(invoice_total) AS total_revenue,
       ROUND(AVG(invoice_total), 2) AS avg_invoice_amount
FROM invoices
GROUP BY vendor_id;
```

## Example 2: Filter groups with HAVING
```sql
SELECT vendor_id,
       SUM(invoice_total) AS vendor_revenue
FROM invoices
GROUP BY vendor_id
HAVING SUM(invoice_total) > 15000;
```

## Example 3: Running total using window functions
```sql
SELECT vendor_id,
       invoice_date,
       invoice_total,
       SUM(invoice_total) OVER(PARTITION BY vendor_id ORDER BY invoice_date) AS running_vendor_total
FROM invoices;
```

---

These examples align with the chapter 6 scripts in `repository sample scripts/ch06/`.
