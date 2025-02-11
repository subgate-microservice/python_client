import pytest

from subgatekit.v2_0.domain.entities import Plan, UsageRate, Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.utils import get_current_datetime
from .conftest import client, wrapper


class TestCreatePlan:
    @pytest.mark.asyncio
    async def test_create_plan(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        await wrapper(client.plan_client().create(plan))

    @pytest.mark.asyncio
    async def test_create_plan_with_usage_rates(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        plan.usage_rates.add(
            UsageRate("First", "first", "GB", 100, Period.Monthly)
        )
        plan.usage_rates.add(
            UsageRate("Second", "second", "request", 10_000, Period.Daily)
        )
        await wrapper(client.plan_client().create(plan))


class TestGetPlan:
    @pytest.mark.asyncio
    async def test_get_by_id(self, client):
        # Before
        expected = Plan("SimplePlan", 100, "USD", Period.Annual)
        await wrapper(client.plan_client().create(expected))

        # Test
        real = await wrapper(client.plan_client().get_by_id(expected.id))
        assert real.id == expected.id

    @pytest.mark.asyncio
    async def test_get_plan_with_usage_rates(self, client):
        # Before
        expected = Plan("With usage rates", 100, "USD", Period.Annual)
        expected.usage_rates.add(UsageRate("First", "first", "GB", 100, Period.Monthly))
        expected.usage_rates.add(UsageRate("Second", "sec", "call", 10_000, Period.Daily))
        await wrapper(client.plan_client().create(expected))

        # Test
        real: Plan = await wrapper(client.plan_client().get_by_id(expected.id))
        assert real.id == expected.id
        assert len(real.usage_rates.get_all()) == 2
        assert real.usage_rates.get("first").title == "First"
        assert real.usage_rates.get("sec").title == "Second"

    @pytest.mark.asyncio
    async def test_get_plan_with_discounts(self, client):
        # Before
        expected = Plan("With discounts", 333, "EUR", Period.Monthly)
        expected.discounts.add(Discount("First", "first", 0.2, get_current_datetime()))
        expected.discounts.add(Discount("Second", "second", 0.2, get_current_datetime()))
        client.plan_client().create(expected)

        # Test
        real: Plan = await wrapper(client.plan_client().get_by_id(expected.id))
        assert real.id == expected.id
        assert len(real.discounts.get_all()) == len(expected.discounts.get_all())
        assert real.discounts.get("first").title == "First"
        assert real.discounts.get("second").title == "Second"

    @pytest.mark.asyncio
    async def test_get_plan_with_fields(self, client):
        # Before
        expected = Plan("With fields", 365, "USD", Period.Annual, fields={"Hello": {"World!": 1}})
        await wrapper(client.plan_client().create(expected))

        # Test
        real: Plan = await wrapper(client.plan_client().get_by_id(expected.id))
        assert real.fields == expected.fields


class TestUpdatePlan:
    @pytest.mark.asyncio
    async def test_add_usage_rates(self, client):
        # Before
        plan = Plan("Simple plan", 100, "USD", Period.Monthly)
        await wrapper(client.plan_client().create(plan))

        # Update
        plan: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        plan.usage_rates.add(UsageRate("Hello", "first", "GB", 100, Period.Monthly))
        await wrapper(client.plan_client().update(plan))

        # Check
        real: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        assert len(real.usage_rates.get_all()) == 1
        assert real.usage_rates.get("first").title == "Hello"
