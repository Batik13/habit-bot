-- Users
CREATE TABLE users (
    user_id     INTEGER PRIMARY KEY,
    tz          NVARCHAR(50) NOT NULL DEFAULT 'Etc/UTC',
    locale      NVARCHAR(10) NOT NULL DEFAULT 'ru',
    created_at  DATETIME NOT NULL DEFAULT GETDATE()
);

-- Habits
CREATE TABLE habits (
    habit_id    INTEGER PRIMARY KEY IDENTITY(1,1),
    user_id     INTEGER NOT NULL,
    name        NVARCHAR(255) NOT NULL,
    hour        INTEGER NOT NULL CHECK (hour >= 0 AND hour < 24),
    minute      INTEGER NOT NULL CHECK (minute >= 0 AND minute < 60),
    xp          INTEGER NOT NULL DEFAULT 0,
    streak      INTEGER NOT NULL DEFAULT 0,
    last_answer_date DATETIME,
    snooze_date DATETIME,
    snooze_used BIT NOT NULL DEFAULT 0,
    active      BIT NOT NULL DEFAULT 1,
    created_at  DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE INDEX idx_habits_user_id ON habits(user_id);

-- Logs (one per habit per day)
CREATE TABLE logs (
    id          INTEGER PRIMARY KEY IDENTITY(1,1),
    user_id     INTEGER NOT NULL,
    habit_id    INTEGER NOT NULL,
    date        DATE NOT NULL, -- YYYY-MM-DD
    answer      NVARCHAR(10) NOT NULL CHECK(answer IN ('yes','no','skip')),
    ts_utc      DATETIME NOT NULL,
    src         NVARCHAR(50) NOT NULL DEFAULT 'regular',
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(habit_id) REFERENCES habits(habit_id),
    CONSTRAINT UQ_logs UNIQUE(user_id, habit_id, date)
);

CREATE INDEX idx_logs_user ON logs(user_id);
CREATE INDEX idx_logs_habit ON logs(habit_id);

-- Schema migrations tracking
CREATE TABLE schema_migrations (
    version NVARCHAR(50) PRIMARY KEY,
    applied_at DATETIME NOT NULL DEFAULT GETDATE()
);

INSERT INTO schema_migrations(version) VALUES ('001_init');