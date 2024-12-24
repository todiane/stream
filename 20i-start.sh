#!/bin/bash

# Exit on error
set -e

echo "Starting application setup..."

# Set up log directory if it doesn't exist
mkdir -p logs

# Collect static files
python3.9 manage.py collectstatic --noinput

# Run migrations
python3.9 manage.py migrate --noinput

# Clean up any existing processes and files
pkill -f "gunicorn" || true
rm -f gunicorn.pid

# Gunicorn configuration
GUNICORN_CMD="gunicorn stream.wsgi:application \
    --bind 127.0.0.1:8000 \
    --workers 1 \
    --threads 2 \
    --timeout 120 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --log-level info \
    --max-requests 500 \
    --max-requests-jitter 50 \
    --capture-output \
    --pid gunicorn.pid \
    --daemon"

# Start Gunicorn
nohup $GUNICORN_CMD >> logs/nohup.out 2>&1

# Wait for gunicorn to start
sleep 5

# Check if gunicorn is running
if ! pgrep -f "gunicorn stream.wsgi:application" > /dev/null; then
    echo "Failed to start gunicorn"
    exit 1
fi

echo "Gunicorn started successfully. Monitoring..."

# Monitor in the background
(
while true; do
    if ! pgrep -f "gunicorn stream.wsgi:application" > /dev/null; then
        echo "$(date): Gunicorn not running, restarting..." >> logs/gunicorn-monitor.log
        
        # Clean up
        pkill -f "gunicorn" || true
        rm -f gunicorn.pid
        
        # Restart using same configuration
        $GUNICORN_CMD
    fi
    sleep 60
done
) &

echo "Monitor started in background. You can safely exit this terminal."