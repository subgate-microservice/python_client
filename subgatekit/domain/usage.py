from typing import Self

from subgatekit.domain.cycle import Cycle
from subgatekit.domain.enums import Period


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


class Usage:
    def __init__(
            self,
            title: str,
            code: str,
            unit: str,
            available_units: float,
            used_units: float,
            renew_cycle: Period,
    ):
        self.title = title
        self.code = code
        self.unit = unit
        self.available_units = available_units
        self.used_units = used_units
        self.renew_cycle = Cycle.from_code(renew_cycle)

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


class UsageForm:
    def __init__(self, code: str, value: float):
        self.code = code
        self.value = value
