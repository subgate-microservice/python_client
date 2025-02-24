import pytest

from subgatekit.entities import Plan, UsageRate, Discount
from subgatekit.enums import Period
from subgatekit.utils import get_current_datetime
from tests.fakes import simple_plan, plan_with_rates, plan_with_discounts, plan_with_fields
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
    async def test_get_by_id(self, client, simple_plan):
        real = await wrapper(client.plan_client().get_by_id(simple_plan.id))
        assert real.id == simple_plan.id

    @pytest.mark.asyncio
    async def test_get_plan_with_usage_rates(self, client, plan_with_rates):
        real: Plan = await wrapper(client.plan_client().get_by_id(plan_with_rates.id))
        assert real.id == plan_with_rates.id
        assert len(real.usage_rates.get_all()) == 2
        assert real.usage_rates.get("first").title == "First"
        assert real.usage_rates.get("second").title == "Second"

    @pytest.mark.asyncio
    async def test_get_plan_with_discounts(self, client, plan_with_discounts):
        real: Plan = await wrapper(client.plan_client().get_by_id(plan_with_discounts.id))
        assert real.id == plan_with_discounts.id
        assert len(real.discounts.get_all()) == len(plan_with_discounts.discounts.get_all())
        assert real.discounts.get("first").title == "First"
        assert real.discounts.get("second").title == "Second"

    @pytest.mark.asyncio
    async def test_get_plan_with_fields(self, client, plan_with_fields):
        real: Plan = await wrapper(client.plan_client().get_by_id(plan_with_fields.id))
        assert real.fields == plan_with_fields.fields

    @pytest.mark.asyncio
    async def test_get_all_plans(self, client, simple_plan, plan_with_rates, plan_with_fields):
        real = await wrapper(client.plan_client().get_selected())
        assert len(real) == 3

    @pytest.mark.asyncio
    async def test_get_selected_plans(self, client, simple_plan, plan_with_rates, plan_with_fields):
        real = await wrapper(client.plan_client().get_selected(ids=[simple_plan.id, plan_with_rates.id]))
        assert len(real) == 2


class TestUpdatePlan:
    @pytest.mark.asyncio
    async def test_add_usage_rates(self, client, simple_plan):
        # Update
        plan: Plan = await wrapper(client.plan_client().get_by_id(simple_plan.id))
        plan.usage_rates.add(UsageRate("Hello", "first", "GB", 100, Period.Monthly))
        await wrapper(client.plan_client().update(plan))

        # Check
        real: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        assert len(real.usage_rates.get_all()) == 1
        assert real.usage_rates.get("first").title == "Hello"

    @pytest.mark.asyncio
    async def test_remove_usage_rates(self, client, plan_with_rates):
        plan: Plan = await wrapper(client.plan_client().get_by_id(plan_with_rates.id))
        plan.usage_rates.remove("second")
        await wrapper(client.plan_client().update(plan))

        # Check
        real: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        assert len(real.usage_rates.get_all()) == 1
        assert real.usage_rates.get("first").title == "First"

    @pytest.mark.asyncio
    async def test_add_discounts(self, client, simple_plan):
        plan: Plan = await wrapper(client.plan_client().get_by_id(simple_plan.id))
        plan.discounts.add(Discount("Hello", "first", 0.5, get_current_datetime()))
        await wrapper(client.plan_client().update(plan))

        # Check
        real: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        assert len(real.discounts.get_all()) == 1
        assert real.discounts.get("first").title == "Hello"

    @pytest.mark.asyncio
    async def test_remove_discounts(self, client, plan_with_discounts):
        plan: Plan = await wrapper(client.plan_client().get_by_id(plan_with_discounts.id))
        plan.discounts.remove("first")
        await wrapper(client.plan_client().update(plan))

        # Check
        real: Plan = await wrapper(client.plan_client().get_by_id(plan.id))
        assert len(real.discounts.get_all()) == 1
        assert real.discounts.get("second").title == "Second"
