import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 3
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Logging
errorlog = "logs/gunicorn-error.log"
accesslog = "logs/gunicorn-access.log"
loglevel = "debug"

# Process naming
proc_name = "stream_english"

# Django WSGI application path in pattern MODULE_NAME:VARIABLE_NAME
wsgi_app = "stream.wsgi:application"

# Server mechanics
daemon = False
pidfile = "logs/gunicorn.pid"
user = None
group = None
umask = 0
tmp_upload_dir = None

# Environment variables
raw_env = ["DJANGO_SETTINGS_MODULE=stream.settings"]
