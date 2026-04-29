# Module 6: Introduction to Database Administration

## Database Administrator Responsibilities
- User management: creating, modifying, and deleting users
- Privilege management: granting and revoking permissions
- System variables: configuring server behavior
- Backup and recovery: planning and executing backups

## Example: Creating a User
```sql
CREATE USER 'dba_user'@'localhost' IDENTIFIED BY 'securePass!';
GRANT ALL PRIVILEGES ON *.* TO 'dba_user'@'localhost' WITH GRANT OPTION;
```

## Example: Setting a System Variable
```sql
SET GLOBAL max_connections = 200;
```

---

For more examples, see the built-in examples in this repository. ch17/` and solutions in `the repository sample solutions and internal examples. /`.
