import datetime
from typing import Self

from subgatekit.domain.cycle import Cycle
from subgatekit.domain.enums import Period
from subgatekit.utils import get_current_datetime, Number


class UsageRate:
    def __init__(
            self,
            title: str,
            code: str,
            unit: str,
            available_units: float,
            renew_cycle: Period,
    ):
        self.title = title
        self.code = code
        self.unit = unit
        self.available_units = available_units
        self.renew_cycle = Cycle.from_code(renew_cycle)


class Usage(UsageRate):
    def __init__(
            self,
            title: str,
            code: str,
            unit: str,
            available_units: Number,
            renew_cycle: Period,
            used_units: Number = 0,
            last_renew: datetime.datetime = None,
    ):
        super().__init__(title, code, unit, available_units, renew_cycle)
        self.used_units = used_units
        self.last_renew = last_renew if last_renew else get_current_datetime()

    @classmethod
    def from_usage_rate(cls, usage_rate: UsageRate) -> Self:
        return cls(
            title=usage_rate.title,
            code=usage_rate.code,
            unit=usage_rate.unit,
            available_units=usage_rate.available_units,
            used_units=0,
            renew_cycle=usage_rate.renew_cycle.code,
        )
