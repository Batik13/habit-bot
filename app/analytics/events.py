from __future__ import annotations
import json
from dataclasses import asdict, is_dataclass
from typing import Any, Mapping
from app.repositories.db import DB
from app.utils.time import now_iso_utc

class Events:
    def __init__(self, db: DB):
        self.db = db

    def emit(self, *, event: str, user_id: int | None = None, habit_id: int | None = None, payload: Mapping[str, Any] | None = None) -> None:
        data = json.dumps(payload or {}, ensure_ascii=False)
        self.db.conn.execute(
            "INSERT INTO product_events(ts_utc, user_id, habit_id, event, payload) VALUES (?,?,?,?,?)",
            (now_iso_utc(), user_id, habit_id, event, data),
        )
        self.db.commit()