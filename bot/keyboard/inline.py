from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Новости за сегодня", callback_data="today"),
            InlineKeyboardButton(text="Новости за неделю", callback_data="week")
        ],
        [
            InlineKeyboardButton(text="Десять самых актуальных новостей", callback_data="ten_popular")
        ]
    ]
)

cancel_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Назад", callback_data="cancel")],
    ]
)
