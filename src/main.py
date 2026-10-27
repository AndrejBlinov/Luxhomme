import json
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from openai import OpenAI

# 1. Загрузка переменных окружения (Безопасность!)
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AI_API_KEY = os.getenv("AI_API_KEY")
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
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

        user_prompt = f"Проанализируй следующие данные отзывов:\n{reviews_text}"

        # РЕАЛЬНЫЙ ВЫЗОВ API (готов к работе)
        client = OpenAI(api_key=AI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        print(f"❌ Ошибка при вызове LLM: {e}")
        return {}


def send_to_telegram(data: dict):
    """Формирует и отправляет красивое сообщение в Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Ошибка: Не указаны TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID в .env")
        return

    # Формируем текст в формате Markdown
    summary = data.get("summary", {})
    msg = f"📊 *Еженедельная сводка по отзывам*\n\n"
    msg += f"🔹 Всего отзывов: {summary.get('total_reviews', 'N/A')}\n"
    msg += f"⭐️ Средний рейтинг: {summary.get('avg_rating', 'N/A')}\n\n"

    msg += "📌 *Основные темы:*\n"
    for topic, count in data.get("topics", {}).items():
        msg += f"• {topic}: {count}\n"

    msg += "\n🚨 *Топ жалоб:*\n"
    for comp in data.get("top_complaints", []):
        msg += (
            f'• *{comp.get("issue")}* ({comp.get("sku")}):\n  _"{comp.get("quote")}"_\n'
        )

    msg += f"\n📈 *Динамика к прошлой неделе (WoW):*\n_{data.get('wow_change', 'Нет данных')}_\n"
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
