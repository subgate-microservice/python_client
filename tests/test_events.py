import asyncio

import pytest
import pytest_asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, AwareDatetime

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan, Period


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

    def check(self, code: EventCode, count: int):
        assert self._events.get(code) is not None
        assert self._counter.get(code, -1) == count

    def clear(self):
        self._events = {}
        self._counter = {}


event_store = EventStore()


@app.post("/event-handler")
async def event_handler(event: Event) -> str:
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


@pytest_asyncio.fixture(scope="module")
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
async def test_plan_created(fastapi_server):
    plan = Plan("Business", 100, "USD", Period.Annual)
    client.plan_client().create(plan)
    await asyncio.sleep(1)
    event_store.check(EventCode.PlanCreated, 1)
