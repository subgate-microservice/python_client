from datetime import datetime

from subgatekit.v2_0.domain.entities import Plan, UsageRate, Usage, Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.factories import create_plan_with_internal_fields
from subgatekit.v2_0.domain.utils import ID


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
