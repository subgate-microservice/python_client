import asyncio
import math
from copy import deepcopy
from uuid import uuid4

import pytest

from subgatekit.v2_0.domain.exceptions import ItemNotExist, MultipleError, ValidationError, ItemAlreadyExist
from subgatekit.domain.enums import Period, SubscriptionStatus
from subgatekit.domain.subscription import Subscription
from subgatekit.domain.usage import Usage, UsageRate
from tests.conftest import fake_plan, subs, client, wrapper


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_all(self, subs, client):
        all_subs = await wrapper(client.subscription_client().get_selected_subscriptions())
        assert len(all_subs) > 0
        await wrapper(client.subscription_client().delete_selected_subscriptions())
        all_subs = await wrapper(client.subscription_client().get_selected_subscriptions())
        assert len(all_subs) == 0


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_one(self, fake_plan, client):
        real = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan))
        assert real.subscriber_id == "AnyId"

    @pytest.mark.asyncio
    async def test_create_subscription_with_usages(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "database", 100, 2, Period.Weekly),
            Usage("AnyTitle", "second", "request", 222, 2, Period.Weekly),
        ]
        real: Subscription = await wrapper(client.subscription_client().create_subscription(
            "AnyID",
            fake_plan,
            usages=usages,
        ))
        assert len(real.usages) == len(usages)
        assert len(set(x.code for x in usages).difference(set(x.code for x in real.usages))) == 0

    @pytest.mark.asyncio
    async def test_create_subscription_with_incorrect_usages(self, fake_plan, client):
        with pytest.raises(MultipleError) as err:
            bad_usages = [
                Usage("AnyTitle", 1, "database", 100, 2, Period.Weekly),
                Usage("AnyTitle", "second", "request", "10_000", 2, Period.Weekly),
            ]
            _ = await wrapper(client.subscription_client().create_subscription(
                "AnyID",
                fake_plan,
                usages=bad_usages,
            ))
        assert len(err.value.exceptions) == 2

    @pytest.mark.asyncio
    async def test_create_subscription_with_duplicated_usages(self, fake_plan, client):
        with pytest.raises(ItemAlreadyExist) as err:
            bad_usages = [
                Usage("AnyTitle", "second", "database", 100, 2, Period.Weekly),
                Usage("AnyTitle", "second", "request", 222, 2, Period.Weekly),
            ]
            _ = await wrapper(client.subscription_client().create_subscription(
                "AnyID",
                fake_plan,
                usages=bad_usages,
            ))
        assert err.value.index_key == "code"
        assert err.value.index_value == "second"
        assert err.value.item_type == "Usage"

    @pytest.mark.asyncio
    async def test_create_subscription_with_incorrect_subscriber_id(self, fake_plan, client):
        with pytest.raises(ValidationError) as err:
            _ = await wrapper(client.subscription_client().create_subscription(
                22,
                fake_plan,
            ))
        assert err.value.field == "SubscriptionCreate.subscriber_id"
        assert err.value.value == 22
        assert err.value.value_type == int


class TestGet:
    @pytest.mark.asyncio
    async def test_get_one_by_id(self, subs, client):
        expected = subs[4]
        real = await wrapper(client.subscription_client().get_subscription_by_id(expected.id))
        assert real.id == expected.id

    @pytest.mark.asyncio
    async def test_get_one_that_not_exist(self, client):
        with pytest.raises(ItemNotExist) as err:
            sub_id = uuid4()
            await wrapper(client.subscription_client().get_subscription_by_id(sub_id))
        assert err.value.lookup_field_key == "id"
        assert err.value.lookup_field_value == str(sub_id)
        assert err.value.item_type == "Subscription"

    @pytest.mark.asyncio
    async def test_get_subscriber_active_one_that_not_exist(self, client):
        real = await wrapper(client.subscription_client().get_current_subscription("subscriber_id_that_not_exist"))
        assert real is None

    @pytest.mark.asyncio
    async def test_get_subscriber_active_one(self, client, subs):
        subscriber_id = subs[4].subscriber_id
        real = await wrapper(client.subscription_client().get_current_subscription(subscriber_id))
        assert real.id == subs[4].id


class TestGetSelected:
    @pytest.mark.asyncio
    async def test_get_selected_by_ids(self, subs, client):
        expected = subs[4:7]
        ids = [x.id for x in expected]
        real = await wrapper(client.subscription_client().get_selected_subscriptions(ids=ids))
        assert len(real) == len(expected)
        assert len(set(x.id for x in real).difference(ids)) == 0

    @pytest.mark.asyncio
    async def test_get_selected_by_subscriber_ids(self, subs, client):
        expected = subs[4:7]
        subscriber_ids = [x.subscriber_id for x in expected]
        real = await wrapper(client.subscription_client().get_selected_subscriptions(subscriber_ids=subscriber_ids))
        assert len(real) == len(expected)
        assert len(set(x.subscriber_id for x in real).difference(subscriber_ids)) == 0

    @pytest.mark.asyncio
    async def test_get_selected_by_statuses(self, subs, client):
        real = await wrapper(client.subscription_client().get_selected_subscriptions(statuses=SubscriptionStatus.Paused))
        assert len(real) == 0

        real = await wrapper(client.subscription_client().get_selected_subscriptions(statuses=SubscriptionStatus.Expired))
        assert len(real) == 0

        real = await wrapper(client.subscription_client().get_selected_subscriptions(statuses=SubscriptionStatus.Active))
        assert len(real) == len(subs)

    @pytest.mark.asyncio
    async def test_get_selected_by_ids_and_subscriber_ids(self, subs, client):
        subscriber_ids = [x.subscriber_id for x in subs[4:7]]
        id_ = subs[5].id
        real = await wrapper(
            client.subscription_client().get_selected_subscriptions(subscriber_ids=subscriber_ids, ids=id_))
        assert len(real) == 1
        real = real.pop()
        assert real.id == id_
        assert real.subscriber_id == subs[5].subscriber_id

    @pytest.mark.asyncio
    async def test_get_selected_by_subscriber_ids_and_statuses(self, subs, client):
        subscriber_ids = [x.subscriber_id for x in subs[4:7]]
        statuses = [SubscriptionStatus.Paused, SubscriptionStatus.Expired]
        real = await wrapper(client.subscription_client().get_selected_subscriptions(
            subscriber_ids=subscriber_ids,
            statuses=statuses,

        ))
        assert len(real) == 0

        statuses = [SubscriptionStatus.Active]
        real = await wrapper(client.subscription_client().get_selected_subscriptions(
            subscriber_ids=subscriber_ids,
            statuses=statuses,

        ))
        assert len(real) == len(subscriber_ids)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_one_with_correct_data(self, subs, client):
        target = subs[5]
        target.autorenew = True
        await wrapper(client.subscription_client().update_subscription(target))

        real = await wrapper(client.subscription_client().get_subscription_by_id(target.id))
        assert real.autorenew == target.autorenew

    @pytest.mark.asyncio
    async def test_update_subscription_plan(self, fake_plan, client):
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan))

        updated_plan = deepcopy(fake_plan)
        updated_plan.title = "UpdatedTitle"
        updated_plan.price = 40

        await wrapper(client.subscription_client().update_subscription_plan(sub.id, updated_plan))

        real = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert real.plan.title == updated_plan.title
        assert real.plan.price == updated_plan.price

    @pytest.mark.asyncio
    async def test_update_subscription_plan_with_bad_validation(self, fake_plan, client):
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan))
        fake_plan.title = 123134
        with pytest.raises(ValidationError):
            await wrapper(client.subscription_client().update_subscription_plan(sub.id, fake_plan))

    @pytest.mark.asyncio
    async def test_pause_and_resume_subscription(self, fake_plan, client):
        sub = await wrapper(client.subscription_client().create_subscription("AnyID", fake_plan))

        await wrapper(client.subscription_client().pause_subscription(sub.id))
        real: Subscription = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert real.status == SubscriptionStatus.Paused
        assert real.paused_from is not None

        await wrapper(client.subscription_client().resume_subscription(sub.id))
        real: Subscription = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert real.status == SubscriptionStatus.Active

    @pytest.mark.asyncio
    async def test_resume_already_active_subscription(self, subs, client):
        target = subs[2]
        await wrapper(client.subscription_client().resume_subscription(target.id))
        real: Subscription = await wrapper(client.subscription_client().get_subscription_by_id(target.id))
        assert real.status == SubscriptionStatus.Active

    @pytest.mark.asyncio
    async def test_renew_subscription(self, fake_plan, client):
        sub: Subscription = await wrapper(client.subscription_client().create_subscription("AnyID", fake_plan, ))
        last_billing = sub.last_billing
        await asyncio.sleep(3)
        await wrapper(client.subscription_client().renew_subscription(sub.id))
        sub = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert (sub.last_billing - last_billing).seconds >= 3


class TestUsages:
    @pytest.mark.asyncio
    async def test_create_subscription_with_custom_usages(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        real = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))
        assert len(real.usages) == 2

    @pytest.mark.asyncio
    async def test_create_subscription_with_usages_from_plan(self, client):
        rates = [
            UsageRate("AnyTitle", "first", "RPS", 100_000, Period.Monthly),
            UsageRate("AnyTitle", "second", "GB", 20, Period.Monthly),
        ]
        sub_plan = await wrapper(client.plan_client().create_plan("PlanWithUsages", 20, "USD", usage_rates=rates))

        real = await wrapper(client.subscription_client().create_subscription("MyId", sub_plan))
        assert len(real.usages) == len(sub_plan.usage_rates)

    @pytest.mark.asyncio
    async def test_increase_usages(self, fake_plan, client):
        usages = [Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly)]
        sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        await wrapper(client.subscription_client().increase_usage(sub.id, "first", 100))

        updated = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert math.isclose(
            updated.usages[0].used_units,
            sub.usages[0].used_units + 100
        )

    @pytest.mark.asyncio
    async def test_decrease_usages(self, fake_plan, client):
        usages = [Usage("AnyTitle", "first", "Request", 100_000, 900, Period.Monthly)]
        sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        await wrapper(client.subscription_client().increase_usage(sub.id, "first", -100))

        updated = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert math.isclose(
            updated.usages[0].used_units,
            sub.usages[0].used_units - 100
        )

    @pytest.mark.asyncio
    async def test_increase_usage_with_wrong_code(self, fake_plan, client):
        usages = [Usage("AnyTitle", "first", "Request", 100_000, 900, Period.Monthly)]
        sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))
        with pytest.raises(Exception):
            await wrapper(client.subscription_client().increase_usage(sub.id, "AnyWrongResource", -100))

    @pytest.mark.asyncio
    async def test_add_usages(self, fake_plan, client):
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan))

        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]

        await wrapper(client.subscription_client().add_usages(sub.id, usages))

        real = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert len(real.usages) == len(usages)

    @pytest.mark.asyncio
    async def test_remove_usages(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan, usages))

        await wrapper(client.subscription_client().remove_usages(sub.id, ["first"]))

        real = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert len(real.usages) == 1
        assert real.usages[0].code == "second"

    @pytest.mark.asyncio
    async def test_update_usages(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan, usages))

        updated = [
            Usage("AnyTitle", "first", "UPDATED", 2, 0, Period.Monthly),
            Usage("AnyTitle", "second", "UPDATED", 2, 0, Period.Monthly),
        ]
        await wrapper(client.subscription_client().update_usages(sub.id, updated))

        real = await wrapper(client.subscription_client().get_subscription_by_id(sub.id))
        assert len(real.usages) == 2
        for usage in real.usages:
            assert usage.unit == "UPDATED"

    @pytest.mark.asyncio
    async def test_update_usages_with_extra_data(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan, usages))

        updated = [
            Usage("AnyTitle", "extra_usage", "UPDATED", 2, 0, Period.Monthly),
        ]
        with pytest.raises(Exception):
            await wrapper(client.subscription_client().update_usages(sub.id, updated))

    @pytest.mark.asyncio
    async def test_add_usage_with_not_unique_code(self, fake_plan, client):
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan, usages))

        updated = [
            Usage("AnyTitle", "first", "UPDATED", 2, 0, Period.Monthly),
        ]
        with pytest.raises(Exception):
            await wrapper(client.subscription_client().add_usages(sub.id, updated))

    @pytest.mark.asyncio
    async def test_add_usages_with_bad_validation(self, fake_plan, client):
        bad_usages = [
            Usage("AnyTitle", "first", 22, 1111, 0, Period.Monthly),
            Usage("AnyTitle", "second", 22, 2342342, 22, Period.Annual),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("Hello", fake_plan))
        with pytest.raises(MultipleError) as err:
            await wrapper(client.subscription_client().add_usages(sub.id, bad_usages))
        print(err.value)
        assert len(err.value.exceptions) == 2


class TestErrors:
    @pytest.mark.asyncio
    async def test_get_subscription_that_not_exist(self, client):
        with pytest.raises(ItemNotExist) as err:
            target_id = uuid4()
            _ = await wrapper(client.subscription_client().get_subscription_by_id(target_id))
        assert err.value.item_type == "Subscription"
        assert err.value.lookup_field_value == str(target_id)
        assert err.value.lookup_field_key == "id"

    @pytest.mark.asyncio
    async def test_increase_usage_with_code_that_not_exist(self, fake_plan, client):
        # Before
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        # Test
        with pytest.raises(ItemNotExist) as err:
            await wrapper(client.subscription_client().increase_usage(sub.id, "code_that_not_exist", 100))
        assert err.value.item_type == "Usage"
        assert err.value.lookup_field_value == "code_that_not_exist"
        assert err.value.lookup_field_key == "code"

    @pytest.mark.asyncio
    async def test_increase_usage_of_subscription_that_not_exist(self, fake_plan, client):
        # Before
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        _sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        # Test
        with pytest.raises(ItemNotExist) as err:
            sub_id = uuid4()
            await wrapper(client.subscription_client().increase_usage(sub_id, "any_code", 100))
        assert err.value.lookup_field_value == str(sub_id)
        assert err.value.item_type == "Subscription"
        assert err.value.lookup_field_key == "id"

    @pytest.mark.asyncio
    async def test_update_usage_with_code_that_not_exist(self, fake_plan, client):
        # Before
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        # Test
        fake_usages = [
            Usage("AnyTitle", "fake_code", "Request", 100_000, 0, Period.Monthly),
        ]
        with pytest.raises(ItemNotExist) as err:
            await wrapper(client.subscription_client().update_usages(sub.id, fake_usages))
        assert err.value.lookup_field_value == "fake_code"
        assert err.value.item_type == "Usage"
        assert err.value.lookup_field_key == "code"

    @pytest.mark.asyncio
    async def test_update_usage_of_subscription_that_not_exist(self, fake_plan, client):
        # Before
        usages = [
            Usage("AnyTitle", "first", "Request", 100_000, 0, Period.Monthly),
            Usage("AnyTitle", "second", "GB", 20, 0, Period.Monthly),
        ]
        _sub = await wrapper(client.subscription_client().create_subscription("AnyId", fake_plan, usages=usages))

        # Test
        with pytest.raises(ItemNotExist) as err:
            sub_id = uuid4()
            await wrapper(client.subscription_client().update_usages(sub_id, usages))
        assert err.value.lookup_field_value == str(sub_id)
        assert err.value.item_type == "Subscription"
        assert err.value.lookup_field_key == "id"
