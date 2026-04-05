from aiogram import F, Router
from aiogram.types import CallbackQuery

# from bot.database.request import get_content_by_category
# from bot.keyboard.inline import CANCEL_BUTTON
# from bot.service import message_maker

router = Router()


# @router.callback_query(F.data.contains("topic_"))
# async def send_news_by_topic(callback: CallbackQuery) -> None:
#     topic = callback.data.replace("topic_", "")
#     await callback.answer()
#     data = await get_content_by_category(topic)

#     answer_message = await message_maker.make_new_message(topic, data)
#     # await callback.message.edit_text(
#     #     answer_message, reply_markup=CANCEL_BUTTON, parse_mode="HTML"
#     # )
#     await callback.message.answer(
#         answer_message, reply_markup=CANCEL_BUTTON, parse_mode="HTML"
#     )


@router.callback_query(F.data == "cancel")
async def delete_current_message(callback: CallbackQuery) -> None:
    await callback.message.delete()
    await callback.answer()
