#!/bin/bash

# Exit on error
set -e

echo "Starting application deployment: $(date)"

# Function to run migrations with error handling
run_migrations() {
    echo "Running migrations..."
    if python manage.py migrate --noinput; then
        echo "Migrations completed successfully"
    else
        echo "Migration failed. Exiting."
        exit 1
    fi
}

# Function to collect static files with error handling
collect_static() {
    echo "Collecting static files..."
    if python manage.py collectstatic --noinput; then
        echo "Static files collected successfully"
    else
        echo "Static file collection failed. Exiting."
        exit 1
    fi
}

# Kill any hanging processes before starting
clean_up() {
    echo "Cleaning up any previous processes..."
    pkill -f "manage.py" || true
    pkill -f "gunicorn" || true
}

# Ensure migrations don't hang by cleaning up before running
clean_up

# Run setup tasks
collect_static
run_migrations

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance
