from typing import Union, Iterable
from uuid import UUID

from subgatekit.client.base_client import SyncBaseClient, AsyncBaseClient
from subgatekit.client.deserializers import deserialize_plan
from subgatekit.client.serailizers import (
    serialize_plan,
)
from subgatekit.client.services import OrderBy, build_query_params
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

    def delete_by_id(self, plan_id: ID) -> None:
        url = f"/plan/{plan_id}"
        self._base_client.request("DELETE", url)

    def delete_selected(
            self,
            ids: Union[UUID, Iterable[UUID]] = None,
    ):
        url = f"/plan/"
        params = build_query_params(ids=ids)
        self._base_client.request("DELETE", url, params=params)

    def get_by_id(self, plan_id: ID) -> Plan:
        url = f"/plan/{plan_id}"
        json_data = self._base_client.request("GET", url)
        return deserialize_plan(json_data)

    def get_selected(
            self,
            ids: Union[UUID, Iterable[UUID]] = None,
            order_by: OrderBy = None,
            skip=0,
            limit=100,
    ):
        url = "/plan"
        params = build_query_params(ids, skip=skip, limit=limit, order_by=order_by)
        json_data = self._base_client.request("GET", url, params=params)
        return [deserialize_plan(x) for x in json_data]


class AsyncPlanClient:
    def __init__(self, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def create(self, plan: Plan) -> None:
        url = "/plan"
        data = serialize_plan(plan)
        await self._base_client.request("POST", url, json=data)

    async def update(self, plan: Plan) -> None:
        url = f"/plan/{plan.id}"
        data = serialize_plan(plan)
        await self._base_client.request("PUT", url, json=data)

    async def delete_by_id(self, plan_id: ID) -> None:
        url = f"/plan/{plan_id}"
        await self._base_client.request("DELETE", url)

    async def delete_selected(
            self,
            ids: Union[UUID, Iterable[UUID]] = None,
    ):
        url = f"/plan/"
        params = build_query_params(ids=ids)
        await self._base_client.request("DELETE", url, params=params)

    async def get_by_id(self, plan_id: ID) -> Plan:
        url = f"/plan/{plan_id}"
        json_data = await self._base_client.request("GET", url)
        return deserialize_plan(json_data)

    async def get_selected(
            self,
            ids: Union[UUID, Iterable[UUID]] = None,
            order_by: OrderBy = None,
            skip=0,
            limit=100,
    ):
        url = "/plan"
        params = build_query_params(ids, skip=skip, limit=limit, order_by=order_by)
        json_data = await self._base_client.request("GET", url, params=params)
        return [deserialize_plan(x) for x in json_data]
