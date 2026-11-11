import json
import api_test


def test_healthy_to_slow_sends_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    # Prepare temporary configuration
    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    # Initial API state
    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Healthy"}))

    # Initial performance state
    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({url: "Normal"}))

    # Temporary report path
    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    # Simulate a slow but healthy API
    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 1500,
        },
    )

    # Capture alerts instead of sending real messages
    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    # Execute monitoring
    api_test.main()

    # Verify alert
    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "SLOW RESPONSE"

    # Verify updated performance state
    updated_states = json.loads(performance_file.read_text())

    assert updated_states[url] == "Slow"


def test_slow_to_normal_sends_recovery_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Healthy"}))

    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({url: "Slow"}))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 200,
        },
    )

    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    api_test.main()

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "RESPONSE TIME RECOVERED"

    updated_states = json.loads(performance_file.read_text())
    assert updated_states[url] == "Normal"


def test_healthy_to_failed_sends_down_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Healthy"}))

    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({url: "Normal"}))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": None,
            "result": "Timeout",
            "response_time_ms": 2000,
        },
    )

    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    api_test.main()

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "API DOWN"

    updated_states = json.loads(states_file.read_text())
    assert updated_states[url] == "Timeout"

    updated_performance = json.loads(performance_file.read_text())
    assert url not in updated_performance


def test_failed_to_healthy_sends_recovery_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Timeout"}))

    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({}))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 200,
        },
    )

    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    api_test.main()

    assert len(alerts) == 1
    assert alerts[0]["alert_type"] == "API RECOVERED"

    updated_states = json.loads(states_file.read_text())
    assert updated_states[url] == "Healthy"


def test_repeated_failed_does_not_send_duplicate_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Timeout"}))

    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({}))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": None,
            "result": "Timeout",
            "response_time_ms": 2000,
        },
    )

    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    api_test.main()

    assert len(alerts) == 0


def test_repeated_slow_does_not_send_duplicate_alert(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    states_file.write_text(json.dumps({url: "Healthy"}))

    performance_file = tmp_path / "api_performance_states.json"
    performance_file.write_text(json.dumps({url: "Slow"}))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 1500,
        },
    )

    alerts = []

    def mock_batch_alert(batch):
        alerts.extend(batch)
        return {
            "telegram": "success",
            "email": "success"
        }


    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        mock_batch_alert
    )

    api_test.main()

    assert len(alerts) == 0


def test_failed_alert_delivery_does_not_save_states(tmp_path, monkeypatch):

    url = "https://example.com/api"

    config_file = tmp_path / "config.json"
    config_file.write_text(json.dumps({"urls": [url]}))

    states_file = tmp_path / "api_states.json"
    original_states = {url: "Healthy"}
    states_file.write_text(json.dumps(original_states))

    performance_file = tmp_path / "api_performance_states.json"
    original_performance = {url: "Normal"}
    performance_file.write_text(json.dumps(original_performance))

    report_file = tmp_path / "api_report.json"

    monkeypatch.setattr(api_test, "config_path", config_file)
    monkeypatch.setattr(api_test, "states_path", states_file)
    monkeypatch.setattr(api_test, "performance_states_path", performance_file)
    monkeypatch.setattr(api_test, "report_path", report_file)

    monkeypatch.setattr(
        api_test,
        "check_api",
        lambda url: {
            "url": url,
            "status": None,
            "result": "Timeout",
            "response_time_ms": 2000,
        },
    )

    monkeypatch.setattr(
        api_test,
        "create_and_send_batch_alert",
        lambda alerts: {
            "telegram": "failed: Telegram unavailable",
            "email": "failed: Email unavailable",
        },
    )

    api_test.main()

    saved_states = json.loads(states_file.read_text())
    saved_performance = json.loads(performance_file.read_text())

    assert saved_states == original_states
    assert saved_performance == original_performance
