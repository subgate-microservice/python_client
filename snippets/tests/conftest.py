import pytest

from snippets.tests.client import client


@pytest.fixture(autouse=True)
def clear_all():
    # client.subscription_client().delete_selected_subscriptions()
    # client.plan_client().delete_selected_plans()
    # client.webhook_client().delete_all_webhooks()
    yield
