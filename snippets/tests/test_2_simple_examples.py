from snippets.tests.client import get_client

client = get_client()


def test_create_plan():
    from subgatekit import Period, Plan

    plan = Plan(
        title='Business',
        price=100,
        currency='USD',
        billing_cycle=Period.Monthly,
    )
    client.plan_client().create(plan)


def test_create_subscription():
    # From python
    from subgatekit import Period

    plan = client.plan_client().create_plan("Business", 100, "USD", Period.Monthly)

    subscription = client.subscription_client().create_subscription(
        subscriber_id='AnySubscriberID',
        plan=plan,
    )

    assert subscription.plan.id == plan.id
