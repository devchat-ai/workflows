import time
from functools import wraps


def print_exec_time(message: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = end_time - start_time
            print(f"{message} ({duration:.3f} s)", flush=True)
            return result

        return wrapper

    return decorator
