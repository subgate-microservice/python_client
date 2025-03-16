from datetime import timedelta

import pytest

from subgatekit.entities import Plan, Subscription, Discount, Usage, UsageRate
from subgatekit.enums import Period, SubscriptionStatus
from subgatekit.exceptions import ActiveStatusConflict, ItemNotExist
from subgatekit.utils import get_current_datetime
from tests.conftest import client, wrapper
from tests.fakes import (simple_subscription, subscription_with_usages, subscription_with_discounts,
                         paused_subscription, subscription_with_fields)


class TestCreateSubscription:
    @pytest.mark.asyncio
    async def test_create_simple_subscription(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID")
        real = await wrapper(client.subscription_client().create_then_get(sub))
        assert real.id == sub.id

    @pytest.mark.asyncio
    async def test_create_subscription_with_usages(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        plan.usage_rates.add(UsageRate("First", "first", "GB", 100, Period.Lifetime))
        sub = Subscription.from_plan(plan, "AnyID")
        real = await wrapper(client.subscription_client().create_then_get(sub))
        assert len(real.usages) == 1

    @pytest.mark.asyncio
    async def test_create_subscription_with_discounts(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        plan.discounts.add(Discount("First", "first", 0.5, get_current_datetime()))
        sub = Subscription.from_plan(plan, "AnyID")
        real = await wrapper(client.subscription_client().create_then_get(sub))
        assert len(real.discounts) == 1

    @pytest.mark.asyncio
    async def test_create_subscription_with_fields(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        sub = Subscription.from_plan(plan, "AnyID", fields={"Hello": "World!"})
        real = await wrapper(client.subscription_client().create_then_get(sub))
        assert real.fields == {"Hello": "World!"}


class TestGetSubscription:
    @pytest.mark.asyncio
    async def test_get_test_get_one_by_id(self, client, simple_subscription):
        real = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert real.id == simple_subscription.id

    @pytest.mark.asyncio
    async def test_get_one_with_usages(self, client, subscription_with_usages):
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_usages.id))
        assert real.id == subscription_with_usages.id
        assert len(real.usages) == 1

    @pytest.mark.asyncio
    async def test_get_one_with_discounts(self, client, subscription_with_discounts):
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_discounts.id))
        assert real.id == subscription_with_discounts.id
        assert len(real.discounts) == 2

    @pytest.mark.asyncio
    async def test_get_one_with_fields(self, client, subscription_with_fields):
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_fields.id))
        assert real.id == subscription_with_fields.id
        assert real.fields == {"Hello": "World!"}

    @pytest.mark.asyncio
    async def test_get_current_subscription(self, client, simple_subscription):
        real = await wrapper(client.subscription_client().get_current_subscription(simple_subscription.subscriber_id))
        assert real.id == simple_subscription.id

    @pytest.mark.asyncio
    async def test_get_none_current_subscription(self, client):
        real = await wrapper(client.subscription_client().get_current_subscription("NotExistUserID"))
        assert real is None

    @pytest.mark.asyncio
    async def test_get_selected_subscriptions(self, client, simple_subscription, subscription_with_usages):
        real = await wrapper(client.subscription_client().get_selected())
        assert len(real) == 2


class TestUpdateSubscription:
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

    @pytest.mark.asyncio
    async def test_increase_usage(self, client, subscription_with_usages):
        # Update
        subscription_with_usages.usages.get("api_call").increase(45)
        await wrapper(client.subscription_client().update(subscription_with_usages))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_usages.id))
        assert real.usages.get("api_call").used_units == 45

    @pytest.mark.asyncio
    async def test_add_usages(self, client, simple_subscription):
        # Update
        simple_subscription.usages.add(
            Usage("First", "first", "GB", 1000, Period.Monthly)
        )
        await wrapper(client.subscription_client().update(simple_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert len(real.usages.get_all()) == 1
        assert real.usages.get("first").used_units == 0

    @pytest.mark.asyncio
    async def test_remove_usages(self, client, subscription_with_usages):
        # Update
        subscription_with_usages.usages.remove("api_call")
        await wrapper(client.subscription_client().update(subscription_with_usages))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_usages.id))
        assert len(real.usages.get_all()) == 0

    @pytest.mark.asyncio
    async def test_add_discounts(self, client, simple_subscription):
        # Update
        simple_subscription.discounts.add(Discount("First", "first", 0.2, get_current_datetime()))
        simple_subscription.discounts.add(Discount("Second", "second", 0.2, get_current_datetime()))
        await wrapper(client.subscription_client().update(simple_subscription))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))
        assert len(real.discounts) == 2
        assert real.discounts.get("second").size == 0.2

    @pytest.mark.asyncio
    async def test_remove_discounts(self, client, subscription_with_discounts):
        # Update
        subscription_with_discounts.discounts.remove("first")
        await wrapper(client.subscription_client().update(subscription_with_discounts))

        # Check
        real: Subscription = await wrapper(client.subscription_client().get_by_id(subscription_with_discounts.id))
        assert len(real.discounts) == 1


class TestDeleteSubscription:
    @pytest.mark.asyncio
    async def test_delete_by_id(self, simple_subscription, client):
        await wrapper(client.subscription_client().delete_by_id(simple_subscription.id))

        # Check
        with pytest.raises(ItemNotExist):
            _ = await wrapper(client.subscription_client().get_by_id(simple_subscription.id))

    @pytest.mark.asyncio
    async def test_delete_selected(self, simple_subscription, subscription_with_usages, subscription_with_discounts,
                                   client):
        await wrapper(client.subscription_client().delete_selected(ids=simple_subscription.id))
        await wrapper(client.subscription_client().delete_selected(
            subscriber_ids=subscription_with_usages.subscriber_id)
        )

        #  Check
        real = await wrapper(client.subscription_client().get_selected())
        assert len(real) == 1

    @pytest.mark.asyncio
    async def test_delete_selected_two(self, simple_subscription, subscription_with_usages, subscription_with_discounts,
                                       client):
        await wrapper(client.subscription_client().delete_selected(
            ids=[
                simple_subscription.id,
                subscription_with_usages.id,
            ]
        ))

        #  Check
        real = await wrapper(client.subscription_client().get_selected())
        assert len(real) == 1

    @pytest.mark.asyncio
    async def test_delete_all(self, simple_subscription, subscription_with_usages, subscription_with_discounts,
                              client):
        await wrapper(client.subscription_client().delete_selected())

        # Check
        real = await wrapper(client.subscription_client().get_selected())
        assert len(real) == 0
