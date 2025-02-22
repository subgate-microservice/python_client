import asyncio

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, AwareDatetime
from starlette.responses import JSONResponse

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan, Period

client = get_client()

host = "localhost"
port = 5678

app = FastAPI()


class Foo(BaseModel):
    type: str
    event_code: str
    occurred_at: AwareDatetime
    payload: dict


@app.post("/event-handler")
async def event_handler(event: Foo) -> str:
    print(event)
    return "OK"


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(_request: Request, exc: RequestValidationError):
    detail = [
        dict(
            field=x["loc"][1],
            value=x["input"],
            value_type=x["input"].__class__.__name__,
            message=x["msg"],
        )
        for x in exc.errors()
    ]
    for x in detail:
        print(x)
    return JSONResponse(
        status_code=422,
        content={
            "exception_code": "request_validation_error",
            "message": str(exc),
            "detail": detail,
        },
    )


def create_webhooks():
    client.webhook_client().delete_all()
    hook = Webhook(event_code=EventCode.PlanCreated, target_url=f"http://{host}:{port}/event-handler")
    client.webhook_client().create(hook)


def run_fastapi():
    conf = uvicorn.Config(app, host=host, port=port)
    server = uvicorn.Server(conf)
    coro = server.serve()
    task = asyncio.create_task(coro)
    task.set_name("Server")
    return server


def core_logic():
    plan = Plan("Business", 100, "USD", Period.Annual)
    client.plan_client().create(plan)


async def main():
    server = run_fastapi()
    create_webhooks()
    core_logic()

    await asyncio.sleep(11)
    await server.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
