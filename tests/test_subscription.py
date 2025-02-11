from datetime import timedelta

import pytest

from subgatekit.v2_0.domain.entities import Plan, Subscription, UsageRate, Discount
from subgatekit.v2_0.domain.enums import Period, SubscriptionStatus
from subgatekit.v2_0.domain.utils import get_current_datetime
from tests.conftest import client, wrapper


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


class TestUpdateSubscription:
    @pytest.mark.asyncio
    async def test_pause_subscription(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", )
        sub: Subscription = await wrapper(client.subscription_client().create_then_get(sub))
        assert sub.status == SubscriptionStatus.Active

        # Update
        sub.pause()
        await wrapper(client.subscription_client().update(sub))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.status == SubscriptionStatus.Paused
        assert real.paused_from is not None

    @pytest.mark.asyncio
    async def test_resume_subscription(self, client):
        # Before
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", )
        sub.pause()
        sub: Subscription = await wrapper(client.subscription_client().create_then_get(sub))
        assert sub.status == SubscriptionStatus.Paused

        # Update
        sub.resume()
        await wrapper(client.subscription_client().update(sub))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.status == SubscriptionStatus.Active
        assert real.paused_from is None

    @pytest.mark.asyncio
    async def test_renew_subscription(self, client):
        # Before
        last_bill = get_current_datetime() - timedelta(2)
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", )
        sub.billing_info.last_billing = last_bill
        sub: Subscription = await wrapper(client.subscription_client().create_then_get(sub))
        assert sub.billing_info.last_billing == last_bill

        # Update
        sub.renew()
        await wrapper(client.subscription_client().update(sub))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(sub.id))
        assert real.billing_info.last_billing.date() == get_current_datetime().date()

    @pytest.mark.asyncio
    async def test_resume_subscription_with_active_status_conflict(self, client):
        raise NotImplemented

    @pytest.mark.asyncio
    async def test_renew_subscription_with_active_status_conflict(self, client):
        raise NotImplemented

    @pytest.mark.asyncio
    async def test_expire_subscription(self, client):
        raise NotImplemented
