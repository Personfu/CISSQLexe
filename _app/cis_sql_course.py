"""
CIS SQL Essentials — Desktop Learning Platform
==============================================
A self-contained higher-education-style learning platform that walks a
student through Modules 0–16 plus the Final Project of the FLLC
"SQL Essentials for the Real World" course.

Run from source:
    python cis_sql_course.py

Build a Windows .exe:
    pip install pyinstaller
    build.bat

Author:   Personfu / FLLC
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import textwrap
import threading
import time
import tkinter as tk
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, Dict, List, Optional, Tuple


# --------------------------------------------------------------------------- #
#                              PATHS & PERSISTENCE                            #
# --------------------------------------------------------------------------- #

APP_NAME = "CISSQL"
APP_VERSION = "1.0.0"


def app_root() -> Path:
    """Return directory holding bundled assets (works both for PyInstaller and source)."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).parent.resolve()


def user_data_dir() -> Path:
    base = os.environ.get("APPDATA") or os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local/share")
    p = Path(base) / APP_NAME
    p.mkdir(parents=True, exist_ok=True)
    return p


CONTENT_DIR = app_root() / "content"
PROGRESS_FILE = user_data_dir() / "progress.json"
SESSION_DB = user_data_dir() / "session.db"  # student's persistent SQLite playground


# --------------------------------------------------------------------------- #
#                                THEME / COLORS                               #
# --------------------------------------------------------------------------- #

class Theme:
    """Dark academic theme — a little NASA console, a little LMS."""
    bg          = "#0B1220"
    bg_alt      = "#11192C"
    panel       = "#16213E"
    panel_alt   = "#1B2747"
    rail        = "#0E1729"
    border      = "#243154"
    text        = "#E5ECFB"
    text_dim    = "#9AAAC9"
    text_muted  = "#6E7FA0"
    accent      = "#4FC3F7"   # cyan headline
    accent_2    = "#7B61FF"   # purple
    success     = "#3EDC81"
    warn        = "#FFB454"
    danger      = "#FF5C7A"
    code_bg     = "#0A1322"
    code_text   = "#D2DCF5"
    keyword     = "#7B61FF"
    string      = "#3EDC81"
    number      = "#FFB454"
    comment     = "#6E7FA0"
    badge_bg    = "#1F3357"
    badge_fg    = "#A6CFFB"
    chip_done   = "#10381F"
    chip_done_fg= "#3EDC81"
    chip_now    = "#1B2A52"
    chip_now_fg = "#4FC3F7"
    chip_lock   = "#1A1F31"
    chip_lock_fg= "#6E7FA0"

    font_ui     = ("Segoe UI", 10)
    font_ui_b   = ("Segoe UI Semibold", 10)
    font_h1     = ("Segoe UI", 22, "bold")
    font_h2     = ("Segoe UI", 16, "bold")
    font_h3     = ("Segoe UI", 13, "bold")
    font_code   = ("Consolas", 11)
    font_code_b = ("Consolas", 11, "bold")


# --------------------------------------------------------------------------- #
#                              MODULE METADATA                                #
# --------------------------------------------------------------------------- #

MODULE_META = [
    ("module_00", "Module 0",  "Course Orientation",                     5),
    ("module_01", "Module 1",  "Relational Databases & Schema Design",  10),
    ("module_02", "Module 2",  "MySQL Workbench & Database Setup",      10),
    ("module_03", "Module 3",  "Retrieving Data From a Single Table",   15),
    ("module_04", "Module 4",  "Joining Multiple Tables",               20),
    ("module_05", "Module 5",  "Insert, Update, Delete (DML)",          15),
    ("module_06", "Module 6",  "Basic Database Administration",         10),
    ("module_07", "Module 7",  "Database Security & Privileges",        15),
    ("module_08", "Module 8",  "Backup & Restore",                      10),
    ("module_09", "Module 9",  "Summary Queries & Aggregation",         15),
    ("module_10", "Module 10", "Subqueries & Correlated Queries",       20),
    ("module_11", "Module 11", "Data Types & Constraints",              15),
    ("module_12", "Module 12", "Views & Logical Presentation",          15),
    ("module_13", "Module 13", "Stored Programs",                       20),
    ("module_14", "Module 14", "Transactions & Locking",                15),
    ("module_15", "Module 15", "Functions & Stored Procedures",         20),
    ("module_16", "Module 16", "Triggers & Scheduled Events",           20),
    ("module_final", "Final",  "Final Project — my_web_db",             50),
]
MODULE_IDS  = [m[0] for m in MODULE_META]
MODULE_INDEX = {m[0]: i for i, m in enumerate(MODULE_META)}


# --------------------------------------------------------------------------- #
#                            AUTOGRADER RULES                                 #
# --------------------------------------------------------------------------- #
#
# For each module we define an ordered list of "checks". A check is a callable
# that takes (sql_text, last_results, last_error) and returns (passed, message).
# A module passes when ALL its checks return True.

@dataclass
class CheckResult:
    passed: bool
    message: str


def _has(sql: str, *patterns: str) -> bool:
    s = sql.lower()
    return all(re.search(p, s, re.IGNORECASE | re.DOTALL) for p in patterns)


def _result_contains(rows, needle: str) -> bool:
    if not rows: return False
    return any(needle.lower() in str(c).lower() for r in rows for c in r)


CHECKS: Dict[str, List[Tuple[str, Callable]]] = {
    "module_00": [
        ("Run the smoke-test SELECT and return 'Ready for SQL Essentials'",
         lambda sql, rows, err: CheckResult(_result_contains(rows, "ready for sql essentials"),
            "Run: SELECT 'Ready for SQL Essentials' AS status;")),
    ],
    "module_01": [
        ("Create a Products table with primary key",
         lambda sql, rows, err: CheckResult(_has(sql, r"create\s+table\s+products?", r"primary\s+key"),
            "CREATE TABLE Products with a PRIMARY KEY")),
        ("Reference customer_id with a FOREIGN KEY",
         lambda sql, rows, err: CheckResult(_has(sql, r"foreign\s+key"),
            "Add a FOREIGN KEY referencing customer_id")),
    ],
    "module_02": [
        ("Issue a DDL statement (CREATE / DROP / USE / SHOW)",
         lambda sql, rows, err: CheckResult(
            _has(sql, r"\b(create|drop|use|show)\b"),
            "Try: SHOW TABLES; or CREATE DATABASE workbench_demo;")),
    ],
    "module_03": [
        ("Use SELECT ... FROM ...",
         lambda sql, rows, err: CheckResult(_has(sql, r"select", r"from"), "SELECT … FROM …")),
        ("Filter results with WHERE",
         lambda sql, rows, err: CheckResult(_has(sql, r"where"), "Add a WHERE clause")),
        ("Sort results with ORDER BY",
         lambda sql, rows, err: CheckResult(_has(sql, r"order\s+by"), "Add ORDER BY")),
    ],
    "module_04": [
        ("Use an INNER or implicit JOIN",
         lambda sql, rows, err: CheckResult(_has(sql, r"\bjoin\b"), "Use JOIN")),
        ("Show a LEFT JOIN somewhere",
         lambda sql, rows, err: CheckResult(_has(sql, r"\bleft\s+join\b"), "Demonstrate LEFT JOIN")),
    ],
    "module_05": [
        ("INSERT data",  lambda sql, rows, err: CheckResult(_has(sql, r"\binsert\s+into\b"), "INSERT INTO …")),
        ("UPDATE data",  lambda sql, rows, err: CheckResult(_has(sql, r"\bupdate\b\s+\w+\s+set"), "UPDATE … SET …")),
        ("DELETE data",  lambda sql, rows, err: CheckResult(_has(sql, r"\bdelete\s+from\b"), "DELETE FROM …")),
    ],
    "module_06": [
        ("Inspect schema with SHOW or sqlite_master",
         lambda sql, rows, err: CheckResult(
            _has(sql, r"(show\s+tables|sqlite_master|pragma\s+table_info)"),
            "Try: SELECT name FROM sqlite_master WHERE type='table';")),
    ],
    "module_07": [
        ("Demonstrate GRANT / REVOKE / role syntax",
         lambda sql, rows, err: CheckResult(_has(sql, r"\b(grant|revoke|role|privilege)\b"),
            "Use GRANT / REVOKE / CREATE ROLE")),
    ],
    "module_08": [
        ("Reference backup or restore concept",
         lambda sql, rows, err: CheckResult(_has(sql, r"(backup|mysqldump|restore|\.dump|attach|detach)"),
            "Mention BACKUP / RESTORE / mysqldump")),
    ],
    "module_09": [
        ("Use an aggregate function",
         lambda sql, rows, err: CheckResult(_has(sql, r"\b(count|sum|avg|min|max)\s*\("),
            "Use COUNT/SUM/AVG/MIN/MAX")),
        ("Use GROUP BY",
         lambda sql, rows, err: CheckResult(_has(sql, r"group\s+by"), "Add GROUP BY")),
    ],
    "module_10": [
        ("Use a subquery",
         lambda sql, rows, err: CheckResult(bool(re.search(r"select.*\(\s*select", sql, re.IGNORECASE | re.DOTALL)),
            "Embed (SELECT …) inside another query")),
    ],
    "module_11": [
        ("Use NOT NULL or UNIQUE or CHECK or DEFAULT",
         lambda sql, rows, err: CheckResult(_has(sql, r"(not\s+null|unique|check\s*\(|default\s)"),
            "Add a NOT NULL / UNIQUE / CHECK / DEFAULT constraint")),
    ],
    "module_12": [
        ("Create a VIEW",
         lambda sql, rows, err: CheckResult(_has(sql, r"create\s+view"), "CREATE VIEW some_view AS SELECT …")),
    ],
    "module_13": [
        ("Reference a stored program / procedure",
         lambda sql, rows, err: CheckResult(_has(sql, r"(procedure|trigger|function|begin|end)"),
            "Use a PROCEDURE / FUNCTION / TRIGGER")),
    ],
    "module_14": [
        ("Use BEGIN/COMMIT (or ROLLBACK)",
         lambda sql, rows, err: CheckResult(_has(sql, r"(begin|commit|rollback)"),
            "Wrap statements in BEGIN … COMMIT;")),
    ],
    "module_15": [
        ("Define a function or procedure",
         lambda sql, rows, err: CheckResult(_has(sql, r"create\s+(function|procedure)"),
            "CREATE FUNCTION or CREATE PROCEDURE")),
    ],
    "module_16": [
        ("Reference a TRIGGER or EVENT",
         lambda sql, rows, err: CheckResult(_has(sql, r"create\s+(trigger|event)"),
            "CREATE TRIGGER … or CREATE EVENT …")),
    ],
    "module_final": [
        ("Create the my_web_db tables (users, products, downloads)",
         lambda sql, rows, err: CheckResult(
            _has(sql, r"create\s+table\s+users") and
            _has(sql, r"create\s+table\s+products") and
            _has(sql, r"create\s+table\s+downloads"),
            "CREATE TABLE users / products / downloads")),
        ("Define foreign keys on downloads",
         lambda sql, rows, err: CheckResult(_has(sql, r"foreign\s+key.*references\s+users",
                                                  r"foreign\s+key.*references\s+products"),
            "Both FOREIGN KEYs on downloads (users + products)")),
        ("Insert sample data into all three tables",
         lambda sql, rows, err: CheckResult(
            _has(sql, r"insert\s+into\s+users") and
            _has(sql, r"insert\s+into\s+products") and
            _has(sql, r"insert\s+into\s+downloads"),
            "INSERT INTO users / products / downloads")),
        ("Join the three tables sorted by email DESC, product ASC",
         lambda sql, rows, err: CheckResult(
            _has(sql, r"join.*users", r"join.*products",
                 r"order\s+by\s+(u\.)?email\s+desc"),
            "Final reporting JOIN sorted by email DESC, product ASC")),
        ("ALTER products to add price and date_added",
         lambda sql, rows, err: CheckResult(_has(sql, r"alter\s+table\s+products", r"price", r"date_added"),
            "ALTER TABLE products ADD price + date_added")),
        ("ALTER users.first_name to NOT NULL VARCHAR(20)",
         lambda sql, rows, err: CheckResult(_has(sql, r"alter\s+table\s+users", r"first_name", r"varchar\s*\(\s*20"),
            "ALTER TABLE users MODIFY first_name VARCHAR(20) NOT NULL")),
    ],
}


# --------------------------------------------------------------------------- #
#                          SQL EXECUTION SANDBOX                              #
# --------------------------------------------------------------------------- #

class SQLSandbox:
    """
    A persistent SQLite database that translates a few common MySQL-isms
    so course exercises mostly work as written.
    """

    MYSQL_REWRITES = [
        # SQLite requires `INTEGER PRIMARY KEY AUTOINCREMENT` exactly
        (re.compile(r"\b(INT|INTEGER|BIGINT|SMALLINT|TINYINT|MEDIUMINT)\s+AUTO_INCREMENT\s+PRIMARY\s+KEY\b", re.IGNORECASE),
            "INTEGER PRIMARY KEY AUTOINCREMENT"),
        (re.compile(r"\b(INT|INTEGER|BIGINT|SMALLINT|TINYINT|MEDIUMINT)\s+PRIMARY\s+KEY\s+AUTO_INCREMENT\b", re.IGNORECASE),
            "INTEGER PRIMARY KEY AUTOINCREMENT"),
        (re.compile(r"\bAUTO_INCREMENT\b", re.IGNORECASE),                ""),
        (re.compile(r"\bENGINE\s*=\s*\w+\s*", re.IGNORECASE),             ""),
        (re.compile(r"\bDEFAULT\s+CHARACTER\s+SET\s*=?\s*\w+", re.I),     ""),
        (re.compile(r"\bCHARACTER\s+SET\s+\w+", re.I),                    ""),
        (re.compile(r"\bCOLLATE\s+\w+", re.I),                            ""),
        (re.compile(r"\bUNSIGNED\b", re.IGNORECASE),                      ""),
        (re.compile(r"\bSHOW\s+TABLES\s*;?", re.IGNORECASE),
            "SELECT name AS Tables FROM sqlite_master WHERE type='table' ORDER BY name;"),
        (re.compile(r"\bSHOW\s+DATABASES\s*;?", re.IGNORECASE),
            "SELECT 'main' AS Database;"),
        (re.compile(r"\bUSE\s+\w+\s*;?", re.IGNORECASE),                  ""),
        (re.compile(r"\bDROP\s+DATABASE\s+(IF\s+EXISTS\s+)?\w+\s*;?", re.IGNORECASE), ""),
        (re.compile(r"\bCREATE\s+DATABASE\s+(IF\s+NOT\s+EXISTS\s+)?\w+\s*;?", re.IGNORECASE), ""),
        (re.compile(r"\bNOW\s*\(\s*\)", re.IGNORECASE),                   "CURRENT_TIMESTAMP"),
        (re.compile(r"\bDATETIME\b", re.IGNORECASE),                      "TEXT"),
        (re.compile(r"\bDECIMAL\s*\([^)]*\)", re.IGNORECASE),             "REAL"),
        (re.compile(r"\bVARCHAR\s*\([^)]*\)", re.IGNORECASE),             "TEXT"),
    ]

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._seed_if_empty()

    def _seed_if_empty(self):
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        if "Customers" in tables:
            return
        cur.executescript("""
        CREATE TABLE Customers (
            customer_id INTEGER PRIMARY KEY,
            first_name  TEXT NOT NULL,
            last_name   TEXT NOT NULL,
            email       TEXT UNIQUE
        );
        CREATE TABLE Products (
            product_id   INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            price        REAL NOT NULL,
            category     TEXT
        );
        CREATE TABLE Orders (
            order_id     INTEGER PRIMARY KEY,
            customer_id  INTEGER NOT NULL,
            order_date   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            total_amount REAL,
            FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        );
        CREATE TABLE Order_Items (
            order_id   INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            qty        INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (order_id, product_id),
            FOREIGN KEY (order_id)   REFERENCES Orders(order_id),
            FOREIGN KEY (product_id) REFERENCES Products(product_id)
        );

        INSERT INTO Customers VALUES
            (1,'Cassandra','Lee','cassandra@example.com'),
            (2,'Andrew','Scott','andrew@example.com'),
            (3,'Maria','Hernandez','maria@example.com'),
            (4,'Devon','Walker','devon@example.com');

        INSERT INTO Products VALUES
            (101,'Business Intelligence Guide',  49.99,'eBook'),
            (102,'Advanced SQL Video Course',   199.00,'Video'),
            (103,'Database Design Workbook',     29.99,'eBook'),
            (104,'PostgreSQL for Pros',         149.00,'Video'),
            (105,'MySQL Admin Cheatsheet',        9.99,'Reference');

        INSERT INTO Orders (order_id,customer_id,total_amount) VALUES
            (1001,1, 248.99),
            (1002,2,  49.99),
            (1003,2, 159.00),
            (1004,3, 179.99),
            (1005,4,   9.99);

        INSERT INTO Order_Items VALUES
            (1001,101,1),(1001,102,1),
            (1002,101,1),
            (1003,104,1),(1003,105,1),
            (1004,103,2),(1004,105,2),
            (1005,105,1);
        """)
        self.conn.commit()

    def reset(self):
        self.conn.close()
        try: self.db_path.unlink()
        except Exception: pass
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self._seed_if_empty()

    def execute(self, sql: str) -> Tuple[List[str], List[List], Optional[str]]:
        """
        Run one-or-many statements. Returns (columns, rows, error). On success
        we return the *last* SELECT result (or affected-row counts if no SELECT).
        """
        translated = sql
        for pat, repl in self.MYSQL_REWRITES:
            translated = pat.sub(repl, translated)

        # Split on ; while respecting strings — best-effort: collect errors
        # but keep running so a single MySQL-only quirk doesn't kill the run.
        statements = self._split_sql(translated)
        cur = self.conn.cursor()
        executed = 0
        errors: List[str] = []
        select_cols: Optional[List[str]] = None
        select_rows: Optional[List[List]] = None
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                cur.execute(stmt)
                executed += 1
                if cur.description:  # SELECT
                    select_cols = [d[0] for d in cur.description]
                    select_rows = [list(r) for r in cur.fetchall()]
            except Exception as ex:
                preview = re.sub(r"\s+", " ", stmt)[:80]
                errors.append(f"{type(ex).__name__}: {ex}  ⟶  {preview}")
        try:
            self.conn.commit()
        except Exception:
            self.conn.rollback()

        err_text = ("\n".join(f" • {e}" for e in errors)) if errors else None
        if select_cols is not None:
            return select_cols, select_rows or [], err_text
        if executed == 0 and errors:
            return ["status"], [], err_text
        msg = f"Executed {executed} statement(s) successfully."
        if errors: msg += f"  ({len(errors)} statement(s) skipped — see Console)"
        return ["status"], [[msg]], err_text

    @staticmethod
    def _split_sql(sql: str) -> List[str]:
        out, buf, in_s, in_d = [], [], False, False
        for ch in sql:
            if ch == "'" and not in_d: in_s = not in_s
            elif ch == '"' and not in_s: in_d = not in_d
            if ch == ";" and not in_s and not in_d:
                out.append("".join(buf)); buf = []
            else:
                buf.append(ch)
        tail = "".join(buf).strip()
        if tail: out.append(tail)
        return out


# --------------------------------------------------------------------------- #
#                              PROGRESS STORE                                 #
# --------------------------------------------------------------------------- #

@dataclass
class Progress:
    student_name: str = ""
    started_at:  str = ""
    last_module: str = "module_00"
    completed:   List[str] = field(default_factory=list)
    xp:          int = 0
    achievements: List[str] = field(default_factory=list)
    submissions: Dict[str, str] = field(default_factory=dict)  # module_id -> last submitted SQL

    def is_done(self, mid: str) -> bool:
        return mid in self.completed

    def mark_done(self, mid: str, xp: int) -> bool:
        if mid in self.completed:
            return False
        self.completed.append(mid)
        self.xp += xp
        return True

    def percent_complete(self) -> int:
        return round(100 * len(self.completed) / max(1, len(MODULE_META)))


def load_progress() -> Progress:
    if PROGRESS_FILE.exists():
        try:
            data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
            return Progress(**{k: data.get(k, getattr(Progress(), k)) for k in Progress().__dict__})
        except Exception:
            pass
    return Progress()


def save_progress(p: Progress):
    PROGRESS_FILE.write_text(json.dumps(asdict(p), indent=2), encoding="utf-8")


# --------------------------------------------------------------------------- #
#                              CONTENT LOADER                                 #
# --------------------------------------------------------------------------- #

def load_content(mid: str) -> Dict[str, str]:
    base = CONTENT_DIR / mid
    out = {}
    for fname in ("Overview.md", "InstructionalMaterial.md", "Assignment.md",
                  "Quiz.md", "Reflections.md", "Examples.md", "Notes.txt", "Lab.sql"):
        p = base / fname
        out[fname] = p.read_text(encoding="utf-8") if p.exists() else ""
    return out


def load_bonus() -> Dict[str, str]:
    base = CONTENT_DIR / "_bonus"
    if not base.is_dir(): return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(base.iterdir()) if p.is_file()}


# --------------------------------------------------------------------------- #
#                            MARKDOWN RENDERER                                #
# --------------------------------------------------------------------------- #

class MarkdownRenderer:
    """Lightweight markdown renderer for tk.Text — supports headings, lists,
       code fences, inline code, bold and links (rendered as text)."""

    def __init__(self, text: tk.Text):
        self.text = text
        self._tag_setup()

    def _tag_setup(self):
        T = self.text
        T.tag_configure("h1", font=Theme.font_h1, foreground=Theme.accent, spacing1=12, spacing3=8)
        T.tag_configure("h2", font=Theme.font_h2, foreground=Theme.text,    spacing1=10, spacing3=6)
        T.tag_configure("h3", font=Theme.font_h3, foreground=Theme.text,    spacing1=8,  spacing3=4)
        T.tag_configure("p",  font=Theme.font_ui, foreground=Theme.text,    spacing3=6, lmargin1=2, lmargin2=2)
        T.tag_configure("li", font=Theme.font_ui, foreground=Theme.text,    spacing1=2, lmargin1=18, lmargin2=32)
        T.tag_configure("li_marker", font=Theme.font_ui_b, foreground=Theme.accent)
        T.tag_configure("bold", font=("Segoe UI", 10, "bold"), foreground=Theme.text)
        T.tag_configure("hr", foreground=Theme.border, spacing1=10, spacing3=10)
        T.tag_configure("inline_code", font=Theme.font_code, background=Theme.code_bg, foreground=Theme.code_text)
        T.tag_configure("code_block", font=Theme.font_code, background=Theme.code_bg, foreground=Theme.code_text,
                        lmargin1=14, lmargin2=14, rmargin=14, spacing1=6, spacing3=6,
                        relief="flat", borderwidth=0)
        T.tag_configure("link", foreground=Theme.accent, underline=True)

    def render(self, md: str):
        T = self.text
        T.config(state="normal")
        T.delete("1.0", "end")
        if not md:
            T.insert("end", "(no content)\n", ("p",))
            T.config(state="disabled"); return

        in_code = False
        code_lang = ""
        code_buf: List[str] = []
        for raw in md.splitlines():
            line = raw.rstrip("\n")
            if line.strip().startswith("```"):
                if not in_code:
                    in_code = True
                    code_lang = line.strip()[3:].strip()
                    code_buf = []
                else:
                    in_code = False
                    code = "\n".join(code_buf) + "\n"
                    self._insert_code(code)
                    code_buf = []
                continue
            if in_code:
                code_buf.append(line)
                continue
            if not line.strip():
                T.insert("end", "\n")
                continue
            if line.startswith("# "):
                T.insert("end", line[2:].strip() + "\n", ("h1",)); continue
            if line.startswith("## "):
                T.insert("end", line[3:].strip() + "\n", ("h2",)); continue
            if line.startswith("### "):
                T.insert("end", line[4:].strip() + "\n", ("h3",)); continue
            if line.strip() == "---":
                T.insert("end", "─" * 60 + "\n", ("hr",)); continue
            stripped = line.lstrip()
            if stripped.startswith(("- ", "* ", "+ ")):
                indent = len(line) - len(stripped)
                T.insert("end", " " * indent, ("li",))
                T.insert("end", "•  ", ("li_marker",))
                self._insert_inline(stripped[2:])
                T.insert("end", "\n")
                continue
            m = re.match(r"^(\d+)\.\s+(.*)$", stripped)
            if m:
                T.insert("end", "  ", ("li",))
                T.insert("end", f"{m.group(1)}.  ", ("li_marker",))
                self._insert_inline(m.group(2))
                T.insert("end", "\n")
                continue
            self._insert_inline(line)
            T.insert("end", "\n", ("p",))
        T.config(state="disabled")

    def _insert_inline(self, line: str):
        T = self.text
        # Tokens: **bold**, `code`, [text](url)
        pattern = re.compile(r"(\*\*[^\*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")
        pos = 0
        for m in pattern.finditer(line):
            T.insert("end", line[pos:m.start()], ("p",))
            tok = m.group(0)
            if tok.startswith("**"):
                T.insert("end", tok[2:-2], ("bold",))
            elif tok.startswith("`"):
                T.insert("end", " " + tok[1:-1] + " ", ("inline_code",))
            elif tok.startswith("["):
                lm = re.match(r"\[([^\]]+)\]\(([^)]+)\)", tok)
                if lm:
                    T.insert("end", lm.group(1), ("link",))
            pos = m.end()
        T.insert("end", line[pos:], ("p",))

    def _insert_code(self, code: str):
        T = self.text
        T.insert("end", code, ("code_block",))


# --------------------------------------------------------------------------- #
#                             SQL EDITOR WIDGET                               #
# --------------------------------------------------------------------------- #

class SQLEditor(tk.Text):
    KEYWORDS = (
        "select","from","where","and","or","not","in","like","between","order","by","group","having",
        "limit","offset","insert","into","values","update","set","delete","create","table","drop",
        "alter","add","modify","column","primary","key","foreign","references","unique","default",
        "null","check","auto_increment","engine","innodb","char","varchar","text","int","integer",
        "decimal","date","datetime","timestamp","boolean","join","inner","left","right","outer","on",
        "as","case","when","then","else","end","union","all","distinct","exists","is","procedure",
        "function","trigger","view","grant","revoke","commit","rollback","begin","transaction",
        "show","tables","databases","use","describe","explain","truncate","index","with",
    )

    def __init__(self, master, **kw):
        super().__init__(master, undo=True, wrap="none",
                         bg=Theme.code_bg, fg=Theme.code_text,
                         insertbackground=Theme.accent,
                         selectbackground=Theme.accent_2, selectforeground="#FFFFFF",
                         font=Theme.font_code, padx=10, pady=10,
                         borderwidth=0, highlightthickness=0, **kw)
        self.tag_configure("kw",      foreground=Theme.keyword, font=Theme.font_code_b)
        self.tag_configure("string",  foreground=Theme.string)
        self.tag_configure("number",  foreground=Theme.number)
        self.tag_configure("comment", foreground=Theme.comment, font=("Consolas", 11, "italic"))
        self.bind("<KeyRelease>", lambda e: self._highlight())
        self.bind("<<Modified>>", lambda e: self._on_modified())
        self.bind("<Tab>", self._tab_insert)

    def _tab_insert(self, _evt):
        self.insert("insert", "    ")
        return "break"

    def _on_modified(self):
        self.edit_modified(False)
        self._highlight()

    def _highlight(self):
        for tag in ("kw","string","number","comment"):
            self.tag_remove(tag, "1.0", "end")
        text = self.get("1.0", "end-1c")
        # comments
        for m in re.finditer(r"--[^\n]*", text):
            self._tag_range("comment", m.start(), m.end())
        for m in re.finditer(r"/\*.*?\*/", text, re.DOTALL):
            self._tag_range("comment", m.start(), m.end())
        # strings
        for m in re.finditer(r"'(?:''|[^'])*'", text):
            self._tag_range("string", m.start(), m.end())
        # numbers
        for m in re.finditer(r"\b\d+(?:\.\d+)?\b", text):
            self._tag_range("number", m.start(), m.end())
        # keywords
        kw_pat = r"\b(" + "|".join(self.KEYWORDS) + r")\b"
        for m in re.finditer(kw_pat, text, re.IGNORECASE):
            self._tag_range("kw", m.start(), m.end())

    def _tag_range(self, tag, start, end):
        self.tag_add(tag, f"1.0+{start}c", f"1.0+{end}c")

    def set_text(self, s: str):
        self.delete("1.0", "end")
        self.insert("1.0", s)
        self._highlight()


# --------------------------------------------------------------------------- #
#                              MAIN APPLICATION                               #
# --------------------------------------------------------------------------- #

class CISCourseApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title(f"CISSQL — SQL Essentials for the Real World  •  v{APP_VERSION}")
        self.geometry("1380x880")
        self.minsize(1180, 720)
        self.configure(bg=Theme.bg)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self._setup_ttk_style()

        self.progress = load_progress()
        self.sandbox = SQLSandbox(SESSION_DB)
        self.current_module: str = self.progress.last_module or "module_00"
        self.last_run_rows: List[List] = []
        self.last_run_error: Optional[str] = None
        self._toast_jobs: List[str] = []

        if not self.progress.student_name:
            self._launch_onboarding()
        else:
            self._build_app()

    # -------------------- ttk style ------------------------------------- #
    def _setup_ttk_style(self):
        st = ttk.Style(self)
        try: st.theme_use("clam")
        except Exception: pass
        st.configure(".", background=Theme.bg, foreground=Theme.text, font=Theme.font_ui)
        st.configure("TFrame", background=Theme.bg)
        st.configure("Panel.TFrame", background=Theme.panel)
        st.configure("Rail.TFrame", background=Theme.rail)
        st.configure("PanelAlt.TFrame", background=Theme.panel_alt)
        st.configure("TLabel", background=Theme.bg, foreground=Theme.text)
        st.configure("Panel.TLabel", background=Theme.panel, foreground=Theme.text)
        st.configure("Rail.TLabel", background=Theme.rail, foreground=Theme.text)
        st.configure("Dim.TLabel", background=Theme.bg, foreground=Theme.text_dim)
        st.configure("PanelDim.TLabel", background=Theme.panel, foreground=Theme.text_dim)
        st.configure("RailDim.TLabel", background=Theme.rail, foreground=Theme.text_dim)
        st.configure("H1.TLabel", background=Theme.panel, foreground=Theme.accent, font=Theme.font_h1)
        st.configure("H2.TLabel", background=Theme.panel, foreground=Theme.text,   font=Theme.font_h2)
        st.configure("H3.TLabel", background=Theme.panel, foreground=Theme.text,   font=Theme.font_h3)
        st.configure("Bold.TLabel", background=Theme.panel, foreground=Theme.text, font=Theme.font_ui_b)
        st.configure("Accent.TButton", background=Theme.accent, foreground="#0B1220",
                     borderwidth=0, focusthickness=0, padding=(14, 8),
                     font=Theme.font_ui_b)
        st.map("Accent.TButton", background=[("active", "#7AD8FF"), ("disabled", "#456")],
                                  foreground=[("disabled", "#789")])
        st.configure("Ghost.TButton", background=Theme.panel, foreground=Theme.text,
                     borderwidth=1, padding=(12, 7), focusthickness=0)
        st.map("Ghost.TButton", background=[("active", Theme.panel_alt)])
        st.configure("Run.TButton", background=Theme.success, foreground="#06281A",
                     borderwidth=0, padding=(14, 8), font=Theme.font_ui_b, focusthickness=0)
        st.map("Run.TButton", background=[("active", "#5CE89B")])
        st.configure("Submit.TButton", background=Theme.accent_2, foreground="#FFFFFF",
                     borderwidth=0, padding=(14, 8), font=Theme.font_ui_b, focusthickness=0)
        st.map("Submit.TButton", background=[("active", "#9D86FF")])
        st.configure("Reset.TButton", background=Theme.warn, foreground="#1A1006",
                     borderwidth=0, padding=(10, 6), font=Theme.font_ui_b, focusthickness=0)
        st.configure("Treeview", background=Theme.code_bg, fieldbackground=Theme.code_bg,
                     foreground=Theme.code_text, rowheight=24, borderwidth=0,
                     font=("Consolas", 10))
        st.configure("Treeview.Heading", background=Theme.panel_alt, foreground=Theme.accent,
                     font=Theme.font_ui_b, relief="flat")
        st.map("Treeview.Heading", background=[("active", Theme.panel_alt)])
        st.configure("TNotebook", background=Theme.bg, borderwidth=0)
        st.configure("TNotebook.Tab", background=Theme.panel, foreground=Theme.text_dim,
                     padding=(18, 8), font=Theme.font_ui_b, borderwidth=0)
        st.map("TNotebook.Tab",
               background=[("selected", Theme.panel_alt), ("active", Theme.panel_alt)],
               foreground=[("selected", Theme.accent), ("active", Theme.text)])
        st.configure("Course.Horizontal.TProgressbar",
                     background=Theme.accent, troughcolor=Theme.panel_alt,
                     bordercolor=Theme.panel_alt, lightcolor=Theme.accent,
                     darkcolor=Theme.accent, thickness=16)

    # -------------------- onboarding ------------------------------------ #
    def _launch_onboarding(self):
        for w in self.winfo_children(): w.destroy()
        wrap = tk.Frame(self, bg=Theme.bg)
        wrap.pack(expand=True, fill="both")
        center = tk.Frame(wrap, bg=Theme.panel, highlightbackground=Theme.border, highlightthickness=1)
        center.place(relx=.5, rely=.5, anchor="center", width=620, height=520)
        ttk.Label(center, text="SQL Essentials", style="H1.TLabel").pack(pady=(34, 0))
        ttk.Label(center, text="for the Real World", style="H2.TLabel").pack()
        ttk.Label(center, text="A higher-education microcourse — 17 modules + capstone",
                  style="PanelDim.TLabel", background=Theme.panel).pack(pady=(8, 22))

        meta = tk.Frame(center, bg=Theme.panel)
        meta.pack(pady=4)
        for label, value in (("Instructor", "Personfu / FLLC"),
                             ("Modules",    "0 → 16  +  Final Project"),
                             ("Engine",     "Embedded SQLite (MySQL-flavored)"),
                             ("Total XP",   sum(m[3] for m in MODULE_META))):
            row = tk.Frame(meta, bg=Theme.panel); row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{label}", style="PanelDim.TLabel", background=Theme.panel,
                      width=14, anchor="e").pack(side="left", padx=(0, 14))
            ttk.Label(row, text=str(value), style="Bold.TLabel", background=Theme.panel).pack(side="left")

        tk.Frame(center, bg=Theme.panel, height=22).pack()
        ttk.Label(center, text="What name should we put on your transcript?",
                  style="Panel.TLabel", background=Theme.panel).pack()
        name_var = tk.StringVar()
        entry = tk.Entry(center, textvariable=name_var, font=("Segoe UI", 14),
                         bg=Theme.panel_alt, fg=Theme.text, insertbackground=Theme.accent,
                         relief="flat", justify="center", width=30)
        entry.pack(pady=(6, 16), ipady=10)
        entry.focus_set()

        def begin():
            n = name_var.get().strip() or "Student"
            self.progress.student_name = n
            self.progress.started_at = datetime.now().strftime("%Y-%m-%d %H:%M")
            save_progress(self.progress)
            self._build_app()

        ttk.Button(center, text="Enroll & Begin Course →", style="Accent.TButton",
                   command=begin).pack(pady=10)
        entry.bind("<Return>", lambda e: begin())
        ttk.Label(center, text="Progress saved to %APPDATA%\\CIS_SQL_Course",
                  style="PanelDim.TLabel", background=Theme.panel).pack(side="bottom", pady=18)

    # -------------------- main shell ------------------------------------ #
    def _build_app(self):
        for w in self.winfo_children(): w.destroy()
        self._build_topbar()
        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True)
        self._build_rail(body)
        self._build_main(body)
        self.show_module(self.current_module)
        self._toast(f"Welcome back, {self.progress.student_name}.", kind="info")

    # -------------------- top bar --------------------------------------- #
    def _build_topbar(self):
        top = tk.Frame(self, bg=Theme.panel, height=64,
                       highlightbackground=Theme.border, highlightthickness=1)
        top.pack(fill="x", side="top")
        top.pack_propagate(False)

        left = tk.Frame(top, bg=Theme.panel); left.pack(side="left", padx=22, pady=10)
        tk.Label(left, text="CIS", bg=Theme.accent, fg="#0B1220",
                 font=("Segoe UI Black", 13), padx=10, pady=4).pack(side="left")
        tk.Label(left, text="  SQL Essentials for the Real World",
                 bg=Theme.panel, fg=Theme.text, font=Theme.font_h3).pack(side="left")
        tk.Label(left, text="    Personfu / FLLC", bg=Theme.panel,
                 fg=Theme.text_muted, font=Theme.font_ui).pack(side="left")

        right = tk.Frame(top, bg=Theme.panel); right.pack(side="right", padx=22, pady=8)
        ttk.Button(right, text="↻ Reset SQL Lab", style="Reset.TButton",
                   command=self._reset_sandbox).pack(side="right", padx=(8, 0))
        ttk.Button(right, text="📜 Transcript", style="Ghost.TButton",
                   command=self._show_transcript).pack(side="right", padx=8)

        self.lbl_xp = tk.Label(right, text=self._xp_text(), bg=Theme.panel, fg=Theme.warn,
                               font=Theme.font_ui_b)
        self.lbl_xp.pack(side="right", padx=10)
        self.lbl_pct = tk.Label(right, text=self._pct_text(), bg=Theme.panel, fg=Theme.success,
                                font=Theme.font_ui_b)
        self.lbl_pct.pack(side="right", padx=10)
        tk.Label(right, text=self.progress.student_name, bg=Theme.panel, fg=Theme.text,
                 font=Theme.font_ui_b).pack(side="right", padx=10)
        avatar = tk.Canvas(right, width=32, height=32, bg=Theme.panel, highlightthickness=0)
        avatar.pack(side="right")
        avatar.create_oval(2, 2, 30, 30, fill=Theme.accent_2, outline=Theme.accent_2)
        initials = "".join(p[0] for p in self.progress.student_name.split()[:2]).upper() or "U"
        avatar.create_text(16, 17, text=initials, fill="#FFFFFF", font=("Segoe UI Black", 11))

    def _xp_text(self):
        total = sum(m[3] for m in MODULE_META)
        return f"⚡ {self.progress.xp} / {total} XP"

    def _pct_text(self):
        return f"✓ {self.progress.percent_complete()}% complete"

    # -------------------- side rail ------------------------------------- #
    def _build_rail(self, parent):
        rail = tk.Frame(parent, bg=Theme.rail, width=320,
                        highlightbackground=Theme.border, highlightthickness=1)
        rail.pack(side="left", fill="y")
        rail.pack_propagate(False)

        tk.Label(rail, text="COURSE OUTLINE", bg=Theme.rail, fg=Theme.text_muted,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(16, 4))
        self.bar_pct = ttk.Progressbar(rail, orient="horizontal", mode="determinate",
                                        maximum=100, style="Course.Horizontal.TProgressbar",
                                        length=280)
        self.bar_pct.pack(padx=18, pady=(0, 4))
        self.bar_pct["value"] = self.progress.percent_complete()
        self.lbl_bar = tk.Label(rail,
            text=f"{len(self.progress.completed)} of {len(MODULE_META)} modules complete",
            bg=Theme.rail, fg=Theme.text_dim, font=Theme.font_ui)
        self.lbl_bar.pack(anchor="w", padx=18, pady=(0, 8))

        # Scrollable list
        outer = tk.Frame(rail, bg=Theme.rail)
        outer.pack(fill="both", expand=True, padx=10, pady=4)
        canvas = tk.Canvas(outer, bg=Theme.rail, highlightthickness=0)
        sb = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self.rail_inner = tk.Frame(canvas, bg=Theme.rail)
        canvas.create_window((0, 0), window=self.rail_inner, anchor="nw", width=290)
        self.rail_inner.bind("<Configure>",
                             lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-e.delta/120), "units"))

        self.rail_buttons: Dict[str, tk.Frame] = {}
        for mid, num, title, xp in MODULE_META:
            self.rail_buttons[mid] = self._build_rail_item(self.rail_inner, mid, num, title, xp)

        # Footer (bonus + about)
        foot = tk.Frame(rail, bg=Theme.rail)
        foot.pack(fill="x", side="bottom", pady=12, padx=14)
        tk.Label(foot, text="REFERENCE", bg=Theme.rail, fg=Theme.text_muted,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        ttk.Button(foot, text="📚 Cheatsheets & Security Labs", style="Ghost.TButton",
                   command=self._open_bonus).pack(fill="x", pady=4)

    def _build_rail_item(self, parent, mid, num, title, xp) -> tk.Frame:
        frame = tk.Frame(parent, bg=Theme.rail, padx=8, pady=4)
        frame.pack(fill="x", pady=2)

        chip = tk.Frame(frame, bg=Theme.rail, padx=12, pady=10,
                        highlightbackground=Theme.border, highlightthickness=1)
        chip.pack(fill="x")

        head = tk.Frame(chip, bg=chip["bg"]); head.pack(fill="x")
        status = tk.Label(head, text="", bg=chip["bg"], font=Theme.font_ui_b)
        status.pack(side="left")
        tk.Label(head, text=num, bg=chip["bg"], fg=Theme.text_muted,
                 font=("Segoe UI", 9, "bold")).pack(side="left", padx=(6, 0))
        tk.Label(head, text=f"  •  {xp} XP", bg=chip["bg"], fg=Theme.text_muted,
                 font=("Segoe UI", 9)).pack(side="right")
        body = tk.Label(chip, text=title, bg=chip["bg"], fg=Theme.text,
                        font=Theme.font_ui_b, justify="left", anchor="w", wraplength=240)
        body.pack(fill="x", pady=(4, 0))

        for w in (chip, head, body, status):
            w.bind("<Button-1>", lambda e, m=mid: self.show_module(m))
            w.bind("<Enter>", lambda e, c=chip: c.config(bg=Theme.panel))
            w.bind("<Leave>", lambda e, c=chip: self._restyle_rail())
        frame._chip = chip; frame._status = status; frame._body = body; frame._head = head
        frame._mid = mid
        return frame

    def _restyle_rail(self):
        for mid, frame in self.rail_buttons.items():
            done = self.progress.is_done(mid)
            current = (mid == self.current_module)
            if done:
                bg = Theme.chip_done; fg = Theme.chip_done_fg; mark = "✓"
            elif current:
                bg = Theme.chip_now;  fg = Theme.chip_now_fg;  mark = "▶"
            else:
                bg = Theme.chip_lock; fg = Theme.chip_lock_fg; mark = "○"
            frame._chip.config(bg=bg, highlightbackground=Theme.border)
            for w in (frame._head, frame._body, frame._status):
                w.config(bg=bg)
            frame._body.config(fg=Theme.text if (current or done) else Theme.text_dim)
            frame._status.config(text=mark, fg=fg)

    # -------------------- main panel ------------------------------------ #
    def _build_main(self, parent):
        main = tk.Frame(parent, bg=Theme.bg)
        main.pack(side="left", fill="both", expand=True)
        self.main_frame = main

        # Module header strip
        header = tk.Frame(main, bg=Theme.panel, height=84,
                          highlightbackground=Theme.border, highlightthickness=1)
        header.pack(fill="x"); header.pack_propagate(False)
        self.lbl_mod_kicker = tk.Label(header, text="MODULE", bg=Theme.panel,
                                        fg=Theme.accent, font=("Segoe UI", 10, "bold"))
        self.lbl_mod_kicker.pack(anchor="w", padx=24, pady=(14, 0))
        self.lbl_mod_title  = tk.Label(header, text="—", bg=Theme.panel,
                                        fg=Theme.text, font=Theme.font_h2)
        self.lbl_mod_title.pack(anchor="w", padx=24)
        self.lbl_mod_meta = tk.Label(header, text="", bg=Theme.panel,
                                     fg=Theme.text_muted, font=Theme.font_ui)
        self.lbl_mod_meta.pack(anchor="w", padx=24, pady=(2, 0))

        nav = tk.Frame(header, bg=Theme.panel)
        nav.place(relx=1.0, rely=0.5, anchor="e", x=-22)
        ttk.Button(nav, text="← Previous", style="Ghost.TButton",
                   command=self._prev_module).pack(side="left", padx=4)
        ttk.Button(nav, text="Next →", style="Accent.TButton",
                   command=self._next_module).pack(side="left", padx=4)

        # Tab notebook
        self.nb = ttk.Notebook(main, style="TNotebook")
        self.nb.pack(fill="both", expand=True, padx=16, pady=16)

        self.tab_overview   = self._build_text_tab("Overview")
        self.tab_material   = self._build_text_tab("Material")
        self.tab_assignment = self._build_text_tab("Assignment")
        self.tab_quiz       = self._build_text_tab("Quiz")
        self.tab_reflect    = self._build_text_tab("Reflections")
        self.tab_lab        = self._build_lab_tab()
        self.tab_progress   = self._build_progress_tab()

    def _build_text_tab(self, label: str) -> tk.Text:
        f = tk.Frame(self.nb, bg=Theme.panel)
        self.nb.add(f, text=label)
        body = tk.Frame(f, bg=Theme.panel)
        body.pack(fill="both", expand=True, padx=10, pady=10)
        text = tk.Text(body, wrap="word", bg=Theme.panel, fg=Theme.text,
                       relief="flat", padx=22, pady=18, borderwidth=0,
                       highlightthickness=0, font=Theme.font_ui)
        sb = ttk.Scrollbar(body, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); text.pack(side="left", fill="both", expand=True)
        text.config(state="disabled")
        text._renderer = MarkdownRenderer(text)
        return text

    def _build_lab_tab(self) -> tk.Frame:
        f = tk.Frame(self.nb, bg=Theme.panel)
        self.nb.add(f, text="SQL Lab")

        # Top: instructions strip
        strip = tk.Frame(f, bg=Theme.panel_alt,
                         highlightbackground=Theme.border, highlightthickness=1)
        strip.pack(fill="x", padx=10, pady=(10, 6))
        tk.Label(strip, text="🧪 SQL Lab", bg=Theme.panel_alt, fg=Theme.accent,
                 font=Theme.font_h3).pack(side="left", padx=14, pady=10)
        tk.Label(strip, text="Embedded SQLite engine • MySQL-flavored • run as many times as you want",
                 bg=Theme.panel_alt, fg=Theme.text_dim, font=Theme.font_ui).pack(side="left", pady=10)

        ctrl = tk.Frame(strip, bg=Theme.panel_alt); ctrl.pack(side="right", padx=10)
        ttk.Button(ctrl, text="▶ Run Query (F5)", style="Run.TButton",
                   command=self._run_query).pack(side="left", padx=4)
        ttk.Button(ctrl, text="✓ Submit Assignment", style="Submit.TButton",
                   command=self._submit_assignment).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Load Lab Template", style="Ghost.TButton",
                   command=self._load_lab_template).pack(side="left", padx=4)
        self.bind("<F5>", lambda e: self._run_query())

        # Editor + results split
        paned = tk.PanedWindow(f, orient="vertical", bg=Theme.panel,
                               sashwidth=8, sashrelief="flat", borderwidth=0)
        paned.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        ed_wrap = tk.Frame(paned, bg=Theme.panel,
                           highlightbackground=Theme.border, highlightthickness=1)
        sb = ttk.Scrollbar(ed_wrap, orient="vertical")
        self.editor = SQLEditor(ed_wrap, yscrollcommand=sb.set)
        sb.config(command=self.editor.yview)
        sb.pack(side="right", fill="y"); self.editor.pack(side="left", fill="both", expand=True)
        paned.add(ed_wrap, height=320, minsize=160)

        # Results notebook
        res_wrap = tk.Frame(paned, bg=Theme.panel)
        paned.add(res_wrap, minsize=140)

        self.res_nb = ttk.Notebook(res_wrap, style="TNotebook")
        self.res_nb.pack(fill="both", expand=True)

        # Results tab
        self.res_results = tk.Frame(self.res_nb, bg=Theme.panel)
        self.res_nb.add(self.res_results, text="Results")
        self.tree = ttk.Treeview(self.res_results, show="headings",
                                  style="Treeview")
        vsb = ttk.Scrollbar(self.res_results, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.res_results, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.pack(side="right", fill="y"); hsb.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        # Console tab
        self.res_console = tk.Frame(self.res_nb, bg=Theme.panel)
        self.res_nb.add(self.res_console, text="Console")
        self.console = tk.Text(self.res_console, bg=Theme.code_bg, fg=Theme.code_text,
                                font=Theme.font_code, relief="flat", padx=10, pady=10,
                                borderwidth=0, highlightthickness=0)
        self.console.pack(fill="both", expand=True)
        self.console.tag_configure("ok",   foreground=Theme.success)
        self.console.tag_configure("err",  foreground=Theme.danger)
        self.console.tag_configure("info", foreground=Theme.accent)
        self.console.config(state="disabled")

        # Checks tab
        self.res_checks = tk.Frame(self.res_nb, bg=Theme.panel)
        self.res_nb.add(self.res_checks, text="Completion Checks")
        self.checks_view = tk.Frame(self.res_checks, bg=Theme.panel)
        self.checks_view.pack(fill="both", expand=True, padx=14, pady=14)
        return f

    def _build_progress_tab(self) -> tk.Frame:
        f = tk.Frame(self.nb, bg=Theme.panel)
        self.nb.add(f, text="Dashboard")
        wrap = tk.Frame(f, bg=Theme.panel)
        wrap.pack(fill="both", expand=True, padx=24, pady=24)

        self.dash_h1 = tk.Label(wrap, text="Welcome", bg=Theme.panel, fg=Theme.text,
                                font=Theme.font_h1, anchor="w")
        self.dash_h1.pack(fill="x")
        self.dash_h2 = tk.Label(wrap, text="", bg=Theme.panel, fg=Theme.text_dim,
                                font=Theme.font_ui, anchor="w")
        self.dash_h2.pack(fill="x", pady=(0, 18))

        # KPI row
        row = tk.Frame(wrap, bg=Theme.panel); row.pack(fill="x", pady=(0, 16))
        self.kpi_widgets = []
        for label, key in (("Modules complete","mods"), ("Total XP","xp"),
                            ("Course progress","pct"), ("Achievements","ach")):
            card = tk.Frame(row, bg=Theme.panel_alt, padx=18, pady=14,
                            highlightbackground=Theme.border, highlightthickness=1)
            card.pack(side="left", padx=6, fill="both", expand=True)
            tk.Label(card, text=label, bg=Theme.panel_alt, fg=Theme.text_muted,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w")
            v = tk.Label(card, text="0", bg=Theme.panel_alt, fg=Theme.accent,
                         font=("Segoe UI", 22, "bold"))
            v.pack(anchor="w")
            self.kpi_widgets.append((key, v))

        # Module grid
        tk.Label(wrap, text="Course path", bg=Theme.panel, fg=Theme.text,
                 font=Theme.font_h3).pack(anchor="w", pady=(8, 6))
        grid = tk.Frame(wrap, bg=Theme.panel); grid.pack(fill="x")
        self.dash_chips = []
        cols = 6
        for i, (mid, num, title, xp) in enumerate(MODULE_META):
            r, c = divmod(i, cols)
            chip = tk.Frame(grid, bg=Theme.panel_alt, padx=10, pady=8,
                            highlightbackground=Theme.border, highlightthickness=1, cursor="hand2")
            chip.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            l1 = tk.Label(chip, text=num, bg=chip["bg"], fg=Theme.accent,
                          font=("Segoe UI", 10, "bold"))
            l1.pack(anchor="w")
            l2 = tk.Label(chip, text=title, bg=chip["bg"], fg=Theme.text,
                          font=Theme.font_ui, wraplength=170, justify="left")
            l2.pack(anchor="w")
            l3 = tk.Label(chip, text="", bg=chip["bg"], fg=Theme.text_muted,
                          font=("Segoe UI", 9))
            l3.pack(anchor="w", pady=(4, 0))
            for w in (chip, l1, l2, l3):
                w.bind("<Button-1>", lambda e, m=mid: (self.show_module(m), self.nb.select(self.tab_overview.master.master)))
            self.dash_chips.append((mid, chip, l1, l2, l3))
        for c in range(cols): grid.grid_columnconfigure(c, weight=1, uniform="m")

        # Achievements panel
        tk.Label(wrap, text="Achievements", bg=Theme.panel, fg=Theme.text,
                 font=Theme.font_h3).pack(anchor="w", pady=(20, 6))
        self.ach_panel = tk.Frame(wrap, bg=Theme.panel)
        self.ach_panel.pack(fill="x")
        return f

    # -------------------- module navigation ----------------------------- #
    def show_module(self, mid: str):
        if mid not in MODULE_INDEX:
            return
        self.current_module = mid
        self.progress.last_module = mid
        save_progress(self.progress)
        meta = MODULE_META[MODULE_INDEX[mid]]
        _id, num, title, xp = meta
        self.lbl_mod_kicker.config(text=num.upper())
        self.lbl_mod_title.config(text=title)
        status = "✓ Completed" if self.progress.is_done(mid) else f"{xp} XP available"
        self.lbl_mod_meta.config(text=f"{status}  •  {len(self.progress.completed)} of {len(MODULE_META)} modules done")

        c = load_content(mid)
        self.tab_overview._renderer.render(c["Overview.md"])
        self.tab_material._renderer.render(c["InstructionalMaterial.md"] +
                                            ("\n\n---\n\n# Examples\n\n" + c["Examples.md"] if c.get("Examples.md") else ""))
        self.tab_assignment._renderer.render(c["Assignment.md"])
        self.tab_quiz._renderer.render(c["Quiz.md"])
        self.tab_reflect._renderer.render(c["Reflections.md"] +
                                          ("\n\n---\n\n## Notes\n\n```\n" + c["Notes.txt"] + "\n```\n"
                                           if c.get("Notes.txt") else ""))
        # Editor template
        prior = self.progress.submissions.get(mid)
        self.editor.set_text(prior or c.get("Lab.sql") or "-- Write your SQL here\nSELECT 1 AS hello;\n")
        self._render_checks(passed=False, results=[])
        self._restyle_rail()
        self._refresh_dashboard()

    def _prev_module(self):
        i = MODULE_INDEX[self.current_module]
        if i > 0: self.show_module(MODULE_IDS[i - 1])

    def _next_module(self):
        i = MODULE_INDEX[self.current_module]
        if i < len(MODULE_IDS) - 1: self.show_module(MODULE_IDS[i + 1])

    def _load_lab_template(self):
        c = load_content(self.current_module)
        if c.get("Lab.sql"):
            self.editor.set_text(c["Lab.sql"])

    # -------------------- query execution ------------------------------- #
    def _run_query(self):
        sql = self.editor.get("1.0", "end-1c").strip()
        if not sql:
            self._console_log("No SQL to run.\n", "err"); return
        cols, rows, err = self.sandbox.execute(sql)
        # cache
        self.last_run_rows = rows
        self.last_run_error = err
        # tree
        for col in self.tree.get_children(): self.tree.delete(col)
        self.tree["columns"] = cols
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=160, stretch=True, anchor="w")
        for r in rows: self.tree.insert("", "end", values=r)
        # console
        if err:
            self._console_log(f"[{datetime.now().strftime('%H:%M:%S')}] ✗ {err}\n", "err")
            self.res_nb.select(self.res_console)
        else:
            self._console_log(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ {len(rows)} row(s)\n", "ok")
            self.res_nb.select(self.res_results)
        # auto-evaluate completion checks
        self._render_checks(passed=False, results=self._evaluate_checks(sql))

    def _console_log(self, msg, tag="info"):
        self.console.config(state="normal")
        self.console.insert("end", msg, (tag,))
        self.console.see("end")
        self.console.config(state="disabled")

    # -------------------- checks ---------------------------------------- #
    def _evaluate_checks(self, sql: str) -> List[Tuple[str, bool, str]]:
        rules = CHECKS.get(self.current_module, [])
        results = []
        for label, fn in rules:
            try:
                cr = fn(sql, self.last_run_rows, self.last_run_error)
                results.append((label, cr.passed, cr.message))
            except Exception as ex:
                results.append((label, False, f"check failed: {ex}"))
        return results

    def _render_checks(self, passed: bool, results: List[Tuple[str, bool, str]]):
        for w in self.checks_view.winfo_children(): w.destroy()
        rules = CHECKS.get(self.current_module, [])
        if not rules:
            tk.Label(self.checks_view,
                text="This module has no automated checks. Review the assignment, then click Submit Assignment.",
                bg=Theme.panel, fg=Theme.text_dim, font=Theme.font_ui, wraplength=600,
                justify="left").pack(anchor="w")
            return
        rmap = {label: (ok, msg) for label, ok, msg in results}
        passed_count = sum(1 for _, ok, _ in results if ok)
        tk.Label(self.checks_view,
                 text=f"{passed_count} of {len(rules)} checks passing",
                 bg=Theme.panel, fg=Theme.accent, font=Theme.font_h3).pack(anchor="w", pady=(0, 8))
        for label, fn in rules:
            ok, msg = rmap.get(label, (False, "run a query to evaluate"))
            row = tk.Frame(self.checks_view, bg=Theme.panel_alt,
                            highlightbackground=Theme.border, highlightthickness=1)
            row.pack(fill="x", pady=3)
            mk = tk.Label(row, text=("✓" if ok else "○"),
                          bg=Theme.panel_alt,
                          fg=Theme.success if ok else Theme.text_muted,
                          font=("Segoe UI", 14, "bold"), padx=12, pady=8)
            mk.pack(side="left")
            txt = tk.Frame(row, bg=Theme.panel_alt); txt.pack(side="left", fill="x", expand=True, pady=6)
            tk.Label(txt, text=label, bg=Theme.panel_alt, fg=Theme.text,
                     font=Theme.font_ui_b, anchor="w").pack(anchor="w")
            tk.Label(txt, text=msg, bg=Theme.panel_alt, fg=Theme.text_dim,
                     font=Theme.font_ui, anchor="w", wraplength=720, justify="left").pack(anchor="w")

    def _submit_assignment(self):
        sql = self.editor.get("1.0", "end-1c")
        results = self._evaluate_checks(sql)
        rules = CHECKS.get(self.current_module, [])
        if not results or not rules:
            # No automated checks — accept on submit
            results = [("Manual review", True, "Submitted for review.")]
        all_pass = all(ok for _, ok, _ in results)
        self._render_checks(all_pass, results)
        self.res_nb.select(self.res_checks)
        self.progress.submissions[self.current_module] = sql
        if all_pass:
            xp = MODULE_META[MODULE_INDEX[self.current_module]][3]
            new = self.progress.mark_done(self.current_module, xp)
            save_progress(self.progress)
            self._refresh_topbar(); self._refresh_dashboard(); self._restyle_rail()
            if new:
                self._award_xp(xp)
                self._toast(f"Module complete! +{xp} XP", kind="success")
                self._maybe_award_achievements()
                # Auto-advance prompt
                self.after(500, self._prompt_advance)
        else:
            self._toast("Some checks did not pass yet — keep iterating.", kind="warn")

    def _prompt_advance(self):
        i = MODULE_INDEX[self.current_module]
        if i < len(MODULE_IDS) - 1:
            if messagebox.askyesno("Next Module",
                f"Advance to {MODULE_META[i+1][1]} — {MODULE_META[i+1][2]}?"):
                self._next_module()
        else:
            messagebox.showinfo("Course Complete!",
                "🎓  Capstone delivered. Visit the Dashboard for your final transcript.")

    def _award_xp(self, xp: int):
        # Tiny non-modal animation
        flash = tk.Label(self, text=f"+{xp} XP", bg=Theme.bg, fg=Theme.success,
                         font=("Segoe UI Black", 28))
        flash.place(relx=0.5, rely=0.5, anchor="center")
        def fade(step=0):
            if step > 12: flash.destroy(); return
            flash.place_configure(rely=0.5 - 0.02 * step)
            self.after(40, lambda: fade(step + 1))
        fade()

    def _maybe_award_achievements(self):
        ach = self.progress.achievements
        def grant(name):
            if name not in ach:
                ach.append(name); save_progress(self.progress)
                self._toast(f"🏆 Achievement: {name}", kind="info", ms=2400)

        c = len(self.progress.completed)
        if c >= 1:  grant("First Query Fired")
        if c >= 5:  grant("SQL Apprentice")
        if c >= 10: grant("Query Smith")
        if c >= 17: grant("Schema Architect")
        if "module_final" in self.progress.completed: grant("Capstone Complete")
        if self.progress.xp >= 100: grant("Centurion XP")
        if self.progress.xp >= sum(m[3] for m in MODULE_META): grant("Maxed Out")

    # -------------------- dashboard / topbar refresh -------------------- #
    def _refresh_topbar(self):
        self.lbl_xp.config(text=self._xp_text())
        self.lbl_pct.config(text=self._pct_text())
        self.bar_pct["value"] = self.progress.percent_complete()
        self.lbl_bar.config(text=f"{len(self.progress.completed)} of {len(MODULE_META)} modules complete")

    def _refresh_dashboard(self):
        self.dash_h1.config(text=f"Welcome, {self.progress.student_name}")
        self.dash_h2.config(text=f"Started {self.progress.started_at}  •  current module: {MODULE_META[MODULE_INDEX[self.current_module]][2]}")
        for key, lbl in self.kpi_widgets:
            if key == "mods": lbl.config(text=f"{len(self.progress.completed)} / {len(MODULE_META)}")
            elif key == "xp": lbl.config(text=str(self.progress.xp))
            elif key == "pct": lbl.config(text=f"{self.progress.percent_complete()}%")
            elif key == "ach": lbl.config(text=str(len(self.progress.achievements)))
        for mid, chip, l1, l2, l3 in self.dash_chips:
            if self.progress.is_done(mid):
                bg = Theme.chip_done; fg = Theme.chip_done_fg; status = "✓ done"
            elif mid == self.current_module:
                bg = Theme.chip_now;  fg = Theme.chip_now_fg;  status = "▶ in progress"
            else:
                bg = Theme.chip_lock; fg = Theme.chip_lock_fg; status = "○ pending"
            chip.config(bg=bg)
            for w in (l1, l2, l3): w.config(bg=bg)
            l3.config(text=status, fg=fg)
        # Achievements
        for w in self.ach_panel.winfo_children(): w.destroy()
        if not self.progress.achievements:
            tk.Label(self.ach_panel, text="No achievements yet — finish a module to earn one.",
                     bg=Theme.panel, fg=Theme.text_dim, font=Theme.font_ui).pack(anchor="w")
        else:
            for a in self.progress.achievements:
                pill = tk.Frame(self.ach_panel, bg=Theme.badge_bg, padx=10, pady=5,
                                highlightbackground=Theme.border, highlightthickness=1)
                pill.pack(side="left", padx=4, pady=4)
                tk.Label(pill, text="🏆 " + a, bg=Theme.badge_bg, fg=Theme.badge_fg,
                         font=Theme.font_ui_b).pack()

    # -------------------- toasts ---------------------------------------- #
    def _toast(self, msg: str, kind="info", ms=1800):
        colors = {"info": Theme.accent, "success": Theme.success,
                  "warn": Theme.warn, "err": Theme.danger}
        bg = Theme.panel; fg = colors.get(kind, Theme.accent)
        toast = tk.Frame(self, bg=bg, highlightbackground=fg, highlightthickness=1)
        tk.Label(toast, text=msg, bg=bg, fg=fg, font=Theme.font_ui_b,
                 padx=14, pady=8).pack()
        toast.place(relx=0.5, rely=0.05, anchor="n")
        self.after(ms, toast.destroy)

    def _reset_sandbox(self):
        if not messagebox.askyesno("Reset SQL Lab",
            "Wipe the embedded SQLite database and restore the sample tables?"):
            return
        self.sandbox.reset()
        self._toast("Lab database reset to seed data.", "warn")

    def _show_transcript(self):
        win = tk.Toplevel(self); win.title("Transcript"); win.configure(bg=Theme.panel)
        win.geometry("680x620")
        tk.Label(win, text="Official Course Transcript", bg=Theme.panel, fg=Theme.accent,
                 font=Theme.font_h1).pack(pady=(20, 6))
        tk.Label(win, text="SQL Essentials for the Real World — Personfu / FLLC",
                 bg=Theme.panel, fg=Theme.text_dim, font=Theme.font_ui).pack()
        tk.Frame(win, bg=Theme.border, height=1).pack(fill="x", padx=24, pady=14)
        meta = (("Student", self.progress.student_name or "—"),
                ("Started", self.progress.started_at or "—"),
                ("Modules complete", f"{len(self.progress.completed)} / {len(MODULE_META)}"),
                ("Total XP earned",  f"{self.progress.xp} / {sum(m[3] for m in MODULE_META)}"),
                ("Achievements",     ", ".join(self.progress.achievements) or "—"))
        for k, v in meta:
            row = tk.Frame(win, bg=Theme.panel); row.pack(fill="x", padx=24, pady=2)
            tk.Label(row, text=k, bg=Theme.panel, fg=Theme.text_muted,
                     font=Theme.font_ui_b, width=18, anchor="w").pack(side="left")
            tk.Label(row, text=v, bg=Theme.panel, fg=Theme.text,
                     font=Theme.font_ui, anchor="w", wraplength=440, justify="left").pack(side="left")

        tk.Frame(win, bg=Theme.border, height=1).pack(fill="x", padx=24, pady=14)
        tk.Label(win, text="Module Status", bg=Theme.panel, fg=Theme.text,
                 font=Theme.font_h3).pack(anchor="w", padx=24)
        body = tk.Frame(win, bg=Theme.panel); body.pack(fill="both", expand=True, padx=24, pady=8)
        for mid, num, title, xp in MODULE_META:
            ok = self.progress.is_done(mid)
            row = tk.Frame(body, bg=Theme.panel); row.pack(fill="x", pady=1)
            tk.Label(row, text="✓" if ok else "○", bg=Theme.panel,
                     fg=Theme.success if ok else Theme.text_muted,
                     font=Theme.font_ui_b, width=2).pack(side="left")
            tk.Label(row, text=f"{num:>9}  ·  {title}", bg=Theme.panel,
                     fg=Theme.text if ok else Theme.text_dim,
                     font=Theme.font_ui, anchor="w").pack(side="left", fill="x", expand=True)
            tk.Label(row, text=f"{xp} XP", bg=Theme.panel, fg=Theme.text_muted,
                     font=Theme.font_ui).pack(side="right")
        ttk.Button(win, text="Export to text file", style="Ghost.TButton",
                   command=self._export_transcript).pack(pady=12)

    def _export_transcript(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
            initialfile=f"{self.progress.student_name.replace(' ', '_')}_transcript.txt",
            filetypes=[("Text", "*.txt")])
        if not path: return
        lines = ["CIS — SQL Essentials for the Real World",
                 "=" * 50,
                 f"Student:           {self.progress.student_name}",
                 f"Started:           {self.progress.started_at}",
                 f"Modules complete:  {len(self.progress.completed)}/{len(MODULE_META)}",
                 f"Total XP:          {self.progress.xp}/{sum(m[3] for m in MODULE_META)}",
                 f"Achievements:      {', '.join(self.progress.achievements) or '—'}",
                 "", "Module status:"]
        for mid, num, title, xp in MODULE_META:
            tag = "[x]" if self.progress.is_done(mid) else "[ ]"
            lines.append(f"  {tag} {num:>10}  {title}  ({xp} XP)")
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        self._toast(f"Transcript saved to {Path(path).name}", "success")

    def _open_bonus(self):
        bonus = load_bonus()
        if not bonus:
            messagebox.showinfo("Bonus", "No bonus material bundled."); return
        win = tk.Toplevel(self); win.title("Reference — Cheatsheets & Security Labs")
        win.geometry("1100x780"); win.configure(bg=Theme.panel)
        side = tk.Frame(win, bg=Theme.rail, width=240); side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Label(side, text="REFERENCE", bg=Theme.rail, fg=Theme.text_muted,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=14, pady=(14, 6))
        body = tk.Frame(win, bg=Theme.panel); body.pack(side="left", fill="both", expand=True)
        text = tk.Text(body, bg=Theme.panel, fg=Theme.text, relief="flat", padx=22, pady=18,
                       borderwidth=0, highlightthickness=0, font=Theme.font_ui, wrap="word")
        sb = ttk.Scrollbar(body, orient="vertical", command=text.yview)
        text.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); text.pack(side="left", fill="both", expand=True)
        text.config(state="disabled")
        rd = MarkdownRenderer(text)
        for name in bonus:
            ttk.Button(side, text=name.replace(".md", ""), style="Ghost.TButton",
                       command=lambda n=name: rd.render(bonus[n])).pack(fill="x", padx=10, pady=2)
        rd.render(next(iter(bonus.values())))


# --------------------------------------------------------------------------- #
#                                  ENTRY                                      #
# --------------------------------------------------------------------------- #

def main():
    try:
        app = CISCourseApp()
        app.mainloop()
    except Exception:
        traceback.print_exc()
        messagebox.showerror("Fatal", traceback.format_exc())


if __name__ == "__main__":
    main()
