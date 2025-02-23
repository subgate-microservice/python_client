from snippets.tests.client import get_client
from snippets.tests.fakes import fake_webhook

client = get_client()


def test_create_webhook():
    from subgatekit import EventCode, Webhook

    webhook = Webhook(
        event_code=EventCode.SubCreated,
        target_url="http://my-site.com",
    )
    client.webhook_client().create(webhook)


def test_get_webhook_by_id(fake_webhook):
    from uuid import UUID

    target_id: UUID = fake_webhook.id
    webhook = client.webhook_client().get_by_id(target_id)


def test_get_all_webhooks():
    webhooks = client.webhook_client().get_all()


def test_update_webhook(fake_webhook):
    from uuid import UUID
    from subgatekit import EventCode

    target_id: UUID = fake_webhook.id
    webhook = client.webhook_client().get_by_id(target_id)

    webhook.target_url = "http://updated-site.com"
    webhook.event_code = EventCode.SubExpired
    client.webhook_client().update(webhook)


def test_delete_webhook_by_id(fake_webhook):
    from uuid import UUID

    target_id: UUID = fake_webhook.id
    client.webhook_client().delete_by_id(target_id)


def test_delete_all_webhooks():
    client.webhook_client().delete_all()
