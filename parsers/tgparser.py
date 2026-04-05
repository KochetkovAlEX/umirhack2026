import asyncio
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

tg_urls = [
    "https://t.me/s/etorostov",
    "https://t.me/s/rostov_glavniy",
    "https://t.me/s/news161ru",
    "https://t.me/s/privet_rostov_ru",
    "https://t.me/s/rostov_smi",
    "https://t.me/s/glavnyi_rostov",
    "https://t.me/s/konstantinovsk161",
    "https://t.me/s/smkmain",
    "https://t.me/s/bloknot_morozovsk",
    "https://t.me/s/millerovo_live",
    "https://t.me/s/sulinnews",
    "https://t.me/s/aksayland",
    "https://t.me/s/Aksay_v_detalyh",
    "https://t.me/s/salsk_glavnyi",
    "https://t.me/s/kalitvatoday",
    "https://t.me/s/belka_kalitva",
    "https://t.me/s/shakhty_official",
    "https://t.me/s/rushahty",
    "https://t.me/s/taganrog_chp61",
    "https://t.me/s/Novoshakhtinsk61",
    "https://t.me/s/novochtoday",
    "https://t.me/s/online_kamensk",
    "https://t.me/s/overhear_vkamenske, https://t.me/s/bloknot_vdonsk1"
    "https://t.me/s/my_bataysk",
    "https://t.me/s/azov_v_kurse",
    "https://t.me/s/azovnews161",
]


async def parse_telegram(urls=tg_urls, limit_posts: int = 60):
    results = []
    news_number = 0
    for url in urls:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }

            r = requests.get(url, timeout=10, headers=headers)
            soup = BeautifulSoup(r.text, "lxml")

            messages = soup.find_all("div", class_="tgme_widget_message")
            if not messages:
                print(f"Не полчается спарсить: {url}")
                continue

            messages = messages[-limit_posts:]

            for msg in messages:
                news_number += 1
                text_div = msg.find("div", class_="tgme_widget_message_text")
                content = text_div.get_text(separator=" ").strip() if text_div else ""

                views = msg.find("span", class_="tgme_widget_message_views").get_text()

                pub_date = datetime.now()
                time_tag = msg.find("time")
                if time_tag and "datetime" in time_tag.attrs:
                    pub_date = datetime.fromisoformat(
                        time_tag["datetime"].replace("Z", "+00:00")
                    )

                reactions_wrap = msg.find("div", class_="tgme_widget_message_reactions")
                total_reactions = 0
                reactions_wrap = msg.find("div", class_="tgme_widget_message_reactions")
                if reactions_wrap:
                    for span in reactions_wrap.find_all("span", class_="tgme_reaction"):
                        count_txt = span.get_text(strip=True)
                        if "K" in count_txt.upper():
                            num = float(
                                count_txt.upper().replace("K", "").replace(",", ".")
                            )
                            total_reactions += int(num * 1000)
                        else:
                            digits = "".join(filter(str.isdigit, count_txt))
                            if digits:
                                total_reactions += int(digits)

                results.append(
                    {
                        # "id": news_number,
                        "source": url,
                        "source_type": "Парсинг из Телеграмма",
                        "date": pub_date,
                        "title": " ".join(content[:150].split())
                        if content
                        else "Нет текста",
                        "text": " ".join(content.split()),
                        "url": url,
                        "activity": None,
                        "views": int(views),
                        "likes": total_reactions,
                    }
                )

        except Exception as e:
            print(f"Ошибка при парсинге для {url}: {e}")
            continue

    return results
