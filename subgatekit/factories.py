from datetime import datetime
from typing import Any, Optional

from subgatekit.entities import UsageRate, Discount, Plan, BillingInfo, PlanInfo, Usage, Subscription, Webhook
from subgatekit.enums import Period, SubscriptionStatus, EventCode
from subgatekit.utils import ID


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


def create_webhook_with_internal_fields(
        id: ID,
        event_code: EventCode,
        target_url: str,
        delays: tuple[int],
        created_at: datetime,
        updated_at: datetime,
) -> Webhook:
    instance = Webhook(event_code, target_url, delays, id)
    object.__setattr__(instance, "_created_at", created_at)
    object.__setattr__(instance, "_updated_at", updated_at)
    return instance
