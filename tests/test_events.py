import asyncio
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, AwareDatetime

from snippets.tests.client import get_client
from subgatekit import Webhook, EventCode, Plan, Period, Subscription, Usage, Discount, SubscriptionStatus
from subgatekit.utils import get_current_datetime


class Event(BaseModel):
    type: str
    event_code: EventCode
    occurred_at: AwareDatetime
    payload: dict


HOST = "localhost"
PORT = 5678

client = get_client()
app = FastAPI()


def convert(value):
    try:
        value = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        pass

    if isinstance(value, datetime):
        value = value.replace(second=0, microsecond=0)

    if isinstance(value, dict):
        value = {k: convert(v) for k, v in value.items()}
    return value


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
        for field, expected in kwargs.items():
            real = convert(self._events.get(code).payload[field])
            expected = convert(expected)
            assert real == expected

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
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionCreated, 1, subscriber_id=self.subscription.subscriber_id)

    async def add_usage(self):
        self.subscription.usages.add(
            Usage("First", "first", "GB", 100, Period.Monthly)
        )
        client.subscription_client().update(self.subscription)

        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionUsageAdded, 1, title="First")
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"usages.first": "action:added"})
        event_store.clear()

    async def update_usage(self):
        self.subscription.usages.get("first").increase(100)
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionUsageUpdated, 1, delta=100)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"usages.first": "action:updated"})
        event_store.clear()

    async def remove_usage(self):
        self.subscription.usages.remove("first")
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionUsageRemoved, 1, title="First")
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"usages.first": "action:removed"})
        event_store.clear()

    async def add_discount(self):
        self.subscription.discounts.add(
            Discount("Black friday", "black", 0.2, get_current_datetime())
        )
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionDiscountAdded, 1, title="Black friday")
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"discounts.black": "action:added"})
        event_store.clear()

    async def update_discount(self):
        self.subscription.discounts.get("black").size = 0.5
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionDiscountUpdated, 1, changes={"size": 0.5})
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"discounts.black": "action:updated"})
        event_store.clear()

    async def remove_discount(self):
        self.subscription.discounts.remove("black")
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionDiscountRemoved, 1, title="Black friday")
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"discounts.black": "action:removed"})
        event_store.clear()

    async def pause_subscription(self):
        self.subscription.pause()
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionPaused, 1)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={
            "status": SubscriptionStatus.Paused,
            "paused_from": self.subscription.paused_from,
        })
        event_store.clear()

    async def resume_subscription(self):
        self.subscription.resume()
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionResumed, 1)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={
            "status": SubscriptionStatus.Active,
            "paused_from": None,
        })
        event_store.clear()

    async def renew_subscription(self):
        from_date = get_current_datetime() + timedelta(days=2)
        self.subscription.renew(from_date=from_date)
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionRenewed, 1)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={
            "billing_info.last_billing": from_date,
        })
        event_store.clear()

    async def expire_subscription(self):
        self.subscription.expire()
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionExpired, 1)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={
            "status": SubscriptionStatus.Expired,
        })
        event_store.clear()

    async def update_subscription(self):
        self.subscription.plan_info.title = "Updated"
        client.subscription_client().update(self.subscription)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionUpdated, 1, changes={"plan_info.title": "Updated"})
        event_store.clear()

    async def delete_subscription(self):
        client.subscription_client().delete_by_id(self.subscription.id)
        await asyncio.sleep(0.1)
        event_store.check(EventCode.SubscriptionDeleted, 1, id=str(self.subscription.id))
        event_store.clear()

    @pytest.mark.asyncio
    async def test_check_events(self):
        await self.create()
        await self.add_usage()
        await self.update_usage()
        await self.remove_usage()
        await self.add_discount()
        await self.update_discount()
        await self.remove_discount()
        await self.pause_subscription()
        await self.resume_subscription()
        await self.renew_subscription()
        await self.expire_subscription()
        await self.update_subscription()
        await self.delete_subscription()
