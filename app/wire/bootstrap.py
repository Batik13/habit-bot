from __future__ import annotations

from typing import Optional

from telegram.ext import Application, ApplicationBuilder

from app.handlers.router import register_handlers
from app.repositories.db import DB
from app.repositories.sqlite_repo import SQLiteUserRepo, SQLiteHabitRepo, SQLiteLogRepo
from app.services.habit_service import HabitService
from app.services.reminder_service import ReminderService
from app.services.stats_service import StatsService
from app.scheduler.scheduler import Scheduler
from app.analytics.events import Events


class Services:
    def __init__(
        self,
        habit: HabitService,
        reminder: ReminderService,
        stats: StatsService,
        events: Optional[Events] = None,
    ):
        self.habit = habit
        self.reminder = reminder
        self.stats = stats
        self.events = events


async def build_tg_application(bot_token: str) -> Application:
    app = ApplicationBuilder().token(bot_token).build()
    await register_handlers(app)
    return app


async def bootstrap_application(bot_token: str):
    # Build PTB Application
    app = await build_tg_application(bot_token)

    # DB + repos
    db = DB()
    users = SQLiteUserRepo(db)
    habits = SQLiteHabitRepo(db)
    logs = SQLiteLogRepo(db)

    # Scheduler on JobQueue
    scheduler = Scheduler(app=app, habits=habits)

    # Analytics
    events = Events(db)

    # Services
    habit = HabitService(users, habits, logs, events=events)
    reminder = ReminderService(db, scheduler)
    stats = StatsService(habits, logs)

    services = Services(habit=habit, reminder=reminder, stats=stats, events=events)

    # Expose for handlers
    app.bot_data["services"] = services

    return app, services
