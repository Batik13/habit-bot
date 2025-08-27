from __future__ import annotations
from app.domain.rules import xp_for

class XpService:
    def xp_for_answer(self, answer: str) -> int:
        return xp_for(answer)