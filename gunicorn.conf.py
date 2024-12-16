import multiprocessing

# Path: /home/virtual/vps-cbced9/a/a588fe7474/stream/gunicorn.conf.py

# Gunicorn configuration
bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/virtual/vps-cbced9/a/a588fe7474/stream/logs/gunicorn-access.log"
errorlog = "/home/virtual/vps-cbced9/a/a588fe7474/stream/logs/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "stream_english"
