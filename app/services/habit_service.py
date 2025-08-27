from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import datetime as dt  # (оставлен, если где-то используется наружным кодом)

from app.repositories.base import UserRepo, HabitRepo, LogRepo
from app.domain.models import User, Habit, LogEntry
from app.domain import rules
from app.config.constants import XP_PER_YES
from app.services.types import CompleteResult, NoResult
from app.utils.time import today_ymd, now_iso_utc
from app.analytics.events import Events


@dataclass
class UnlockEvent:
    reason: str  # 'xp' | 'streak'


class HabitService:
    def __init__(
        self,
        users: UserRepo,
        habits: HabitRepo,
        logs: LogRepo,
        events: Optional[Events] | None = None,
    ):
        self.users = users
        self.habits = habits
        self.logs = logs
        self.events = events

    # ---- Create & ensure ----
    async def ensure_user(self, user_id: int, tz: str = "Etc/UTC", locale: str = "ru") -> None:
        u = self.users.get(user_id)
        if not u:
            self.users.upsert(User(user_id=user_id, tz=tz, locale=locale))

    async def add_habit(self, user_id: int, name: str, hour: int, minute: int) -> int:
        await self.ensure_user(user_id)
        habit = Habit(
            habit_id=0,
            user_id=user_id,
            name=name,
            hour=hour,
            minute=minute,
            xp=0,
            streak=0,
            last_answer_date=None,
            snooze_date=None,
            snooze_used=False,
            active=True,
        )
        hid = self.habits.add(habit)
        if self.events:
            self.events.emit(
                event="habit_created",
                user_id=user_id,
                habit_id=hid,
                payload={"hour": hour, "minute": minute},
            )
        return hid

    # ---- Answers ----
    async def complete_today(self, user_id: int, habit_id: int, src: str = "regular") -> CompleteResult:
        h = self.habits.get(user_id, habit_id)
        if not h or not h.active:
            # treat as no-op; in real app raise a domain error
            return CompleteResult(already_marked=True, streak=0, xp_total=0)

        today = today_ymd()
        if h.last_answer_date == today:
            # already answered today (either yes or no); enforce idempotency
            return CompleteResult(already_marked=True, streak=h.streak, xp_total=h.xp)

        # Was yesterday a YES? Determine based on logs
        from datetime import date, timedelta

        yday = (date.fromisoformat(today) - timedelta(days=1)).isoformat()
        ylog = self.logs.get_by_date(user_id, habit_id, yday)
        answered_yesterday_yes = (ylog is not None and getattr(ylog, "answer", None) == "yes")

        new_streak = rules.next_streak(h.streak, answered_yesterday_yes, True)
        new_xp = h.xp + XP_PER_YES

        # Persist log and habit
        self.logs.upsert_answer(
            LogEntry(
                user_id=user_id,
                habit_id=habit_id,
                date=today,
                answer="yes",
                ts_utc=now_iso_utc(),
                src=src,
            )
        )
        h.streak = new_streak
        h.xp = new_xp
        h.last_answer_date = today
        # Reset snooze allowance for next day automatically when date changes; here only mark usage status unaffected
        self.habits.update(h)

        # Emit analytics event
        if self.events:
            self.events.emit(
                event="answer_yes",
                user_id=user_id,
                habit_id=habit_id,
                payload={"streak": h.streak, "xp": h.xp, "src": src},
            )

        # Unlock check
        unlock = rules.should_unlock_slot(h.xp, h.streak)
        if unlock:
            # In MVP we only emit event; integration layer will send UNLOCK message
            _ = UnlockEvent(reason=("xp" if h.xp >= 50 else "streak"))
            if self.events:
                self.events.emit(
                    event="slot_unlocked",
                    user_id=user_id,
                    habit_id=habit_id,
                    payload={"reason": ("xp" if h.xp >= 50 else "streak")},
                )

        return CompleteResult(already_marked=False, streak=h.streak, xp_total=h.xp)

    async def mark_no(self, user_id: int, habit_id: int) -> NoResult:
        h = self.habits.get(user_id, habit_id)
        if not h or not h.active:
            return NoResult(already_marked=True)

        today = today_ymd()
        if h.last_answer_date == today:
            return NoResult(already_marked=True)

        # NO resets streak
        self.logs.upsert_answer(
            LogEntry(
                user_id=user_id,
                habit_id=habit_id,
                date=today,
                answer="no",
                ts_utc=now_iso_utc(),
                src="regular",
            )
        )
        h.streak = 0
        h.last_answer_date = today
        self.habits.update(h)

        if self.events:
            self.events.emit(event="answer_no", user_id=user_id, habit_id=habit_id, payload={})

        return NoResult(already_marked=False)

    # ---- Snooze ----
    async def can_snooze_today(self, h: Habit, today: str) -> bool:
        return rules.can_snooze(today, h.snooze_date, h.snooze_used)

    async def mark_snoozed(self, h: Habit, today: str) -> None:
        h.snooze_used = True
        h.snooze_date = today
        self.habits.update(h)
