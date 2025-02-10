import datetime
from typing import Any, Optional, Self
from uuid import UUID, uuid4

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
            created_at: datetime.datetime = None,
            updated_at: datetime.datetime = None,
            id: ID = None,
    ):
        self._created_at = created_at if created_at else get_current_datetime()
        self._updated_at = updated_at if updated_at else self._created_at

        self.id = id if id else uuid4()
        self.price = price
        self.title = title
        self.description = description
        self.fields = fields if fields else {}
        self.features = features
        self.level = level
        self.currency = currency
        self.billing_cycle = billing_cycle
        self.discounts = discounts if discounts is not None else []
        self.usage_rates = usage_rates if usage_rates is not None else []

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at


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
