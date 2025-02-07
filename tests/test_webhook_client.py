import datetime

import pytest

from subgatekit.domain.events import EventCode
from subgatekit.domain.plan import ID
from subgatekit.domain.webhook import Webhook
from tests.conftest import webhooks, client, wrapper


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_one(self, client):
        real: Webhook = await wrapper(
            client.webhook_client().create_webhook(EventCode.SubscriptionCreated, "https://my-site.com"))
        assert real.event_code == EventCode.SubscriptionCreated
        assert real.target_url == "https://my-site.com"

    @pytest.mark.asyncio
    async def test_create_webhooks_with_all_event_codes(self, client):
        for code in EventCode:
            hook = await wrapper(client.webhook_client().create_webhook(code, "https://my-site.com"))
            real = await wrapper(client.webhook_client().get_webhook_by_id(hook.id))
            assert real.id == hook.id
            assert real.target_url == hook.target_url


class TestGet:
    @pytest.mark.asyncio
    async def test_get_one_by_id(self, webhooks, client):
        target = webhooks[3]
        real = await wrapper(client.webhook_client().get_webhook_by_id(target.id))
        assert real.id == target.id
        assert real.event_code == target.event_code

    @pytest.mark.asyncio
    async def test_get_all(self, webhooks, client):
        real = await wrapper(client.webhook_client().get_all_webhooks())
        assert len(real) == len(webhooks)


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_all(self, webhooks, client):
        real = await wrapper(client.webhook_client().get_all_webhooks())
        assert len(real) == len(webhooks)
        assert len(real) > 0

        await wrapper(client.webhook_client().delete_all_webhooks())

        real = await wrapper(client.webhook_client().get_all_webhooks())
        assert len(real) == 0

    @pytest.mark.asyncio
    async def test_delete_one_by_id(self, webhooks, client):
        target = webhooks[3]

        await wrapper(client.webhook_client().delete_webhook_by_id(target.id))

        hooks = await wrapper(client.webhook_client().get_all_webhooks())
        assert target.id not in set(hook.id for hook in hooks)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_one(self, webhooks, client):
        target = webhooks[3]
        target.target_url = "https://updated-site.com"

        await wrapper(client.webhook_client().update_webhook(target))

        real = await wrapper(client.webhook_client().get_webhook_by_id(target.id))
        assert real.target_url == target.target_url


class TestTypes:
    @staticmethod
    def _check_types(data: Webhook):
        assert isinstance(data.event_code, str)
        assert isinstance(data.target_url, str)
        assert isinstance(data.id, ID)
        assert isinstance(data.created_at, datetime.datetime)
        assert isinstance(data.updated_at, datetime.datetime)
        assert data.created_at.tzinfo is not None
        assert data.updated_at.tzinfo is not None

    @pytest.mark.asyncio
    async def test_types_in_create(self, client):
        real: Webhook = await wrapper(
            client.webhook_client().create_webhook(EventCode.SubscriptionCreated, "https://my-site.com")
        )
        self._check_types(real)

    @pytest.mark.asyncio
    async def test_types_in_retrieve(self, client, webhooks):
        real: Webhook = await wrapper(client.webhook_client().get_webhook_by_id(webhooks[2].id))
        self._check_types(real)

        all_webhooks: list[Webhook] = await wrapper(client.webhook_client().get_all_webhooks())
        assert len(all_webhooks) > 0
        for real in all_webhooks:
            self._check_types(real)
