from __future__ import annotations
from typing import Callable, Awaitable
from app.repositories.db import DB
from app.config.constants import SNOOZE_DELAY_SECONDS

# We expect an injected scheduler with two methods
class SchedulerProto:
    async def schedule_daily(self, user_id: int, habit_id: int, hour: int, minute: int, cb: Callable[..., Awaitable[None]] | None = None): ...
    async def schedule_once_in(self, user_id: int, habit_id: int, seconds: int, cb: Callable[..., Awaitable[None]] | None = None): ...

class ReminderService:
    def __init__(self, db: DB, scheduler: SchedulerProto):
        self.db = db
        self.scheduler = scheduler

    async def schedule_daily(self, user_id: int, habit_id: int, hour: int, minute: int):
        # In MVP, we only schedule; the actual callback sending is wired at router level
        await self.scheduler.schedule_daily(user_id=user_id, habit_id=habit_id, hour=hour, minute=minute, cb=None)

    async def snooze(self, user_id: int, habit_id: int, hours: int = 2) -> bool:
        # Wrapper: convert hours to seconds; actual allowance checked by HabitService before calling here
        seconds = hours * 3600
        await self.scheduler.schedule_once_in(user_id=user_id, habit_id=habit_id, seconds=seconds, cb=None)
        return True