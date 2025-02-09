from datetime import datetime

from subgatekit.domain.events import EventCode
from subgatekit.domain.plan import ID


class Webhook:
    def __init__(
            self,
            id: ID,
            event_code: EventCode,
            target_url: str,
            created_at: datetime,
            updated_at: datetime
    ):
        self.id = id
        self.event_code = event_code
        self.target_url = target_url
        self.created_at = created_at
        self.updated_at = updated_at


class WebhookCreate:
    def __init__(
            self,
            event_code: EventCode,
            target_url: str,

    ):
        self.event_code = event_code
        self.target_url = target_url


class WebhookUpdate:
    def __init__(
            self,
            id: ID,
            event_code: EventCode,
            target_url: str,
            created_at: datetime,
    ):
        self.id = id
        self.event_code = event_code
        self.target_url = target_url
        self.created_at = created_at

    @classmethod
    def from_webhook(cls, data: Webhook):
        return cls(id=data.id, event_code=data.event_code, target_url=data.target_url, created_at=data.created_at)
