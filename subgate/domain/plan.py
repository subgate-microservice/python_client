import datetime
from typing import Any
from uuid import UUID, uuid4

from subgate.domain.cycle import Cycle
from subgate.domain.discount import Discount
from subgate.domain.enums import Period
from subgate.domain.usage import UsageRate
from subgate.utils import get_current_datetime

ID = UUID


class Plan:
    def __init__(
            self,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Cycle | Period,
            description: str = None,
            level: int = 10,
            features: str = None,
            fields: dict[str, Any] = None,
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            created_at: datetime.datetime = None,
            updated_at: datetime.datetime = None,
            id: ID = None,
    ):
        self.id = id if id else uuid4()
        self.title = title
        self.price = price
        self.currency = currency
        self.billing_cycle = billing_cycle if isinstance(billing_cycle, Cycle) else Cycle.from_code(billing_cycle)
        self.description = description
        self.level = level
        self.features = features
        self.fields = fields if fields else {}
        self.usage_rates = usage_rates if usage_rates else []
        self.discounts = discounts if discounts else []
        self.created_at = created_at if created_at else get_current_datetime()
        self.updated_at = updated_at if updated_at else self.created_at

    def get_usage_rate(self, code: str) -> UsageRate:
        for rate in self.usage_rates:
            if rate.code == code:
                return rate
        raise KeyError(code)


class PlanCreate:
    def __init__(
            self,
            title: str,
            price: float,
            currency: str,
            cycle: Period = Period.Monthly,
            description: str = "",
            level: int = 10,
            features: str = "",
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            fields: dict[str, Any] = None,
    ):
        self.title = title
        self.price = price
        self.currency = currency
        self.billing_cycle = Cycle.from_code(cycle)
        self.description = description
        self.level = level
        self.features = features
        self.usage_rates = usage_rates if usage_rates is not None else []
        self.discounts = discounts if discounts is not None else []
        self.fields = fields if fields is not None else {}

    def get_usage_rate(self, code: str) -> UsageRate:
        for rate in self.usage_rates:
            if rate.code == code:
                return rate
        raise KeyError(code)
