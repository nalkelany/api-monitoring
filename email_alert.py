import os
import smtplib
from pathlib import Path
from email.message import EmailMessage

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


def send_email_alert(subject, message):

    email_address = os.getenv("YANDEX_EMAIL")
    email_password = os.getenv("YANDEX_APP_PASSWORD")

    if not email_address or not email_password:
        raise ValueError("Email credentials are missing.")

    email = EmailMessage()
    email["From"] = email_address
    email["To"] = email_address
    email["Subject"] = subject
    email.set_content(message)

    with smtplib.SMTP_SSL("smtp.yandex.com", 465, timeout=10) as smtp:
        smtp.login(email_address, email_password)
        smtp.send_message(email)

    return True


if __name__ == "__main__":
    send_email_alert("API Monitoring Test", "Email Alert is working successfully!")

    print("Email alert sent successfully.")
