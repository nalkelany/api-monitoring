import requests
import json
import time
import logging
import os
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from alert_manager import create_and_send_batch_alert


class CustomRotatingFileHandler(RotatingFileHandler):

    def __init__(self, filename, *args, **kwargs):
        log_path = Path(filename).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(str(log_path), *args, **kwargs)

    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        log_path = Path(self.baseFilename)

        if log_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

            archive_name = f"{log_path.stem}_{timestamp}{log_path.suffix}"

            archive_path = log_path.parent / archive_name

            os.replace(log_path, archive_path)

        if self.backupCount > 0:
            archived_logs = sorted(
                log_path.parent.glob(f"{log_path.stem}_*{log_path.suffix}"),
                reverse=True,
            )

            for old_log in archived_logs[self.backupCount :]:
                old_log.unlink()

        if not self.delay:
            self.stream = self._open()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        CustomRotatingFileHandler(
            "log/api_monitor.log",
            maxBytes=5 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        ),
    ],
)

config_path = Path(__file__).parent / "config.json"
report_path = Path(__file__).parent / "api_report.json"
states_path = Path(__file__).parent / "api_states.json"
performance_states_path = Path(__file__).parent / "api_performance_states.json"
SLOW_RESPONSE_THRESHOLD_MS = 1000


def check_api(url):
    start_time = time.perf_counter()
    try:
        response = requests.get(url, timeout=2)
        response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        response.raise_for_status()
        logging.info("API is healthy: %s | Status: %s", url, response.status_code)
        return {
            "url": url,
            "status": response.status_code,
            "result": "Healthy",
            "response_time_ms": response_time_ms,
        }

    except requests.exceptions.Timeout:
        response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logging.warning("API request timed out: %s", url)
        return {
            "url": url,
            "status": None,
            "result": "Timeout",
            "response_time_ms": response_time_ms,
        }

    except requests.exceptions.HTTPError:
        response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logging.error("HTTP error %s for URL: %s", response.status_code, url)
        return {
            "url": url,
            "status": response.status_code,
            "result": "HTTP Error",
            "response_time_ms": response_time_ms,
        }

    except requests.exceptions.ConnectionError:
        response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logging.error("Connection failed for URL: %s", url)
        return {
            "url": url,
            "status": None,
            "result": "Connection Failed",
            "response_time_ms": response_time_ms,
        }

    except requests.exceptions.RequestException:
        response_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logging.error("Request failed for URL: %s", url)
        return {
            "url": url,
            "status": None,
            "result": "Request Failed",
            "response_time_ms": response_time_ms,
        }


def generate_report(results):
    response_times = [
        result["response_time_ms"] for result in results if "response_time_ms" in result
    ]

    slow_apis = [
        result
        for result in results
        if result.get("response_time_ms", 0) >= SLOW_RESPONSE_THRESHOLD_MS
    ]

    average_response_time = (
        round(sum(response_times) / len(response_times), 2) if response_times else 0
    )

    min_response_time = round(min(response_times), 2) if response_times else 0

    max_response_time = round(max(response_times), 2) if response_times else 0

    report = {
        "total": len(results),
        "healthy": 0,
        "failed": 0,
        "average_response_time_ms": average_response_time,
        "min_response_time_ms": min_response_time,
        "max_response_time_ms": max_response_time,
        "slow_apis": len(slow_apis),
        "slow_apis_details": slow_apis,
    }

    for result in results:
        if result["result"] == "Healthy":
            report["healthy"] += 1
        else:
            report["failed"] += 1

    return report


def load_api_states():

    try:
        with open(states_path, "r") as file:
            states = json.load(file)

        return states

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError:
        logging.error("api_states.json contains invalid JSON.")
        return {}


def load_performance_states():

    try:
        with open(performance_states_path, "r") as file:
            states = json.load(file)

        return states

    except FileNotFoundError:
        return {}

    except json.JSONDecodeError:
        logging.error("api_performance_states.json contains invalid JSON.")
        return {}


def save_performance_states(states):

    with open(performance_states_path, "w") as file:
        json.dump(states, file, indent=4)


def save_api_states(states):

    with open(states_path, "w") as file:
        json.dump(states, file, indent=4)


def main():
    logging.info("Starting API Monitoring...")

    try:
        with open(config_path, "r") as file:
            config = json.load(file)

        if "urls" not in config:
            print("Error: 'urls' key is missing from config.json.")
            return

        urls = config["urls"]

        if not isinstance(urls, list):
            print("Error: 'urls' must be a list.")
            return

        if not urls:
            print("Error: No URLs configured in config.json.")
            return

        if not all(isinstance(url, str) for url in urls):
            print("Error: All URLs must be strings.")
            return

    except FileNotFoundError:
        logging.error("config.json not found.")
        return

    except json.JSONDecodeError:
        logging.error("config.json contains invalid JSON.")
        return

    urls = config["urls"]

    for url in urls:
        parsed_url = urlparse(url)

        if parsed_url.scheme not in ("http", "https") or not parsed_url.netloc:
            print(f"Error: Invalid URL: {url}")
            return

    api_states = load_api_states()
    performance_states = load_performance_states()
    results = []
    alerts = []

    for url in urls:
        result = check_api(url)
        results.append(result)

        previous_state = api_states.get(url)
        current_state = result["result"]

        performance_status = (
            "Slow"
            if result["response_time_ms"] >= SLOW_RESPONSE_THRESHOLD_MS
            else "Normal"
        )
        previous_performance = performance_states.get(url)
        current_performance = performance_status

        if current_state == "Healthy":

            if current_performance == "Slow" and previous_performance != "Slow":

                alerts.append(
                    {
                        "alert_type": "SLOW RESPONSE",
                        "url": url,
                        "status": current_state,
                        "response_time_ms": result["response_time_ms"],
                    }
                )

            elif current_performance == "Normal" and previous_performance == "Slow":

                alerts.append(
                    {
                        "alert_type": "RESPONSE TIME RECOVERED",
                        "url": url,
                        "status": current_state,
                        "response_time_ms": result["response_time_ms"],
                    }
                )

            performance_states[url] = current_performance

        else:
            performance_states.pop(url, None)

        if previous_state is None or previous_state == "Healthy":

            if current_state != "Healthy":

                alerts.append(
                    {
                        "alert_type": "API DOWN",
                        "url": url,
                        "status": current_state,
                        "response_time_ms": result["response_time_ms"],
                    }
                )

        elif previous_state != "Healthy" and current_state == "Healthy":

            alerts.append(
                {
                    "alert_type": "API RECOVERED",
                    "url": url,
                    "status": current_state,
                    "response_time_ms": result["response_time_ms"],
                }
            )

        api_states[url] = current_state

        logging.info(
            "%s | Status: %s | Response Time: %s ms | URL: %s",
            result["result"],
            result["status"],
            result.get("response_time_ms", "N/A"),
            result["url"],
        )

    if alerts:

        alert_results = create_and_send_batch_alert(alerts)

        logging.info("Batch alert results: %s", alert_results)

        delivery_success = any(
            result == "success"
            for result in alert_results.values()
        )

        if delivery_success:
            save_api_states(api_states)
            save_performance_states(performance_states)

        else:
            logging.error(
                "All alert channels failed. States were not saved."
            )

    else:
        save_api_states(api_states)
        save_performance_states(performance_states)

    summary = generate_report(results)

    print("\nSummary:")
    print(summary)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "summary": summary,
    }

    with open(report_path, "w") as file:
        json.dump(report, file, indent=4)
        print("Report saved to api_report.json")


if __name__ == "__main__":
    main()
