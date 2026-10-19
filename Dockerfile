FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY api_test.py .
COPY setup_db.py .
COPY config.json .

CMD ["python", "api_test.py"]