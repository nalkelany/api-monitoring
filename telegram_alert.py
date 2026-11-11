import os
import requests
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


def send_telegram_alert(message):
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not BOT_TOKEN or not CHAT_ID:
        raise ValueError("Telegram credentials are missing.")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {"chat_id": CHAT_ID, "text": message}

    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    send_telegram_alert("API Monitoring: Telegram Alert is working!")
    print("Telegram alert sent successfully.")
