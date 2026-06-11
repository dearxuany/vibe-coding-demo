#!/usr/bin/env python3
"""Flask web service exposing Prometheus-compatible metrics at /metrics."""

from flask import Flask, request, jsonify
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CollectorRegistry,
    multiprocess,
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
)
import time
import os

app = Flask(__name__)

# Create a dedicated registry so built-in process metrics are included
registry = CollectorRegistry(auto_describe=True)

# Register built-in collectors for process/GC/platform metrics
registry.register(PROCESS_COLLECTOR)
registry.register(PLATFORM_COLLECTOR)
registry.register(GC_COLLECTOR)

# Custom metrics
REQUEST_COUNT = Counter(
    "flask_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "flask_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
    registry=registry,
)

IN_FLIGHT = Gauge(
    "flask_http_requests_in_flight",
    "Currently in-flight HTTP requests",
    registry=registry,
)


@app.before_request
def before_request():
    request._start_time = time.time()
    IN_FLIGHT.inc()


@app.after_request
def after_request(response):
    IN_FLIGHT.dec()
    latency = time.time() - request._start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.endpoint or request.path,
        status=response.status_code,
    ).inc()
    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.endpoint or request.path,
    ).observe(latency)
    return response


@app.route("/")
def index():
    return jsonify({
        "service": "flask-metrics-demo",
        "endpoints": {
            "/": "this info",
            "/metrics": "Prometheus metrics",
            "/health": "health check",
            "/api/hello": "sample API endpoint",
        },
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


@app.route("/api/hello")
def hello():
    name = request.args.get("name", "world")
    return jsonify({"message": f"Hello, {name}!"})


@app.route("/metrics")
def metrics():
    """Expose metrics in Prometheus text format."""
    return generate_latest(registry), 200, {"Content-Type": "text/plain; charset=utf-8"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
