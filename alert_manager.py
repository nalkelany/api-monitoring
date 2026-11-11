from telegram_alert import send_telegram_alert
from email_alert import send_email_alert
from datetime import datetime


def format_alert(alert_type, url, status, response_time_ms):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    alert_message = (
        f"[{alert_type}]\n\n"
        f"URL: {url}\n"
        f"Status: {status}\n"
        f"Response Time: {response_time_ms} ms\n"
        f"Time: {timestamp}"
    )

    return alert_message


def send_alert(subject, message):

    results = {}

    try:
        send_telegram_alert(message)
        results["telegram"] = "success"

    except Exception as error:
        results["telegram"] = f"failed: {error}"

    try:
        send_email_alert(subject, message)
        results["email"] = "success"

    except Exception as error:
        results["email"] = f"failed: {error}"

    return results


def create_and_send_alert(alert_type, url, status, response_time_ms):

    subject = f"API Monitoring Alert: {alert_type}"

    message = format_alert(alert_type, url, status, response_time_ms)

    results = send_alert(subject, message)

    return results


def create_and_send_batch_alert(alerts):

    if not alerts:
        return {}

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    message_parts = ["API MONITORING ALERT", f"Time: {timestamp}", ""]

    for index, alert in enumerate(alerts, start=1):

        message_parts.extend(
            [
                f"{index}. {alert['alert_type']}",
                f"URL: {alert['url']}",
                f"Status: {alert['status']}",
                f"Response Time: {alert['response_time_ms']} ms",
                "",
            ]
        )

    message_parts.append(f"Total Alerts: {len(alerts)}")

    subject = f"API Monitoring: {len(alerts)} Alerts"

    message = "\n".join(message_parts)

    return send_alert(subject, message)
