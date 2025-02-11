from subgatekit.client.base_client import SyncBaseClient
from subgatekit.client.plan_client import SyncPlanClient
from subgatekit.client.subscription_client import SyncSubscriptionClient


class SubgateClient:
    def __init__(self, base_url: str, apikey: str):
        base_client = SyncBaseClient(base_url, apikey)
        self._plan_client = SyncPlanClient(base_client)
        self._sub_client = SyncSubscriptionClient(base_client)

    def plan_client(self):
        return self._plan_client

    def subscription_client(self):
        return self._sub_client
