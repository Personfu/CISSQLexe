# Module 15 Assignment: How to Create Stored Procedures and Functions

**Course:** SQL Essentials for the Real World
**Module:** 15 – How to Create Stored Procedures and Functions
**Learning Outcomes:**
- Build stored procedures and functions
- Validate input with custom errors
- Use functions for reusable calculations
- Test stored routines using `CALL`

---

## Tasks
Write SQL scripts for these exercises.

### Exercise 1: `insert_category`
Create a procedure named `insert_category` with one parameter for `category_name` to insert into `Categories`.

### Exercise 2: `discount_price`
Create a stored function named `discount_price` that returns the discount price for an item in `Order_Items`.

### Exercise 3: `item_total`
Create a stored function named `item_total` that uses `discount_price` to calculate total amount for an item.

### Exercise 4: `insert_product`
Create a stored procedure named `insert_product` with parameters for `category_id`, `product_code`, `product_name`, `list_price`, and `discount_percent`. Set `description` to an empty string and `date_added` to the current date. Raise an error if `list_price` or `discount_percent` is negative.

### Exercise 5: `update_product_discount`
Create a stored procedure named `update_product_discount` that updates `discount_percent` for a product and signals an error if the value is negative.

---

## Submission
Save your work in `module15_procedures_functions.sql` and include a short `module15_notes.txt` summary.

**Deliverables:**
- `module15_procedures_functions.sql`
- `module15_notes.txt`

**Grading rubric:**
- Correct procedure/function definitions: 40%
- Validation and error handling: 30%
- Comments and testing: 20%
- Documentation: 10%
