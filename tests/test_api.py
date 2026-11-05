from api_test import generate_report
from unittest.mock import Mock, patch
from api_test import check_api
import requests


def test_generate_report():
    results = [
        {
            "url": "https://example.com",
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 100,
        },
        {
            "url": "https://example.com/error",
            "status": 404,
            "result": "HTTP Error",
            "response_time_ms": 200,
        },
        {
            "url": "https://example.com/slow",
            "status": None,
            "result": "Timeout",
            "response_time_ms": 300,
        },
        {
            "url": "https://example.com/slow-api",
            "status": 200,
            "result": "Healthy",
            "response_time_ms": 1500,
        },
    ]

    summary = generate_report(results)

    assert summary == {
        "total": 4,
        "healthy": 2,
        "failed": 2,
        "average_response_time_ms": 525.0,
        "min_response_time_ms": 100,
        "max_response_time_ms": 1500,
        "slow_apis": 1,
        "slow_apis_details": [
            {
                "url": "https://example.com/slow-api",
                "status": 200,
                "result": "Healthy",
                "response_time_ms": 1500,
            }
        ],
    }
    assert len(summary["slow_apis_details"]) == 1

    assert summary["slow_apis_details"][0]["url"] == ("https://example.com/slow-api")

    assert summary["slow_apis_details"][0]["response_time_ms"] == 1500


def test_check_api_healthy():
    mock_response = Mock()
    mock_response.status_code = 200

    with patch("api_test.requests.get", return_value=mock_response):
        result = check_api("https://example.com")

    assert result["url"] == "https://example.com"
    assert result["status"] == 200
    assert result["result"] == "Healthy"
    assert isinstance(result["response_time_ms"], (int, float))
    assert result["response_time_ms"] >= 0


def test_check_api_http_error():
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError()

    with patch("api_test.requests.get", return_value=mock_response):
        result = check_api("https://example.com/missing")

    assert result["url"] == "https://example.com/missing"
    assert result["status"] == 404
    assert result["result"] == "HTTP Error"
    assert isinstance(result["response_time_ms"], (int, float))
    assert result["response_time_ms"] >= 0


def test_check_api_timeout():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.Timeout,
    ):
        result = check_api("https://example.com/slow")

    assert result["url"] == "https://example.com/slow"
    assert result["status"] is None
    assert result["result"] == "Timeout"
    assert isinstance(result["response_time_ms"], (int, float))
    assert result["response_time_ms"] >= 0


def test_check_api_connection_error():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        result = check_api("https://example.com/unreachable")

    assert result["url"] == "https://example.com/unreachable"
    assert result["status"] is None
    assert result["result"] == "Connection Failed"
    assert isinstance(result["response_time_ms"], (int, float))
    assert result["response_time_ms"] >= 0


def test_check_api_request_failed():
    with patch(
        "api_test.requests.get",
        side_effect=requests.exceptions.RequestException,
    ):
        result = check_api("https://example.com/request-error")

    assert result["url"] == "https://example.com/request-error"
    assert result["status"] is None
    assert result["result"] == "Request Failed"
    assert isinstance(result["response_time_ms"], (int, float))
    assert result["response_time_ms"] >= 0
