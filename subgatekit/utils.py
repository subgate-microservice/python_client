import datetime
from typing import Union


def get_current_datetime():
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0)


Number = Union[int, float]
