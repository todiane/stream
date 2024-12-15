# utils/logging_utils.py
import logging
import traceback
from functools import wraps

logger = logging.getLogger("stream")


def log_exception(func):
    """
    Decorator to log exceptions with full traceback
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__name__}: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            raise

    return wrapper


def log_database_errors():
    """
    Test database connection and log any issues
    """
    from django.db import connections
    from django.db.utils import OperationalError

    try:
        db_conn = connections["default"]
        db_conn.cursor()
    except OperationalError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected database error: {str(e)}")
        raise
