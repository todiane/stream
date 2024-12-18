import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Create logs directory if it doesn't exist
logs_dir = BASE_DIR / "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {module} {process} {thread} {message}\n{exc_info}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "stream": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
