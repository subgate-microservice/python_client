from subgatekit.client.base_client import SyncBaseClient, AsyncBaseClient
from subgatekit.client.plan_client import SyncPlanClient, AsyncPlanClient
from subgatekit.client.subscription_client import SyncSubscriptionClient, AsyncSubscriptionClient
from subgatekit.client.webhook_client import SyncWebhookClient, AsyncWebhookClient


class SubgateClient:
    def __init__(
            self,
            base_url: str,
            apikey_public_id: str,
            apikey_secret: str
    ):
        base_client = SyncBaseClient(base_url, f"{apikey_public_id}:{apikey_secret}")
        self._plan_client = SyncPlanClient(base_client)
        self._sub_client = SyncSubscriptionClient(base_client)
        self._webhook_client = SyncWebhookClient(base_client)

    def plan_client(self) -> SyncPlanClient:
        return self._plan_client

    def subscription_client(self) -> SyncSubscriptionClient:
        return self._sub_client

    def webhook_client(self) -> SyncWebhookClient:
        return self._webhook_client


class AsyncSubgateClient:
    def __init__(self, base_url: str, apikey_public_id: str, apikey_secret: str):
        base_client = AsyncBaseClient(base_url, f"{apikey_public_id}:{apikey_secret}")
        self._plan_client = AsyncPlanClient(base_client)
        self._sub_client = AsyncSubscriptionClient(base_client)
        self._webhook_client = AsyncWebhookClient(base_client)

    def plan_client(self) -> AsyncPlanClient:
        return self._plan_client

    def subscription_client(self) -> AsyncSubscriptionClient:
        return self._sub_client

    def webhook_client(self) -> AsyncWebhookClient:
        return self._webhook_client
