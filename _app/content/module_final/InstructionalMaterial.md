# Final Project Instructional Material

## What you will do
- Create an EER model for a download tracking database
- Export the model as SQL using MySQL Workbench
- Implement the `my_web_db` schema with UTF8MB4 and InnoDB
- Add sample data and join queries to validate the model

## Key design decisions
- Use surrogate primary keys for all dimension tables
- Enforce `NOT NULL` and length constraints on text fields
- Add indexes on foreign keys and frequent query fields
- Keep transaction work simple and verifiable
