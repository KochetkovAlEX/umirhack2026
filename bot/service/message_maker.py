async def make_new_message(topic: str, data: list) -> str:
    message_text = f"<b>Проблем по теме: {topic}: {len(data)}</b>\n\n"

    for i in range(len(data)):
        message_text += f"{i + 1}. {data[i].source_type}: <a href='{data[i].url}'>{data[i].title}</a> {data[i].date.strftime('%d.%m.%Y')}\n"

    return message_text
