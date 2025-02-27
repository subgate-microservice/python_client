from snippets.tests.client import get_client
from snippets.tests.fakes import fake_sub

client = get_client()


def test_delete_subscription_by_id(fake_sub):
    from uuid import UUID

    target_id: UUID = fake_sub.id
    client.subscription_client().delete_by_id(target_id)


def test_delete_all_subscriptions():
    client.subscription_client().delete_selected()


def test_delete_selected_subscriptions():
    # From python
    client.subscription_client().delete_selected(
        ids=None,  # UUID | Iterable[UUID]
        subscriber_ids=None,  # str | Iterable[str]
        statuses=None,  # SubscriptionStatus | Iterable[SubscriptionStatus]
        expiration_date_gt=None,  # datetime with tz_info
        expiration_date_gte=None,  # datetime with tz_info
        expiration_date_lt=None,  # datetime with tz_info
        expiration_date_lte=None,  # datetime with tz_info
    )
