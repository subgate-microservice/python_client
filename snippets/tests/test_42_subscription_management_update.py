from snippets.tests.client import get_client
from snippets.tests.fakes import fake_sub, fake_sub_with_usages

client = get_client()


def test_pause_subscription(fake_sub):
    from uuid import UUID

    target_id: UUID = fake_sub.id

    subscription = client.subscription_client().get_by_id(target_id)
    subscription.pause()

    client.subscription_client().update(subscription)


def test_resume_subscription(fake_sub):
    from uuid import UUID

    target_id: UUID = fake_sub.id

    subscription = client.subscription_client().get_by_id(target_id)
    subscription.resume()

    client.subscription_client().update(subscription)


def test_renew_subscription(fake_sub):
    from uuid import UUID

    target_id: UUID = fake_sub.id

    subscription = client.subscription_client().get_by_id(target_id)
    subscription.renew(from_date=None)

    client.subscription_client().update(subscription)


def test_adjust_usage(fake_sub_with_usages):
    from uuid import UUID

    target_id: UUID = fake_sub_with_usages.id
    subscription = client.subscription_client().get_by_id(target_id)

    # Check usage is zero
    assert subscription.usages.get('api_call').used_units == 0

    # Increasing and decreasing usages
    subscription.usages.get('api_call').increase(20)
    subscription.usages.get('api_call').increase(80)
    subscription.usages.get('api_call').increase(-10)
    client.subscription_client().update(subscription)

    # Check result
    updated = client.subscription_client().get_by_id(subscription.id)
    assert updated.usages.get('api_call').used_units == 90


def test_update_usages(fake_sub_with_usages):
    from uuid import UUID
    from subgatekit import Usage, Period

    target_id: UUID = fake_sub_with_usages.id
    subscription = client.subscription_client().get_by_id(target_id)

    # Update
    subscription = client.subscription_client().get_by_id(subscription.id)
    subscription.usages.update(
        Usage(
            title='Updated title',
            code='api_call',
            unit='request',
            used_units=30,
            available_units=10_000,
            renew_cycle=Period.Monthly,
        )
    )
    client.subscription_client().update(subscription)


def test_add_usages(fake_sub):
    from uuid import UUID

    from subgatekit import Usage, Period

    target_id: UUID = fake_sub.id
    subscription = client.subscription_client().get_by_id(target_id)
    subscription.usages.add(
        Usage(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=1_000,
            used_units=0,
            renew_cycle=Period.Daily,
        )
    )

    client.subscription_client().update(subscription)


def test_remove_usages(fake_sub_with_usages):
    from uuid import UUID

    target_id: UUID = fake_sub_with_usages.id
    subscription = client.subscription_client().get_by_id(target_id)

    subscription.usages.remove('api_call')
    client.subscription_client().update(subscription)


def test_full_update_subscription(fake_sub):
    import datetime
    from uuid import UUID
    from subgatekit import Period

    target_id: UUID = fake_sub.id
    subscription = client.subscription_client().get_by_id(target_id)

    subscription.billing_info.last_billing = datetime.datetime.now(datetime.UTC)
    subscription.billing_info.billing_cycle = Period.Semiannual
    subscription.plan_info.title = 'Updated title'

    client.subscription_client().update(subscription)
