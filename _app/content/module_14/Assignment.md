# Module 14 Assignment: How to Use Transactions and Locking

**Course:** SQL Essentials for the Real World
**Module:** 14 – How to Use Transactions and Locking
**Learning Outcomes:**
- Create transactional stored procedures
- Use commit and rollback correctly
- Lock rows before updates in concurrent environments
- Handle failure conditions safely

---

## Tasks
Write SQL scripts that create and call stored procedures for these exercises.

### Exercise 1: Delete customer transaction
Create a procedure named `test` that deletes `Addresses` rows for `customer_id = 8`, then deletes the corresponding `Customers` row, all inside a transaction. Commit on success and rollback on failure.

### Exercise 2: Insert order transaction
Create a procedure named `test` that inserts an order into `Orders`, retrieves `LAST_INSERT_ID()` into `order_id`, and inserts two `Order_Items` rows. Commit on success and rollback on failure.

### Exercise 3: Combine customers transaction
Create a procedure named `test` that selects the `Customers` row for `customer_id = 6` with `FOR UPDATE NOWAIT`, reassigns any order and address rows to `customer_id = 3`, then deletes the original customer. Commit or rollback as appropriate.

---

## Submission
Save your work in `module14_transactions.sql` and include a short `module14_notes.txt` summary.

**Deliverables:**
- `module14_transactions.sql`
- `module14_notes.txt`

**Grading rubric:**
- Correct transaction handling: 40%
- Proper row locking and update logic: 30%
- Clear comments and formatting: 15%
- Complete testing examples: 15%
