import datetime
from typing import Any, Optional, Self
from uuid import UUID, uuid4

from subgatekit.utils import get_current_datetime, Number
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.item_manager import ItemManager
from subgatekit.v2_0.domain.usage import UsageRate
from subgatekit.v2_0.domain.validators import (TypeValidator, FieldsValidator, raise_errors_if_necessary,
                                               ListTypeValidator, EnumValidator)

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
        self._validate(title, price, currency, billing_cycle, description, level, features, fields, usage_rates,
                       discounts, id)

        self._created_at = get_current_datetime()
        self._updated_at = self._created_at
        self._discounts = ItemManager(lambda x: x.code, discounts)
        self._usage_rates = ItemManager(lambda x: x.code, usage_rates)

        self.id = id if id else uuid4()
        self.price = price
        self.title = title
        self.description = description
        self.fields = fields if fields is not None else {}
        self.features = features
        self.level = level
        self.currency = currency
        self.billing_cycle = billing_cycle

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def usage_rates(self) -> ItemManager[UsageRate]:
        return self._usage_rates

    @property
    def discounts(self) -> ItemManager[Discount]:
        return self._discounts

    @staticmethod
    def _validate(
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
        validators = [
            TypeValidator("Plan.title", title, str),
            TypeValidator("Plan.price", price, Number),
            TypeValidator("Plan.currency", currency, str),
            EnumValidator("Plan.billing_cycle", billing_cycle, Period),
            TypeValidator("Plan.description", description, str, True),
            TypeValidator("Plan.level", level, int),
            TypeValidator("Plan.features", features, str, True),
            FieldsValidator("Plan.fields", fields),
            ListTypeValidator("Plan.usage_rates", usage_rates, UsageRate, True),
            ListTypeValidator("Plan.discounts", discounts, Discount, True),
            TypeValidator("Plan.id", id, ID),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


def create_plan_with_internal_fields(
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
    instance = Plan(title, price, currency, billing_cycle, description, level, features, fields, usage_rates,
                    discounts, id)
    object.__setattr__(instance, "_created_at", created_at)
    object.__setattr__(instance, "_updated_at", updated_at)
    return instance


class PlanInfo:
    def __init__(
            self,
            title: str,
            description: Optional[str] = None,
            level: int = 10,
            features: Optional[str] = None,
            id: ID = None,
    ):
        self._validate(title, description, level, features, id)
        self.title = title
        self.id = id if id else uuid4()
        self.description = description
        self.level = level
        self.features = features

    @classmethod
    def from_plan(cls, plan: Plan) -> Self:
        return cls(plan.title, plan.description, plan.level, plan.features, plan.id)

    @staticmethod
    def _validate(
            title: str,
            description: str = None,
            level: int = 10,
            features: str = None,
            id: ID = None,
    ):
        validators = [
            TypeValidator("Plan.title", title, str),
            TypeValidator("Plan.description", description, str, True),
            TypeValidator("Plan.level", level, int),
            TypeValidator("Plan.features", features, str, True),
            TypeValidator("Plan.id", id, ID),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)
