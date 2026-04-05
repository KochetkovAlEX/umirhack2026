import asyncio
from datetime import datetime

from playwright.async_api import async_playwright

TARGET_CHATS = {
    "Семикаракорск": ["https://web.telegram.org/k/#@znakomstva_obshchenietx"],
    "Зерноград": [
        "https://web.telegram.org/k/#@znakomstva_obshcheniesz",
    ],
    "Ростов": [
        "https://web.telegram.org/k/#@proletarsk0",
        "https://web.telegram.org/k/#@poskonstantinovskiy ",
        "https://web.telegram.org/k/#@zksvoboda",
        "https://web.telegram.org/k/#@krasniyaksai",
    ],
    "Белая Калитва": ["https://web.telegram.org/k/#@BK_Chat161"],
    "Аксай": ["https://web.telegram.org/k/#@aksay_chat"],
    "Новочеркасск": ["https://web.telegram.org/k/#@chatnovochcity"],
    "Каменск-Шахтинский": ["https://web.telegram.org/k/#@online_kamensk"],
    "Донецк": ["https://web.telegram.org/k/#@anondonetsk"],
    "Волгодонск": ["https://web.telegram.org/k/#@znakomstva_obshchenieet"],
    "Батайск": ["https://web.telegram.org/k/#@znakomstva_obshcheniefq"],
    "Азов": ["https://web.telegram.org/k/#@azov_v_kurse"],
}


semaphore = asyncio.Semaphore(4)


async def parse_url(p, city, url, results_list):
    async with semaphore:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(storage_state="parsers/auth.json")
        page = await context.new_page()

        print(f"Начат парсинг города {city}, ссылка: {url}")

        try:
            await page.goto(url)
            await page.wait_for_selector(".bubble-content", timeout=30000)
            await asyncio.sleep(2)

            await page.mouse.move(600, 400)
            await page.evaluate("""
                const scrollable = document.querySelector('.MessageList, .messages-container, .bubbles-inner, .scrollable-list');
                if (scrollable) {
                    scrollable.scrollBy(0, -5000);
                }
            """)
            await asyncio.sleep(2)

            messages = await page.query_selector_all(".bubble-content")
            count = messages[-20:]

            for msg in count:
                time_el = await msg.query_selector(".time-inner")
                all_text_elements = await msg.query_selector_all(
                    ".translatable-message"
                )

                final_text = ""
                for el in all_text_elements:
                    is_reply = await el.evaluate(
                        "(node) => !!node.closest('.reply, .reply-wrapper, .quoted-message')"
                    )
                    if not is_reply:
                        raw_text = await el.inner_text()
                        final_text = " ".join(raw_text.split())
                        break

                if final_text:
                    time_raw = await time_el.get_attribute("title") if time_el else None
                    try:
                        if time_raw:
                            clean_time = time_raw.split("Edited: ")[-1].strip()
                            dt_object = datetime.strptime(
                                clean_time, "%d %B %Y, %H:%M:%S"
                            )

                        else:
                            dt_object = datetime.now()
                    except Exception:
                        dt_object = datetime.now()

                    results_list.append(
                        {
                            "city": city,
                            "date": dt_object,
                            "text": final_text,
                            "url": url,
                        }
                    )
        except Exception as e:
            print(f"Пропуск {url} из-за ошибки: {e}")
        finally:
            await browser.close()


async def use_auth(chats_dict):
    async with async_playwright() as p:
        results = []
        tasks = []

        for city, urls in chats_dict.items():
            for url in urls:
                tasks.append(parse_url(p, city, url, results))

        await asyncio.gather(*tasks)

        # for i, res in enumerate(results, 1):
        #     res["id"] = i

        return results


if __name__ == "__main__":
    final_results = asyncio.run(use_auth(TARGET_CHATS))
    print(final_results)

# async def use_auth(chats_dict):
#     async with async_playwright() as p:
#         results = []
#         message_count = 0

#         for city, urls in chats_dict.items():
#             for url in urls:
#                 browser = await p.chromium.launch(headless=True)
#                 context = await browser.new_context(storage_state="auth.json")
#                 page = await context.new_page()

#                 print(f"Парсинг города {city}, ссылка: {url}")

#                 try:
#                     await page.goto(url)
#                     await page.wait_for_selector(".bubble-content", timeout=15000)
#                     await asyncio.sleep(2)

#                     await page.mouse.move(600, 400)

#                     await page.evaluate("""
#                         const scrollable = document.querySelector('.MessageList, .messages-container, .bubbles-inner');
#                         if (scrollable) {
#                             scrollable.scrollBy(0, -5000);
#                         }
#                     """)
#                     await asyncio.sleep(2)

#                     messages = await page.query_selector_all(".bubble-content")
#                     count = messages[-20:]

#                     for msg in count:
#                         time_el = await msg.query_selector(".time-inner")
#                         all_text_elements = await msg.query_selector_all(".translatable-message")

#                         final_text = ""
#                         for el in all_text_elements:
#                             is_reply = await el.evaluate("(node) => !!node.closest('.reply, .reply-wrapper, .quoted-message')")
#                             if not is_reply:
#                                 raw_text = await el.inner_text()
#                                 final_text = " ".join(raw_text.split())
#                                 break

#                         if final_text:
#                             message_count += 1
#                             time_raw = await time_el.get_attribute("title") if time_el else None

#                             try:
#                                 if time_raw:
#                                     clean_time = time_raw.split("Edited: ")[-1].strip()
#                                     dt_object = datetime.strptime(clean_time, "%d %B %Y, %H:%M:%S")
#                                     time_val = dt_object.strftime("%d.%m.%y %H:%M")
#                                 else:
#                                     time_val = "00.00.00 00:00"
#                             except:
#                                 time_val = "Error Date"

#                             results.append({
#                                 'id': message_count,
#                                 'city': city,
#                                 'date': time_val,
#                                 'text': final_text,
#                                 'url': url
#                             })

#                     await browser.close()

#                 except Exception as e:
#                     print(f"Пропуск {url} из-за ошибки: {e}")
#                     try:
#                         await browser.close()
#                     except:
#                         pass
#                     continue

#         return results


# if __name__ == "__main__":
#     final_results = asyncio.run(use_auth(TARGET_CHATS))
#     print(f"{final_results}")
