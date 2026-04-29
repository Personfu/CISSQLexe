-- Module 10 submission: subquery exercises
SELECT invoice_number
FROM Invoices
WHERE invoice_total > (
    SELECT AVG(invoice_total)
    FROM Invoices
);

SELECT vendor_id
FROM Invoices
GROUP BY vendor_id
HAVING MAX(invoice_total) > (
    SELECT MAX(invoice_total)
    FROM Invoices
    WHERE vendor_id = 95
);

SELECT DISTINCT v.vendor_name
FROM Vendors v
WHERE EXISTS (
    SELECT 1
    FROM Invoices i
    WHERE i.vendor_id = v.vendor_id
      AND i.payment_total < (
          SELECT AVG(payment_total)
          FROM Invoices
          WHERE vendor_id = v.vendor_id
      )
);
