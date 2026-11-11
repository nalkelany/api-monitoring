import alert_manager


def test_batch_alert_sends_one_message_to_each_channel(monkeypatch):

    alerts = [
        {
            "alert_type": "API DOWN",
            "url": "https://api1.example.com",
            "status": "Timeout",
            "response_time_ms": 2000,
        },
        {
            "alert_type": "SLOW RESPONSE",
            "url": "https://api2.example.com",
            "status": "Healthy",
            "response_time_ms": 1500,
        },
    ]

    telegram_messages = []
    email_messages = []

    monkeypatch.setattr(
        alert_manager,
        "send_telegram_alert",
        lambda message: telegram_messages.append(message),
    )

    monkeypatch.setattr(
        alert_manager,
        "send_email_alert",
        lambda subject, message: email_messages.append(
            {"subject": subject, "message": message}
        ),
    )

    results = alert_manager.create_and_send_batch_alert(alerts)

    # Verify one call per channel
    assert len(telegram_messages) == 1
    assert len(email_messages) == 1

    # Verify both channels received the same message
    assert telegram_messages[0] == email_messages[0]["message"]

    # Verify all alerts are included
    message = telegram_messages[0]

    assert "API DOWN" in message
    assert "SLOW RESPONSE" in message
    assert "api1.example.com" in message
    assert "api2.example.com" in message
    assert "Total Alerts: 2" in message

    # Verify delivery results
    assert results == {"telegram": "success", "email": "success"}


def test_email_succeeds_when_telegram_fails(monkeypatch):

    def failed_telegram(message):
        raise ConnectionError("Telegram unavailable")

    email_messages = []

    monkeypatch.setattr(alert_manager, "send_telegram_alert", failed_telegram)

    monkeypatch.setattr(
        alert_manager,
        "send_email_alert",
        lambda subject, message: email_messages.append(message),
    )

    results = alert_manager.create_and_send_batch_alert(
        [
            {
                "alert_type": "API DOWN",
                "url": "https://example.com",
                "status": "Timeout",
                "response_time_ms": 2000,
            }
        ]
    )

    assert results["telegram"].startswith("failed:")
    assert results["email"] == "success"
    assert len(email_messages) == 1
