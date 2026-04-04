import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def generate_inline_kb(topics: list):
    """Функция для создания кнопок"""
    builder = InlineKeyboardBuilder()
    random_five = random.sample(topics, 5)
    for topic in random_five:
        builder.button(
            text=f"Актуальное по теме {topic}",
            callback_data=f"topic_{topic}",
        )

    builder.adjust(1)
    return builder.as_markup()


CANCEL_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Назад", callback_data="cancel")]]
)


NONE_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="Проблем нет", callback_data="pass")]]
)
