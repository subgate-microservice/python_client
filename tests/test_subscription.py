from datetime import timedelta

import pytest

from subgatekit.entities import Plan, Subscription, UsageRate, Discount
from subgatekit.enums import Period, SubscriptionStatus
from subgatekit.exceptions import ActiveStatusConflict
from subgatekit.utils import get_current_datetime
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
    @pytest.fixture()
    def simple_subscription(self, sync_client):
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", )
        sync_client.subscription_client().create(sub)
        yield sub

    @pytest.fixture()
    def paused_subscription(self, sync_client):
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", )
        sub.pause()
        sub: Subscription = sync_client.subscription_client().create_then_get(sub)
        assert sub.status == SubscriptionStatus.Paused
        yield sub

    @pytest.fixture()
    def two_subs_for_one_subscriber(self, sync_client):
        plan = Plan("Business", 100, "USD", Period.Monthly)
        sub1 = Subscription.from_plan(plan, "AnyID")
        sub1 = sync_client.subscription_client().create_then_get(sub1)
        assert sub1.status == SubscriptionStatus.Active

        sub2 = Subscription.from_plan(plan, "AnyID")
        sub2: Subscription = sync_client.subscription_client().create_then_get(sub2)
        assert sub2.status == SubscriptionStatus.Paused

        yield sub1, sub2

    @pytest.mark.asyncio
    async def test_pause_subscription(self, client, simple_subscription):
        # Update
        simple_subscription.pause()
        await wrapper(client.subscription_client().update(simple_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert real.status == SubscriptionStatus.Paused
        assert real.paused_from is not None

    @pytest.mark.asyncio
    async def test_resume_subscription(self, client, paused_subscription):
        # Update
        paused_subscription.resume()
        await wrapper(client.subscription_client().update(paused_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(paused_subscription.id))
        assert real.status == SubscriptionStatus.Active
        assert real.paused_from is None

    @pytest.mark.asyncio
    async def test_renew_subscription(self, client, simple_subscription):
        # Update
        renew_date = get_current_datetime() + timedelta(10)
        simple_subscription.renew(renew_date)
        await wrapper(client.subscription_client().update(simple_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert real.billing_info.last_billing == renew_date

    @pytest.mark.asyncio
    async def test_resume_subscription_with_active_status_conflict(self, client, two_subs_for_one_subscriber):
        active, paused = two_subs_for_one_subscriber

        # Try to resume
        with pytest.raises(ActiveStatusConflict):
            paused.resume()
            await wrapper(client.subscription_client().update(paused))

    @pytest.mark.asyncio
    async def test_renew_subscription_with_active_status_conflict(self, client, two_subs_for_one_subscriber):
        active, paused = two_subs_for_one_subscriber

        # Try to renew
        with pytest.raises(ActiveStatusConflict):
            paused.renew()
            await wrapper(client.subscription_client().update(paused))

    @pytest.mark.asyncio
    async def test_expire_subscription(self, client, simple_subscription):
        # Update
        simple_subscription.expire()
        await wrapper(client.subscription_client().update(simple_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert real.status == SubscriptionStatus.Expired
