import pytest

from snippets.tests.client import get_client

client = get_client()


@pytest.fixture()
def fake_plan():
    plan = client.plan_client().create_plan("Personal", 100, "USD")
    yield plan


"""
Create
"""


def test_create_simple_plan():
    from subgatekit import Period, Plan

    personal_plan = Plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        description='This is a personal plan description',
        level=10,
        features='Any features you want to describe',
    )

    business_plan = Plan(
        title='Business',
        price=200,
        currency='USD',
        billing_cycle=Period.Annual,
        description='This is a business plan description',
        level=20,
        features='Any features you want to describe',
    )

    client.plan_client().create(personal_plan)
    client.plan_client().create(business_plan)


def test_create_plan_with_usage_rates():
    from subgatekit import UsageRate, Period, Plan

    usage_rates = [
        UsageRate(
            title='Storage',
            code='storage',
            unit='GB',
            available_units=100,
            renew_cycle=Period.Lifetime,
        ),
        UsageRate(
            title='API Calls',
            code='api_calls',
            unit='CALL',
            available_units=10_000,
            renew_cycle=Period.Daily,
        ),
    ]

    plan = Plan('Personal', 30, 'USD', Period.Quarterly, usage_rates=usage_rates)
    client.plan_client().create(plan)


def test_create_plan_with_discounts():
    import datetime
    from subgatekit import Discount, Period, Plan

    discounts = [
        Discount(
            title='Black friday',
            code='black',
            size=0.3,  # Percentage (min=0, max=1)
            valid_until=datetime.datetime.now(tz=datetime.UTC),
        ),
    ]

    plan = Plan('Personal', 30, 'USD', Period.Quarterly, discounts=discounts)
    client.plan_client().create(plan)


def test_create_plan_with_custom_fields():
    from subgatekit import Period, Plan

    fields = {
        'my_specific_field': 1,
        'any_list_data': ['Hello', 'World!'],
        'any_dict_data': {
            'property1': 1,
            'property2': 2,
        },
    }

    plan = Plan('Personal', 30, 'USD', Period.Quarterly, fields=fields)
    client.plan_client().create(plan)


"""
Retrieve
"""


def test_get_plan_by_id(fake_plan):
    from uuid import UUID

    target_id: UUID = fake_plan.id
    plan = client.plan_client().get_by_id(target_id)


def test_get_all_plans():
    plans = client.plan_client().get_selected(
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )


def test_get_selected_plans():
    plans = client.plan_client().get_selected_plans(
        ids=None,  # UUID | Iterable[UUID]
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )


"""
Update
"""


def test_update_plan():
    from subgatekit import Period, Plan

    # Create
    plan = Plan('Personal', 30, 'USD', Period.Quarterly)
    client.plan_client().create(plan)

    # Update
    plan.price = 100
    plan.currency = 'EUR'
    client.plan_client().update_plan(plan)


def test_delete_plan_by_id(fake_plan):
    from uuid import UUID

    target_id: UUID = fake_plan.id
    client.plan_client().delete_by_id(target_id)


def test_delete_all_plans():
    client.plan_client().delete_selected()


def test_delete_selected_plans():
    client.plan_client().delete_selected_plans(
        ids=None,  # UUID | Iterable[UUID]
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )
