from snippets.tests.client import get_client

client = get_client()


def test_create_subscription():
    from subgatekit import Period, Plan, Subscription

    personal_plan = Plan('Personal', 30, 'USD', Period.Quarterly)
    subscription = Subscription.from_plan(personal_plan, 'AnySubscriberID')
    client.subscription_client().create(subscription)

    created = client.subscription_client().get_by_id(subscription.id)


def test_create_usage_based_subscription():
    import datetime
    from subgatekit import Period, UsageRate, Plan, Subscription, Usage

    # Create from plan
    rates = [
        UsageRate(
            title='Api Call',
            code='api_call',
            unit='call',
            available_units=1_000,
            renew_cycle=Period.Daily,
        ),
    ]
    personal_plan = Plan('Personal', 30, 'USD', Period.Quarterly, usage_rates=rates)
    subscription = Subscription.from_plan(personal_plan, 'AnySubscriberID')
    client.subscription_client().create(subscription)

    # Or directly usage management
    plan_without_usages = Plan('Simple', 50, 'USD', Period.Monthly)
    subscription = Subscription.from_plan(plan_without_usages, 'AnotherSubscriber')
    subscription.usages.add(
        Usage(
            title='Storage Usage',
            code='storage_usage',
            unit='GB',
            available_units=100,
            renew_cycle=Period.Lifetime,
            used_units=0,
            last_renew=datetime.datetime.now(datetime.UTC),
        )
    )
    client.subscription_client().create(subscription)


def test_create_subscription_with_specific_plan():
    import datetime

    from subgatekit import Period, Subscription, PlanInfo, BillingInfo

    plan_info = PlanInfo(
        title='Specific plan',
        description='This PlanInfo was created for the next subscription only',
        level=50,
    )
    billing_info = BillingInfo(
        price=100,
        currency='USD',
        billing_cycle=Period.Annual,
        last_billing=datetime.datetime.now(datetime.UTC),
    )

    subscription = Subscription(
        subscriber_id='AnySubscriberID',
        plan_info=plan_info,
        billing_info=billing_info,
    )

    client.subscription_client().create(subscription)


def test_create_subscription_with_custom_fields():
    from subgatekit import Period, Plan, Subscription

    plan = Plan('Business', 100, 'USD', Period.Annual)

    fields = {
        'key1': 'value1',
        'key2': {
            'inner_key1': 22,
            'inner_key2': 'Hello world!',
        },
    }

    subscription = Subscription.from_plan(plan, 'AnySubscriberID', fields=fields)
    client.subscription_client().create(subscription)
