-- Module 8 submission: backup and restore commands
-- Exercise 1: Full backup using mysqldump
-- mysqldump -u root -p mydb > mydb_backup.sql

-- Exercise 2: Restore to a new database
-- mysql -u root -p -e "CREATE DATABASE mydb_restored;"
-- mysql -u root -p mydb_restored < mydb_backup.sql

-- Exercise 3: Recovery plan notes: see module08_notes.txt
