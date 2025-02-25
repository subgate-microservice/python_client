import pytest

from subgatekit import Webhook, EventCode
from subgatekit.exceptions import ItemNotExist
from tests.conftest import client, wrapper, sync_client
from tests.fakes import simple_webhook


@pytest.fixture()
def webhooks(sync_client):
    hooks = []
    for i in range(10):
        hook = Webhook(event_code=EventCode.PlanCreated, target_url=f"http://my-site-{i}.com")
        sync_client.webhook_client().create(hook)
        hooks.append(hook)
    yield hooks


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_webhook(self, client):
        hook = Webhook(event_code=EventCode.PlanCreated, target_url="http://my-site.com")
        await wrapper(client.webhook_client().create(hook))


class TestGet:
    @pytest.mark.asyncio
    async def test_get_webhook_by_id(self, simple_webhook, client):
        real = await wrapper(client.webhook_client().get_by_id(simple_webhook.id))
        assert real.id == simple_webhook.id

    @pytest.mark.asyncio
    async def test_get_all_webhooks(self, client, webhooks):
        real = await wrapper(client.webhook_client().get_all())
        assert len(real) == len(webhooks)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_webhook(self, client, simple_webhook):
        simple_webhook.target_url = "http://updated-site.com"
        await wrapper(client.webhook_client().update(simple_webhook))

        # Check
        real = await wrapper(client.webhook_client().get_by_id(simple_webhook.id))
        assert real.target_url == simple_webhook.target_url


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_by_id(self, client, simple_webhook):
        await wrapper(client.webhook_client().delete_by_id(simple_webhook.id))

        # Check
        with pytest.raises(ItemNotExist):
            _real = await wrapper(client.webhook_client().get_by_id(simple_webhook.id))

    @pytest.mark.asyncio
    async def test_delete_all(self, webhooks, client):
        await wrapper(client.webhook_client().delete_all())

        # Check
        real = await wrapper(client.webhook_client().get_all())
        assert len(real) == 0
