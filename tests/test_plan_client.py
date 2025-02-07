from datetime import timedelta

import pytest

from subgatekit.client.exceptions import ItemAlreadyExist, ValidationError
from subgatekit.domain.enums import Period
from subgatekit.domain.discount import Discount
from subgatekit.domain.plan import Plan
from subgatekit.domain.usage import UsageRate
from subgatekit.utils import get_current_datetime
from tests.conftest import client, wrapper, plans


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_one(self, client):
        real = await wrapper(client.plan_client().create_plan("Personal", 120, "USD", billing_cycle=Period.Monthly))
        assert real.title == "Personal"

    @pytest.mark.asyncio
    async def test_create_with_discounts(self, client):
        discounts = [
            Discount("First", "first", 0.3, get_current_datetime() + timedelta(30)),
            Discount("Second", "second", 0.1, get_current_datetime() + timedelta(30)),
        ]
        real = await wrapper(
            client.plan_client().create_plan(
                "AnyPlan",
                110,
                "USD",
                discounts=discounts,
            )
        )
        assert len(real.discounts) == len(discounts)

    @pytest.mark.asyncio
    async def test_create_with_usage_rates(self, client):
        rates = [
            UsageRate("DB", "database", "GB", 100, Period.Annual),
            UsageRate("Other", "other", "RPS", 33, Period.Annual),

        ]
        real: Plan = await wrapper(
            client.plan_client().create_plan(
                "AnyPlan",
                110,
                "USD",
                usage_rates=rates,
            )
        )
        assert len(real.usage_rates) == len(rates)

    @pytest.mark.asyncio
    async def test_create_with_incorrect_usage_rates(self, client):
        rates = [
            UsageRate("DB", "database", "GB", 100, Period.Annual),
            UsageRate("DB", "database", "RPS", 33, Period.Annual),

        ]
        with pytest.raises(ItemAlreadyExist) as err:
            _ = await wrapper(
                client.plan_client().create_plan(
                    "AnyPlan",
                    110,
                    "USD",
                    usage_rates=rates,
                )
            )
        assert err.value.item_type == "UsageRate"
        assert err.value.index_key == "code"
        assert err.value.index_value == "database"

    @pytest.mark.asyncio
    async def test_create_with_incorrect_discounts(self, client):
        discounts = [
            Discount("First", "first", 0.3, get_current_datetime() + timedelta(30)),
            Discount("First", "first", 0.1, get_current_datetime() + timedelta(30)),
        ]
        with pytest.raises(ItemAlreadyExist) as err:
            _ = await wrapper(
                client.plan_client().create_plan(
                    "AnyPlan",
                    110,
                    "USD",
                    discounts=discounts,
                )
            )
        assert err.value.item_type == "Discount"
        assert err.value.index_key == "code"
        assert err.value.index_value == "first"


@pytest.mark.asyncio
async def test_get_one_by_id(plans, client):
    expected = plans[2]
    real = await wrapper(client.plan_client().get_plan_by_id(expected.id))
    assert real.id == expected.id
    assert real.title == expected.title


class TestGetSelected:
    @pytest.mark.asyncio
    async def test_get_selected_by_ids(self, client, plans):
        ids = {plans[0].id, plans[1].id}
        real = await wrapper(client.plan_client().get_selected_plans(ids))
        assert len(real) == len(ids)

    @pytest.mark.asyncio
    async def test_get_all(self, client, plans):
        assert len(plans) > 0
        real = await wrapper(client.plan_client().get_selected_plans())
        assert len(real) == len(plans)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_one(self, plans, client):
        target = plans[2]
        target.title = "UPDATED"
        target.price = 787_222

        await wrapper(client.plan_client().update_plan(target))

        real = await wrapper(client.plan_client().get_plan_by_id(target.id))
        assert real.title == "UPDATED"
        assert real.price == 787_222

    @pytest.mark.asyncio
    async def test_update_with_incorrect_discounts(self, plans, client):
        target = plans[2]
        target.discounts = [
            Discount("First", "first", 0.3, get_current_datetime() + timedelta(30)),
            Discount("First", "first", 0.1, get_current_datetime() + timedelta(30)),
        ]
        with pytest.raises(ItemAlreadyExist) as err:
            await wrapper(client.plan_client().update_plan(target))
        assert err.value.item_type == "Discount"
        assert err.value.index_value == "first"
        assert err.value.index_key == "code"

        real = await wrapper(client.plan_client().get_plan_by_id(target.id))
        assert len(real.discounts) == 0

    @pytest.mark.asyncio
    async def test_update_with_incorrect_discount_size(self, plans, client):
        target = plans[2]
        target.discounts = [
            Discount("First", "first", 333, get_current_datetime() + timedelta(30)),
        ]
        with pytest.raises(ValidationError) as err:
            await wrapper(client.plan_client().update_plan(target))
        assert err.value.value_type == float or err.value.value_type == int
        assert err.value.value == 333
        assert err.value.field == "Plan.discounts[0].size"

        real = await wrapper(client.plan_client().get_plan_by_id(target.id))
        assert len(real.discounts) == 0


@pytest.mark.asyncio
async def test_delete_one(plans, client):
    target = plans[2]
    await wrapper(client.plan_client().delete_plan_by_id(target.id))
    real = await wrapper(client.plan_client().get_selected_plans())
    assert len(real) == len(plans) - 1
    assert target.id not in {x.id for x in real}


class TestDeleteSelected:
    @pytest.mark.asyncio
    async def test_delete_all(self, client, plans):
        await wrapper(client.plan_client().delete_selected_plans())
        real = await wrapper(client.plan_client().get_selected_plans())
        assert len(real) == 0

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, client, plans):
        ids = {plans[0].id, plans[1].id}
        await wrapper(client.plan_client().delete_selected_plans(ids=ids))

        real = await wrapper(client.plan_client().get_selected_plans())
        assert len(real) == len(plans) - len(ids)
        real_ids = [x.id for x in real]
        for id_ in ids:
            assert id_ not in real_ids
