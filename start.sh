#!/bin/bash

# Start Insurance OCR Application

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$APP_DIR/.app.pid"
LOG_FILE="$APP_DIR/.app.log"

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Application is already running (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

echo "Starting Insurance OCR..."
cd "$APP_DIR"
nohup python3 app.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

sleep 2

# Verify it started
PID=$(cat "$PID_FILE")
if ps -p "$PID" > /dev/null 2>&1; then
    echo "Application started successfully (PID: $PID)"
    echo "Access: http://localhost:8000"
    echo "Log: $LOG_FILE"
else
    echo "Failed to start application. Check $LOG_FILE for details."
    rm -f "$PID_FILE"
    exit 1
fi
