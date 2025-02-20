import pytest

from tests.client import get_client

client = get_client()


@pytest.fixture(autouse=True)
def fake_item():
    from subgatekit import Period, Plan
    plan = Plan("Business", 100, "USD", billing_cycle=Period.Monthly)
    subscription = client.subscription_client().create_subscription('AnySubscriberID', plan)
    yield subscription


"""
Create
"""


def test_create_subscription():
    # From python
    from subgatekit import Period

    personal_plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
    )

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=personal_plan,
    )

    assert subscription.subscriber_id == 'AnySubscriberID'


def test_create_usage_based_subscription():
    # From  python
    from subgatekit import Period, UsageRate

    usage_rates = [
        UsageRate(
            title='Api Call',
            code='api_call',
            unit='call',
            available_units=1_000,
            renew_cycle=Period.Daily,
        ),
    ]
    personal_plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        usage_rates=usage_rates,
    )

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=personal_plan,
    )

    assert subscription.subscriber_id == 'AnySubscriberID'


def test_create_subscription_with_specific_plan():
    # From  python
    from uuid import uuid4

    from subgatekit import Plan, Period

    # The plan is not saved anywhere except within the associated subscription
    individual_plan = Plan(
        id=uuid4(),
        title='SuperIndividualPlan',
        price=0,
        currency='USD',
        billing_cycle=Period.Lifetime,
    )

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=individual_plan,
    )

    assert subscription.subscriber_id == 'AnySubscriberID'


def test_create_subscription_with_custom_fields():
    # From  python
    from subgatekit import Period

    plan = client.plan_client().create_plan(
        title='Business',
        price=100,
        currency='USD',
        billing_cycle=Period.Annual,
    )

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=plan,
        fields={
            'key1': 'value1',
            'key2': {
                'inner_key1': 22,
                'inner_key2': 'Hello world!',
            },
        }
    )

    assert len(subscription.fields) == 2


"""
Retrieve
"""


def test_get_current_subscription(fake_item):
    # From python
    # Returns None if there is no active subscription
    subscription = client.subscription_client().get_current_subscription(
        'AnySubscriberID'
    )
    assert subscription.id == fake_item.id


def test_get_subscription_by_id(fake_item):
    # From python
    from uuid import UUID

    target_id: UUID = fake_item.id
    subscription = client.subscription_client().get_subscription_by_id(target_id)


def test_get_all_subscriptions():
    # From python
    subscriptions = client.subscription_client().get_selected_subscriptions()


def test_get_selected_subscriptions():
    # From python
    subscriptions = client.subscription_client().get_selected_subscriptions(
        ids=None,  # UUID | Iterable[UUID]
        subscriber_ids=None,  # UUID | Iterable[UUID]
        statuses=None,  # SubscriptionStatus | Iterable[SubscriptionStatus]
        expiration_date_lt=None,  # datetime with tz_info
        expiration_date_lte=None,  # datetime with tz_info
        expiration_date_gt=None,  # datetime with tz_info
        expiration_date_gte=None,  # datetime with tz_info
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )


"""
Update
"""


def test_pause_subscription(fake_item):
    # From python
    from uuid import UUID
    from datetime import datetime, UTC

    from subgatekit import SubscriptionStatus

    target_id: UUID = fake_item.id
    client.subscription_client().pause_subscription(target_id)

    subscription = client.subscription_client().get_subscription_by_id(target_id)
    assert subscription.status == SubscriptionStatus.Paused
    assert subscription.paused_from.date() == datetime.now(UTC).date()


def test_resume_subscription(fake_item):
    # From python
    from uuid import UUID

    from subgatekit import SubscriptionStatus

    target_id: UUID = fake_item.id
    client.subscription_client().resume_subscription(target_id)

    subscription = client.subscription_client().get_subscription_by_id(target_id)
    assert subscription.status == SubscriptionStatus.Active
    assert subscription.paused_from is None


def test_renew_subscription(fake_item):
    # From python
    from uuid import UUID
    from datetime import datetime, UTC

    target_id: UUID = fake_item.id
    client.subscription_client().renew_subscription(target_id, from_date=None)

    subscription = client.subscription_client().get_subscription_by_id(target_id)
    assert subscription.last_billing.date() == datetime.now(UTC).date()


def test_adjust_usage():
    # From python
    from subgatekit import Plan, UsageRate, Period

    # Create a subscription with Usages
    usage_rates = [
        UsageRate(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=10_000,
            renew_cycle=Period.Monthly,
        )
    ]
    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=Plan('Business', 100, 'USD', Period.Annual, usage_rates=usage_rates),
    )

    # Check that used_units is zero
    assert subscription.get_usage('api_call').used_units == 0

    # Increasing and decreasing usages
    client.subscription_client().adjust_usage(subscription.id, 'api_call', 20)
    client.subscription_client().adjust_usage(subscription.id, 'api_call', 80)
    client.subscription_client().adjust_usage(subscription.id, 'api_call', -10)

    # Check result
    updated = client.subscription_client().get_subscription_by_id(subscription.id)
    assert updated.get_usage('api_call').used_units == 90


def test_update_usages():
    # From python
    from subgatekit import Plan, UsageRate, Usage, Period

    # Create a subscription with Usages
    rates = [
        UsageRate(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=10_000,
            renew_cycle=Period.Monthly,
        )
    ]
    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=Plan('Business', 100, 'USD', Period.Annual, usage_rates=rates),
    )

    # Update
    updated_usages = [
        Usage(
            title='Updated title',
            code='api_call',
            unit='request',
            used_units=30,
            available_units=10_000,
            renew_cycle=Period.Monthly,
        ),
    ]
    client.subscription_client().update_usages(subscription.id, updated_usages)

    # Checks
    subscription = client.subscription_client().get_subscription_by_id(subscription.id)
    assert subscription.get_usage('api_call').title == 'Updated title'
    assert subscription.get_usage('api_call').used_units == 30
    assert subscription.plan.get_usage_rate('api_call').title == 'Updated title'


def test_add_usages(fake_item):
    # From python
    from uuid import UUID

    from subgatekit import Usage, Period

    new_usages = [
        Usage(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=1_000,
            used_units=0,
            renew_cycle=Period.Daily,
        ),
    ]

    subscription_id: UUID = fake_item.id
    client.subscription_client().add_usages(subscription_id, new_usages)


def test_remove_usages():
    # From python
    from subgatekit import Plan, UsageRate, Period

    # Create a subscription with Usages
    usage_rates = [
        UsageRate(
            title='API Call',
            code='api_call',
            unit='request',
            available_units=10_000,
            renew_cycle=Period.Monthly,
        )
    ]
    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=Plan('Business', 100, 'USD', Period.Annual, usage_rates=usage_rates),
    )

    # Remove
    client.subscription_client().remove_usages(subscription.id, 'api_call')


def test_update_subscription_plan():
    # From python
    from subgatekit import Plan, Period

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=Plan('Personal', 100, 'USD', Period.Annual),
    )

    # Update plan
    updated_plan = Plan('Business', 500, 'USD', Period.Annual)
    client.subscription_client().update_subscription_plan(subscription.id, updated_plan)

    # Check results
    subscription = client.subscription_client().get_subscription_by_id(subscription.id)
    assert subscription.plan.title == 'Business'
    assert subscription.plan.price == 500


def test_full_update_subscription(fake_item):
    # From python
    import datetime
    from uuid import UUID

    from subgatekit import Plan, Period

    target_id: UUID = fake_item.id
    target = client.subscription_client().get_subscription_by_id(target_id)

    target.last_billing = datetime.datetime.now(datetime.UTC)
    target.plan = Plan(
        title='Custom plan',
        price=50,
        currency='USD',
        billing_cycle=Period.Monthly,
    )

    client.subscription_client().update_subscription(target)


"""
Delete
"""


def test_delete_subscription_by_id(fake_item):
    # From python
    from uuid import UUID

    target_id: UUID = fake_item.id
    client.subscription_client().delete_subscription_by_id(target_id)


def test_delete_all_subscriptions():
    # From python
    client.subscription_client().delete_selected_subscriptions()


def test_delete_selected_subscriptions():
    # From python
    client.subscription_client().delete_selected_subscriptions(
        ids=None,  # UUID | Iterable[UUID]
        subscriber_ids=None,  # str | Iterable[str]
        statuses=None,  # SubscriptionStatus | Iterable[SubscriptionStatus]
        expiration_date_gt=None,  # datetime with tz_info
        expiration_date_gte=None,  # datetime with tz_info
        expiration_date_lt=None,  # datetime with tz_info
        expiration_date_lte=None,  # datetime with tz_info
    )
