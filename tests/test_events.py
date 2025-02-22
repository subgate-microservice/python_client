import asyncio

import pytest
import pytest_asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, AwareDatetime

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan, Period


class Event[T](BaseModel):
    type: str
    event_code: str
    occurred_at: AwareDatetime
    payload: dict


HOST = "localhost"
PORT = 5678

client = get_client()
app = FastAPI()


@app.post("/event-handler")
async def event_handler(event: Event) -> str:
    print(event)
    return "OK"


def create_webhooks():
    client.webhook_client().delete_all()
    hook = Webhook(event_code=EventCode.PlanCreated, target_url=f"http://{HOST}:{PORT}/event-handler")
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
    create_webhooks()  # Создаем вебхуки
    yield
    await server.shutdown()
    task.cancel()


@pytest.mark.asyncio
async def test_webhooks(fastapi_server):
    core_logic()
    await asyncio.sleep(10)
