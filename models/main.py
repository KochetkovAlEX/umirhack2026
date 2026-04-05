import asyncio
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta

import google.generativeai as genai
import nltk
import numpy as np
import pandas as pd
import pymorphy3
from bertopic import BERTopic
from hdbscan import HDBSCAN
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
from umap import UMAP

PATH_TOX = "./models/rubert-tiny-toxicity"
PATH_SPAM = "./models/spamNS_v1"
PATH_EMB = "./models/rubert-tiny2"
URG_FILE = "urgency_keywords.txt"
STOP_WORDS_FILE = "stop_words.txt"

MIN_TOPIC_SIZE = 3
EMERGENCY_WINDOW = 2  # количесвто часов, для отслеживания взрывной активности
URGENCY_BONUS = 0.2

genai.configure(api_key="AIzaSyDafRm-72i3GypZTQpIuvNObaidt5zxJpI")
model = genai.GenerativeModel("models/gemini-2.5-flash")

# 1. Модели и загрузка словаря нужно сделать один раз при запуске бота
emb_model = SentenceTransformer(PATH_EMB)
spam_pipe = pipeline("text-classification", model=PATH_SPAM, tokenizer=PATH_SPAM)
tox_pipe = pipeline(
    "text-classification", model=PATH_TOX, tokenizer=PATH_TOX, top_k=None
)

morph = pymorphy3.MorphAnalyzer()
executor = ThreadPoolExecutor(max_workers=3)


# Чтение URGENCY и STOP_WORDS
if os.path.exists(URG_FILE):
    f = open(URG_FILE, "r", encoding="utf-8")
    URGENCY_WORDS = f.readline().split(", ")
    f.close()
else:
    raise FileNotFoundError(
        f"Файл не найден: {URG_FILE}"
    )  # Потом переписать, чтобы бот не падал

LEMMATIZED_URGENCY = list(
    set([morph.parse(w.strip())[0].normal_form for w in URGENCY_WORDS])
)

if os.path.exists(STOP_WORDS_FILE):
    f = open(STOP_WORDS_FILE, "r", encoding="utf-8")
    my_stop_words = f.readline().split(", ")
    f.close()

nltk.download("stopwords")

# Загружаем список
STOP_WORDS = stopwords.words("russian")
if my_stop_words:
    STOP_WORDS.extend(my_stop_words)
    STOP_WORDS = list(set(STOP_WORDS))


def count_urgency(text):
    score = 0
    # Очищаем текст от знаков и разбиваем на слова
    words = re.findall(r"\b[а-яА-ЯёЁ]+\b", text.lower())

    for word in words:
        # Приводим каждое слово из сообщения к начальной форме
        lemma = morph.parse(word)[0].normal_form
        if lemma in LEMMATIZED_URGENCY:
            score += URGENCY_BONUS
    return score


def clean_text(text):
    # Оставляем только кириллицу и цифры
    words = re.findall(r"\b[а-яА-ЯёЁ\d]{3,}\b", str(text).lower())
    # Приводим к начальной форме
    return " ".join([morph.parse(w)[0].normal_form for w in words])


def drop_similar_messages(df, threshold=0.90):
    # 1. Получаем вектора (используем вашу emb_model)
    embeddings = emb_model.encode(df["text"].tolist())

    # 2. Считаем косинусное сходство
    cosine_sim = cosine_similarity(embeddings)

    # 3. Находим индексы дубликатов
    to_drop = set()
    for i in range(len(cosine_sim)):
        for j in range(i + 1, len(cosine_sim)):
            if cosine_sim[i][j] > threshold:
                to_drop.add(j)  # Помечаем сообщение j как дубликат сообщения i

    # 4. Удаляем
    return df.drop(df.index[list(to_drop)]).reset_index(drop=True)


async def refine_with_gemini(title, messages):
    """
    Функция для обработки одной темы через Gemini
    """
    messages_context = (
        title + "\n" + "\n".join(messages)
    )  # Берем первые 10 сообщений темы

    prompt = f"""
    Ты — аналитик ситуационного центра. Ты получаешь группы, сгенерированные BERTopic. Твоя задача
    1. Проанализируй сообщения и старый заголовок каждой группы и дай ей краткое, официальное название на русском языке (до 5 слов).
    2. Удали сообщения, которые являются рекламой
    3. Делай строго только это

    Сообщения темы:
    {messages_context}

    Ответ дай строго в формате JSON:
    {{"title": "Название темы", "items": "Python список оставшихся сообщений в группе"}}
    """

    try:
        response = await model.generate_content_async(prompt)
        # Очищаем ответ от возможных markdown-тегов ```json
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_json)
    except Exception as e:
        print("--------Гемини не сработала----------------- Ошибка:", e)
        return {"title": title, "items": messages}


async def process_final_report(report_df):
    """
    Функция принимает результат работы функции analyze и обрабатывает основные темы через Gemini
    """
    final_data = []

    # Берет только 10 самых важных тем
    top_report = report_df.head(10)

    for index, row in top_report.iterrows():
        old_title = row["Name"]
        messages = row["messages"]

        # Вызывает функцию
        # Передает заголовок и список сообщений
        refined = await refine_with_gemini(old_title, messages)

        # Обновляет данные в строке
        row["Name"] = refined.get("title", old_title)
        row["messages"] = refined.get(
            "items", messages
        )  # Обновленный список без рекламы

        # Если Gemini удалила все сообщения (значит тема - сплошная реклама),
        # такую тему можно вообще пропустить
        if len(row["messages"]) > 0:
            final_data.append(row)

    # Возвращает обновленный DataFrame
    return pd.DataFrame(final_data)


def analyze(data):
    df = pd.DataFrame(data)

    # 2. Очистка и скоринг (через apply)
    # title/text
    field = "text"  # откуда брать сам текст

    df = drop_similar_messages(df, threshold=0.90)
    df = df[df[field].str.strip().fillna("") != ""].copy()
    df = df[df[field].apply(lambda x: spam_pipe(x[:512])[0]["label"] != "spam")].copy()
    df["tox"] = df[field].apply(
        lambda x: max(
            r["score"] for r in tox_pipe(x[:512])[0] if r["label"] != "non-toxic"
        )
    )
    df["urg"] = df[field].apply(count_urgency)

    # 3. Тематическое моделирование
    vectorizer_model = CountVectorizer(
        stop_words=STOP_WORDS, token_pattern=r"(?u)\b[а-яА-ЯёЁ]{3,}\b"
    )

    # Уменьшаем n_neighbors, чтобы модель искала мелкие детали, а не общие черты
    umap_model = UMAP(n_neighbors=2, n_components=5, min_dist=0.0, metric="cosine")

    # Увеличиваем min_samples, чтобы в тему попадали только ОЧЕНЬ похожие тексты
    hdbscan_model = HDBSCAN(min_cluster_size=3, min_samples=1, prediction_data=True)

    topic_model = BERTopic(
        embedding_model=emb_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer_model,  # со стоп-словами
        language="russian",
        min_topic_size=MIN_TOPIC_SIZE,
    )

    df["clean_text"] = df[field].apply(clean_text)
    df["topic"], _ = topic_model.fit_transform(df["clean_text"].tolist())

    # 4. Агрегация
    now = df["date"].max()
    df["is_recent"] = (df["date"] > (now - timedelta(hours=EMERGENCY_WINDOW))).astype(
        int
    )

    # Оставляем только значимые темы (не шум)
    res = df[df["topic"] != -1].copy()

    # ПРОВЕРКА: Если значимых тем нет, возвращаем пустой результат
    if res.empty:
        return pd.DataFrame(columns=["topic_id", "idx", "Name"])

    res = res.groupby("topic").agg(
        n=("topic", "count"),
        e=("tox", "mean"),
        a=("activity", "sum"),
        u=("urg", "max"),
        v=("is_recent", "sum"),  # за последние два часа
    )

    # 5. Безопасная нормализация через numpy
    n_val = res["n"].values.astype(float)
    a_val = np.log1p(res["a"].values.astype(float))
    e_val = res["e"].values.astype(float)
    v_val = res["v"].values.astype(float)
    u_val = res["u"].values.astype(float)

    # Локальная функция нормализации с защитой
    def nm(x):
        return (x - x.min()) / (x.max() - x.min() + 1e-6)

    res["idx"] = (
        0.1 * nm(n_val) + 0.1 * nm(a_val) + 0.3 * nm(e_val) + 0.4 * nm(v_val) + u_val
    )

    # Создаем словарь: ключ — ID темы, значение — список текстов
    topic_messages = df.groupby("topic")["title"].apply(list).to_dict()

    # Добавляем этот список в итоговую таблицу
    res["messages"] = res.index.map(topic_messages)

    return res.join(
        topic_model.get_topic_info().set_index("Topic")[["Name"]]
    ).sort_values("idx", ascending=False)


async def analyze_async(data):
    """Асинхронная обертка над тяжелыми вычислениями"""
    loop = asyncio.get_running_loop()

    # Запускаем синхронную функцию analyze в отдельном потоке
    report = await loop.run_in_executor(executor, analyze, data)

    return report


async def get_results(data):
    report = await analyze_async(data)

    if not report.empty:
        # 2. Уточнение через Gemini (LLM)
        final_report = await process_final_report(report)
        return final_report
    return 0


if __name__ == "__main__":
    tg_chan_data = asyncio.run(parse_telegram(tg_urls))

    results = asyncio.run(get_results(tg_chan_data))

    if not results.empty:
        for _, row in results.iterrows():
            # 1. Заголовок и основной индекс
            print(f"\n📍 ТЕМА: {row['Name'].upper()}")
            print(f"🔥 ИНДЕКС КРИТИЧНОСТИ: {row['idx']:.2f}")

            # 2. Полная статистика по теме
            print(f"📈 СТАТИСТИКА:")
            print(
                f"   • Сообщений (n): {int(row['n'])} | Число сообщений за последние 2 часа: {int(row['v'])}"
            )
            print(
                f"   • Индекс негатива (e): {row['e']:.2f} | Срочность (u): {row['u']:.1f}"
            )
            print(f"   " + "-" * 30)

            # 3. Список сообщений со ссылками
            print(f"📝 СООБЩЕНИЯ:")

            # Если Gemini вернула только тексты, сопоставляем их со ссылками из оригинала
            # Здесь предполагается, что в row['messages_with_links'] лежат пары (текст, ссылка)
            for msg_text in row["messages"][:5]:
                # Укорачиваем текст для вывода, если он слишком длинный
                display_text = (
                    (msg_text[:100] + "...") if len(str(msg_text)) > 100 else msg_text
                )
                print(f"   • {display_text}")
                print()  # Отступ между сообщениями

            if row["n"] > 5:
                print(f"   ... и еще {int(row['n']) - 5} сообщений в этой категории.")

    else:
        print("Тем нет")
