-- Product analytics events (minimal schema)
CREATE TABLE IF NOT EXISTS product_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts_utc TEXT NOT NULL,             -- ISO timestamp
  user_id INTEGER,                  -- nullable if not applicable
  habit_id INTEGER,                 -- nullable
  event TEXT NOT NULL,              -- e.g., 'habit_created','reminder_sent','answer_yes','slot_unlocked'
  payload TEXT                      -- JSON string with arbitrary details
);

INSERT INTO schema_migrations(version) VALUES ('002_events');