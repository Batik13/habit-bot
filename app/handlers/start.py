from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
from app.handlers.states import Onboarding
from app.ui.texts import START_RULES, ASK_TIME, CONFIRM_HABIT

# Expect services injected elsewhere: context.application.bot_data['services']

def start_handler() -> CommandHandler:
    return CommandHandler("start", start)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(START_RULES)
    context.user_data["onboarding"] = {}
    return Onboarding.AWAITING_HABIT_NAME

async def receive_habit_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = (update.effective_message.text or '').strip()
    if not (1 <= len(name) <= 50):
        await update.effective_message.reply_text("Название 1–50 символов. Введи снова.")
        return Onboarding.AWAITING_HABIT_NAME

    context.user_data["onboarding"]["name"] = name
    await update.effective_message.reply_text(ASK_TIME.format(habit=name))
    return Onboarding.AWAITING_HABIT_TIME

async def receive_habit_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_str = (update.effective_message.text or '').strip()
    import re
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        await update.effective_message.reply_text("Формат времени HH:MM, пример 08:30. Введи снова.")
        return Onboarding.AWAITING_HABIT_TIME

    hour, minute = map(int, time_str.split(":"))
    if not (0 <= hour < 24 and 0 <= minute < 60):
        await update.effective_message.reply_text("Часы 00–23, минуты 00–59. Попробуй ещё раз.")
        return Onboarding.AWAITING_HABIT_TIME

    name = context.user_data["onboarding"]["name"]

    # Call service to persist + schedule
    services = context.application.bot_data.get("services")
    habit_id = await services.habit.add_habit(user_id=update.effective_user.id, name=name, hour=hour, minute=minute)
    await services.reminder.schedule_daily(user_id=update.effective_user.id, habit_id=habit_id, hour=hour, minute=minute)

    await update.effective_message.reply_text(CONFIRM_HABIT.format(habit=name, time=time_str))
    context.user_data.pop("onboarding", None)
    return ConversationHandler.END


def onboarding_conv() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[start_handler()],
        states={
            Onboarding.AWAITING_HABIT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_habit_name)],
            Onboarding.AWAITING_HABIT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_habit_time)],
        },
        fallbacks=[],
    )