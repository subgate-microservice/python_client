from copy import copy
from datetime import datetime
from typing import Optional, Self
from uuid import uuid4

from subgatekit.utils import get_current_datetime
from subgatekit.v2_0.domain.billing_info import BillingInfo
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import SubscriptionStatus
from subgatekit.v2_0.domain.item_manager import ItemManager
from subgatekit.v2_0.domain.plan import ID, PlanInfo, Plan
from subgatekit.v2_0.domain.usage import Usage
from subgatekit.v2_0.domain.validators import (TypeValidator, FieldsValidator, raise_errors_if_necessary,
                                               ListTypeValidator)


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


def create_subscription_with_internal_fields(
        subscriber_id: str,
        billing_info: BillingInfo,
        plan_info: PlanInfo,
        status: SubscriptionStatus,
        paused_from: Optional[datetime],
        usages: list[Usage],
        discounts: list[Discount],
        autorenew: bool,
        fields: dict,
        created_at: datetime,
        updated_at: datetime,
        id: ID,
) -> Subscription:
    instance = Subscription(subscriber_id, billing_info, plan_info, usages, discounts, autorenew, fields, id)
    object.__setattr__(instance, "_status", status)
    object.__setattr__(instance, "_paused_from", paused_from)
    object.__setattr__(instance, "_created_at", created_at)
    object.__setattr__(instance, "_updated_at", updated_at)
    return instance
