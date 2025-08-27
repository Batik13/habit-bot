# app/repositories/migrate.py
import sqlite3
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent / "migrations"
DB_PATH = ROOT / "data" / "app.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def apply_migrations():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version TEXT PRIMARY KEY,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    applied = {row[0] for row in cur.execute("SELECT version FROM schema_migrations").fetchall()}

    for sql_file in sorted(MIGRATIONS_DIR.glob("*.sql")):
        version = sql_file.stem
        if version not in applied:
            print(f"Applying migration {version} from {sql_file} ...")
            sql = sql_file.read_text(encoding="utf-8")
            try:
                cur.executescript(sql)
            except sqlite3.OperationalError as e:
                print(f"\n[SQL ERROR] in {sql_file}:\n{e}\n")
                raise
            cur.execute("INSERT OR IGNORE INTO schema_migrations(version) VALUES (?)", (version,))
            conn.commit()

    conn.close()

if __name__ == "__main__":
    apply_migrations()
    print("Migrations applied.")
