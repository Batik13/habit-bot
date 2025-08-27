from __future__ import annotations

# Project‑wide constants matching the spec
DEFAULT_TZ = "Etc/UTC" # personalize later
XP_PER_YES = 10
# Snooze rules (MVP): only 1 per day per habit, fixed delay 2h
SNOOZE_DELAY_SECONDS = 2 * 60 * 60
SNOOZE_PER_DAY = 1

# Unlock logic thresholds
UNLOCK_XP_THRESHOLD = 50
UNLOCK_STREAK_THRESHOLD = 7