from subgatekit.client.base_client import SyncBaseClient
from subgatekit.client.deserializers import deserialize_plan
from subgatekit.client.serailizers import (
    serialize_plan,
)
from subgatekit.entities import Plan
from subgatekit.utils import ID


class SyncPlanClient:
    def __init__(self, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(self, plan: Plan) -> None:
        url = "/plan"
        data = serialize_plan(plan)
        self._base_client.request("POST", url, json=data)

    def update(self, plan: Plan) -> None:
        url = f"/plan/{plan.id}"
        data = serialize_plan(plan)
        self._base_client.request("PUT", url, json=data)

    def delete(self, plan_id: ID) -> None:
        url = f"/plan/{plan_id}"
        self._base_client.request("DELETE", url)

    def get_by_id(self, plan_id: ID) -> Plan:
        url = f"/plan/{plan_id}"
        json_data = self._base_client.request("GET", url)
        return deserialize_plan(json_data)
