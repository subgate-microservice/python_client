from copy import copy
from datetime import datetime
from typing import Optional, Self
from uuid import uuid4

from subgatekit.client.exceptions import ItemAlreadyExist
from subgatekit.utils import get_current_datetime, Number
from subgatekit.v2_0.domain.billing_info import BillingInfo
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import SubscriptionStatus
from subgatekit.v2_0.domain.plan import ID, PlanInfo, Plan
from subgatekit.v2_0.domain.usage import Usage


class Subscription:

    def __init__(
            self,
            subscriber_id: str,
            billing_info: BillingInfo,
            plan_info: PlanInfo,
            status: SubscriptionStatus = SubscriptionStatus.Active,
            paused_from: Optional[datetime] = None,
            usages: list[Usage] = None,
            discounts: list[Discount] = None,
            autorenew: bool = False,
            fields: dict = None,
            id: ID = None
    ):
        self._status = status
        self._paused_from = paused_from
        self._created_at = get_current_datetime()
        self._updated_at = self._created_at
        self.id = id if id else uuid4()

        self._usages = {x.code: x for x in usages} if usages else {}
        self._discounts = {x.code: x for x in discounts} if discounts else {}

        self.billing_info = billing_info
        self.plan_info = plan_info
        self.autorenew = autorenew
        self.subscriber_id = subscriber_id
        self.fields = fields if fields else {}

    @classmethod
    def _create_internal(
            cls,
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
    ):
        instance = cls(subscriber_id, billing_info, plan_info, status, paused_from, usages, discounts, autorenew,
                       fields, id)
        object.__setattr__(instance, "_created_at", created_at)
        object.__setattr__(instance, "_updated_at", updated_at)
        return instance

    @classmethod
    def from_plan(cls, plan: Plan, subscriber_id: str) -> Self:
        billing_info = BillingInfo.from_plan(plan)
        plan_info = PlanInfo.from_plan(plan)
        usages = [Usage.from_usage_rate(rate) for rate in plan.usage_rates]
        discounts = [copy(dis) for dis in plan.discounts]
        return cls(subscriber_id, billing_info, plan_info, usages=usages, discounts=discounts)

    @property
    def paused_from(self) -> Optional[datetime]:
        return self._paused_from

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def add_usage(self, usage: Usage) -> None:
        if self._usages.get(usage.code) is not None:
            raise ItemAlreadyExist(Usage.__class__.__name__, usage.code, "code")
        self._usages[usage.code] = usage

    def remove_usage(self, code: str) -> None:
        self._usages.pop(code, None)

    def get_usages(self) -> list[Usage]:
        return list(self._usages.values())

    def increase_usage(self, code: str, delta: Number) -> None:
        self._usages[code] += delta

    def add_discount(self, discount: Discount) -> None:
        if self._discounts.get(discount.code) is not None:
            raise ItemAlreadyExist(Discount.__class__.__name__, discount.code, "code")
        self._discounts[discount.code] = discount

    def remove_discount(self, code: str) -> None:
        self._discounts.pop(code, None)

    def get_discounts(self) -> list[Discount]:
        return list(self._discounts.values())

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

    def renew(self, from_date: datetime = None):
        if not from_date:
            from_date = get_current_datetime()
        self.billing_info.last_billing = from_date
        self._status = SubscriptionStatus.Active
