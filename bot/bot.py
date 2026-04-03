import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.database.request import reload_database
from bot.handlers import commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher(storage=MemoryStorage())


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MARKDOWN"))
    dp.include_router(commands.router)
    await dp.start_polling(bot)
