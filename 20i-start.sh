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

# Start Gunicorn with enhanced configuration
exec gunicorn stream.wsgi:application \
    --bind unix:/tmp/gunicorn.sock \
    --workers 2 \
    --timeout 60 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --log-level info \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --capture-output \
    --pid gunicorn.pid \
    --daemon

# Add monitoring check
while true; do
    if ! pgrep -f "gunicorn stream.wsgi:application" > /dev/null; then
        echo "$(date): Gunicorn not running, restarting..." >> logs/gunicorn-monitor.log
        exec gunicorn stream.wsgi:application \
            --bind unix:/tmp/gunicorn.sock \
            --workers 2 \
            --timeout 60 \
            --access-logfile logs/gunicorn-access.log \
            --error-logfile logs/gunicorn-error.log \
            --log-level info \
            --max-requests 1000 \
            --max-requests-jitter 50 \
            --capture-output \
            --pid gunicorn.pid \
            --daemon
    fi
    sleep 300  # Check every 5 minutes
done