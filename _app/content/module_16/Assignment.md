# Module 16 Assignment: How to Create Triggers and Events

**Course:** SQL Essentials for the Real World
**Module:** 16 – How to Create Triggers and Events
**Learning Outcomes:**
- Create triggers for validation and auditing
- Automatically populate default values
- Record changes in an audit table
- Schedule cleanup with MySQL events

---

## Tasks
Write SQL scripts for these exercises.

### Exercise 1: `products_before_update`
Create a trigger named `products_before_update` that raises an error if `NEW.discount_percent` is less than 0 or greater than 100. If the value is between 0 and 1, multiply it by 100.

### Exercise 2: `products_before_insert`
Create a trigger named `products_before_insert` that sets `NEW.date_added` to the current date when it is null.

### Exercise 3: `Products_Audit` and `products_after_update`
Create a table named `Products_Audit` with all columns from `Products` except `description`, plus `audit_id` as primary key and `date_updated`. Create a trigger named `products_after_update` that writes the old row to the audit table after updates.

### Exercise 4: Daily cleanup event
Enable the event scheduler if needed, create a daily event that deletes `Products_Audit` rows older than 1 week, verify the event with `SHOW EVENTS`, then drop the event.

---

## Submission
Save your work in `module16_triggers_events.sql` and include a short `module16_notes.txt` summary.

**Deliverables:**
- `module16_triggers_events.sql`
- `module16_notes.txt`

**Grading rubric:**
- Correct triggers and audit logging: 40%
- Correct event scheduler automation: 25%
- Clear comments and testing: 15%
- Documentation: 20%
