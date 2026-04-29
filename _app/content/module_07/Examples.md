# Module 7 Examples

## Example 1: Create User and Grant Privileges
```sql
CREATE USER 'security_admin'@'localhost' IDENTIFIED BY 'securePass!';
GRANT SELECT, UPDATE ON mydb.* TO 'security_admin'@'localhost';
```

## Example 2: Revoke Privileges
```sql
REVOKE UPDATE ON mydb.* FROM 'security_admin'@'localhost';
```

## Example 3: Security Best Practices
- Use strong passwords for all users
- Grant only necessary privileges
- Regularly review and audit user accounts

---

For more examples, see scripts in `the repository sample scripts contained in this module and the course materials. ` and solutions in `the repository sample solutions and internal examples. /`.