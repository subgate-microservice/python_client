import pytest

from tests.client import get_client

client = get_client()


@pytest.fixture()
def fake_item():
    from subgatekit import EventCode

    webhook = client.webhook_client().create_webhook(
        event_code=EventCode.SubscriptionCreated,
        target_url="http://my-site.com"
    )
    yield webhook


"""
Create
"""


def test_create_webhook():
    # From python
    from subgatekit import EventCode

    webhook = client.webhook_client().create_webhook(
        event_code=EventCode.SubscriptionCreated,
        target_url="http://my-site.com"
    )


"""
Retrieve
"""


def test_get_webhook_by_id(fake_item):
    # From python
    from uuid import UUID

    target_id: UUID = fake_item.id
    webhook = client.webhook_client().get_webhook_by_id(target_id)


def test_get_all_webhooks():
    # From python
    webhooks = client.webhook_client().get_all_webhooks()


"""
Update
"""


def test_update_webhook():
    # From python
    from subgatekit import EventCode

    webhook = client.webhook_client().create_webhook(
        event_code=EventCode.SubscriptionCreated,
        target_url="http://my-site.com"
    )

    # Update
    webhook.target_url = "http://updated-site.com"
    webhook.event_code = EventCode.SubscriptionExpired
    client.webhook_client().update_webhook(webhook)

    # Check
    webhook = client.webhook_client().get_webhook_by_id(webhook.id)
    assert webhook.target_url == "http://updated-site.com"
    assert webhook.event_code == EventCode.SubscriptionExpired


"""
Delete
"""


def test_delete_webhook_by_id(fake_item):
    # From python
    from uuid import UUID

    target_id: UUID = fake_item.id
    client.webhook_client().delete_webhook_by_id(target_id)


def test_delete_all_webhooks():
    # From python
    client.webhook_client().delete_all_webhooks()
