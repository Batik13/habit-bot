from __future__ import annotations
from app.repositories.db import DB
from app.repositories.sqlite_repo import SQLiteUserRepo, SQLiteHabitRepo, SQLiteLogRepo
from app.services.habit_service import HabitService
from app.services.reminder_service import ReminderService
from app.services.stats_service import StatsService
from app.services.xp_service import XpService

class Container:
    def __init__(self, scheduler):
        self.db = DB()
        self.users = SQLiteUserRepo(self.db)
        self.habits = SQLiteHabitRepo(self.db)
        self.logs = SQLiteLogRepo(self.db)
        self.xp = XpService()
        self.reminder = ReminderService(self.db, scheduler)
        self.habit = HabitService(self.users, self.habits, self.logs)
        self.stats = StatsService(self.habits, self.logs)