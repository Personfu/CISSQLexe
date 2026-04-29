# Module 13 Assignment: Language Skills for Writing Stored Programs

**Course:** SQL Essentials for the Real World
**Module:** 13 – Language Skills for Writing Stored Programs
**Learning Outcomes:**
- Write stored procedures with variables and conditional logic
- Use cursors inside stored programs
- Handle SQL exceptions in stored procedures
- Return messages and result sets from stored procedures

---

## Tasks
Write SQL scripts that create and call stored procedures for each exercise.

### Exercise 1: Product count procedure
Create a procedure named `test` that counts the number of products in `Products`. If the count is greater than or equal to 7, display `The number of products is greater than or equal to 7`. Otherwise, display `The number of products is less than 7`.

### Exercise 2: Count and average procedure
Create a procedure named `test` that calculates the product count and average list price. If the count is greater than or equal to 7, display both values. Otherwise, display `The number of products is less than 7`.

### Exercise 3: Common factor procedure
Create a procedure named `test` that finds the common factors of 10 and 20 using modulo logic and returns a string such as `Common factors of 10 and 20: 1 2 5`.

### Exercise 4: Cursor procedure
Create a procedure named `test` that uses a cursor to process products with `list_price > 700`, ordered by list price descending. Build a string output formatted like `"Gibson SG","2517.00"|"Gibson Les Paul","1199.00"|`.

### Exercise 5: Insert category procedure with duplicate handling
Create a procedure named `test` that inserts `Guitars` into `Categories` and returns either `1 row was inserted.` or `Row was not inserted - duplicate entry.` depending on the result.

---

## Submission
Save your work in `module13_stored_programs.sql` and include a short `module13_notes.txt` summary.

**Deliverables:**
- `module13_stored_programs.sql`
- `module13_notes.txt`

**Grading rubric:**
- Correct stored procedure implementation: 45%
- Cursor and conditional logic: 25%
- Error handling and output: 15%
- Documentation and testing: 15%
