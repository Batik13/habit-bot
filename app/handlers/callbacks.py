from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from app.ui.texts import RECORDED_YES, RECORDED_NO, SNOOZE_OK, SNOOZE_DENY, ALREADY_MARKED

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cq = update.callback_query
    if not cq or not cq.data:
        return

    try:
        prefix, habit_id_str, action = cq.data.split(":", 2)
        if prefix != "ans":
            return
        habit_id = int(habit_id_str)
    except Exception:
        await cq.answer("Некорректные данные", show_alert=True)
        return

    services = context.application.bot_data.get("services")

    if action == "yes":
        result = await services.habit.complete_today(user_id=update.effective_user.id, habit_id=habit_id, src="regular")
        # result has fields: already_marked, xp_total, streak
        if result.already_marked:
            await cq.answer(ALREADY_MARKED, show_alert=True)
        else:
            await cq.edit_message_text(RECORDED_YES.format(streak=result.streak, xp=result.xp_total))
        return

    if action == "no":
        result = await services.habit.mark_no(user_id=update.effective_user.id, habit_id=habit_id)
        if result.already_marked:
            await cq.answer(ALREADY_MARKED, show_alert=True)
        else:
            await cq.edit_message_text(RECORDED_NO)
        return

    if action == "snooze":
        ok = await services.reminder.snooze(user_id=update.effective_user.id, habit_id=habit_id, hours=2)
        if ok:
            await cq.edit_message_text(SNOOZE_OK)
        else:
            await cq.answer(SNOOZE_DENY, show_alert=True)
        return


def callbacks_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(on_button, pattern=r"^ans:\d+:(yes|no|snooze)$")