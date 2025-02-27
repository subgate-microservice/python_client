from subgatekit.client.base_client import SyncBaseClient, AsyncBaseClient
from subgatekit.client.deserializers import deserialize_webhook
from subgatekit.client.serailizers import serialize_webhook
from subgatekit.entities import Webhook
from subgatekit.utils import ID


class SyncWebhookClient:
    def __init__(self, base_client: SyncBaseClient):
        self._base_client = base_client

    def create(self, webhook: Webhook) -> None:
        url = "/webhook"
        data = serialize_webhook(webhook)
        self._base_client.request("POST", url, json=data)

    def update(self, webhook: Webhook) -> None:
        url = f"/webhook/{webhook.id}"
        data = serialize_webhook(webhook)
        self._base_client.request("PUT", url, json=data)

    def delete_by_id(self, webhook_id: ID) -> None:
        url = f"/webhook/{webhook_id}"
        self._base_client.request("DELETE", url)

    def delete_all(self):
        url = f"/webhook"
        self._base_client.request("DELETE", url, json={})

    def get_by_id(self, webhook_id: ID) -> Webhook:
        url = f"/webhook/{webhook_id}"
        json_data = self._base_client.request("GET", url)
        return deserialize_webhook(json_data)

    def get_all(self):
        url = f"/webhook"
        json_data = self._base_client.request("GET", url)
        return [deserialize_webhook(x) for x in json_data]


class AsyncWebhookClient:
    def __init__(self, base_client: AsyncBaseClient):
        self._base_client = base_client

    async def create(self, webhook: Webhook) -> None:
        url = "/webhook"
        data = serialize_webhook(webhook)
        await self._base_client.request("POST", url, json=data)

    async def update(self, webhook: Webhook) -> None:
        url = f"/webhook/{webhook.id}"
        data = serialize_webhook(webhook)
        await self._base_client.request("PUT", url, json=data)

    async def delete_by_id(self, webhook_id: ID) -> None:
        url = f"/webhook/{webhook_id}"
        await self._base_client.request("DELETE", url)

    async def delete_all(self):
        url = f"/webhook"
        await self._base_client.request("DELETE", url, json={})

    async def get_by_id(self, webhook_id: ID) -> Webhook:
        url = f"/webhook/{webhook_id}"
        json_data = await self._base_client.request("GET", url)
        return deserialize_webhook(json_data)

    async def get_all(self):
        url = f"/webhook"
        json_data = await self._base_client.request("GET", url)
        return [deserialize_webhook(x) for x in json_data]
