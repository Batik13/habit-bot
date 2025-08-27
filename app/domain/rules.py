from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from app.config.constants import (
    XP_PER_YES,
    UNLOCK_XP_THRESHOLD,
    UNLOCK_STREAK_THRESHOLD,
)

def next_streak(prev_streak: int, answered_yesterday_yes: bool, answer_today_yes: bool) -> int:
    """Compute new streak per spec.
    - If today is not YES -> streak resets to 0
    - If today is YES and yesterday also YES -> prev + 1
    - If today is YES and yesterday not YES -> 1
    """
    if not answer_today_yes:
        return 0
    return prev_streak + 1 if answered_yesterday_yes else 1

def xp_for(answer: str) -> int:
    """Return XP gain for today’s answer.
    MVP: +10 only for 'yes', 0 otherwise.
    """
    return XP_PER_YES if answer == "yes" else 0

def should_unlock_slot(xp: int, streak: int) -> bool:
    """Unlock when XP >= 50 OR streak >= 7 (inclusive)."""
    return (xp >= UNLOCK_XP_THRESHOLD) or (streak >= UNLOCK_STREAK_THRESHOLD)

def can_snooze(today_date: str, snooze_date: Optional[str], snooze_used: bool) -> bool:
    """Allow snooze once per (habit, day). If snooze_date != today, reset allowance.
    Returns True if user can snooze now.
    """
    return (not snooze_used) or (snooze_date != today_date)

# Convenience: a tiny evaluator struct (useful in service tests later)
@dataclass(frozen=True)
class DayEval:
    prev_streak: int
    yesterday_yes: bool
    answer_today: str  # 'yes' | 'no'

    def new_streak(self) -> int:
        return next_streak(self.prev_streak, self.yesterday_yes, self.answer_today == "yes")

    def xp_delta(self) -> int:
        return xp_for(self.answer_today)