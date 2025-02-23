from enum import StrEnum


class Period(StrEnum):
    Daily = "daily"
    Weekly = "weekly"
    Monthly = "monthly"
    Quarterly = "quarterly"
    Semiannual = "semiannual"
    Annual = "annual"
    Lifetime = "lifetime"


class SubscriptionStatus(StrEnum):
    Active = "active"
    Paused = "paused"
    Expired = "expired"


class EventCode(StrEnum):
    PlanCreated = "plan_created"
    PlanUpdated = "plan_updated"
    PlanDeleted = "plan_deleted"
    SubscriptionCreated = "subscription_created"
    SubscriptionUpdated = "subscription_updated"
    SubscriptionDeleted = "subscription_deleted"
    SubscriptionExpired = "subscription_expired"
    SubscriptionPaused = "subscription_paused"
    SubscriptionResumed = "subscription_resumed"
    SubscriptionRenewed = "subscription_renewed"
    SubscriptionUsageChanged = "subscription_usage_changed"
    SubscriptionUsageAdded = "subscription_usage_added"
    SubscriptionUsageUpdated = "subscription_usage_updated"
    SubscriptionUsageRemoved = "subscription_usage_removed"
