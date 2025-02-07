import asyncio
from typing import Coroutine, Union
from uuid import uuid4

import pytest
import pytest_asyncio

from subgate.client.subgate_client import SubgateClient, AsyncSubgateClient
from subgate.domain.events import EventCode

CLIENT_BASE_URL = "http://localhost:3000/api/v1"
CLIENT_APIKEY_VALUE = "TEST_APIKEY_VALUE"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Создаёт общий event loop для всех тестов."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


foo = SubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE)


def get_client():
    return foo


@pytest.fixture(autouse=True)
def clear_all():
    get_client().subscription_client().delete_selected_subscriptions()
    get_client().plan_client().delete_selected_plans()
    get_client().webhook_client().delete_all_webhooks()
    yield


@pytest_asyncio.fixture()
async def plans():
    data = []
    for _ in range(5):
        created_plan = get_client().plan_client().create_plan("Business", 11, "USD")
        data.append(created_plan)
    yield data


@pytest.fixture()
def fake_plan(plans):
    yield plans[2]


@pytest.fixture()
def subs(fake_plan):
    data = []
    for _ in range(11):
        sub = get_client().subscription_client().create_subscription(subscriber_id=str(uuid4()), plan=fake_plan)
        data.append(sub)
    yield data
    get_client().subscription_client().delete_selected_subscriptions()


@pytest.fixture()
def webhooks():
    data = []
    for event in EventCode:
        hook = get_client().webhook_client().create_webhook(event, "https://my-site.com")
        data.append(hook)
    yield data


@pytest_asyncio.fixture(params=[
    SubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE),
    AsyncSubgateClient(CLIENT_BASE_URL, CLIENT_APIKEY_VALUE),
])
async def client(request) -> Union[SubgateClient, AsyncSubgateClient]:
    yield request.param


async def wrapper(result_or_coro):
    if isinstance(result_or_coro, Coroutine):
        return await result_or_coro
    else:
        return result_or_coro
