# Module 3 Examples

## Example 1: Select All Products
```sql
SELECT * FROM Products;
```

## Example 2: Filter by Price
```sql
SELECT * FROM Products WHERE price > 100;
```

## Example 3: Sort by Price Descending
```sql
SELECT product_name, price FROM Products ORDER BY price DESC;
```

## Example 4: Aliasing Columns
```sql
SELECT product_name AS Product, price AS Cost FROM Products;
```

---

For more examples, see the built-in examples in this repository. ch03/`.