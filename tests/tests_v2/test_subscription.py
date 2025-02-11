import pytest

from subgatekit.v2_0.domain.entities import Plan, Subscription, Usage, Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.utils import get_current_datetime
from tests.tests_v2.conftest import client, wrapper


def test_usage_management():
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "AnyID")

    sub.usages.add(
        Usage("ApiCall", "api_call", "request", 1_000, Period.Monthly)
    )

    sub.discounts.add(
        Discount("Black friday", "black", 0.2, get_current_datetime(), "")
    )

    sub.usages.get_all()

    sub.usages.get("api_call").increase(50)
    assert sub.usages.get("api_call").used_units == 50


class TestGetSubscription:
    @pytest.mark.asyncio
    async def test_get_test_get_one_by_id(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID")
        await wrapper(client.subscription_client().create(sub))

        # Test
        real = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.id == sub.id
