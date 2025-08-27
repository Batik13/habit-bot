from app.domain.rules import next_streak, xp_for, should_unlock_slot, can_snooze
from app.config.constants import XP_PER_YES


def test_xp_for_yes_and_no():
    assert xp_for('yes') == XP_PER_YES
    assert xp_for('no') == 0
    assert xp_for('skip') == 0


def test_streak_yes_after_yes_increments():
    assert next_streak(prev_streak=3, answered_yesterday_yes=True, answer_today_yes=True) == 4


def test_streak_yes_after_no_resets_to_one():
    assert next_streak(prev_streak=5, answered_yesterday_yes=False, answer_today_yes=True) == 1


def test_streak_no_resets_to_zero():
    assert next_streak(prev_streak=7, answered_yesterday_yes=True, answer_today_yes=False) == 0


def test_should_unlock_by_xp():
    assert should_unlock_slot(xp=50, streak=0) is True
    assert should_unlock_slot(xp=49, streak=0) is False


def test_should_unlock_by_streak():
    assert should_unlock_slot(xp=0, streak=7) is True
    assert should_unlock_slot(xp=0, streak=6) is False


def test_can_snooze_first_time_today():
    assert can_snooze(today_date='2025-08-27', snooze_date='2025-08-27', snooze_used=False) is True


def test_can_snooze_not_more_than_once_per_day():
    assert can_snooze(today_date='2025-08-27', snooze_date='2025-08-27', snooze_used=True) is False


def test_can_snooze_new_day_resets_allowance():
    assert can_snooze(today_date='2025-08-28', snooze_date='2025-08-27', snooze_used=True) is True