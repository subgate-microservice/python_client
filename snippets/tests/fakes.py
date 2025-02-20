import pytest

from snippets.tests.client import get_client
from subgatekit import Subscription, Period, Plan, UsageRate

client = get_client()


@pytest.fixture(autouse=True)
def fake_sub():
    plan = Plan("Business", 100, "USD", billing_cycle=Period.Monthly)
    sub = Subscription.from_plan(plan, 'AnySubscriberID')
    sub = client.subscription_client().create_then_get(sub)
    yield sub


@pytest.fixture(autouse=True)
def fake_sub_with_usages():
    rates = [
        UsageRate(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=10_000,
            renew_cycle=Period.Monthly,
        )
    ]
    plan = Plan('Business', 100, 'USD', Period.Annual, usage_rates=rates)
    subscription = Subscription.from_plan(plan, 'AnySubscriberID')
    sub = client.subscription_client().create_then_get(subscription)
    yield sub
