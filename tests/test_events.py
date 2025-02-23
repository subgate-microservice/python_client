import asyncio

import pytest
import pytest_asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, AwareDatetime

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan, Period, Subscription, Usage


class Event(BaseModel):
    type: str
    event_code: EventCode
    occurred_at: AwareDatetime
    payload: dict


HOST = "localhost"
PORT = 5678

client = get_client()
app = FastAPI()


class EventStore:
    def __init__(self):
        self._events = {}
        self._counter = {}

    def add(self, event: Event):
        self._events[event.event_code] = event
        if event.event_code not in self._counter:
            self._counter[event.event_code] = 0
        self._counter[event.event_code] += 1

    def check(self, code: EventCode, count: int, **kwargs):
        assert self._events.get(code) is not None
        assert self._counter.get(code, -1) == count
        for field, value in kwargs.items():
            assert self._events.get(code).payload[field] == value

    def clear(self):
        self._events = {}
        self._counter = {}


event_store = EventStore()


@app.post("/event-handler")
async def event_handler(event: Event) -> str:
    print(f"{event.event_code} received")
    event_store.add(event)
    return "OK"


def create_webhooks():
    client.webhook_client().delete_all()
    for code in EventCode:
        code: EventCode
        hook = Webhook(event_code=code, target_url=f"http://{HOST}:{PORT}/event-handler")
        client.webhook_client().create(hook)


async def run_fastapi():
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    await asyncio.sleep(1)  # Ждем запуска сервера
    return server, task


def core_logic():
    plan = Plan("Business", 100, "USD", Period.Annual)
    client.plan_client().create(plan)


@pytest_asyncio.fixture(scope="module", autouse=True)
async def fastapi_server():
    server, task = await run_fastapi()
    create_webhooks()
    yield
    await server.shutdown()
    task.cancel()


@pytest.fixture(autouse=True)
def clear_events():
    event_store.clear()


@pytest.mark.asyncio
async def test_plan(fastapi_server):
    plan = Plan("Business", 100, "USD", Period.Annual)
    client.plan_client().create(plan)

    plan.price = 200
    client.plan_client().update(plan)

    client.plan_client().delete_by_id(plan.id)

    # Check
    await asyncio.sleep(0.2)
    event_store.check(EventCode.PlanCreated, 1, title="Business")
    event_store.check(EventCode.PlanUpdated, 1, changes={"price": 200.0})
    event_store.check(EventCode.PlanDeleted, 1, title="Business", price=200)


class TestSubscription:
    async def create(self):
        plan = Plan("Business", 100, "USD", Period.Annual)
        self.subscription = Subscription.from_plan(plan, "AnyID")
        client.subscription_client().create(self.subscription)

        await asyncio.sleep(0.2)
        event_store.check(EventCode.SubscriptionCreated, 1, subscriber_id=self.subscription.subscriber_id)

    async def add_usage(self):
        self.subscription.usages.add(
            Usage("First", "first", "GB", 100, Period.Monthly)
        )
        client.subscription_client().update(self.subscription)

        await asyncio.sleep(0.2)
        event_store.check(EventCode.SubscriptionUsageAdded, 1, title="First")
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"usages.first": "action:added"})

    @pytest.mark.asyncio
    async def test_check_events(self):
        await self.create()
        await self.add_usage()
