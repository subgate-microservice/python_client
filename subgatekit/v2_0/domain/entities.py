from _datetime import datetime
from copy import copy
from typing import Self, Optional, Any
from uuid import uuid4

from subgatekit.v2_0.domain.enums import Period, SubscriptionStatus, EventCode
from subgatekit.v2_0.domain.item_manager import ItemManager
from subgatekit.v2_0.domain.utils import get_current_datetime, Number, ID
from subgatekit.v2_0.domain.validators import (
    TypeValidator,
    EnumValidator,
    BoundaryValidator,
    ListTypeValidator,
    FieldsValidator,
    raise_errors_if_necessary,
)


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
            last_renew: datetime = None,
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
            last_renew: Optional[datetime],
    ):
        validators = [
            TypeValidator("UsageRate.title", title, str),
            TypeValidator("UsageRate.code", code, str),
            TypeValidator("UsageRate.unit", unit, str),
            TypeValidator("UsageRate.available_units", available_units, Number),
            EnumValidator("UsageRate.renew_cycle", renew_cycle, Period),
            TypeValidator("UsageRate.used_units", used_units, Number),
            TypeValidator("UsageRate.last_renew", last_renew, datetime, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


class Discount:
    def __init__(
            self,
            title: str,
            code: str,
            size: float,
            valid_until: datetime,
            description: str = None,
    ):
        self._validate(title, code, size, valid_until, description)
        self.title = title
        self.code = code
        self.description = description
        self.size = size
        self.valid_until = valid_until

    @staticmethod
    def _validate(
            title: str,
            code: str,
            size: float,
            valid_until: datetime,
            description: str,
    ):
        validators = [
            TypeValidator("Discount.title", title, str),
            TypeValidator("Discount.code", code, str),
            TypeValidator("Discount.size", size, float),
            BoundaryValidator("Discount.size", size, ge=0, lt=1),
            TypeValidator("Discount.valid_until", valid_until, datetime),
            TypeValidator("Discount.description", description, str, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


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
            FieldsValidator("Plan.fields", fields, True),
            ListTypeValidator("Plan.usage_rates", usage_rates, UsageRate, True),
            ListTypeValidator("Plan.discounts", discounts, Discount, True),
            TypeValidator("Plan.id", id, ID, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


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


class BillingInfo:
    def __init__(
            self,
            price: Number,
            currency: str,
            billing_cycle: Period,
            last_billing: datetime = None,
    ):
        self.billing_cycle = billing_cycle
        self.currency = currency
        self.price = price
        self.last_billing = last_billing if last_billing else get_current_datetime()

    @classmethod
    def from_plan(cls, plan: Plan) -> Self:
        return cls(plan.price, plan.currency, plan.billing_cycle, get_current_datetime())

    @staticmethod
    def _validate(
            price: Number,
            currency: str,
            billing_cycle: Period,
            last_billing: datetime,
    ):
        validators = [
            TypeValidator("BillingInfo.price", price, Number),
            TypeValidator("BillingInfo.currency", currency, str),
            EnumValidator("BillingInfo.billing_cycle", billing_cycle, Period),
            TypeValidator("BillingInfo.last_billing", last_billing, datetime, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


class Subscription:

    def __init__(
            self,
            subscriber_id: str,
            billing_info: BillingInfo,
            plan_info: PlanInfo,
            usages: list[Usage] = None,
            discounts: list[Discount] = None,
            autorenew: bool = False,
            fields: dict = None,
            id: ID = None,
    ):
        self._validate(subscriber_id, billing_info, plan_info, usages, discounts, autorenew, fields, id)

        self._status = SubscriptionStatus.Active
        self._paused_from = None
        self._created_at = get_current_datetime()
        self._updated_at = self._created_at
        self._usages: ItemManager[Usage] = ItemManager(lambda x: x.code, usages)
        self._discounts: ItemManager[Discount] = ItemManager(lambda x: x.code, discounts)

        self.id = id if id else uuid4()
        self.billing_info = billing_info
        self.plan_info = plan_info
        self.autorenew = autorenew
        self.subscriber_id = subscriber_id
        self.fields = fields if fields else {}

    @classmethod
    def from_plan(cls, plan: Plan, subscriber_id: str) -> Self:
        billing_info = BillingInfo.from_plan(plan)
        plan_info = PlanInfo.from_plan(plan)
        usages = [Usage.from_usage_rate(rate) for rate in plan.usage_rates.get_all()]
        discounts = [copy(dis) for dis in plan.discounts.get_all()]
        return cls(subscriber_id, billing_info, plan_info, usages=usages, discounts=discounts)

    @property
    def status(self) -> SubscriptionStatus:
        return self._status

    @property
    def paused_from(self) -> Optional[datetime]:
        return self._paused_from

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def discounts(self) -> ItemManager[Discount]:
        return self._discounts

    @property
    def usages(self) -> ItemManager[Usage]:
        return self._usages

    def pause(self) -> None:
        if self._status == SubscriptionStatus.Paused:
            return
        if self._status == SubscriptionStatus.Expired:
            raise ValueError("Cannot pause the expired subscription")
        self._status = SubscriptionStatus.Paused
        self._paused_from = get_current_datetime()

    def resume(self) -> None:
        if self._status == SubscriptionStatus.Active:
            return
        if self._status == SubscriptionStatus.Expired:
            raise ValueError("Cannot resume the expired subscription")
        self._status = SubscriptionStatus.Active
        self._paused_from = None

    def renew(self, from_date: datetime = None) -> None:
        if not from_date:
            from_date = get_current_datetime()
        self.billing_info.last_billing = from_date
        self._status = SubscriptionStatus.Active

    def expire(self) -> None:
        self._status = SubscriptionStatus.Expired

    @staticmethod
    def _validate(
            subscriber_id: str,
            billing_info: BillingInfo,
            plan_info: PlanInfo,
            usages: list[Usage] = None,
            discounts: list[Discount] = None,
            autorenew: bool = False,
            fields: dict = None,
            id: ID = None,
    ) -> None:
        validators = [
            TypeValidator("Subscription.id", id, ID, True),
            TypeValidator("Subscription.subscriber_id", subscriber_id, str),
            TypeValidator("Subscription.billing_info", billing_info, BillingInfo),
            TypeValidator("Subscription.plan_info", plan_info, PlanInfo),
            ListTypeValidator("Subscription.usages", usages, Usage, True),
            ListTypeValidator("Subscription.discounts", discounts, Discount, True),
            TypeValidator("Subscription.autorenew", autorenew, bool),
            FieldsValidator("Subscription.fields", fields, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)


class Webhook:
    def __init__(
            self,
            id: ID,
            event_code: EventCode,
            target_url: str,
            created_at: datetime,
            updated_at: datetime
    ):
        self.id = id
        self.event_code = event_code
        self.target_url = target_url
        self.created_at = created_at
        self.updated_at = updated_at
