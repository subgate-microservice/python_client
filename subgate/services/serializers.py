from subgate.domain.cycle import Cycle
from subgate.domain.discount import Discount
from subgate.domain.plan import Plan, PlanCreate
from subgate.domain.subscription import SubscriptionCreate, Subscription
from subgate.domain.usage import UsageRate, Usage, UsageForm
from subgate.domain.webhook import Webhook, WebhookCreate, WebhookUpdate


def serialize_cycle(item: Cycle) -> dict:
    return {
        "title": item.title,
        "code": item.code,
        "cycle_in_days": item.cycle_in_days,
    }


def serialize_usage_rate(item: UsageRate) -> dict:
    return {
        "title": item.title,
        "code": item.code,
        "unit": item.unit,
        "available_units": item.available_units,
        "renew_cycle": serialize_cycle(item.renew_cycle),
    }


def serialize_usage(item: Usage) -> dict:
    return {
        "title": item.title,
        "code": item.code,
        "unit": item.unit,
        "available_units": item.available_units,
        "used_units": item.used_units,
        "renew_cycle": serialize_cycle(item.renew_cycle),
    }


def serialize_usage_form(item: UsageForm) -> dict:
    return {
        "code": item.code,
        "value": item.value,
    }


def serialize_discount(item: Discount) -> dict:
    return {
        "title": item.title,
        "code": item.code,
        "description": item.description,
        "size": item.size,
        "valid_until": item.valid_until.isoformat(),
    }


def serialize_plan(item: Plan) -> dict:
    fields = item.fields if item.fields else {}
    usage_rates = [serialize_usage_rate(x) for x in item.usage_rates]
    discounts = [serialize_discount(x) for x in item.discounts]
    billing_cycle = serialize_cycle(item.billing_cycle)
    return {
        "id": str(item.id),
        "title": item.title,
        "price": item.price,
        "currency": item.currency,
        "billing_cycle": billing_cycle,
        "description": item.description,
        "level": item.level,
        "features": item.features,
        "fields": fields,
        "usage_rates": usage_rates,
        "discounts": discounts,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def serialize_plan_create(item: PlanCreate) -> dict:
    rates = [serialize_usage_rate(x) for x in item.usage_rates]
    discounts = [serialize_discount(x) for x in item.discounts]
    billing_cycle = serialize_cycle(item.billing_cycle)
    return {
        "title": item.title,
        "price": item.price,
        "currency": item.currency,
        "billing_cycle": billing_cycle,
        "description": item.description,
        "level": item.level,
        "features": item.features,
        "usage_rates": rates,
        "discounts": discounts,
        "fields": item.fields,
    }


def serialize_subscription(item: Subscription) -> dict:
    paused_from = item.paused_from.isoformat() if item.paused_from else None
    usages = [serialize_usage(x) for x in item.usages]
    plan = serialize_plan(item.plan)
    return {
        "id": str(item.id),
        "subscriber_id": item.subscriber_id,
        "plan": plan,
        "last_billing": item.last_billing.isoformat(),
        "status": item.status,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
        "paused_from": paused_from,
        "autorenew": item.autorenew,
        "usages": usages,
        "fields": item.fields,
    }


def serialize_subscription_create(item: SubscriptionCreate) -> dict:
    paused_from = item.paused_from.isoformat() if item.paused_from else None
    usages = [serialize_usage(x) for x in item.usages]
    plan = serialize_plan(item.plan)
    return {
        "plan": plan,
        "subscriber_id": item.subscriber_id,
        "status": item.status,
        "usages": usages,
        "paused_from": paused_from,
        "autorenew": item.autorenew,
        "fields": item.fields,
    }


def serialize_webhook(item: Webhook) -> dict:
    return {
        "id": str(item.id),
        "event_code": str(item.event_code),
        "target_url": item.target_url,
        "created_at": item.created_at.isoformat(),
        "updated_at": item.updated_at.isoformat(),
    }


def serialize_webhook_create(item: WebhookCreate) -> dict:
    return {
        "event_code": str(item.event_code),
        "target_url": item.target_url,
    }


def serialize_webhook_update(item: WebhookUpdate) -> dict:
    return {
        "id": str(item.id),
        "event_code": str(item.event_code),
        "target_url": item.target_url,
        "created_at": item.created_at.isoformat()
    }
