import pytest

from tests.client import get_client

client = get_client()


@pytest.fixture()
def fake_plan():
    plan = client.plan_client().create_plan("Personal", 100, "USD")
    yield plan


"""
Create
"""


def test_create_simple_plan():
    # From python
    from subgatekit import Period

    personal_plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        description='This is a personal plan description',
        level=10,
        features='Any features you want to describe',
    )

    business_plan = client.plan_client().create_plan(
        title='Business',
        price=200,
        currency='USD',
        billing_cycle=Period.Annual,
        description='This is a business plan description',
        level=20,
        features='Any features you want to describe',
    )

    assert personal_plan.title == 'Personal'
    assert business_plan.title == 'Business'


def test_create_plan_with_usage_rates():
    # From python
    from subgatekit import UsageRate, Period

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

    plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        usage_rates=usage_rates,
    )

    assert plan.title == 'Personal'


def test_create_plan_with_discounts():
    # From python
    import datetime
    from subgatekit import Discount, Period

    discounts = [
        Discount(
            title='Black friday',
            code='black',
            size=0.3,  # Percentage (min=0, max=1)
            valid_until=datetime.datetime.now(tz=datetime.UTC),
        ),
    ]

    plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        discounts=discounts,
    )

    assert len(plan.discounts) == len(discounts)


def test_create_plan_with_custom_fields():
    # From python
    from subgatekit import Period

    plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
        fields={
            'my_specific_field': 1,
            'any_list_data': ['Hello', 'World!'],
            'any_dict_data': {
                'property1': 1,
                'property2': 2,
            },
        }
    )

    assert len(plan.fields) == 3


"""
Retrieve
"""


def test_get_plan_by_id(fake_plan):
    # From python
    from uuid import UUID

    target_id: UUID = fake_plan.id
    plan = client.plan_client().get_plan_by_id(target_id)

    assert plan.id == target_id


def test_get_all_plans():
    # From python
    plans = client.plan_client().get_selected_plans()


def test_get_selected_plans():
    # From python
    plans = client.plan_client().get_selected_plans(
        ids=None,  # Iterable[UUID]
        order_by=[('created_at', 1)],
        skip=0,
        limit=100,
    )


"""
Update
"""


def test_update_plan():
    # From python
    from subgatekit import Period

    plan = client.plan_client().create_plan(
        title='Personal',
        price=30,
        currency='USD',
        billing_cycle=Period.Quarterly,
    )

    plan.price = 100
    plan.currency = 'EUR'
    client.plan_client().update_plan(plan)


def test_delete_plan_by_id(fake_plan):
    # From python
    from uuid import UUID

    target_id: UUID = fake_plan.id
    client.plan_client().delete_plan_by_id(target_id)


def test_delete_all_plans():
    # From python
    client.plan_client().delete_selected_plans()


def test_delete_selected_plans():
    # From python
    client.plan_client().delete_selected_plans(
        ids=None,  # Iterable[UUID]
    )
