"""
URL Monitoring & Automation System
===========
Project: URL Monitoring & Automation System
Difficulty: Intermediate
Skills: Python, Flask, SQL, REST APIs, Automation, HTTP Requests, HTML, CSS, JavaScript
Time: Medium 

What you will build:

This project is a full-stack URL Monitoring and Automation web application where users can add website URLs and continuously monitor their availability and performance. The system automatically checks whether a website is online or offline, measures response time, stores monitoring history, and displays the current status in a dashboard. Users can track multiple URLs from one place and receive updates whenever a website becomes unavailable.
The backend will be developed using Python Flask to handle API routes, automation logic, scheduled monitoring tasks, database operations, and status updates. SQL databases such as SQLite or MySQL will store URL records, monitoring logs, uptime history, and response times. The frontend will be built using HTML, CSS, and JavaScript to provide a responsive dashboard showing live website statuses, uptime percentages, and monitoring reports.
The application will include automation functionality where the server periodically checks all saved URLs using HTTP requests and updates their status automatically without user interaction. Admin users can add, edit, or delete monitored URLs and view detailed monitoring logs. This project helps in learning backend automation, REST API development, database management, scheduled tasks, HTTP requests handling, CRUD operations, and dashboard creation, making it a strong intermediate-level real-world Flask project.

How to run:

pip install flask flask_sqlalchemy requests

Create folders:
templates/
static/

Run the application:
python app.py

Open browser:
http://127.0.0.1:5000

Learning goals:

-Understand Flask backend development
-Learn REST API creation
-Implement CRUD operations
-Work with SQL databases
-Learn website monitoring automation
-Send HTTP requests using Python
-Build dashboards using HTML/CSS/JavaScript
-Store uptime and response history
-Handle scheduled background tasks

REST endpoint reference:

GET /urls
Retrieve all monitored URLs

GET /urls/<id>
Retrieve details for one monitored URL

POST /urls
Add a new URL for monitoring

PUT /urls/<id>
Update monitored URL details

DELETE /urls/<id>
Remove a monitored URL

GET /logs/<id>
Retrieve monitoring logs for a URL

POST /check/<id>
Manually trigger a URL status check

Automation Concept:

response = requests.get(url, timeout=5)

if response.status_code == 200:
    status = "online"
else:
    status = "offline"

Roadmap:

1. Set up Flask application
2. Configure SQL database
3. Create URL and Log models
4. Build CRUD APIs
5. Implement automatic URL checking
6. Store monitoring history
7. Create frontend dashboard
8. Add filtering and search
9. Deploy on Render or Railway

Optional Advanced Features:

-Email alerts
-Telegram/Discord notifications
-Real-time dashboard updates
-Uptime percentage analytics
-Charts using Chart.js
-Authentication system
-Multi-user support


Skills You Will Learn:

-Flask backend development
-SQLAlchemy ORM
-REST API design
-Python automation
-Scheduled background jobs
-HTTP request handling
-Full-stack integration
-Database relationships
-Dashboard UI development


"""

import os
import time
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

URLS = [
    "https://google.com",
    "https://github.com",
    "https://openai.com"
]

CHECK_TIMEOUT = 5


# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------

def check_url_status(url):
    """
    Check whether a URL is online or offline.
    """

    try:
        start_time = time.time()

        response = requests.get(url, timeout=CHECK_TIMEOUT)

        end_time = time.time()

        response_time = round(end_time - start_time, 2)

        return {
            "url": url,
            "status": "online",
            "status_code": response.status_code,
            "response_time": response_time
        }

    except requests.exceptions.RequestException:

        return {
            "url": url,
            "status": "offline",
            "status_code": None,
            "response_time": None
        }


# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "URL Monitoring System Running",
        "total_urls": len(URLS)
    })


@app.route("/check-all", methods=["GET"])
def check_all_urls():

    results = []

    for url in URLS:

        result = check_url_status(url)

        results.append(result)

    return jsonify({
        "results": results
    })


@app.route("/check", methods=["POST"])
def check_single_url():

    data = request.get_json()

    if not data or "url" not in data:

        return jsonify({
            "error": "URL is required"
        }), 400

    url = data["url"]

    result = check_url_status(url)

    return jsonify(result)


# -------------------------------------------------------------------
# Save Results To File
# -------------------------------------------------------------------

@app.route("/save-results", methods=["GET"])
def save_results():

    results = []

    for url in URLS:

        result = check_url_status(url)

        results.append(result)

    file_path = "monitor_results.txt"

    with open(file_path, "w", encoding="utf-8") as file:

        for result in results:

            file.write(f"URL: {result['url']}\n")
            file.write(f"Status: {result['status']}\n")
            file.write(f"Status Code: {result['status_code']}\n")
            file.write(f"Response Time: {result['response_time']}\n")
            file.write("-" * 40 + "\n")

    return jsonify({
        "message": "Results saved successfully",
        "file": os.path.abspath(file_path)
    })


# -------------------------------------------------------------------
# Run Server
# -------------------------------------------------------------------

if __name__ == "__main__":

    print("URL Monitoring System Starting...")
    print("Visit: http://127.0.0.1:5000")

    app.run(debug=True)