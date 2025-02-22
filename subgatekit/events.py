from datetime import datetime
from typing import Optional, Any, NamedTuple, Union
from uuid import UUID

from subgatekit.enums import Period, SubscriptionStatus

UnionValue = Union[int, float, str, bool, datetime]


class PlanCreated(NamedTuple):
    id: UUID
    title: str
    price: float
    currency: str
    billing_cycle: Period
    occurred_at: datetime

    @property
    def event_code(self):
        return "plan_created"


class PlanDeleted(NamedTuple):
    id: UUID
    title: str
    price: float
    currency: str
    billing_cycle: Period
    occurred_at: datetime

    @property
    def event_code(self):
        return "plan_deleted"


class PlanUpdated(NamedTuple):
    id: UUID
    changes: dict[str, UnionValue]
    occurred_at: datetime

    @property
    def event_code(self):
        return "plan_updated"


class SubscriptionCreated(NamedTuple):
    id: UUID
    subscriber_id: str
    status: SubscriptionStatus
    price: float
    currency: str
    billing_cycle: Period
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_created"


class SubscriptionDeleted(NamedTuple):
    id: UUID
    subscriber_id: str
    status: SubscriptionStatus
    price: float
    currency: str
    billing_cycle: Period
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_deleted"


class SubscriptionUpdated(NamedTuple):
    id: UUID
    subscriber_id: str
    changes: dict[str, Any]
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_updated"


class SubscriptionPaused(NamedTuple):
    id: UUID
    subscriber_id: str
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_paused"


class SubscriptionResumed(NamedTuple):
    id: UUID
    subscriber_id: str
    occurred_at: datetime
    saved_days: int
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_resumed"


class SubscriptionExpired(NamedTuple):
    id: UUID
    subscriber_id: str
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_expired"


class SubscriptionRenewed(NamedTuple):
    id: UUID
    subscriber_id: str
    last_billing: datetime
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_renewed"


class SubscriptionUsageAdded(NamedTuple):
    subscription_id: UUID
    title: str
    code: str
    unit: str
    available_units: float
    renew_cycle: Period
    used_units: float
    last_renew: datetime
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_usage_added"


class SubscriptionUsageUpdated(NamedTuple):
    subscription_id: UUID
    code: str
    changes: dict[str, UnionValue]
    delta: float
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_usage_updated"


class SubscriptionUsageRemoved(NamedTuple):
    subscription_id: UUID
    title: str
    code: str
    unit: str
    available_units: float
    renew_cycle: Period
    used_units: float
    last_renew: datetime
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_usage_removed"


class SubscriptionDiscountAdded(NamedTuple):
    subscription_id: UUID
    title: str
    code: str
    description: Optional[str]
    size: float
    valid_until: datetime
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_discount_added"


class SubscriptionDiscountRemoved(NamedTuple):
    subscription_id: UUID
    title: str
    code: str
    description: Optional[str]
    size: float
    valid_until: datetime
    occurred_at: datetime

    @property
    def event_code(self):
        return "subscription_discount_removed"


class SubscriptionDiscountUpdated(NamedTuple):
    subscription_id: UUID
    code: str
    changes: dict[str, UnionValue]

    @property
    def event_code(self):
        return "subscription_discount_updated"
