import asyncio
from typing import Coroutine, Awaitable

import pytest
import pytest_asyncio

from subgatekit.client.client import SubgateClient

CLIENT_BASE_URL = "http://localhost:3000/api/v1"
CLIENT_APIKEY_VALUE = "TEST_APIKEY_VALUE"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Создаёт общий event loop для всех тестов."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(params=[
    SubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE),
    # AsyncSubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE),
])
async def client(request) -> SubgateClient:
    yield request.param


@pytest.fixture(scope="session")
def sync_client():
    sclient = SubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE)
    yield sclient


@pytest.fixture(autouse=True, scope="function")
def clear_all(sync_client):
    # subgate_client.plan_client().delete_selected_plans()
    # subgate_client.webhook_client().delete_all_webhooks()
    sync_client.subscription_client().delete_selected()
    yield


async def wrapper[T](result_or_coro: Awaitable[T]) -> T:
    if isinstance(result_or_coro, Coroutine):
        return await result_or_coro
    else:
        return result_or_coro
