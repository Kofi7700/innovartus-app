import psutil
import os
import logging
import time
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# --- Basic logging setup (visible in Render/hosting platform logs) ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("innovartus")

START_TIME = time.time()
REQUEST_COUNT = 0
ERROR_COUNT = 0


# @app.before_request
# def log_request():
#     global REQUEST_COUNT
#     REQUEST_COUNT += 1
#     logger.info(f"Request #{REQUEST_COUNT} received at {datetime.utcnow().isoformat()}")

from prometheus_client import (
    Gauge,
    Counter,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

uptime_gauge = Gauge(
    "app_uptime_seconds",
    "Application uptime in seconds"
)


cpu_gauge = Gauge('app_cpu_percent', 'CPU usage percent')
mem_gauge = Gauge('app_memory_percent', 'Memory usage percent')
requests_counter = Counter('app_requests_total', 'Total requests served')

@app.before_request
def log_request():
    global REQUEST_COUNT
    REQUEST_COUNT += 1
    requests_counter.inc()
    logger.info(f"Request #{REQUEST_COUNT} received at {datetime.utcnow().isoformat()}")

@app.route("/prometheus-metrics")
def prometheus_metrics():
    cpu_gauge.set(psutil.cpu_percent(interval=0.2))
    mem_gauge.set(psutil.virtual_memory().percent)
    uptime_gauge.set(time.time() - START_TIME)

    return (
        generate_latest(),
        200,
        {"Content-Type": CONTENT_TYPE_LATEST},
    )



@app.route("/")
def home():
    return render_template("index.html", request_count=REQUEST_COUNT)


@app.route("/health")
def health():
    """Simple health-check endpoint — useful for uptime monitoring tools
    like UptimeRobot, Render's health checks, or a status page."""
    uptime_seconds = round(time.time() - START_TIME, 2)
    return jsonify({
        "status": "ok",
        "uptime_seconds": uptime_seconds,
        "requests_served": REQUEST_COUNT,
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route("/metrics")
def metrics():
    """Self-reported system metrics -- CPU% and memory, since Render's
    free tier hides these behind a paid plan. This gives us full control
    over polling frequency and graph resolution."""
    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "memory_percent": psutil.virtual_memory().percent,
        "requests_served": REQUEST_COUNT,
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route("/api/stats")
def stats():
    """Fake 'SaaS metric' endpoint — demonstrates an API a real product
    would expose. Also useful to show in your report as a monitored metric."""
    return jsonify({
        "app": "Innovartus SaaS Demo",
        "requests_served": REQUEST_COUNT,
        "errors": ERROR_COUNT,
        "uptime_seconds": round(time.time() - START_TIME, 2)
    })


@app.errorhandler(404)
def not_found(e):
    global ERROR_COUNT
    ERROR_COUNT += 1
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    global ERROR_COUNT
    ERROR_COUNT += 1
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
