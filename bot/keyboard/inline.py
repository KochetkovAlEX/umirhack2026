from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

topics = ["Хакатон1", "Хакатон2", "Хакатон3", "Хакатон4", "Хакатон5"]
# inline_kb = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(
#                 text=f"Десять самых актульаных новостей по теме {topics[0]}",
#                 callback_data=f"{topics[0]}",
#             ),
#         ],
#         [
#             InlineKeyboardButton(
#                 text=f"Десять самых актульаных новостей по теме {topics[1]}",
#                 callback_data=f"{topics[1]}",
#             ),
#         ],
#         [
#             InlineKeyboardButton(
#                 text=f"Десять самых актульаных новостей по теме {topics[2]}",
#                 callback_data=f"{topics[2]}",
#             ),
#         ],
#         [
#             InlineKeyboardButton(
#                 text=f"Десять самых актульаных новостей по теме {topics[3]}",
#                 callback_data=f"{topics[3]}",
#             ),
#         ],
#         [
#             InlineKeyboardButton(
#                 text=f"Десять самых актульаных новостей по теме {topics[4]}",
#                 callback_data=f"{topics[4]}",
#             ),
#         ],
#     ]
# )


def generate_inline_kb(topics: list):
    """Функция для создания кнопок"""
    builder = InlineKeyboardBuilder()
    for topic in topics:
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
