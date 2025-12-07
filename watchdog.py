import time
import docker
import psutil
import os
import requests  # For alerts

client = docker.from_env()
ALERT_WEBHOOK = os.getenv("ALERT_WEBHOOK")  # e.g., Discord

def check_metrics():
    while True:
        # CPU >95% for 10min?
        if psutil.cpu_percent(interval=600) > 95:
            alert("High CPU anomaly")
            kill_abyss()
        # Traffic >5GB/day?
        net_io = psutil.net_io_counters()
        if net_io.bytes_sent + net_io.bytes_recv > 5 * 1024**3:
            alert("High outbound traffic")
            kill_abyss()
        # Check for forbidden repos/publishes
        # (Poll GitHub API or logs)
        time.sleep(60)

def kill_abyss():
    client.containers.get("abyss-caged").kill()
    if ALERT_WEBHOOK:
        requests.post(ALERT_WEBHOOK, json={"content": "ABYSS breached—killed."})

def alert(msg):
    print(f"ALERT: {msg}")  # Or push to Telegram/Discord

if __name__ == "__main__":
    check_metrics()
