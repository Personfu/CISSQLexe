-- Module 9 submission: summary and window queries
SELECT vendor_id,
       COUNT(*) AS invoice_count,
       SUM(invoice_total) AS total_sales
FROM Invoices
GROUP BY vendor_id
HAVING SUM(invoice_total) > 15000;

SELECT invoice_date,
       COUNT(*) AS invoice_count,
       AVG(invoice_total) AS average_total
FROM Invoices
GROUP BY invoice_date
HAVING COUNT(*) > 2
   AND AVG(invoice_total) > 8000;

SELECT vendor_id,
       invoice_id,
       invoice_total,
       SUM(invoice_total) OVER (PARTITION BY vendor_id ORDER BY invoice_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM Invoices
ORDER BY vendor_id, invoice_date;
