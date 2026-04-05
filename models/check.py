import os

from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Создаем базовую директорию для моделей
BASE_MODELS_PATH = "./models"
os.makedirs(BASE_MODELS_PATH, exist_ok=True)


def download_and_save():
    print("🚀 Начинаю загрузку моделей...")

    # 1. rubert-tiny2 (для эмбеддингов / BERTopic)
    print("\n--- Скачиваю rubert-tiny2 ---")
    model_tiny2 = SentenceTransformer("cointegrated/rubert-tiny2")
    model_tiny2.save(os.path.join(BASE_MODELS_PATH, "rubert-tiny2"))
    print("✅ rubert-tiny2 сохранен.")

    # 2. rubert-tiny-toxicity (для оценки негатива)
    print("\n--- Скачиваю rubert-tiny-toxicity ---")
    tox_pipe = pipeline(
        "text-classification", model="cointegrated/rubert-tiny-toxicity"
    )
    tox_pipe.save_pretrained(os.path.join(BASE_MODELS_PATH, "rubert-tiny-toxicity"))
    print("✅ rubert-tiny-toxicity сохранен.")

    # 3. spamNS_v1 (для фильтрации спама)
    print("\n--- Скачиваю spamNS_v1 ---")
    # Обрати внимание: в репозитории автора модель называется RUSpam/spamNS_v1
    spam_pipe = pipeline("text-classification", model="RUSpam/spamNS_v1")
    spam_pipe.save_pretrained(os.path.join(BASE_MODELS_PATH, "spamNS_v1"))
    print("✅ spamNS_v1 сохранен.")

    print("\n🎉 Все модели успешно сохранены локально в папку", BASE_MODELS_PATH)


if __name__ == "__main__":
    download_and_save()
