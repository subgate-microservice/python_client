from subgatekit.v2_0.domain.client.base_client import SyncBaseClient
from subgatekit.v2_0.domain.entities import Plan
from subgatekit.v2_0.domain.serailizers import (
    serialize_plan,
)


class SyncPlanClient:
    def __init__(self, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(self, plan: Plan) -> None:
        url = "/plan"
        data = serialize_plan(plan)
        self._base_client.request("POST", url, json=data)
