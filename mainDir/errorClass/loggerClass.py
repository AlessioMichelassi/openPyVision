import logging
import traceback
from functools import wraps

class ErrorClass:
    def __init__(self):
        pass  # Remove the logging configuration here

    def __del__(self):
        logging.shutdown()

    def log(self, log_level=logging.INFO):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                logging.log(log_level, f"Executing {func.__name__} with args={args}, kwargs={kwargs}")
                try:
                    result = func(*args, **kwargs)
                    logging.log(log_level, f"{func.__name__} completed successfully.")
                    return result
                except Exception as e:
                    logging.error(f"Error in {func.__name__}: {e}")
                    logging.error(traceback.format_exc())  # Log the full traceback
                    print(f"\n\n*** Error ***\nError in {func.__name__}: {e}\n")
                    raise
            return wrapper
        return decorator

    def log_exception(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {func.__name__}: {e}")
                logging.error(traceback.format_exc())
                raise
        return wrapper

# Use a single instance of ErrorClass for decorators
error_logger = ErrorClass()
