"""
Innovartus monitoring script (Project 4).

Generates load bursts against the deployed app while polling its
/metrics endpoint every 2 seconds, then plots:
  - cpu_usage_over_time.png
  - traffic_over_time.png

This works around Render's free-tier limitations (no CPU graphs,
1-hour graph resolution) by pulling self-reported stats directly
from the app and graphing them ourselves.

Usage:
    pip install requests matplotlib --break-system-packages
    python monitor.py https://innovartus-app.onrender.com
"""

import sys
import time
import random
import threading
import requests
import matplotlib.pyplot as plt
from datetime import datetime

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://innovartus-app.onrender.com"
ENDPOINTS = ["/", "/health", "/api/stats"]

# Shared data collected by the poller thread
timestamps = []
cpu_values = []
mem_values = []
request_counts = []

stop_flag = False


def poller(interval=2):
    """Poll /metrics every `interval` seconds until stop_flag is set."""
    while not stop_flag:
        try:
            r = requests.get(BASE_URL + "/metrics", timeout=10)
            data = r.json()
            timestamps.append(datetime.now())
            cpu_values.append(data["cpu_percent"])
            mem_values.append(data["memory_percent"])
            request_counts.append(data["requests_served"])
            print(f"[poll] cpu={data['cpu_percent']}% mem={data['memory_percent']}% "
                  f"reqs={data['requests_served']}")
        except Exception as e:
            print(f"[poll] error: {e}")
        time.sleep(interval)


def burst(n_requests=40):
    print(f"--- Burst of {n_requests} requests ---")
    for i in range(n_requests):
        path = random.choice(ENDPOINTS)
        try:
            requests.get(BASE_URL + path, timeout=10)
        except requests.RequestException:
            pass
        time.sleep(0.1)


def quiet_period(seconds=30):
    print(f"--- Quiet period for {seconds}s ---")
    time.sleep(seconds)


def plot_results():
    if not timestamps:
        print("No data collected -- check that /metrics is deployed and reachable.")
        return

    t0 = timestamps[0]
    elapsed = [(t - t0).total_seconds() for t in timestamps]

    # CPU usage over time
    plt.figure(figsize=(10, 5))
    plt.plot(elapsed, cpu_values, marker="o", color="#0ea5e9")
    plt.title("CPU Usage Over Time")
    plt.xlabel("Seconds since start")
    plt.ylabel("CPU %")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("cpu_usage_over_time.png", dpi=150)
    print("Saved cpu_usage_over_time.png")

    # Traffic (cumulative requests) over time
    plt.figure(figsize=(10, 5))
    plt.plot(elapsed, request_counts, marker="o", color="#38bdf8")
    plt.title("Traffic Pattern (Cumulative Requests Served)")
    plt.xlabel("Seconds since start")
    plt.ylabel("Total requests served")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("traffic_over_time.png", dpi=150)
    print("Saved traffic_over_time.png")

    # Print summary for the results table
    print("\n--- Summary for results table ---")
    print(f"CPU  -> peak: {max(cpu_values):.1f}%  avg: {sum(cpu_values)/len(cpu_values):.1f}%")
    total_reqs = request_counts[-1] - request_counts[0] if len(request_counts) > 1 else 0
    print(f"Traffic -> total requests during run: {total_reqs}")


if __name__ == "__main__":
    print(f"Target: {BASE_URL}")
    poll_thread = threading.Thread(target=poller, args=(2,), daemon=True)
    poll_thread.start()

    for cycle in range(3):
        burst(n_requests=40)
        quiet_period(seconds=30)

    stop_flag = True
    time.sleep(3)  # let poller thread finish its last cycle
    plot_results()
    print("\nDone.")
