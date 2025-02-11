from subgatekit.utils import get_current_datetime
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.plan import Plan
from subgatekit.v2_0.domain.subscription import Subscription
from subgatekit.v2_0.domain.usage import Usage


def test_usage_management():
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "AnyID")

    sub.usages.add(
        Usage("ApiCall", "api_call", "request", 1_000, Period.Monthly)
    )

    sub.discounts.add(
        Discount("Black friday", "black", 0.2, get_current_datetime(), "")
    )

    sub.usages.get_all()

    sub.usages.get("api_call").increase(50)
    assert sub.usages.get("api_call").used_units == 50

