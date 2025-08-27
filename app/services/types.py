from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class CompleteResult:
    already_marked: bool
    streak: int
    xp_total: int

@dataclass
class NoResult:
    already_marked: bool

@dataclass
class WeeklyHabitStats:
    habit_id: int
    name: str
    done: int
    period: int
    streak: int
    xp: int