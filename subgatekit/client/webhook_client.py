from subgatekit.client.base_client import SyncBaseClient, AsyncBaseClient
from subgatekit.domain.plan import ID
from subgatekit.domain.webhook import Webhook, WebhookCreate, WebhookUpdate
from subgatekit.domain.events import EventCode
from subgatekit.services import serializers, deserializers
from subgatekit.services.validators import validate


class AsyncWebhookClient:
    def __init__(self, client: AsyncBaseClient):
        self._client = client

    async def create_webhook(
            self,
            event_code: EventCode | str,
            target_url: str,
    ) -> Webhook:
        webhook = WebhookCreate(event_code, target_url)
        validate(webhook)
        payload = serializers.serialize_webhook_create(webhook)
        response_data = await self._client.request("POST", f"/webhook", json=payload)
        hook = deserializers.deserialize_webhook(response_data)
        validate(hook)
        return hook

    async def get_webhook_by_id(self, webhook_id: ID) -> Webhook:
        response_data = await self._client.request("GET", f"/webhook/{webhook_id}")
        hook = deserializers.deserialize_webhook(response_data)
        validate(hook)
        return hook

    async def get_all_webhooks(self) -> list[Webhook]:
        response_data = await self._client.request("GET", f"/webhook")
        hooks = []
        for json_data in response_data:
            hook = deserializers.deserialize_webhook(json_data)
            validate(hook)
            hooks.append(hook)
        return hooks

    async def update_webhook(self, webhook: Webhook) -> None:
        webhook_update = WebhookUpdate.from_webhook(webhook)
        validate(webhook_update)
        payload = serializers.serialize_webhook_update(webhook_update)
        await self._client.request("PUT", f"/webhook/{webhook.id}", json=payload)

    async def delete_all_webhooks(self) -> None:
        await self._client.request("DELETE", f"/webhook", json={})

    async def delete_webhook_by_id(self, webhook_id: ID) -> None:
        await self._client.request("DELETE", f"/webhook/{webhook_id}")


class SyncWebhookClient:
    def __init__(self, client: SyncBaseClient):
        self._client = client

    def create_webhook(
            self,
            event_code: EventCode | str,
            target_url: str,
    ) -> Webhook:
        webhook = WebhookCreate(event_code, target_url)
        payload = serializers.serialize_webhook_create(webhook)
        response_data = self._client.request("POST", f"/webhook", json=payload)
        hook = deserializers.deserialize_webhook(response_data)
        validate(hook)
        return hook

    def get_webhook_by_id(self, webhook_id: ID) -> Webhook:
        response_data = self._client.request("GET", f"/webhook/{webhook_id}")
        hook = deserializers.deserialize_webhook(response_data)
        validate(hook)
        return hook

    def get_all_webhooks(self) -> list[Webhook]:
        response_data = self._client.request("GET", f"/webhook")
        result = []
        for json_data in response_data:
            hook = deserializers.deserialize_webhook(json_data)
            validate(hook)
            result.append(hook)
        return result

    def update_webhook(self, webhook: Webhook) -> None:
        webhook_update = WebhookUpdate.from_webhook(webhook)
        validate(webhook_update)
        payload = serializers.serialize_webhook_update(webhook_update)
        self._client.request("PUT", f"/webhook/{webhook.id}", json=payload)

    def delete_all_webhooks(self) -> None:
        self._client.request("DELETE", f"/webhook", json={})

    def delete_webhook_by_id(self, webhook_id: ID) -> None:
        self._client.request("DELETE", f"/webhook/{webhook_id}")
