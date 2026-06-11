# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## About

A Flask + Prometheus metrics demo. See [README.md](README.md) for details.

## Commands

```bash
# Setup (one-time)
python3 -m venv flask-metrics-venv
source flask-metrics-venv/bin/activate
pip install flask prometheus-client

# Run the app
python app.py                    # default port 5000, or set PORT env var

# Run quicksort
python3 quicksort.py
```

## Architecture

- `app.py` — Flask web server with four routes (`/`, `/health`, `/api/hello`, `/metrics`). Uses `prometheus_client` for Counter/Histogram/Gauge metrics in a dedicated registry. The `/metrics` endpoint returns `text/plain` Prometheus format.
- `quicksort.py` — standalone quick sort script (in-place, Lomuto partition, median-of-three pivot).
- Virtual env: `flask-metrics-venv/` (gitignored by convention).
