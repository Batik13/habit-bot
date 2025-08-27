from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from app.ui.texts import STATS_EMPTY, STATS_HEADER, STATS_LINE

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    services = context.application.bot_data.get("services")
    data = await services.stats.weekly_stats(user_id=update.effective_user.id)
    if not data:
        await update.effective_message.reply_text(STATS_EMPTY)
        return

    lines = [STATS_HEADER]
    for h in data:
        lines.append(STATS_LINE.format(habit=h.name, done=h.done, period=h.period, streak=h.streak, xp=h.xp))
    await update.effective_message.reply_text("".join(lines))


def stats_handler() -> CommandHandler:
    return CommandHandler("stats", stats)