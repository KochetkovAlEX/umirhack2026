import os
import time
from datetime import datetime

import vk_api
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("VKAPI_TOKEN")
query = "Новости Ростов-На-Дону"
seconds_in_day = 24 * 60 * 60
time_threshold = int(time.time()) - seconds_in_day


def get_token_data(TOKEN: str) -> vk_api.vk_api.VkApiMethod:
    vk_session = vk_api.VkApi(token=TOKEN)
    return vk_session.get_api()


def find_groups_by_name():
    vk = get_token_data(TOKEN)
    results = []
    groups = vk.groups.search(q=query, count=7)
    number_list = 0
    for group in groups["items"]:
        group_id = group["id"]
        try:
            wall = vk.wall.get(owner_id=-group_id, count=25)
            found_recent = False
            for post in wall["items"]:
                number_list += 1
                post_id = post["id"]
                owner_id = post["owner_id"]

                comments_list = []
                if post.get("comments", {}).get("count", 0) > 0:
                    try:
                        comments_data = vk.wall.getComments(
                            owner_id=owner_id, post_id=post_id, count=100
                        )
                        for comment in comments_data["items"]:
                            if "text" in comment and comment["text"].strip():
                                comments_list.append(comment["text"])
                    except Exception as e:
                        print(f"Не удалось получить комменты для поста {post_id}: {e}")

                post_date = post["date"]
                if post_date < time_threshold:
                    continue

                found_recent = True

                text = post.get("text", None)
                title = text.split("\n")[0][:150]
                date_readable = datetime.fromtimestamp(post_date).strftime(
                    "%H:%M:%S %d.%m.%Y"
                )

                likes = post.get("likes", {}).get("count", 0)
                views = post.get("views", {}).get("count", 0)
                link = f"Ссылка: https://vk.com/{group['screen_name']}"

                results.append(
                    {
                        "id": number_list,
                        "source": f"https://vk.com/{group['screen_name']}",
                        "source_type": "Вконтакте",
                        "category": None,
                        "date": date_readable,
                        "title": title,
                        "text": text,
                        "url": f"https://vk.com/{group['screen_name']}?w=wall{owner_id}_{post_id}",
                        "views": views,
                        "likes": likes,
                        "comments_count": len(comments_list),
                        "comments": comments_list,
                    }
                )

            if not found_recent:
                print("За последние 24 часа постов не найдено.")
        except Exception as e:
            print(f"Ошибка при работе с группой {group_id}: {e}")

    return results
