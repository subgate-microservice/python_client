import datetime
from typing import Union
from uuid import UUID


def get_current_datetime():
    return datetime.datetime.now(datetime.UTC).replace(microsecond=0)


Number = Union[int, float]
ID = UUID
