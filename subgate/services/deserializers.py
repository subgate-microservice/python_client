from datetime import datetime

from subgate.domain.cycle import Cycle
from subgate.domain.discount import Discount
from subgate.domain.plan import Plan, ID
from subgate.domain.subscription import Subscription
from subgate.domain.usage import UsageRate, Usage, UsageForm
from subgate.domain.webhook import Webhook


def deserialize_cycle(data: dict) -> Cycle:
    return Cycle(
        title=data["title"],
        code=data["code"],
        cycle_in_days=data["cycle_in_days"],
    )


def deserialize_usage_rate(data: dict) -> UsageRate:
    return UsageRate(
        code=data["code"],
        unit=data["unit"],
        available_units=data["available_units"],
        renew_cycle=data["renew_cycle"]["code"],
        title=data["title"],
    )


def deserialize_usage(data: dict) -> Usage:
    return Usage(
        title=data["title"],
        code=data["code"],
        unit=data["unit"],
        available_units=data["available_units"],
        used_units=data["used_units"],
        renew_cycle=data["renew_cycle"]["code"],
    )


def deserialize_usage_form(data: dict) -> UsageForm:
    return UsageForm(code=data["code"], value=data["value"])


def deserialize_discount(data: dict) -> Discount:
    return Discount(
        title=data["title"],
        code=data["code"],
        description=data["description"],
        size=data["size"],
        valid_until=datetime.fromisoformat(data["valid_until"]),
    )


def deserialize_plan(data: dict) -> Plan:
    usage_rates = [deserialize_usage_rate(x) for x in data["usage_rates"]]
    discounts = [deserialize_discount(x) for x in data["discounts"]]
    billing_cycle = deserialize_cycle(data["billing_cycle"])
    return Plan(
        id=ID(data["id"]),
        title=data["title"],
        price=data["price"],
        currency=data["currency"],
        billing_cycle=billing_cycle,
        description=data["description"],
        level=data["level"],
        features=data["features"],
        fields=data["fields"],
        usage_rates=usage_rates,
        discounts=discounts,
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )


def deserialize_subscription(data: dict) -> Subscription:
    paused_from = datetime.fromisoformat(data["paused_from"]) if data.get("paused_from") else None
    usage_rates = [deserialize_usage(x) for x in data["usages"]]
    plan = deserialize_plan(data["plan"])
    return Subscription(
        id=ID(data["id"]),
        subscriber_id=data["subscriber_id"],
        plan=plan,
        last_billing=datetime.fromisoformat(data["last_billing"]),
        status=data["status"],
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
        paused_from=paused_from,
        autorenew=data["autorenew"],
        usages=usage_rates,
        fields=data["fields"],
    )


def deserialize_webhook(data: dict) -> Webhook:
    return Webhook(
        id=ID(data["id"]),
        event_code=data["event_code"],
        target_url=data["target_url"],
        created_at=datetime.fromisoformat(data["created_at"]),
        updated_at=datetime.fromisoformat(data["updated_at"]),
    )
