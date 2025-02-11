from datetime import timedelta
from uuid import uuid4

import pytest

from subgatekit.client.exceptions import ValidationError, MultipleError
from subgatekit.domain.cycle import Cycle
from subgatekit.domain.discount import Discount
from subgatekit.domain.enums import Period, SubscriptionStatus
from subgatekit.domain.plan import Plan
from subgatekit.domain.subscription import Subscription
from subgatekit.services.validators import validate
from subgatekit.v2_0.domain.utils import get_current_datetime


def fake_plan():
    dt = get_current_datetime()
    return Plan(
        id=uuid4(),
        title="Business",
        price=100,
        currency="USD",
        billing_cycle=Cycle.from_code(Period.Annual),
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
    dt = get_current_datetime()
    return Subscription(
        id=uuid4(),
        subscriber_id="AnyID",
        plan=plan,
        status=SubscriptionStatus.Active,
        created_at=dt,
        updated_at=dt,
        last_billing=dt,
        paused_from=None,
        autorenew=False,
        usages=[],
        fields={},
    )


class TestSubscriptionValidators:
    def test_paused_status_without_paused_from_field_raises_error(self):
        sub = fake_subscription()
        sub.status = SubscriptionStatus.Paused

        with pytest.raises(ValidationError) as err:
            validate(sub)
        print(err.value)

    def test_active_status_with_paused_from_field_raises_error(self):
        sub = fake_subscription()
        sub.paused_from = get_current_datetime()

        with pytest.raises(ValidationError) as err:
            validate(sub)
        print(err.value)

    def test_raise_error_if_created_later_than_updated_or_last_billing(self):
        sub = fake_subscription()
        sub.created_at = get_current_datetime() + timedelta(days=11)

        with pytest.raises(MultipleError) as err:
            validate(sub)
        print(err.value)
        assert len(err.value.exceptions) == 2


class TestPlanValidators:
    def test_plan_with_fields_that_not_json_serializable(self):
        plan = fake_plan()
        plan.fields = {"bad_field": uuid4()}

        with pytest.raises(ValidationError) as err:
            validate(plan)
        print(err.value)


class TestDiscountValidators:
    def test_discount_with_bad_valid_until(self):
        discount = Discount("AnyTitle", "code", 0.5, None)
        with pytest.raises(ValidationError) as err:
            validate(discount)
        print(err.value)

    def test_validate_discount_with_bad_type_of_size(self):
        discount = Discount("AnyTitle", "code", "BigBen", get_current_datetime())
        with pytest.raises(ValidationError) as err:
            validate(discount)
        print(err.value)
