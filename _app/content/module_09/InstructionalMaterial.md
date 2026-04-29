# Module 9: Summary Queries and Aggregations

## Overview of Summary Queries
In this module, you will master aggregation and analytic SQL patterns that turn raw transaction data into meaningful business summaries.

### Core concepts
- Aggregate functions: `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`
- GROUP BY and HAVING clause behavior
- Window functions: `OVER()`, `PARTITION BY`, `ORDER BY`
- When to use grouped results vs. row-level analytics

## Example: Aggregate query
```sql
SELECT vendor_id,
       COUNT(*) AS invoice_count,
       SUM(invoice_total) AS invoice_total_sum,
       AVG(invoice_total) AS invoice_average
FROM invoices
GROUP BY vendor_id
HAVING SUM(invoice_total) > 10000;
```

## Example: Window function
```sql
SELECT vendor_id,
       invoice_date,
       invoice_total,
       SUM(invoice_total) OVER(PARTITION BY vendor_id) AS vendor_total,
       AVG(invoice_total) OVER(PARTITION BY vendor_id) AS vendor_avg
FROM invoices
WHERE invoice_total > 5000;
```

## Practical focus
This module uses chapter 6 scripts and applies them to real business questions such as vendor spending, invoice aging, and peak sales analysis.

---

### Reference materials
- Source scripts: `repository sample scripts/ch06/6-01.sql`, `6-11.sql`
- Example solutions: `repository sample solutions/ch06`
