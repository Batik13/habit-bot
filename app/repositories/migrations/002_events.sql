-- 002_events.sql
CREATE TABLE IF NOT EXISTS product_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc TEXT NOT NULL,             -- ISO timestamp
  user_id INTEGER,                  -- nullable
  habit_id INTEGER,                 -- nullable
  event TEXT NOT NULL,              -- e.g., 'habit_created','reminder_sent','answer_yes','slot_unlocked'
  payload TEXT
);
