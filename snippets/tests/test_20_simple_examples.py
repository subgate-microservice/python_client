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
    from subgatekit import Period, Plan, Subscription

    plan = Plan('Business', 100, 'USD', Period.Monthly)
    sub = Subscription.from_plan(plan, 'AnySubscriberID')

    client.subscription_client().create(sub)
