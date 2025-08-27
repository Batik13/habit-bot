import tempfile
from pathlib import Path
from datetime import datetime, timezone
from app.repositories.db import DB
from app.repositories.sqlite_repo import SQLiteUserRepo, SQLiteHabitRepo, SQLiteLogRepo
from app.domain.models import User, Habit, LogEntry

# Helper to bootstrap schema for tests by running the migration SQL
def bootstrap(db: DB):
    sql_path = Path(__file__).resolve().parents[2] / "migrations" / "001_init.sql"
    with open(sql_path, "r", encoding="utf-8") as f:
        db.conn.executescript(f.read())


def test_user_and_habit_crud():
    with tempfile.TemporaryDirectory() as tmp:
        db = DB(Path(tmp) / "t.db")
        bootstrap(db)

        urepo = SQLiteUserRepo(db)
        hrepo = SQLiteHabitRepo(db)

        urepo.upsert(User(user_id=1, tz="Etc/UTC", locale="ru"))
        assert urepo.get(1) is not None

        habit_id = hrepo.add(Habit(
            habit_id=0, user_id=1, name="Читать 10 минут", hour=8, minute=30
        ))
        h = hrepo.get(1, habit_id)
        assert h and h.name == "Читать 10 минут"

        h.name = "Читать 15 минут"; hrepo.update(h)
        h2 = hrepo.get(1, habit_id)
        assert h2 and h2.name == "Читать 15 минут"


def test_log_upsert_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        db = DB(Path(tmp) / "t.db")
        bootstrap(db)

        lrepo = SQLiteLogRepo(db)
        # minimal FK bootstrap
        db.conn.execute("INSERT INTO users(user_id) VALUES (1)")
        db.conn.execute("INSERT INTO habits(user_id, name, hour, minute) VALUES (1,'h',8,30)")
        hid = db.conn.execute("SELECT habit_id FROM habits").fetchone()[0]

        e = LogEntry(user_id=1, habit_id=hid, date="2025-08-27", answer="yes", ts_utc="2025-08-27T08:00:00Z")
        lrepo.upsert_answer(e)
        # second upsert should update, not duplicate
        e2 = LogEntry(user_id=1, habit_id=hid, date="2025-08-27", answer="no", ts_utc="2025-08-27T09:00:00Z")
        lrepo.upsert_answer(e2)

        row = db.conn.execute("SELECT COUNT(*) FROM logs WHERE user_id=1 AND habit_id=? AND date='2025-08-27'", (hid,)).fetchone()[0]
        assert row == 1