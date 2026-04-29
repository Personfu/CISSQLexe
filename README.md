# CISSQL.exe — SQL Essentials for the Real World

A self-contained Windows desktop **higher-education learning platform** that teaches SQL through 17 modules + a final capstone project. Built from the **[CIS-sql-essentials](https://github.com/Personfu/CIS-sql-essentials)** course curriculum and packaged into a single portable executable.

## Quick Start

1. Download **[`CISSQL.exe`](CISSQL.exe)** from this repository.
2. Double-click. No install, no Python, no admin needed.
3. Enroll with your name on the welcome screen and start Module 0.

> Progress is saved to `%APPDATA%\CISSQL` (Windows). Delete that folder to reset your transcript.

## What's Inside

| Feature | Detail |
|---|---|
| **17 modules + capstone** | Module 0 (Orientation) → Module 16 (Triggers/Events) → Final Project (`my_web_db`) |
| **Per-module content** | Overview, Instructional Material, Examples, Assignment, Quiz, Reflections, Notes, Lab.sql |
| **Embedded SQL Lab** | SQLite engine with MySQL-flavored syntax rewriting; persistent across sessions |
| **Auto-grader** | Per-module rule checks (e.g., requires `JOIN`, `WHERE`, `GROUP BY`, `CREATE VIEW`, etc.) |
| **Progress tracking** | Completed modules, XP per module, achievements, last-submitted SQL per module |
| **Transcript** | In-app transcript view + export to `.txt` |
| **Bonus reference** | SQL cheat sheet, compliance SQL, FLLC security labs (injection, forensics, hardening, AI detection, privesc, exfiltration) |
| **Dashboard** | KPI cards (modules, XP, %, achievements), course-path grid, achievement pills |

## Course Modules

| # | Module | XP |
|---|---|---|
| 0 | Course Orientation | 5 |
| 1 | Relational Databases & Schema Design | 10 |
| 2 | MySQL Workbench & Database Setup | 10 |
| 3 | Retrieving Data From a Single Table | 15 |
| 4 | Joining Multiple Tables | 20 |
| 5 | Insert, Update, Delete (DML) | 15 |
| 6 | Basic Database Administration | 10 |
| 7 | Database Security & Privileges | 15 |
| 8 | Backup & Restore | 10 |
| 9 | Summary Queries & Aggregation | 15 |
| 10 | Subqueries & Correlated Queries | 20 |
| 11 | Data Types & Constraints | 15 |
| 12 | Views & Logical Presentation | 15 |
| 13 | Stored Programs | 20 |
| 14 | Transactions & Locking | 15 |
| 15 | Functions & Stored Procedures | 20 |
| 16 | Triggers & Scheduled Events | 20 |
| Final | Capstone — `my_web_db` | 50 |

**Total available: 280 XP**

## Cross-Referenced Progress

The app tracks each user's progress against the source curriculum:

- **Per-module completion**: Pass automated checks (or manual submit when no checks defined) → module is marked complete and XP is awarded.
- **Submission cache**: The last SQL you submitted is stored per module (`progress.json` → `submissions`), restored when you revisit the module.
- **Achievements** (auto-granted): *First Query Fired, SQL Apprentice, Query Smith, Schema Architect, Capstone Complete, Centurion XP, Maxed Out*.
- **Transcript export**: Generates a plain-text transcript with student name, start date, modules complete, XP, and achievements — ready to submit to an instructor.

All state lives in `%APPDATA%\CISSQL\progress.json` and a persistent SQLite playground in `%APPDATA%\CISSQL\session.db`.

## Build From Source

Requires Python 3.10+ on Windows. Run `BUILD_CISSQL_EXE.bat` from the repo root — it installs PyInstaller and produces `CISSQL.exe` (single-file, windowed, ~12 MB).

```bat
BUILD_CISSQL_EXE.bat
```

To run from source without building:

```bat
python _app\cis_sql_course.py
```

## Source Curriculum

The course content (modules, assignments, quizzes, labs, reflections) is bundled inside `_app/content/` and is derived from [Personfu/CIS-sql-essentials](https://github.com/Personfu/CIS-sql-essentials).

## Repo Layout

```
CISSQL.exe                  ← the standalone Windows binary
BUILD_CISSQL_EXE.bat        ← rebuild from source
_app/
  cis_sql_course.py         ← single-file Tk application
  requirements.txt          ← (just pyinstaller — app uses stdlib only)
  content/                  ← markdown modules + Lab.sql + manifest
    manifest.json
    module_00 .. module_16/ ← Overview/Material/Examples/Assignment/Quiz/Reflections/Notes/Lab.sql
    module_final/
    _bonus/                 ← cheat sheets + FLLC security labs
```

## License & Credits

Course content authored by **Personfu / FLLC** for the *SQL Essentials for the Real World* microcourse. Application packaging by the same. Stdlib-only Python (Tkinter + SQLite); no third-party runtime dependencies.
