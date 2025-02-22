import asyncio

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan
from subgatekit.events import *

client = get_client()

host = "localhost"
port = 5678

app = FastAPI()

EVENTS = {
    "plan_created": PlanCreated,
}


class Foo(BaseModel):
    type: str
    code: str
    payload: dict


@app.post("/event-handler")
async def event_handler(event: Foo) -> str:
    print(event)
    return "OK"


def create_webhooks():
    hook = Webhook(event_code=EventCode.PlanCreated, target_url=f"http://{host}:{port}/event-handler")
    client.webhook_client().create(hook)


def run_fastapi():
    conf = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(conf)
    coro = server.serve()
    task = asyncio.create_task(coro)
    task.set_name("Server")


def core_logic():
    plan = Plan("Business", 100, "USD", Period.Annual)
    client.plan_client().create(plan)


async def main():
    run_fastapi()
    create_webhooks()
    core_logic()

    print("Shutting down...")
    await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(main())
