from typing import Optional

import httpx

from subgatekit.client.services import processing_response


class BaseClient:

    def __init__(self, base_url: str, apikey: str):
        self._base_url = base_url
        self._apikey = apikey
        self._headers = {
            "X-API-Key": f"{apikey}",
            "Content-Type": "application/json",
        }


class SyncBaseClient(BaseClient):
    def __init__(self, base_url: str, apikey: str):
        super().__init__(base_url, apikey)
        self._client = httpx.Client(headers=self._headers, follow_redirects=True)

    def request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        url = f"{self._base_url}{endpoint}"
        headers = {**self._headers, **kwargs.pop("headers", {})}
        response = self._client.request(method, url, headers=headers, **kwargs)
        return processing_response(response)


class AsyncBaseClient(BaseClient):
    def __init__(self, base_url: str, apikey: str):
        super().__init__(base_url, apikey)
        self._client = httpx.AsyncClient(headers=self._headers, follow_redirects=True)

    async def request(self, method: str, endpoint: str, **kwargs) -> Optional[dict]:
        url = f"{self._base_url}{endpoint}"
        headers = {**self._headers, **kwargs.pop("headers", {})}
        response = await self._client.request(method, url, headers=headers, **kwargs)
        return processing_response(response)
