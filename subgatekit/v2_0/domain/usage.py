import datetime
from typing import Self, Optional

from subgatekit.utils import get_current_datetime, Number
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.validators import TypeValidator, EnumValidator, raise_errors_if_necessary


class UsageRate:
    def __init__(
            self,
            title: str,
            code: str,
            unit: str,
            available_units: float,
            renew_cycle: Period,
    ):
        self._validate(title, code, unit, available_units, renew_cycle)
        self.title = title
        self.code = code
        self.unit = unit
        self.available_units = available_units
        self.renew_cycle = renew_cycle

    @staticmethod
    def _validate(
            title: str,
            code: str,
            unit: str,
            available_units: float,
            renew_cycle: Period,
    ):
        validators = [
            TypeValidator("UsageRate.title", title, str),
            TypeValidator("UsageRate.code", code, str),
            TypeValidator("UsageRate.unit", unit, str),
            TypeValidator("UsageRate.available_units", available_units, Number),
            EnumValidator("UsageRate.renew_cycle", renew_cycle, Period),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


class Usage:
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
        self._validate(title, code, unit, available_units, renew_cycle, used_units, last_renew)
        self.title = title
        self.code = code
        self.unit = unit
        self.available_units = available_units
        self.used_units = used_units
        self.renew_cycle = renew_cycle
        self.last_renew = last_renew if last_renew else get_current_datetime()

    @classmethod
    def from_usage_rate(cls, usage_rate: UsageRate) -> Self:
        return cls(
            title=usage_rate.title,
            code=usage_rate.code,
            unit=usage_rate.unit,
            available_units=usage_rate.available_units,
            used_units=0,
            renew_cycle=usage_rate.renew_cycle,
        )

    def increase(self, delta: float) -> None:
        self.used_units += delta

    @staticmethod
    def _validate(
            title: str,
            code: str,
            unit: str,
            available_units: float,
            renew_cycle: Period,
            used_units: Number,
            last_renew: Optional[datetime.datetime],
    ):
        validators = [
            TypeValidator("UsageRate.title", title, str),
            TypeValidator("UsageRate.code", code, str),
            TypeValidator("UsageRate.unit", unit, str),
            TypeValidator("UsageRate.available_units", available_units, Number),
            EnumValidator("UsageRate.renew_cycle", renew_cycle, Period),
            TypeValidator("UsageRate.used_units", used_units, Number),
            TypeValidator("UsageRate.last_renew", last_renew, datetime.datetime, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)
