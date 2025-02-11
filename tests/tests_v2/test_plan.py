import pytest
import pytest_asyncio

from subgatekit.v2_0.domain.entities import Plan
from subgatekit.v2_0.domain.enums import Period
from .conftest import sync_client, client, wrapper


class TestCreatePlan:
    @pytest.mark.asyncio
    async def test_create_plan(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        await wrapper(client.plan_client().create(plan))


class TestGetPlan:
    @pytest_asyncio.fixture()
    async def simple_plan(self, sync_client) -> Plan:
        plan = Plan(f"SimplePlan", 100, "USD", Period.Annual)
        sync_client.plan_client().create(plan)

        yield plan

    @pytest.mark.asyncio
    async def test_get_by_id(self, client, simple_plan):
        real = await wrapper(client.plan_client().get_by_id(simple_plan.id))
        assert real.id == simple_plan.id
