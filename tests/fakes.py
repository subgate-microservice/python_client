import pytest

from subgatekit import Subscription, Plan, Period, SubscriptionStatus, Discount, UsageRate
from subgatekit.utils import get_current_datetime


@pytest.fixture()
def simple_subscription(sync_client):
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "any_id_for_simple_sub", )
    sub = sync_client.subscription_client().create_then_get(sub)
    yield sub


@pytest.fixture()
def paused_subscription(sync_client):
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "any_id_for_paused_sub", )
    sub.pause()
    sub: Subscription = sync_client.subscription_client().create_then_get(sub)
    assert sub.status == SubscriptionStatus.Paused
    yield sub


@pytest.fixture()
def subscription_with_usages(sync_client):
    plan = Plan("Business", 100, "USD", Period.Monthly)
    plan.usage_rates.add(UsageRate("ApiCall", "api_call", "request", 100, Period.Monthly))
    sub = Subscription.from_plan(plan, "any_id_for_usages_sub")
    sub = sync_client.subscription_client().create_then_get(sub)
    yield sub


@pytest.fixture()
def subscription_with_discounts(sync_client):
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "any_id_for_discounts_sub", )
    sub.discounts.add(Discount("First", "first", 0.2, get_current_datetime()))
    sub.discounts.add(Discount("Second", "second", 0.2, get_current_datetime()))
    sub = sync_client.subscription_client().create_then_get(sub)
    yield sub


@pytest.fixture()
def subscription_with_fields(sync_client):
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "any_id_for_fields_sub", fields={"Hello": "World!"})
    sub = sync_client.subscription_client().create_then_get(sub)
    yield sub
