from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.database import request as database_crud
from bot.keyboard import inline

router = Router()


@router.message(CommandStart())
async def greeting(message: Message) -> None:
    await message.answer_photo(
        photo="https://png.klev.club/1733-novosti.html", reply_markup=inline.inline_kb
    )


@router.message(Command("news"))
async def send_news(message: Message) -> None:
    pass


@router.message(Command("db"))
async def send_help(message: Message) -> None:
    await database_crud.reload_database()
    await message.answer("База данных успешно обновлена!")
