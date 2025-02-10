from subgatekit.utils import get_current_datetime
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.plan import Plan
from subgatekit.v2_0.domain.subscription import Subscription
from subgatekit.v2_0.domain.usage import Usage


def test_usage_management():
    plan = Plan("Business", 100, "USD", Period.Monthly)
    sub = Subscription.from_plan(plan, "AnyID")

    sub.add_usage(
        Usage("ApiCall", "api_call", "request", 1_000, Period.Monthly)
    )

    sub.increase_usage("api_call", 33)

    sub.add_discount(
        Discount("Black friday", "black", 0.2, get_current_datetime(), "")
    )

