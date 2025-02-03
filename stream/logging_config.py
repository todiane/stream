# logging_config.py
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
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{asctime}] {levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "debug.log"),
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "profiles": {  # Add specific logger for profiles app
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "courses": {  # Add specific logger for courses app
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
    "root": {  # This will catch all loggers
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
}