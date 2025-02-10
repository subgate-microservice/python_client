import datetime
from typing import Any, Optional, Self
from uuid import UUID, uuid4

from subgatekit.client.exceptions import ItemAlreadyExist
from subgatekit.utils import get_current_datetime
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.usage import UsageRate

ID = UUID


class Plan:
    def __init__(
            self,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Period,
            description: str = None,
            level: int = 10,
            features: str = None,
            fields: dict[str, Any] = None,
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            id: ID = None,
    ):
        self._created_at = get_current_datetime()
        self._updated_at = self._created_at
        self._discounts = {x.code: x for x in discounts} if discounts is not None else []
        self._usage_rates = {x.code: x for x in usage_rates} if usage_rates is not None else []

        self.id = id if id else uuid4()
        self.price = price
        self.title = title
        self.description = description
        self.fields = fields if fields is not None else {}
        self.features = features
        self.level = level
        self.currency = currency
        self.billing_cycle = billing_cycle

    @classmethod
    def _create_internal(
            cls,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Period,
            description: str,
            level: int,
            features: str,
            fields: dict[str, Any],
            usage_rates: list[UsageRate],
            discounts: list[Discount],
            id: ID,
            created_at: datetime,
            updated_at: datetime,
    ):
        instance = cls(title, price, currency, billing_cycle, description, level, features, fields, usage_rates,
                       discounts, id)
        object.__setattr__(instance, "_created_at", created_at)
        object.__setattr__(instance, "_updated_at", updated_at)
        return instance

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    def get_usage_rates(self) -> list[UsageRate]:
        return list(self._usage_rates.values())

    def add_usage_rate(self, usage_rate: UsageRate) -> None:
        if self._usage_rates.get(usage_rate.code):
            raise ItemAlreadyExist(usage_rate.__class__.__name__, usage_rate.code, "code")
        self._usage_rates[usage_rate.code] = usage_rate

    def remove_usage_rate(self, code: str) -> None:
        self._usage_rates.pop(code, None)

    def get_discounts(self) -> list[Discount]:
        return list(self._discounts.values())

    def add_discount(self, discount: Discount) -> None:
        code = discount.code
        if self._discounts.get(code):
            raise ItemAlreadyExist(discount.__class__.__name__, code, "code")
        self._discounts[code] = discount

    def remove_discount(self, code: str) -> None:
        self._discounts.pop(code, None)


class PlanInfo:
    def __init__(
            self,
            title: str,
            description: Optional[str] = None,
            level: int = 10,
            features: Optional[str] = None,
            id: ID = None,
    ):
        self.title = title
        self.id = id if id else uuid4()
        self.description = description
        self.level = level
        self.features = features

    @classmethod
    def from_plan(cls, plan: Plan) -> Self:
        return cls(plan.title, plan.description, plan.level, plan.features, plan.id)
