from subgatekit.v2_0.domain.client.base_client import SyncBaseClient
from subgatekit.v2_0.domain.client.plan_client import SyncPlanClient


class SubgateClient:
    def __init__(self, base_url: str, apikey: str):
        base_client = SyncBaseClient(base_url, apikey)
        self._plan_client = SyncPlanClient(base_client)

    def plan_client(self):
        return self._plan_client
