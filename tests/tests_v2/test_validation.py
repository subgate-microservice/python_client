from uuid import uuid4

from subgatekit.utils import get_current_datetime
from subgatekit.v2_0.domain.cycle import Cycle
from subgatekit.v2_0.domain.enums import Period, SubscriptionStatus
from subgatekit.v2_0.domain.plan import Plan
from subgatekit.v2_0.domain.subscription import Subscription
from subgatekit.v2_0.services.validators import CycleValidator, SubscriptionValidator


class TestCycleValidator:
    def test_validate_cycle_with_bad_cycle_in_days(self):
        cycle = Cycle("WithBadDays", Period.Monthly, 123.123)
        errors = CycleValidator(cycle).validate().parse_errors()
        assert len(errors) == 1
        error = errors.pop()
        print(error)


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

        errors = SubscriptionValidator(sub).validate().parse_errors()
        for err in errors:
            print(err)
        assert len(errors) == 1

    def test_active_status_with_paused_from_field_raises_error(self):
        sub = fake_subscription()
        sub.paused_from = get_current_datetime()

        errors = SubscriptionValidator(sub).validate().parse_errors()
        for err in errors:
            print(err)
        assert len(errors) == 1
