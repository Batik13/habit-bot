from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import time as dtime, datetime, timezone

from telegram.ext import Application
# Если используете типизацию контекста PTB v20+, можно раскомментировать:
# from telegram.ext import ContextTypes

from app.repositories.base import HabitRepo
from app.ui.keyboards import question_kb, snooze_kb
from app.ui.texts import QUESTION
from app.analytics.events import Events


@dataclass
class Scheduler:
    app: Application
    habits: HabitRepo
    # Необязательная прямая инъекция Events; если не передана, попробуем достать через app.bot_data['services'].events
    events: Optional[Events] = None

    async def schedule_daily(self, user_id: int, habit_id: int, hour: int, minute: int, cb=None):
        """
        Планирует ежедневное напоминание на указанный час:минуту (UTC).
        """
        name = f"daily_{user_id}_{habit_id}"
        for j in self.app.job_queue.get_jobs_by_name(name):
            j.schedule_removal()

        # MVP: DEFAULT_TZ = UTC
        t = dtime(hour=hour, minute=minute, tzinfo=timezone.utc)

        # коллбек сам достанет привычку и отправит вопрос
        self.app.job_queue.run_daily(
            self._daily_callback,
            time=t,
            name=name,
            data={"user_id": user_id, "habit_id": habit_id, "snooze": False},
        )

    async def schedule_once_in(self, user_id: int, habit_id: int, seconds: int, cb=None):
        """
        Планирует одноразовое "дремни" напоминание через seconds (UTC).
        """
        suffix = int(datetime.now(tz=timezone.utc).timestamp())
        name = f"snooze_{user_id}_{habit_id}_{suffix}"

        self.app.job_queue.run_once(
            self._snooze_callback,
            when=seconds,
            name=name,
            data={"user_id": user_id, "habit_id": habit_id, "snooze": True},
        )

    async def _send_question(self, chat_id: int, habit_id: int, snoozed: bool):
        """
        Отправляет пользователю вопрос по привычке и, если доступна аналитика, эмитит reminder_sent.
        """
        h = self.habits.get(chat_id, habit_id)
        if not h or not h.active:
            return

        kb = snooze_kb(habit_id) if snoozed else question_kb(habit_id)
        await self.app.bot.send_message(
            chat_id=chat_id,
            text=QUESTION.format(habit=h.name),
            reply_markup=kb,
        )

        # ---- Analytics: reminder_sent
        # 1) приоритет — инъекция через self.events
        events = self.events

        # 2) иначе пробуем достать services.events из bot_data (как вы и предлагали)
        if events is None:
            services = self.app.bot_data.get("services") if isinstance(self.app.bot_data, dict) else None
            events = getattr(services, "events", None) if services is not None else None

        # 3) как fallback, если кто-то положил напрямую app.bot_data['events']
        if events is None and isinstance(self.app.bot_data, dict):
            maybe_events = self.app.bot_data.get("events")
            events = maybe_events if isinstance(maybe_events, Events) else None

        try:
            if events is not None:
                events.emit(
                    event="reminder_sent",
                    user_id=chat_id,
                    habit_id=habit_id,
                    payload={"snooze": snoozed},
                )
        except Exception:
            # Защищаем основной флоу: ошибки аналитики не должны ронять доставку сообщений
            pass

    # В PTB v20+ коллбек получает CallbackContext; держим подпись гибкой для совместимости
    async def _daily_callback(self, ctx):
        data = getattr(ctx.job, "data", {}) or {}
        await self._send_question(
            chat_id=data.get("user_id"),
            habit_id=data.get("habit_id"),
            snoozed=False,
        )

    async def _snooze_callback(self, ctx):
        data = getattr(ctx.job, "data", {}) or {}
        await self._send_question(
            chat_id=data.get("user_id"),
            habit_id=data.get("habit_id"),
            snoozed=True,
        )
