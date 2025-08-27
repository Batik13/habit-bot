from __future__ import annotations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

class DB:
    def __init__(self, path: Path | None = None):
        self.path = path or DB_PATH
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        # pragma tuning for small app, safe defaults
        self.conn.execute("PRAGMA foreign_keys = ON;")

    def cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()