#!/usr/bin/env python3
"""Generate simulated application server logs with embedded anomalies."""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone

random.seed(42)

ENDPOINTS = ["/api/users", "/api/orders", "/api/products", "/api/health"]
METHODS_BY_ENDPOINT = {
    "/api/users": ["GET", "POST", "PUT"],
    "/api/orders": ["GET", "POST"],
    "/api/products": ["GET", "PUT", "DELETE"],
    "/api/health": ["GET"],
}

# Normal hourly request rates (approximate requests per hour)
NORMAL_RATE = 25  # ~25 requests/hour -> ~600 over 24h


def normal_status():
    """Return a status code with ~2% error rate."""
    r = random.random()
    if r < 0.02:
        return random.choice([500, 502, 503])
    elif r < 0.06:
        return random.choice([400, 401, 404, 429])
    return 200


def normal_latency():
    """Return latency in the normal range 50-200ms."""
    return round(random.gauss(120, 35))


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def generate():
    logs = []
    start = datetime(2025, 3, 15, 0, 0, 0, tzinfo=timezone.utc)

    for hour in range(24):
        hour_start = start + timedelta(hours=hour)

        # Determine request count for this hour
        if 3 <= hour < 4:
            # Anomaly 3: traffic drop to ~20%
            count = max(1, int(NORMAL_RATE * 0.2))
        else:
            count = NORMAL_RATE + random.randint(-3, 3)

        for _ in range(count):
            ts = hour_start + timedelta(seconds=random.randint(0, 3599))
            endpoint = random.choice(ENDPOINTS)
            method = random.choice(METHODS_BY_ENDPOINT[endpoint])
            request_id = str(uuid.uuid4())

            # Default normal behavior
            status = normal_status()
            latency = clamp(normal_latency(), 20, 350)

            # Anomaly 2: Latency spike at 09:00-09:15 on /api/products
            if hour == 9 and ts.minute < 15 and endpoint == "/api/products":
                latency = clamp(int(random.gauss(6000, 1500)), 3000, 12000)

            entry = {
                "timestamp": ts.isoformat(),
                "method": method,
                "path": endpoint,
                "status_code": status,
                "latency_ms": latency,
                "request_id": request_id,
            }
            logs.append((ts, entry))

        # Anomaly 2: Inject extra /api/products high-latency traffic at 09:00-09:15
        if hour == 9:
            for _ in range(10):
                ts = hour_start + timedelta(seconds=random.randint(0, 899))  # first 15 min
                method = "GET"
                request_id = str(uuid.uuid4())
                latency = clamp(int(random.gauss(6000, 1500)), 3000, 12000)
                entry = {
                    "timestamp": ts.isoformat(),
                    "method": method,
                    "path": "/api/products",
                    "status_code": 200,
                    "latency_ms": latency,
                    "request_id": request_id,
                }
                logs.append((ts, entry))

        # Anomaly 1: Inject extra /api/orders error-spike traffic at 14:00-14:30
        if hour == 14:
            for _ in range(30):
                ts = hour_start + timedelta(seconds=random.randint(0, 1799))  # first 30 min
                method = random.choice(["GET", "POST"])
                request_id = str(uuid.uuid4())
                if random.random() < 0.40:
                    status = random.choice([500, 502, 503])
                    latency = clamp(int(random.gauss(400, 100)), 200, 800)
                else:
                    status = 200
                    latency = clamp(normal_latency(), 20, 350)
                entry = {
                    "timestamp": ts.isoformat(),
                    "method": method,
                    "path": "/api/orders",
                    "status_code": status,
                    "latency_ms": latency,
                    "request_id": request_id,
                }
                logs.append((ts, entry))

    # Sort by timestamp
    logs.sort(key=lambda x: x[0])

    out_path = "/Users/jinzexu/AgentBench-Live/tasks/fixtures/data-002/server.log.jsonl"
    with open(out_path, "w") as f:
        for _, entry in logs:
            f.write(json.dumps(entry) + "\n")

    print(f"Generated {len(logs)} log entries -> {out_path}")

    # Quick anomaly summary for verification
    error_14 = sum(1 for _, e in logs if e["path"] == "/api/orders"
                   and e["timestamp"].startswith("2025-03-15T14:")
                   and e["timestamp"][14:16] < "30"
                   and e["status_code"] >= 500)
    total_14 = sum(1 for _, e in logs if e["path"] == "/api/orders"
                   and e["timestamp"].startswith("2025-03-15T14:")
                   and e["timestamp"][14:16] < "30")
    print(f"Anomaly 1 (error spike 14:00-14:30 /api/orders): {error_14}/{total_14} 5xx")

    lat_09 = [e["latency_ms"] for _, e in logs if e["path"] == "/api/products"
              and e["timestamp"].startswith("2025-03-15T09:")
              and e["timestamp"][14:16] < "15"]
    if lat_09:
        print(f"Anomaly 2 (latency spike 09:00-09:15 /api/products): "
              f"count={len(lat_09)}, avg={sum(lat_09)/len(lat_09):.0f}ms, "
              f"max={max(lat_09)}ms")

    hour3 = sum(1 for _, e in logs if e["timestamp"].startswith("2025-03-15T03:"))
    hour5 = sum(1 for _, e in logs if e["timestamp"].startswith("2025-03-15T05:"))
    print(f"Anomaly 3 (traffic drop 03:00-04:00): {hour3} reqs vs normal ~{hour5} reqs")


if __name__ == "__main__":
    generate()
