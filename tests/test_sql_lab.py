"""The local SQL lab must keep learner statements in its own database."""

import importlib
import os
import sqlite3
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch


class SQLLabBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        app_dir = str(Path(__file__).resolve().parents[1] / "_app")
        sys.path.insert(0, app_dir)
        try:
            with patch.dict(os.environ, {"APPDATA": cls.temp.name}):
                cls.course = importlib.import_module("cis_sql_course")
        finally:
            sys.path.remove(app_dir)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.path = Path(self.temp.name) / "lab.db"
        self.path.unlink(missing_ok=True)
        self.lab = self.course.SQLSandbox(self.path)

    def tearDown(self):
        self.lab.conn.close()

    def test_queries_still_work_and_foreign_keys_remain_enabled(self):
        cols, rows, err = self.lab.execute("SELECT first_name FROM Customers WHERE customer_id = 1")
        self.assertIsNone(err)
        self.assertEqual(cols, ["first_name"])
        self.assertEqual(rows, [["Cassandra"]])
        self.assertEqual(self.lab.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)

    def test_external_databases_and_vacuum_export_are_denied_after_reset(self):
        external = Path(self.temp.name) / "external.db"
        with closing(sqlite3.connect(external)) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS private_notes (message TEXT)")
            conn.commit()
        exported = Path(self.temp.name) / "exported.db"
        for cycle in range(2):
            _, _, attach_error = self.lab.execute(f"ATTACH DATABASE '{external}' AS external")
            self.assertIsNotNone(attach_error, f"cycle {cycle}")
            _, _, vacuum_error = self.lab.execute(f"VACUUM INTO '{exported}'")
            self.assertIsNotNone(vacuum_error, f"cycle {cycle}")
            self.assertFalse(exported.exists())
            self.lab.reset()

    def test_file_affecting_pragma_is_denied_but_schema_inspection_works(self):
        _, _, error = self.lab.execute("PRAGMA writable_schema = ON")
        self.assertIsNotNone(error)
        _, _, error = self.lab.execute("PRAGMA foreign_keys = OFF")
        self.assertIsNotNone(error)
        self.assertEqual(self.lab.conn.execute("PRAGMA foreign_keys").fetchone()[0], 1)
        cols, rows, err = self.lab.execute("PRAGMA table_info(Customers)")
        self.assertIsNone(err)
        self.assertEqual(cols[1], "name")
        self.assertIn("customer_id", [row[1] for row in rows])


if __name__ == "__main__":
    unittest.main()
