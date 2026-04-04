from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

router = Router()


@router.callback_query(F.data.contains("topic_"))
async def send_news_by_topic(callback: CallbackQuery) -> None:
    await callback.answer()
