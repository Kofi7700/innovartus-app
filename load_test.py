"""
Simple load generator for the Innovartus monitoring case study.

Hits the deployed app's endpoints repeatedly in bursts, with quiet gaps
in between, so Render's CPU/traffic graphs show clear peaks and valleys
instead of a flat line -- useful for the "CPU usage over time" and
"traffic patterns" deliverables.

Usage:
    pip install requests --break-system-packages
    python load_test.py https://innovartus-app.onrender.com
"""

import sys
import time
import random
import requests

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://innovartus-app.onrender.com"
ENDPOINTS = ["/", "/health", "/api/stats"]

def burst(n_requests=40):
    """Fire a burst of requests to create a visible CPU/traffic spike."""
    print(f"--- Burst of {n_requests} requests ---")
    for i in range(n_requests):
        path = random.choice(ENDPOINTS)
        try:
            r = requests.get(BASE_URL + path, timeout=10)
            print(f"[{i+1}/{n_requests}] GET {path} -> {r.status_code}")
        except requests.RequestException as e:
            print(f"[{i+1}/{n_requests}] GET {path} -> ERROR: {e}")
        time.sleep(0.1)  # small delay so it's not instant

def quiet_period(seconds=30):
    print(f"--- Quiet period for {seconds}s (lets graph show a dip) ---")
    time.sleep(seconds)

if __name__ == "__main__":
    print(f"Target: {BASE_URL}")
    print("Running 3 burst/quiet cycles. Watch the Render Metrics tab live.\n")
    for cycle in range(3):
        burst(n_requests=40)
        quiet_period(seconds=30)
    print("\nDone. Check Render's Metrics tab now -- you should see 3 spikes.")
