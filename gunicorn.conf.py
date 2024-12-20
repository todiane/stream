import multiprocessing

# Server socket
bind = "unix:/tmp/gunicorn.sock"
backlog = 2048

# Worker processes
workers = 2  # Changed to match current working setup
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Changed to match current working setup
keepalive = 5

# Logging
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = "info"  # Changed to match current working setup

# Process naming
proc_name = "stream_english"

# Django WSGI application path
wsgi_app = "stream.wsgi:application"

# Server mechanics
daemon = True  # Changed to run in daemon mode
pidfile = "gunicorn.pid"
user = None
group = None
umask = 0
tmp_upload_dir = None

# Performance settings
max_requests = 1000
max_requests_jitter = 50
capture_output = True

# Environment variables
raw_env = ["DJANGO_SETTINGS_MODULE=stream.settings"]
