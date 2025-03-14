from datetime import datetime

from subgatekit.entities import Plan, UsageRate, Usage, Discount, PlanInfo, BillingInfo, Subscription, Webhook
from subgatekit.enums import Period, SubscriptionStatus, EventCode
from subgatekit.factories import (create_plan_with_internal_fields, create_subscription_with_internal_fields,
                                  create_webhook_with_internal_fields)
from subgatekit.utils import ID


def deserialize_usage_rate(data: dict) -> UsageRate:
    renew_cycle = Period(data["renew_cycle"])
    return UsageRate(
        title=data["title"],
        code=data["code"],
        unit=data["unit"],
        available_units=data["available_units"],
        renew_cycle=renew_cycle,
    )


def deserialize_usage(data: dict) -> Usage:
    last_renew = datetime.fromisoformat(data["last_renew"])
    renew_cycle = Period(data["renew_cycle"])
    return Usage(
        title=data["title"],
        code=data["code"],
        unit=data["unit"],
        available_units=data["available_units"],
        renew_cycle=renew_cycle,
        used_units=data["used_units"],
        last_renew=last_renew,
    )


def deserialize_discount(data: dict) -> Discount:
    valid_until = datetime.fromisoformat(data["valid_until"])
    return Discount(
        title=data["title"],
        code=data["code"],
        size=data["size"],
        valid_until=valid_until,
        description=data["description"],
    )


def deserialize_plan(data: dict) -> Plan:
    usage_rates = [deserialize_usage_rate(x) for x in data["usage_rates"]]
    discounts = [deserialize_discount(x) for x in data["discounts"]]
    created_at = datetime.fromisoformat(data["created_at"])
    updated_at = datetime.fromisoformat(data["updated_at"])
    return create_plan_with_internal_fields(
        title=data["title"],
        price=data["price"],
        currency=data["currency"],
        billing_cycle=data["billing_cycle"],
        description=data["description"],
        level=data["level"],
        features=data["features"],
        fields=data["fields"],
        usage_rates=usage_rates,
        discounts=discounts,
        id=ID(data["id"]),
        created_at=created_at,
        updated_at=updated_at,
    )


def deserialize_plan_info(data: dict) -> PlanInfo:
    plan_info_id = ID(data["id"])
    return PlanInfo(
        title=data["title"],
        description=data["description"],
        features=data["features"],
        level=data["level"],
        id=plan_info_id,
    )


def deserialize_billing_info(data: dict) -> BillingInfo:
    billing_cycle = Period(data["billing_cycle"])
    last_billing = datetime.fromisoformat(data["last_billing"])
    return BillingInfo(
        price=data["price"],
        currency=data["currency"],
        billing_cycle=billing_cycle,
        last_billing=last_billing,
        saved_days=data["saved_days"],
    )


def deserialize_subscription(data: dict) -> Subscription:
    billing_info = deserialize_billing_info(data["billing_info"])
    plan_info = deserialize_plan_info(data["plan_info"])
    status = SubscriptionStatus(data["status"])
    paused_from = datetime.fromisoformat(data["paused_from"]) if data["paused_from"] else None
    usages = [deserialize_usage(x) for x in data["usages"]]
    discounts = [deserialize_discount(x) for x in data["discounts"]]
    created_at = datetime.fromisoformat(data["created_at"])
    updated_at = datetime.fromisoformat(data["updated_at"])
    subscription_id = ID(data["id"])
    return create_subscription_with_internal_fields(
        subscriber_id=data["subscriber_id"],
        billing_info=billing_info,
        plan_info=plan_info,
        status=status,
        paused_from=paused_from,
        usages=usages,
        discounts=discounts,
        fields=data["fields"],
        created_at=created_at,
        updated_at=updated_at,
        id=subscription_id,
    )


def deserialize_webhook(data: dict) -> Webhook:
    created_at = datetime.fromisoformat(data["created_at"])
    updated_at = datetime.fromisoformat(data["updated_at"])
    webhook_id = ID(data["id"])
    code = EventCode(data["event_code"])
    delays = tuple(data["delays"]) if isinstance(data["delays"], list) else data["delays"]
    return create_webhook_with_internal_fields(
        id=webhook_id,
        target_url=data["target_url"],
        event_code=code,
        delays=delays,
        created_at=created_at,
        updated_at=updated_at,
    )
