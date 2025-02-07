from datetime import datetime
from typing import Optional

from subgate_client.domain.enums import SubscriptionStatus
from subgate_client.domain.plan import ID, Plan
from subgate_client.domain.usage import Usage


class Subscription:
    def __init__(
            self,
            id: ID,
            subscriber_id: str,
            plan: Plan,
            status: SubscriptionStatus,
            created_at: datetime,
            updated_at: datetime,
            last_billing: datetime,
            paused_from: Optional[datetime],
            autorenew: bool,
            usages: list[Usage],
            fields: dict
    ):
        self.id = id
        self.subscriber_id = subscriber_id
        self.plan = plan
        self.status = status
        self.paused_from = paused_from
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_billing = last_billing
        self.autorenew = autorenew
        self.usages = usages
        self.fields = fields

    @property
    def days_left(self) -> int:
        raise NotImplemented

    def get_usage(self, code: str) -> Usage:
        for usage in self.usages:
            if usage.code == code:
                return usage
        raise KeyError(code)


class SubscriptionCreate:
    def __init__(
            self,
            plan: Plan,
            subscriber_id: str,
            status: SubscriptionStatus = SubscriptionStatus.Active,
            usages: list[Usage] = None,
            paused_from: Optional[datetime] = None,
            autorenew: bool = False,
            fields: dict = None
    ):
        self.plan = plan
        self.subscriber_id = subscriber_id
        self.status = status
        self.usages = usages if usages else [Usage.from_usage_rate(x) for x in plan.usage_rates]
        self.paused_from = paused_from
        self.autorenew = autorenew
        self.fields = fields if fields else {}
