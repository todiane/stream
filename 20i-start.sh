#!/bin/bash

# Exit on error
set -e

echo "Starting application setup..."

# Collect static files
python3.9 manage.py collectstatic --noinput

# Run migrations
python3.9 manage.py migrate --noinput

# Start Gunicorn
exec gunicorn stream.wsgi:application \
    --bind unix:/tmp/gunicorn.sock \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
    