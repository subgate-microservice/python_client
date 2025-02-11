from uuid import uuid4

import pytest

from subgatekit.v2_0.domain.utils import get_current_datetime
from subgatekit.v2_0.domain.entities import Plan, Subscription, BillingInfo, PlanInfo
from subgatekit.v2_0.domain.enums import Period

from subgatekit.v2_0.domain.validators import ValidationError


def fake_plan():
    dt = get_current_datetime()
    return Plan(
        id=uuid4(),
        title="Business",
        price=100,
        currency="USD",
        billing_cycle=Period.Annual,
        description="",
        level=10,
        features="",
        fields={},
        usage_rates=[],
        discounts=[],
        created_at=dt,
        updated_at=dt,
    )


def fake_subscription():
    plan = fake_plan()
    return Subscription.from_plan(plan, "AnyID")


class TestSubscriptionValidators:
    def test_foo(self):
        with pytest.raises(ValidationError) as err:
            billing_info = BillingInfo(100, "USD", Period.Monthly)
            plan_info = PlanInfo.from_plan(fake_plan())
            Subscription(123, billing_info, plan_info)
        print(err.value)

    def test_bar(self):
        with pytest.raises(ValidationError) as err:
            billing_info = BillingInfo(100, "USD", Period.Monthly)
            plan_info = PlanInfo.from_plan(fake_plan())
            Subscription("AnyId", billing_info, plan_info, usages=["WrongType"])
        print(err.value)


class TestPlanValidators:
    def test_plan_with_fields_that_not_json_serializable(self):
        raise NotImplemented


class TestDiscountValidators:
    def test_discount_with_bad_valid_until(self):
        raise NotImplemented

    def test_validate_discount_with_bad_type_of_size(self):
        raise NotImplemented
