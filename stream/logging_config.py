import os
from pathlib import Path
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

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
        "format": "[{asctime}] {levelname} {module} {process} {thread} {message}\n{exc_info}\n{pathname} {lineno}",
        "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "ignore_404_errors": {
            "()": "django.utils.log.CallbackFilter",
            "callback": lambda record: not (
                record.exc_info and record.exc_info[0] in (Http404, ObjectDoesNotExist)
            ),
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": os.path.join(BASE_DIR, "logs", "django.log"),
            "formatter": "verbose",
            "level": "DEBUG",
            "mode": "a",
        },
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false", "ignore_404_errors"],
            "class": "django.utils.log.AdminEmailHandler",
            "include_html": True,
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
        "shop.stripe": {
            "handlers": ["file"],
            "level": "DEBUG",  # Set to DEBUG to catch all Stripe-related logs
            "propagate": True,
        },
        "django.request": {
            "handlers": ["file", "mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "courses": {
            "handlers": ["file"],
            "level": "DEBUG",  # Set to DEBUG to catch all course-related logs
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": False,
        },
        "shop.emails": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
        "profiles": {
            "handlers": ["file"],
            "level": "ERROR",
            "propagate": True,
        },
    },
}
