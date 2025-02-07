from subgate_client.client.base_client import AsyncBaseClient, SyncBaseClient
from subgate_client.client.plan_client import AsyncPlanClient, SyncPlanClient
from subgate_client.client.subscription_client import AsyncSubscriptionClient, SyncSubscriptionClient
from subgate_client.client.webhook_client import AsyncWebhookClient, SyncWebhookClient


class AsyncSubgateClient:
    def __init__(self, base_url: str, apikey: str):
        client = AsyncBaseClient(base_url, apikey)
        self._plan_client = AsyncPlanClient(client)
        self._subscription_client = AsyncSubscriptionClient(client)
        self._webhook_client = AsyncWebhookClient(client)

    def plan_client(self):
        return self._plan_client

    def subscription_client(self):
        return self._subscription_client

    def webhook_client(self):
        return self._webhook_client


class SubgateClient:
    def __init__(self, base_url: str, apikey: str):
        client = SyncBaseClient(base_url, apikey)
        self._plan_client = SyncPlanClient(client)
        self._subscription_client = SyncSubscriptionClient(client)
        self._webhook_client = SyncWebhookClient(client)

    def plan_client(self):
        return self._plan_client

    def subscription_client(self):
        return self._subscription_client

    def webhook_client(self):
        return self._webhook_client
