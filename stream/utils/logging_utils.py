import logging
import traceback
from functools import wraps

logger = logging.getLogger("django")


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


def log_error(message, exception=None):
    """
    Utility function to log errors with consistent formatting
    """
    if exception:
        logger.error(f"{message}: {str(exception)}\n{traceback.format_exc()}")
    else:
        logger.error(message)
