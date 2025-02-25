from subgatekit.entities import UsageRate, Usage, Discount, Plan, PlanInfo, BillingInfo, Subscription, Webhook


def serialize_usage_rate(usage_rate: UsageRate) -> dict:
    return {
        "title": usage_rate.title,
        "code": usage_rate.code,
        "unit": usage_rate.unit,
        "available_units": usage_rate.available_units,
        "renew_cycle": usage_rate.renew_cycle,
    }


def serialize_usage(usage: Usage) -> dict:
    last_renew = usage.last_renew.isoformat() if usage.last_renew else None
    return {
        "title": usage.title,
        "code": usage.code,
        "unit": usage.unit,
        "available_units": usage.available_units,
        "renew_cycle": usage.renew_cycle,
        "used_units": usage.used_units,
        "last_renew": last_renew,
    }


def serialize_discount(discount: Discount) -> dict:
    valid_until = discount.valid_until.isoformat()
    return {
        "title": discount.title,
        "code": discount.code,
        "size": discount.size,
        "valid_until": valid_until,
        "description": discount.description,
    }


def serialize_plan(plan: Plan) -> dict:
    usage_rates = [serialize_usage_rate(x) for x in plan.usage_rates.get_all()]
    discounts = [serialize_discount(x) for x in plan.discounts.get_all()]
    plan_id = str(plan.id)
    return {
        "title": plan.title,
        "price": plan.price,
        "currency": plan.currency,
        "billing_cycle": plan.billing_cycle,
        "description": plan.description,
        "level": plan.level,
        "features": plan.features,
        "fields": plan.fields,
        "usage_rates": usage_rates,
        "discounts": discounts,
        "id": plan_id,
    }


def serialize_plan_info(plan_info: PlanInfo) -> dict:
    plan_info_id = str(plan_info.id)
    return {
        "title": plan_info.title,
        "description": plan_info.description,
        "level": plan_info.level,
        "features": plan_info.features,
        "id": plan_info_id,
    }


def serialize_billing_info(billing_info: BillingInfo) -> dict:
    last_billing = billing_info.last_billing.isoformat() if billing_info.last_billing else None
    return {
        "price": billing_info.price,
        "currency": billing_info.currency,
        "billing_cycle": billing_info.billing_cycle,
        "last_billing": last_billing,
    }


def serialize_subscription(subscription: Subscription) -> dict:
    billing_info = serialize_billing_info(subscription.billing_info)
    plan_info = serialize_plan_info(subscription.plan_info)
    usages = [serialize_usage(x) for x in subscription.usages.get_all()]
    discounts = [serialize_discount(x) for x in subscription.discounts.get_all()]
    subscription_id = str(subscription.id)
    paused_from = subscription.paused_from.isoformat() if subscription.paused_from else None
    return {
        "subscriber_id": subscription.subscriber_id,
        "billing_info": billing_info,
        "plan_info": plan_info,
        "usages": usages,
        "discounts": discounts,
        "autorenew": subscription.autorenew,
        "fields": subscription.fields,
        "id": subscription_id,
        "status": subscription.status,
        "paused_from": paused_from,
    }


def serialize_webhook(webhook: Webhook) -> dict:
    webhook_id = str(webhook.id)
    return {
        "id": webhook_id,
        "target_url": webhook.target_url,
        "event_code": webhook.event_code,
        "delays": webhook.delays,
        "max_retries": webhook.max_retries,
    }
