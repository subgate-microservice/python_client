from datetime import datetime
from typing import Iterable, Optional

from subgatekit.client.base_client import SyncBaseClient
from subgatekit.client.deserializers import deserialize_subscription
from subgatekit.client.serailizers import (
    serialize_subscription,
)
from subgatekit.client.services import build_query_params
from subgatekit.entities import Subscription
from subgatekit.enums import SubscriptionStatus
from subgatekit.utils import ID


class SyncSubscriptionClient:
    def __init__(self, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(self, sub: Subscription) -> None:
        url = "/subscription"
        data = serialize_subscription(sub)
        self._base_client.request("POST", url, json=data)

    def create_then_get(self, sub: Subscription) -> Subscription:
        self.create(sub)
        return self.get_by_id(sub.id)

    def update(self, sub: Subscription) -> None:
        url = f"/subscription/{sub.id}"
        data = serialize_subscription(sub)
        self._base_client.request("PUT", url, json=data)

    def delete_by_id(self, sub_id: ID) -> None:
        url = f"/subscription/{sub_id}"
        self._base_client.request("DELETE", url)

    def delete_selected(
            self,
            ids: Iterable[ID] = None,
            subscriber_ids: Iterable[str] = None,
            statuses: Iterable[SubscriptionStatus] = None,
            expiration_date_gte: datetime = None,
            expiration_date_lt: datetime = None,
    ) -> None:
        sby = build_query_params(
            ids=ids,
            subscriber_ids=subscriber_ids,
            statuses=statuses,
            expiration_date_gte=expiration_date_gte,
            expiration_date_lt=expiration_date_lt,
        )
        self._base_client.request("DELETE", f"/subscription", params=sby)

    def get_by_id(self, sub_id: ID) -> Subscription:
        url = f"/subscription/{sub_id}"
        json_data = self._base_client.request("GET", url)
        return deserialize_subscription(json_data)

    def get_selected(
            self,
    ) -> list[Subscription]:
        raise NotImplemented

    def get_current_subscription(self, subscriber_id: str) -> Optional[Subscription]:
        raise NotImplemented
