import pytest

from subgatekit.v2_0.domain.entities import Plan, Subscription, UsageRate, Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.utils import get_current_datetime
from tests.tests_v2.conftest import client, wrapper


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

    @pytest.mark.asyncio
    async def test_get_one_with_usages(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        plan.usage_rates.add(UsageRate("First", "first", "GB", 100, Period.Monthly))
        plan.usage_rates.add(UsageRate("Second", "sec", "GB", 100, Period.Monthly))
        sub = Subscription.from_plan(plan, "AnyID")
        await wrapper(client.subscription_client().create(sub))

        # Test
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.id == sub.id
        assert len(real.usages.get_all()) == 2
        assert real.usages.get("sec").title == "Second"
        assert real.usages.get("first").title == "First"

    @pytest.mark.asyncio
    async def test_get_one_with_discounts(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        plan.discounts.add(Discount("First", "first", 0.3, get_current_datetime()))
        plan.discounts.add(Discount("Second", "sec", 0.8, get_current_datetime()))
        sub = Subscription.from_plan(plan, "AnyID")
        await wrapper(client.subscription_client().create(sub))

        # Test
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.id == sub.id
        assert len(real.discounts.get_all()) == 2
        assert real.discounts.get("sec").title == "Second"
        assert real.discounts.get("first").title == "First"

    @pytest.mark.asyncio
    async def test_get_one_with_fields(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", fields={"Hello": "World!"})
        await wrapper(client.subscription_client().create(sub))

        # Test
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.id == sub.id
        assert real.fields == {"Hello": "World!"}
