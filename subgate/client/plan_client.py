from typing import Optional, Iterable, Any

from subgate.client.base_client import OrderBy, _build_query_params, AsyncBaseClient, SyncBaseClient
from subgate.domain.enums import Period
from subgate.domain.discount import Discount
from subgate.domain.plan import Plan, ID, PlanCreate
from subgate.domain.usage import UsageRate
from subgate.services import serializers, deserializers
from subgate.services.validators import validate


class AsyncPlanClient:
    def __init__(self, client: AsyncBaseClient):
        self._client = client

    async def get_plan_by_id(self, plan_id: ID) -> Plan:
        json_data = await self._client.request("GET", f"/plan/{plan_id}")
        plan = deserializers.deserialize_plan(json_data)
        validate(plan)
        return plan

    async def get_selected_plans(
            self,
            ids: Optional[Iterable[ID]] = None,
            skip: int = 0,
            limit: int = 100,
            order_by: OrderBy = None,
    ) -> list[Plan]:
        params = _build_query_params(
            ids=ids,
            skip=skip,
            limit=limit,
            order_by=order_by,
        )
        json_data = await self._client.request("GET", "/plan", params=params)
        plans = []
        for plan_json in json_data:
            plan = deserializers.deserialize_plan(plan_json)
            validate(plan)
            plans.append(plan)
        return plans

    async def create_plan(
            self,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Period = Period.Monthly,
            description: str = "",
            level: int = 10,
            features: str = "",
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            fields: dict[str, Any] = None,
    ) -> Plan:
        plan_create = PlanCreate(
            title, price, currency, billing_cycle, description, level, features, usage_rates, discounts, fields,
        )
        validate(plan_create)
        payload = serializers.serialize_plan_create(plan_create)
        response_data = await self._client.request("POST", "/plan", json=payload)
        plan = deserializers.deserialize_plan(response_data)
        validate(plan)
        return plan

    async def update_plan(self, plan: Plan) -> None:
        validate(plan)
        payload = serializers.serialize_plan(plan)
        await self._client.request("PUT", f"/plan/{plan.id}", json=payload)

    async def delete_plan_by_id(self, plan_id: ID) -> None:
        await self._client.request("DELETE", f"/plan/{plan_id}")

    async def delete_selected_plans(self, ids: Optional[Iterable[ID]] = None) -> None:
        sby = _build_query_params(ids=ids)
        await self._client.request("DELETE", f"/plan", json=sby)


class SyncPlanClient:
    def __init__(self, client: SyncBaseClient):
        self._client = client

    def get_plan_by_id(self, plan_id: ID) -> Plan:
        json_data = self._client.request("GET", f"/plan/{plan_id}")
        plan = deserializers.deserialize_plan(json_data)
        validate(plan)
        return plan

    def get_selected_plans(
            self,
            ids: Optional[Iterable[ID]] = None,
            skip: int = 0,
            limit: int = 100,
            order_by: OrderBy = None,
    ) -> list[Plan]:
        params = _build_query_params(
            ids=ids,
            skip=skip,
            limit=limit,
            order_by=order_by,
        )
        json_data = self._client.request("GET", "/plan", params=params)
        plans = []
        for plan_json in json_data:
            plan = deserializers.deserialize_plan(plan_json)
            validate(plan)
            plans.append(plan)
        return plans

    def create_plan(
            self,
            title: str,
            price: float,
            currency: str,
            billing_cycle: Period = Period.Monthly,
            description: str = "",
            level: int = 10,
            features: str = "",
            usage_rates: list[UsageRate] = None,
            discounts: list[Discount] = None,
            fields: dict[str, Any] = None,
    ) -> Plan:
        plan_create = PlanCreate(
            title, price, currency, billing_cycle, description, level, features, usage_rates, discounts, fields,
        )
        validate(plan_create)
        payload = serializers.serialize_plan_create(plan_create)
        response_data = self._client.request("POST", "/plan", json=payload)
        plan = deserializers.deserialize_plan(response_data)
        validate(plan)
        return plan

    def update_plan(self, plan: Plan) -> None:
        validate(plan)
        payload = serializers.serialize_plan(plan)
        self._client.request("PUT", f"/plan/{plan.id}", json=payload)

    def delete_plan_by_id(self, plan_id: ID) -> None:
        self._client.request("DELETE", f"/plan/{plan_id}")

    def delete_selected_plans(self, ids: Optional[Iterable[ID]] = None) -> None:
        sby = _build_query_params(ids=ids)
        self._client.request("DELETE", f"/plan", json=sby)
