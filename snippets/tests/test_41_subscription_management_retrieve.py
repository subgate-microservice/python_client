from snippets.tests.client import get_client
from snippets.tests.fakes import fake_sub

client = get_client()


def test_get_current_subscription(fake_sub):
    # Returns None if there is no active subscription
    sub = client.subscription_client().get_current_subscription('AnySubscriberID')


def test_get_subscription_by_id(fake_sub):
    from uuid import UUID

    target_id: UUID = fake_sub.id
    subscription = client.subscription_client().get_by_id(target_id)


def test_get_all_subscriptions():
    subscriptions = client.subscription_client().get_selected(
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )


def test_get_selected_subscriptions():
    subscriptions = client.subscription_client().get_selected(
        ids=None,  # UUID | Iterable[UUID]
        subscriber_ids=None,  # str | Iterable[str]
        statuses=None,  # SubscriptionStatus | Iterable[SubscriptionStatus]
        expiration_date_lt=None,  # datetime with tz_info
        expiration_date_lte=None,  # datetime with tz_info
        expiration_date_gt=None,  # datetime with tz_info
        expiration_date_gte=None,  # datetime with tz_info
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )
