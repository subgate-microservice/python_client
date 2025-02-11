import pytest

from subgatekit.v2_0.domain.entities import Plan
from subgatekit.v2_0.domain.enums import Period
from .conftest import client, wrapper


class TestCreatePlan:
    @pytest.mark.asyncio
    async def test_create_plan(self, client):
        plan = Plan("Personal", 100, "USD", Period.Monthly)
        await wrapper(client.plan_client().create(plan))
