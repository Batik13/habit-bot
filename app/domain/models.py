from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: int
    tz: str = "Etc/UTC" # personalize later
    locale: str = "ru"

@dataclass
class Habit:
    habit_id: int
    user_id: int
    name: str
    hour: int
    minute: int
    xp: int = 0
    streak: int = 0
    last_answer_date: Optional[str] = None # 'YYYY-MM-DD'
    snooze_date: Optional[str] = None # for controlling 1 snooze/day
    snooze_used: bool = False
    active: bool = True

@dataclass
class LogEntry:
    user_id: int
    habit_id: int
    date: str # 'YYYY-MM-DD'
    answer: str # 'yes' | 'no' | 'skip'
    ts_utc: str # ISO timestamp
    src: str = "regular" # 'regular' | 'snooze'