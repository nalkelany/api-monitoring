
import sqlite3
from pathlib import Path
import json

db_path = Path(__file__).parent / "api_monitoring.db"
report_path = Path(__file__).parent / "api_report.json"
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

with open(report_path, "r") as file:
    report = json.load(file)

print(report["summary"])

for result in report["results"]:
    print(result)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        status INTEGER,
        result TEXT NOT NULL
    )
""")

cursor.execute("DELETE FROM api_results")

cursor.executemany(
    """
    INSERT INTO api_results (url, status, result)
    VALUES (?, ?, ?)
    """,
    [
        (item["url"], item["status"], item["result"])
        for item in report["results"]
    ]
)

connection.commit()

cursor.execute("""
    SELECT result, COUNT(*)
    FROM api_results
    WHERE result != ?
    GROUP BY result
    ORDER BY COUNT(*) DESC
""", ("Healthy",))

for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT COUNT(*) FROM api_results")
print("Total records:", cursor.fetchone()[0])

connection.close()

print("Database updated successfully.")
