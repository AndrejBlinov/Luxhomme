import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# 1. Загрузка переменных окружения (Безопасность!)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
# Если используешь OpenAI: AI_API_KEY = os.getenv("AI_API_KEY")
# Если Яндекс: YANDEX_API_KEY = os.getenv("YANDEX_API_KEY")


def load_reviews(file_path: str) -> str:
    """Читает CSV и возвращает его текстовое представление для LLM"""
    try:
        df = pd.read_csv(file_path, sep=";", encoding="utf-8")
        # Преобразуем DataFrame в простой текст, чтобы LLM было легче читать
        return df.to_string(index=False)
    except Exception as e:
        print(f"Ошибка чтения CSV: {e}")
        return ""


def analyze_with_ai(reviews_text: str, prompt_path: str) -> dict:
    """Отправляет данные в LLM и получает JSON-ответ"""
    with open(prompt_path, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    user_prompt = f"Проанализируй следующие данные отзывов:\n{reviews_text}"

    # --- Пример вызова LLM API ---
    # Пример для OpenAI (раскомментируй и подставь свой ключ):
    # from openai import OpenAI
    # client = OpenAI(api_key=os.getenv("AI_API_KEY"))
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": user_prompt}
    #     ],
    #     response_format={"type": "json_object"} # Важно для строгого JSON!
    # )
    # return json.loads(response.choices[0].message.content)

    # Тест. Блок закоментировать, при переключении на реальную LLM
    print("⚠️ Используется мок-ответ AI. Подключи реальный API в коде.")
    return {
        "summary": {"total_reviews": 40, "avg_rating": 3.2},
        "topics": {
            "Брак/Качество": 15,
            "Доставка": 8,
            "Шум/Производительность": 7,
            "Позитив": 10,
        },
        "top_complaints": [
            {
                "issue": "Массовый брак помпы",
                "sku": "CM-2010",
                "quote": "Третий подряд брак! Что за партия такая?",
            },
            {
                "issue": "Проблемы с доставкой",
                "sku": "AF-5501",
                "quote": "Доставили через 2 недели, курьер хамил.",
            },
        ],
        "wow_change": "Резкий всплеск жалоб на брак (помпа, бойлер) по кофемашинам CM-2010 во вторую неделю.",
    }


def send_to_telegram(data: dict):
    """Формирует и отправляет красивое сообщение в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Не указаны TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в .env")
        return

    # Формируем текст в формате Markdown
    msg = f"📊 *Еженедельная сводка по отзывам*\n\n"
    msg += f"🔹 Всего отзывов: {data['summary']['total_reviews']}\n"
    msg += f"⭐️ Средний рейтинг: {data['summary']['avg_rating']}\n\n"

    msg += "📌 *Основные темы:*\n"
    for topic, count in data["topics"].items():
        msg += f"• {topic}: {count}\n"

    msg += "\n🚨 *Топ жалоб:*\n"
    for comp in data["top_complaints"]:
        msg += f'• *{comp["issue"]}* ({comp["sku"]}):\n  _"{comp["quote"]}"_\n'

    msg += f"\n📈 *Динамика к прошлой неделе (WoW):*\n_{data['wow_change']}_\n"
    msg += "\n🤖 Сгенерировано AI-ассистентом"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("✅ Сводка успешно отправлена в Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        print(msg)


if __name__ == "__main__":
    baseDir = Path(__file__).parent.parent
    print("🚀 Запуск анализа отзывов...")
    csv_text = load_reviews(baseDir / "data" / "reviews.csv")

    if csv_text:
        ai_result = analyze_with_ai(csv_text, baseDir / "src" / "prompt.txt")
        send_to_telegram(ai_result)
    else:
        print("Не удалось загрузить данные для анализа.")
