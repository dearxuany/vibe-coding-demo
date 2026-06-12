#!/usr/bin/env bash
set -e

IMAGE="flask-metrics-demo"
CONTAINER="flask-metrics-demo"
PORT="${PORT:-5000}"

# Build
echo ">>> Building image: $IMAGE ..."
docker build -t "$IMAGE" "$(dirname "$0")/.."

# Stop and remove old container
echo ">>> Removing old container (if any) ..."
docker stop "$CONTAINER" 2>/dev/null || true
docker rm "$CONTAINER" 2>/dev/null || true

# Run
echo ">>> Starting container: $CONTAINER on port $PORT ..."
docker run -d --name "$CONTAINER" -p "$PORT:5000" \
    -v "$(dirname "$0")/../docs:/app/docs" \
    "$IMAGE"

echo ">>> Done."
docker ps --filter "name=$CONTAINER" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
