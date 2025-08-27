from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from app.domain.models import User, Habit, LogEntry
from app.repositories.db import DB

class SQLiteUserRepo:
    def __init__(self, db: DB):
        self.db = db

    def get(self, user_id: int) -> Optional[User]:
        cur = self.db.cursor()
        row = cur.execute("SELECT user_id, tz, locale FROM users WHERE user_id = ?", (user_id,)).fetchone()
        if not row:
            return None
        return User(user_id=row["user_id"], tz=row["tz"], locale=row["locale"])

    def upsert(self, user: User) -> None:
        cur = self.db.cursor()
        cur.execute(
            """
            INSERT INTO users(user_id, tz, locale)
            VALUES(?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET tz=excluded.tz, locale=excluded.locale
            """,
            (user.user_id, user.tz, user.locale),
        )
        self.db.commit()

class SQLiteHabitRepo:
    def __init__(self, db: DB):
        self.db = db

    def list_for_user(self, user_id: int) -> List[Habit]:
        cur = self.db.cursor()
        rows = cur.execute(
            """
            SELECT habit_id, user_id, name, hour, minute, xp, streak, last_answer_date, snooze_date, snooze_used, active
            FROM habits WHERE user_id = ? ORDER BY habit_id
            """,
            (user_id,),
        ).fetchall()
        return [self._row_to_habit(r) for r in rows]

    def get(self, user_id: int, habit_id: int) -> Optional[Habit]:
        cur = self.db.cursor()
        row = cur.execute(
            """
            SELECT habit_id, user_id, name, hour, minute, xp, streak, last_answer_date, snooze_date, snooze_used, active
            FROM habits WHERE user_id = ? AND habit_id = ?
            """,
            (user_id, habit_id),
        ).fetchone()
        return self._row_to_habit(row) if row else None

    def add(self, habit: Habit) -> int:
        cur = self.db.cursor()
        cur.execute(
            """
            INSERT INTO habits(user_id, name, hour, minute, xp, streak, last_answer_date, snooze_date, snooze_used, active)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """,
            (
                habit.user_id,
                habit.name,
                habit.hour,
                habit.minute,
                habit.xp,
                habit.streak,
                habit.last_answer_date,
                habit.snooze_date,
                int(habit.snooze_used),
                int(habit.active),
            ),
        )
        self.db.commit()
        return int(cur.lastrowid)

    def update(self, habit: Habit) -> None:
        cur = self.db.cursor()
        cur.execute(
            """
            UPDATE habits
            SET name=?, hour=?, minute=?, xp=?, streak=?, last_answer_date=?, snooze_date=?, snooze_used=?, active=?
            WHERE habit_id=? AND user_id=?
            """,
            (
                habit.name,
                habit.hour,
                habit.minute,
                habit.xp,
                habit.streak,
                habit.last_answer_date,
                habit.snooze_date,
                int(habit.snooze_used),
                int(habit.active),
                habit.habit_id,
                habit.user_id,
            ),
        )
        self.db.commit()

    @staticmethod
    def _row_to_habit(r) -> Habit:
        return Habit(
            habit_id=r["habit_id"],
            user_id=r["user_id"],
            name=r["name"],
            hour=r["hour"],
            minute=r["minute"],
            xp=r["xp"],
            streak=r["streak"],
            last_answer_date=r["last_answer_date"],
            snooze_date=r["snooze_date"],
            snooze_used=bool(r["snooze_used"]),
            active=bool(r["active"]),
        )

class SQLiteLogRepo:
    def __init__(self, db: DB):
        self.db = db

    def upsert_answer(self, entry: LogEntry) -> None:
        """Idempotent write per (user_id, habit_id, date)."""
        cur = self.db.cursor()
        # Try update first (if exists)
        cur.execute(
            """
            UPDATE logs SET answer=?, ts_utc=?, src=?
            WHERE user_id=? AND habit_id=? AND date=?
            """,
            (entry.answer, entry.ts_utc, entry.src, entry.user_id, entry.habit_id, entry.date),
        )
        if cur.rowcount == 0:
            # Insert new
            cur.execute(
                """
                INSERT INTO logs(user_id, habit_id, date, answer, ts_utc, src)
                VALUES(?,?,?,?,?,?)
                """,
                (entry.user_id, entry.habit_id, entry.date, entry.answer, entry.ts_utc, entry.src),
            )
        self.db.commit()

    def get_by_date(self, user_id: int, habit_id: int, date: str) -> Optional[LogEntry]:
        cur = self.db.cursor()
        row = cur.execute(
            "SELECT user_id, habit_id, date, answer, ts_utc, src FROM logs WHERE user_id=? AND habit_id=? AND date=?",
            (user_id, habit_id, date),
        ).fetchone()
        return self._row_to_log(row) if row else None

    def get_last_days(self, user_id: int, habit_id: int, n: int) -> List[LogEntry]:
        cur = self.db.cursor()
        rows = cur.execute(
            """
            SELECT user_id, habit_id, date, answer, ts_utc, src
            FROM logs WHERE user_id=? AND habit_id=?
            ORDER BY date DESC LIMIT ?
            """,
            (user_id, habit_id, n),
        ).fetchall()
        return [self._row_to_log(r) for r in rows]

    @staticmethod
    def _row_to_log(r) -> LogEntry:
        return LogEntry(
            user_id=r["user_id"],
            habit_id=r["habit_id"],
            date=r["date"],
            answer=r["answer"],
            ts_utc=r["ts_utc"],
            src=r["src"],
        )