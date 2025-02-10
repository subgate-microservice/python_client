import datetime
from functools import wraps
from typing import Union


def get_current_datetime():
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0)


def to_camel_case(snake_str: str) -> str:
    parts = snake_str.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])


def docstring(doc: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper.__doc__ = doc
        return wrapper

    return decorator


Number = Union[int, float]
