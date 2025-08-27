from __future__ import annotations
from typing import List
from datetime import date, timedelta
from app.repositories.base import HabitRepo, LogRepo
from app.services.types import WeeklyHabitStats

class StatsService:
    def __init__(self, habits: HabitRepo, logs: LogRepo):
        self.habits = habits
        self.logs = logs

    async def weekly_stats(self, user_id: int) -> List[WeeklyHabitStats]:
        # MVP: count last 7 days per habit
        today = date.today()
        start = (today - timedelta(days=6)).isoformat()
        habits = self.habits.list_for_user(user_id)
        out: List[WeeklyHabitStats] = []
        for h in habits:
            # simple count using last N rows; in real impl filter by date range
            logs = self.logs.get_last_days(user_id, h.habit_id, 7)
            done = sum(1 for e in logs if e.answer == 'yes')
            out.append(WeeklyHabitStats(habit_id=h.habit_id, name=h.name, done=done, period=7, streak=h.streak, xp=h.xp))
        return out