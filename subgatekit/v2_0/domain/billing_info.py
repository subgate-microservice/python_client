import datetime
from typing import Self

from subgatekit.utils import Number, get_current_datetime
from subgatekit.v2_0.domain.enums import Period
from subgatekit.v2_0.domain.plan import Plan


class BillingInfo:
    def __init__(
            self,
            price: Number,
            currency: str,
            billing_cycle: Period,
            last_billing: datetime,
    ):
        self.billing_cycle = billing_cycle
        self.last_billing = last_billing
        self.price = price
        self.currency = currency

    @classmethod
    def from_plan(cls, plan: Plan) -> Self:
        return cls(plan.price, plan.currency, plan.billing_cycle, get_current_datetime())
