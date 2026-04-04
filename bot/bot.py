import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.handlers import callback, commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())
# На подумать. это нужно решить
# job_store = {"default": SQLAlchemyJobStore("sqlite+aiosqlite:///db.sqlite3")}
# scheduler = AsyncIOScheduler(job_store=job_store)


async def main() -> None:
    """Функция запуска бота"""
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MARKDOWN"))
    dp.include_routers(commands.router, callback.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
