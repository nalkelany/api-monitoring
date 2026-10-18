
# API Monitoring

## Overview
A Python project that monitors multiple APIs, classifies HTTP and connection errors, and generates a JSON report.

## Features
- Checks multiple API endpoints using HTTP requests.
- Handles HTTP errors, timeouts, and connection failures.
- Loads API URLs from an external JSON configuration file.
- Validates configuration structure and URL format.
- Generates a summary of healthy and failed endpoints.
- Saves results, summary, and UTC timestamp to a JSON report.

## Requirements
- Python 3
- requests library

## Project Structure
- `api_test.py` - Main application and monitoring logic.
- `config.json` - API endpoints configuration.
- `api_report.json` - Generated monitoring report.

## Usage
1. Install the dependency:

   `pip install requests`

2. Configure API endpoints in `config.json`.
3. Run the application:

   `python api_test.py`

4. Review the generated `api_report.json`.

## Error Categories
- Healthy
- HTTP Error
- Timeout
- Connection Failed
- Request Failed
