from datetime import datetime

import pandas as pd
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.database import request as database_crud
from bot.database.request import get_all_data
from models.main import get_results
from parsers import sites, tg_groups_parser, tgparser, vkpars

router = Router()


@router.message(CommandStart())
async def greeting(message: Message) -> None:
    """Стартовая функция"""
    await message.answer("Сначала '/db', потом '/news', а затем '/top'")


@router.message(Command("news"))
async def add_news(message: Message) -> None:
    """Функция заполнения базы данных"""
    start_time = datetime.now()
    sites_data = await sites.parse_rss()
    vk_data = await vkpars.find_groups_by_name()
    tg_group_data = await tg_groups_parser.use_auth(tg_groups_parser.TARGET_CHATS)
    tg_data = await tgparser.parse_telegram()
    for item in sites_data:
        await database_crud.insert_data(item)

    for item in vk_data:
        await database_crud.insert_data(item)

    for item in tg_group_data:
        await database_crud.insert_data(item)

    for item in tg_data:
        await database_crud.insert_data(item)

    end_time = datetime.now()
    await message.answer(f"Данные добавлены. Время: {end_time - start_time}")


@router.message(Command("db"))
async def send_help(message: Message) -> None:
    """Функция пересоздания базы данных"""
    await database_crud.reload_database()
    await message.answer("База данных успешно обновлена!")


@router.message(Command("top"))
async def show_top(message: Message):
    await message.answer("🔄 Анализирую данные...")

    data = await get_all_data()
    data = [
        {
            "title": item.title,
            "text": item.text,
            "date": item.date,
            "activity": item.activity,
            "url": item.url,
            "source": item.source,
        }
        for item in data
    ]

    df = await get_results(data)

    if df.empty:
        await message.answer("📭 Тем не найдено")
        return

    for _, row in df.head(10).iterrows():
        text = (
            f"📍 <b>{row['Name'].upper()}</b>\n"
            f"🔥 Индекс критичности: {row['idx']:.2f}\n"
            f"📈 Статистика:\n"
            f"   • Сообщений: {int(row['n'])} | За 2ч: {int(row['v'])}\n"
            f"   • Негатив: {row['e']:.2f} | Срочность: {row['u']:.1f}\n"
            f"📝 Сообщения:\n"
        )

        for i, msg in enumerate(row["messages"][:3]):
            msg_str = str(msg).strip()
            if not msg_str or msg_str.lower() == "nan":
                msg_str = "..."
            short_msg = msg_str[:80] + "..." if len(msg_str) > 80 else msg_str
            text += f"   {i + 1}. {short_msg}\n"
            links = row.get("links", [])
            if i < len(links) and links[i]:
                text += f"      🔗 <a href='{links[i]}'>Ссылка</a>\n"

        if row["n"] > 3:
            text += f"\n   ... и еще {int(row['n']) - 3} сообщений"

        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)
