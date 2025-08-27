-- 001_init.sql

-- Users
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    tz          TEXT NOT NULL DEFAULT 'Etc/UTC',
    locale      TEXT NOT NULL DEFAULT 'ru',
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Habits
CREATE TABLE IF NOT EXISTS habits (
    habit_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    name         TEXT NOT NULL,
    hour         INTEGER NOT NULL CHECK (hour >= 0 AND hour < 24),
    minute       INTEGER NOT NULL CHECK (minute >= 0 AND minute < 60),
    xp           INTEGER NOT NULL DEFAULT 0,
    streak       INTEGER NOT NULL DEFAULT 0,
    last_answer_date TEXT,
    snooze_date  TEXT,
    snooze_used  INTEGER NOT NULL DEFAULT 0,   -- use 0/1 as booleans
    active       INTEGER NOT NULL DEFAULT 1,
    created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE INDEX IF NOT EXISTS idx_habits_user_id ON habits(user_id);

-- Logs (one per habit per day)
CREATE TABLE IF NOT EXISTS logs (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL,
    habit_id  INTEGER NOT NULL,
    date      TEXT NOT NULL, -- YYYY-MM-DD
    answer    TEXT NOT NULL CHECK (answer IN ('yes','no','skip')),
    ts_utc    TEXT NOT NULL,
    src       TEXT NOT NULL DEFAULT 'regular',
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(habit_id) REFERENCES habits(habit_id),
    UNIQUE(user_id, habit_id, date)
);

CREATE INDEX IF NOT EXISTS idx_logs_user ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_habit ON logs(habit_id);

-- Schema migrations tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
