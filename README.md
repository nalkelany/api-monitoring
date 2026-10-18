# API Monitoring

## Overview

A Python application that monitors multiple API endpoints, classifies HTTP and connection errors, generates a JSON report, and stores monitoring results in a SQLite database.

## Features

- Monitors multiple API endpoints using HTTP requests.
- Handles HTTP errors, timeouts, and connection failures.
- Loads API URLs from an external JSON configuration file.
- Validates configuration structure and URL format.
- Generates a summary of healthy and failed endpoints.
- Saves monitoring results, summary, and UTC timestamp to a JSON report.
- Stores monitoring results in a SQLite database.
- Groups and counts error categories using SQL queries.

## Requirements

- Python 3
- `requests` library
- SQLite (included with standard Python installations)

## Project Structure

- `api_test.py` — Main application and API monitoring logic.
- `config.json` — API endpoints configuration.
- `setup_db.py` — Creates and updates the SQLite database using the generated report.
- `README.md` — Project documentation.
- `api_report.json` — Generated monitoring report.
- `api_monitoring.db` — Generated SQLite database.

The JSON report and SQLite database are generated files and are excluded from version control through `.gitignore`.

## Installation

Install the required dependency:

```bash
pip install requests
```

## Usage

### 1. Configure API endpoints

Edit `config.json` and add the API URLs you want to monitor.

### 2. Run API monitoring

```bash
python api_test.py
```

This generates `api_report.json` containing the monitoring results and summary.

### 3. Store results in SQLite

```bash
python setup_db.py
```

This creates or updates `api_monitoring.db` using the generated report and displays a summary of error categories.

## Error Categories

- `Healthy` — The API request completed successfully.
- `HTTP Error` — The server returned an unsuccessful HTTP status.
- `Timeout` — The request exceeded the configured timeout.
- `Connection Failed` — A connection could not be established.
- `Request Failed` — Another request-related error occurred.

## Technologies

- Python
- Requests
- JSON
- SQLite
- SQL
- Git and GitHub

## Future Improvements

- Schedule periodic monitoring.
- Add automated tests.
- Add logging and historical performance tracking.
- Containerize the application with Docker.
