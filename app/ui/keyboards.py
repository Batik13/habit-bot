from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def question_kb(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Да 💪", callback_data=f"ans:{habit_id}:yes"),
            InlineKeyboardButton(text="Нет 😬", callback_data=f"ans:{habit_id}:no"),
            InlineKeyboardButton(text="Напомнить позже", callback_data=f"ans:{habit_id}:snooze"),
        ]
    ])

# Snooze ping without snooze button
def snooze_kb(habit_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="Да 💪", callback_data=f"ans:{habit_id}:yes"),
            InlineKeyboardButton(text="Нет 😬", callback_data=f"ans:{habit_id}:no"),
        ]
    ])