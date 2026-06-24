#!/bin/bash

# Stop Insurance OCR Application

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$APP_DIR/.app.pid"

if [ ! -f "$PID_FILE" ]; then
    echo "Application is not running (no PID file found)"
    exit 0
fi

PID=$(cat "$PID_FILE")

if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "Application is not running (stale PID file)"
    rm -f "$PID_FILE"
    exit 0
fi

echo "Stopping Insurance OCR (PID: $PID)..."
kill "$PID"

# Wait for process to stop
for i in {1..10}; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
        echo "Application stopped successfully"
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
done

# Force kill if still running
echo "Force killing..."
kill -9 "$PID" 2>/dev/null
rm -f "$PID_FILE"
echo "Application stopped (force killed)"
