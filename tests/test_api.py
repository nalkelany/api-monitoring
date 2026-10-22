from api_test import generate_report
from unittest.mock import Mock, patch
from api_test import check_api
import requests

def test_generate_report():
    results = [
        {"url": "https://example.com", "status": 200, "result": "Healthy"},
        {"url": "https://example.com/error", "status": 404, "result": "HTTP Error"},
        {"url": "https://example.com/slow", "status": None, "result": "Timeout"},
    ]

    summary = generate_report(results)

    assert summary == {
        "total": 3,
        "healthy": 1,
        "failed": 2,
    }

def test_check_api_healthy():
    mock_response = Mock()
    mock_response.status_code = 200

    with patch("api_test.requests.get", return_value=mock_response):
        result = check_api("https://example.com")

    assert result == {
        "url": "https://example.com",
        "status": 200,
        "result": "Healthy",
    }

def test_check_api_http_error():
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    with patch("api_test.requests.get", return_value=mock_response):
        result = check_api("https://example.com/missing")

    assert result == {
        "url": "https://example.com/missing",
        "status": 404,
        "result": "HTTP Error",
    }

def test_check_api_timeout():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.Timeout,
    ):
        result = check_api("https://example.com/slow")

    assert result == {
        "url": "https://example.com/slow",
        "status": None,
        "result": "Timeout",
    }

def test_check_api_connection_error():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        result = check_api("https://example.com/unreachable")

    assert result == {
        "url": "https://example.com/unreachable",
        "status": None,
        "result": "Connection Failed",
    }

def test_check_api_request_failed():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.RequestException,
    ):
        result = check_api("https://example.com/request-error")

    assert result == {
        "url": "https://example.com/request-error",
        "status": None,
        "result": "Request Failed",
    }