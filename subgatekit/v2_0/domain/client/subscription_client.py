from subgatekit.services.deserializers import deserialize_subscription
from subgatekit.v2_0.domain.client.base_client import SyncBaseClient
from subgatekit.v2_0.domain.client.serailizers import (
    serialize_subscription,
)
from subgatekit.v2_0.domain.entities import Subscription
from subgatekit.v2_0.domain.utils import ID


class SyncSubscriptionClient:
    def __init__(self, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(self, sub: Subscription) -> None:
        url = "/subscription"
        data = serialize_subscription(sub)
        self._base_client.request("POST", url, json=data)

    def update(self, sub: Subscription) -> None:
        url = f"/subscription/{sub.id}"
        data = serialize_subscription(sub)
        self._base_client.request("PUT", url, json=data)

    def delete(self, sub_id: ID) -> None:
        url = f"/subscription/{sub_id}"
        self._base_client.request("DELETE", url)

    def get_by_id(self, sub_id: ID) -> Subscription:
        url = f"/subscription/{sub_id}"
        json_data = self._base_client.request("GET", url)
        return deserialize_subscription(json_data)
