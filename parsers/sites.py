import asyncio
from datetime import datetime
from email.utils import parsedate_to_datetime

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

months = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]
days = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
]

months_replace = {
    "января": "1",
    "февраля": "2",
    "марта": "3",
    "апреля": "4",
    "мая": "5",
    "июня": "6",
    "июля": "7",
    "августа": "8",
    "сентября": "9",
    "октября": "10",
    "ноября": "11",
    "декабря": "12",
}


async def get_urls(session: aiohttp.ClientSession, url: str) -> str:
    async with session.get(url, timeout=10) as response:
        return await response.text()


async def parse_rss() -> list:
    urls = [
        "https://news-don.ru/rss.xml",
        "https://161.ru/rss-feeds/rss.xml",
        "https://donday.ru/rss.xml",
    ]
    user_agent = UserAgent(browsers=["Chrome", "Firefox"])
    headers = {"User-Agent": f"{user_agent.random}"}

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for url in urls:
            try:
                tasks.append(get_urls(session, url))
            except Exception as ex:
                print(f"Ошибка загрузки {url}: {ex}")

        pages = await asyncio.gather(*tasks, return_exceptions=True)

    results = []
    news_number = 0
    for url, content in zip(urls, pages):
        if isinstance(content, Exception):
            print(f"Ошибка загрузки {url}: {content}")
            continue
        try:
            feed = feedparser.parse(content)
            for entry in feed.entries:
                news_number += 1
                date = parsedate_to_datetime(entry.get("published"))

                results.append(
                    {
                        # "id": news_number,
                        "source": entry.get("link"),
                        "source_type": "Новостное издание",
                        "category": entry.get("category"),
                        "date": date,
                        "title": entry.get("title"),
                        "text": BeautifulSoup(
                            entry.get("description"), "html.parser"
                        ).get_text(strip=True),
                        "url": url,
                    }
                )
        except Exception as ex:
            print(f"Ошибка парсинга контента из {url}: {ex}")

    return results
