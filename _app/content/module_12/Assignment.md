# Module 12 Assignment: How to Create Views

**Course:** SQL Essentials for the Real World
**Module:** 12 – How to Create Views
**Learning Outcomes:**
- Create views that join multiple tables
- Query views like virtual tables
- Update data through a view
- Build summary views for reporting

---

## Tasks
Complete the following exercises in a single SQL script.

### Exercise 1: Create `customer_addresses`
Create a view named `customer_addresses` that returns shipping and billing address columns for each customer from the `Customers` and `Addresses` tables.

### Exercise 2: Query `customer_addresses`
Write a `SELECT` statement that returns `customer_id`, `last_name`, `first_name`, and `bill_line1` from `customer_addresses`, sorted by `last_name` and `first_name`.

### Exercise 3: Update through the view
Write an `UPDATE` statement against `customer_addresses` to set `ship_line1 = '1990 Westwood Blvd.'` for `customer_id = 8`.

### Exercise 4: Create `order_item_products`
Create a view named `order_item_products` that returns columns from `Orders`, `Order_Items`, and `Products`, including `item_price`, `discount_amount`, `final_price`, `quantity`, and `item_total`.

### Exercise 5: Create `product_summary`
Create a view named `product_summary` based on `order_item_products` that returns `product_name`, `order_count`, and `order_total`.

### Exercise 6: Query the top five products
Write a `SELECT` statement from `product_summary` that returns the top five products by `order_total` descending.

---

## Submission
Save your work in `module12_views.sql` and include a short `module12_notes.txt` summary.

**Deliverables:**
- `module12_views.sql`
- `module12_notes.txt`

**Grading rubric:**
- Correct view definitions and queries: 40%
- Correct update behavior: 30%
- Correct summary view and top-five selection: 20%
- Documentation and comments: 10%
