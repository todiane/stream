#!/bin/bash

# Exit on error
set -e

echo "Starting application deployment: $(date)"

# Function to check environment variables
check_environment() {
    echo "Checking environment variables..."
    if [ -z "$DATABASE_URL" ]; then
        echo "ERROR: DATABASE_URL is not set"
        # Print all environment variables for debugging (excluding sensitive values)
        printenv | grep -v "SECRET\|KEY\|PASSWORD"
        exit 1
    else
        echo "DATABASE_URL is set"
    fi
}

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

# Run all checks and setup
clean_up
check_environment
collect_static
run_migrations

echo "Starting Gunicorn..."
exec gunicorn stream.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}" \
    --workers 2 \
    --threads 2 \
    --timeout 60 \
    --log-level debug \
    --capture-output \
    --enable-stdio-inheritance
    