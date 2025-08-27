import sqlite3
import pathlib

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"
DB_PATH = pathlib.Path(__file__).resolve().parent.parent / "app.db"


def apply_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    applied = {row[0] for row in cur.execute("SELECT version FROM schema_migrations").fetchall()}

    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = sql_file.stem
        if version not in applied:
            print(f"Applying migration {version}...")
            with open(sql_file, "r", encoding="utf-8") as f:
                cur.executescript(f.read())
            cur.execute("INSERT INTO schema_migrations(version) VALUES (?)", (version,))
            conn.commit()

    conn.close()

if __name__ == "__main__":
    apply_migrations()
    print("Migrations applied.")