import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.database import request as database_crud
from bot.database.request import get_topics
from bot.keyboard import inline
from parsers import sites, vkpars

router = Router()


@router.message(CommandStart())
async def greeting(message: Message) -> None:
    """Стартовая функция"""
    topics = await get_topics()
    buttons_or_None = (
        inline.generate_inline_kb(topics) if topics else inline.NONE_BUTTON
    )
    await message.answer_photo(
        photo="https://png.klev.club/1733-novosti.html",
        reply_markup=buttons_or_None,
    )


@router.message(Command("news"))
async def add_news(message: Message) -> None:
    """Функция заполнения базы данных"""
    sites_data = await sites.parse_rss()
    vk_data = await vkpars.find_groups_by_name()
    for item in sites_data:
        await database_crud.insert_data(item)

    await message.answer("Данные СМИ добавлены")

    for item in vk_data:
        await database_crud.insert_data(item)

    await message.answer("Данные чатов добавлены")


@router.message(Command("db"))
async def send_help(message: Message) -> None:
    """Функция пересоздания базы данных"""
    await database_crud.reload_database()
    await message.answer("База данных успешно обновлена!")
