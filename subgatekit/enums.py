from enum import StrEnum

_cycle_days = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 92,
    "semiannual": 183,
    "annual": 365,
    "lifetime": 365_000,
}


class Period(StrEnum):
    Daily = "daily"
    Weekly = "weekly"
    Monthly = "monthly"
    Quarterly = "quarterly"
    Semiannual = "semiannual"
    Annual = "annual"
    Lifetime = "lifetime"

    def get_cycle_in_days(self) -> int:
        return _cycle_days[self.value]


class SubscriptionStatus(StrEnum):
    Active = "active"
    Paused = "paused"
    Expired = "expired"


class EventCode(StrEnum):
    PlanCreated = "plan_created"
    PlanUpdated = "plan_updated"
    PlanDeleted = "plan_deleted"
    SubCreated = "sub_created"
    SubUpdated = "sub_updated"
    SubDeleted = "sub_deleted"
    SubExpired = "sub_expired"
    SubPaused = "sub_paused"
    SubResumed = "sub_resumed"
    SubRenewed = "sub_renewed"
    SubUsageAdded = "sub_usage_added"
    SubsUsageUpdated = "sub_usage_updated"
    SubUsageRemoved = "sub_usage_removed"
    SubDiscountAdded = "sub_discount_added"
    SubDiscountUpdated = "sub_discount_updated"
    SubDiscountRemoved = "sub_discount_removed"
