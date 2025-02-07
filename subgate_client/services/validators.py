import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from types import NoneType
from typing import Any, Type, Union, Iterable, Optional

from subgate_client.client.exceptions import ValidationError, MultipleError
from subgate_client.domain.cycle import Cycle
from subgate_client.domain.enums import Period, SubscriptionStatus
from subgate_client.domain.discount import Discount
from subgate_client.domain.events import EventCode
from subgate_client.domain.plan import Plan, ID, PlanCreate
from subgate_client.domain.subscription import Subscription, SubscriptionCreate
from subgate_client.domain.usage import UsageRate, Usage
from subgate_client.domain.webhook import Webhook, WebhookCreate, WebhookUpdate


class Validator(ABC):
    @abstractmethod
    def validate(self, item: Any, field_prefix: str = ""):
        raise NotImplemented

    @abstractmethod
    def parse_errors(self) -> list[ValidationError]:
        raise NotImplemented


class JsonValidator(Validator):
    def __init__(self):
        self._errors = []

    def validate(self, item: Any, field_prefix: str = ""):
        try:
            json.dumps(item)
        except TypeError:
            self._errors.append(
                ValidationError(
                    field=field_prefix,
                    value=item,
                    message="Is not json serializable"
                )
            )

    def parse_errors(self) -> list[ValidationError]:
        result = self._errors
        self._errors = []
        return result


class BaseValidator(Validator, ABC):
    def __init__(self):
        self._errors = []

    def validate_field(
            self,
            field: str,
            value: Any,
            expected_type: Type | tuple[Type, ...],
            ge: float = None,
            lt: float = None,
    ):
        if not isinstance(value, expected_type):
            self._errors.append(ValidationError(field, f"Must be of type {expected_type}", value))
        else:
            if ge is not None and value < ge:
                self._errors.append(ValidationError(field, f"Must be ≥ {ge}", value))
            if lt is not None and value >= lt:
                self._errors.append(ValidationError(field, f"Must be < {lt}", value))

    def validate_enum(self, field: str, value: Any, enum_class: Type[StrEnum]):
        if value not in enum_class:
            self._errors.append(
                ValidationError(
                    field,
                    f"Must be one of {[x for x in enum_class]}",
                    value
                ))

    def validate_dates(self, earlier: (str, datetime), later: (str, datetime)):
        if earlier[1] > later[1]:
            self._errors.append(
                ValidationError(
                    field=earlier[0],
                    value=earlier[1],
                    message=f"{earlier[0]} ({earlier[1]}) must be ≤ {later[0]} ({later[1]})",
                )
            )

    def validate_list(
            self,
            field: str,
            items: Iterable[Any],
            item_validator: "BaseValidator",
    ):
        if not isinstance(items, list):
            self._errors.append(ValidationError(field, "Must be a list", items))
        else:
            for i, item in enumerate(items):
                item_validator.validate(item, f"{field}[{i}]")

    def extend_errors(self, errors: list[ValidationError]):
        self._errors.extend(errors)

    def parse_errors(self) -> list[ValidationError]:
        result = self._errors
        self._errors = []
        return result


class CycleValidator(BaseValidator):
    def validate(self, item: Cycle, field_prefix="Cycle"):
        self.validate_field(field_prefix, item, Cycle)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_enum(f"{field_prefix}.code", item.code, Period)
        self.validate_field(f"{field_prefix}.cycle_in_days", item.cycle_in_days, int)


class UsageRateValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self._cycle_validator = CycleValidator()

    def validate(self, item: UsageRate, field_prefix="UsageRate"):
        self.validate_field(field_prefix, item, UsageRate)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_field(f"{field_prefix}.code", item.code, str)
        self.validate_field(f"{field_prefix}.unit", item.unit, str)
        self.validate_field(f"{field_prefix}.available_units", item.available_units, (int, float))
        self._cycle_validator.validate(item.renew_cycle, f"{field_prefix}.renew_cycle")

        self.extend_errors(self._cycle_validator.parse_errors())


class UsageValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self._cycle_validator = CycleValidator()

    def validate(self, item: Usage, field_prefix="Usage"):
        self.validate_field(field_prefix, item, Usage)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_field(f"{field_prefix}.code", item.code, str)
        self.validate_field(f"{field_prefix}.unit", item.unit, str)
        self.validate_field(f"{field_prefix}.available_units", item.available_units, (int, float))
        self.validate_field(f"{field_prefix}.used_units", item.used_units, (int, float))
        self._cycle_validator.validate(item.renew_cycle, f"{field_prefix}.renew_cycle")

        self.extend_errors(self._cycle_validator.parse_errors())


class DiscountValidator(BaseValidator):
    def validate(self, item: Discount, field_prefix="Discount"):
        self.validate_field(field_prefix, item, Discount)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_field(f"{field_prefix}.code", item.code, str)
        self.validate_field(f"{field_prefix}.description", item.description, (str, NoneType))
        self.validate_field(f"{field_prefix}.size", item.size, (int, float), ge=0, lt=1)
        self.validate_field(f"{field_prefix}.valid_until", item.valid_until, datetime)


class PlanValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self._cycle_validator = CycleValidator()
        self._usage_rate_validator = UsageRateValidator()
        self._discount_validator = DiscountValidator()
        self._json_validator = JsonValidator()

    def validate_plan(self, item: Plan, field_prefix="Plan"):
        self.validate_field(field_prefix, item, Plan)
        self.validate_field(f"{field_prefix}.id", item.id, ID)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_field(f"{field_prefix}.price", item.price, (int, float))
        self.validate_field(f"{field_prefix}.currency", item.currency, str)
        self.validate_field(f"{field_prefix}.description", item.description, (str, NoneType))
        self.validate_field(f"{field_prefix}.level", item.level, int)
        self.validate_field(f"{field_prefix}.features", item.features, (str, NoneType))
        self.validate_field(f"{field_prefix}.fields", item.fields, dict)
        self._json_validator.validate(item.fields, f"{field_prefix}.fields")
        self.validate_field(f"{field_prefix}.created_at", item.created_at, datetime)
        self.validate_field(f"{field_prefix}.updated_at", item.updated_at, datetime)

        self.validate_dates(
            (f"{field_prefix}.created_at", item.created_at),
            (f"{field_prefix}.updated_at", item.updated_at),
        )
        self.validate_list(
            f"{field_prefix}.usage_rates", item.usage_rates, self._usage_rate_validator
        )
        self.validate_list(
            f"{field_prefix}.discounts", item.discounts, self._discount_validator
        )
        self._cycle_validator.validate(item.billing_cycle, f"{field_prefix}.billing_cycle")

    def validate_plan_create(self, item: PlanCreate, field_prefix="PlanCreate"):
        self.validate_field(field_prefix, item, PlanCreate)
        self.validate_field(f"{field_prefix}.title", item.title, str)
        self.validate_field(f"{field_prefix}.price", item.price, (int, float))
        self.validate_field(f"{field_prefix}.currency", item.currency, str)
        self.validate_field(f"{field_prefix}.description", item.description, str)
        self.validate_field(f"{field_prefix}.level", item.level, int)
        self.validate_field(f"{field_prefix}.features", item.features, str)
        self.validate_field(f"{field_prefix}.fields", item.fields, dict)
        self._json_validator.validate(item.fields, f"{field_prefix}.fields")

        self.validate_list(
            f"{field_prefix}.usage_rates", item.usage_rates, self._usage_rate_validator
        )
        self.validate_list(
            f"{field_prefix}.discounts", item.discounts, self._discount_validator
        )
        self._cycle_validator.validate(item.billing_cycle, f"{field_prefix}.billing_cycle")

    def validate(self, item: Union[Plan, PlanCreate], field_prefix: str = None):
        if isinstance(item, Plan):
            field_prefix = field_prefix if field_prefix else "Plan"
            self.validate_plan(item, field_prefix)
        elif isinstance(item, PlanCreate):
            field_prefix = field_prefix if field_prefix else "PlanCreate"
            self.validate_plan_create(item, field_prefix)
        else:
            raise TypeError(item)

        self.extend_errors(self._usage_rate_validator.parse_errors())
        self.extend_errors(self._discount_validator.parse_errors())
        self.extend_errors(self._cycle_validator.parse_errors())
        self.extend_errors(self._json_validator.parse_errors())


class SubscriptionValidator(BaseValidator):
    def __init__(self):
        super().__init__()
        self._plan_validator = PlanValidator()
        self._usage_validator = UsageValidator()
        self._json_validator = JsonValidator()

    def validate_subscription_status(self, status: SubscriptionStatus, paused_from: Optional[datetime], prefix: str):
        if status == SubscriptionStatus.Paused:
            if paused_from is None:
                self._errors.append(
                    ValidationError(
                        field=f"{prefix}",
                        value=paused_from,
                        message="'paused_from' is required when status is 'Paused'"
                    )
                )
        else:
            if paused_from is not None:
                self._errors.append(
                    ValidationError(
                        field=f"{prefix}",
                        value=paused_from,
                        message="'paused_from' must be None when status is not 'Paused'",
                    )
                )

    def validate_subscription(self, item: Subscription, field_prefix="Subscription"):
        self.validate_field(field_prefix, item, Subscription)
        self.validate_field(f"{field_prefix}.id", item.id, ID)
        self.validate_field(f"{field_prefix}.subscriber_id", item.subscriber_id, str)
        self._plan_validator.validate(item.plan, f"{field_prefix}.plan")
        self.validate_enum(f"{field_prefix}.status", item.status, SubscriptionStatus)
        self.validate_field(f"{field_prefix}.created_at", item.created_at, datetime)
        self.validate_field(f"{field_prefix}.updated_at", item.updated_at, datetime)
        self.validate_field(f"{field_prefix}.last_billing", item.last_billing, datetime)
        self.validate_field(f"{field_prefix}.autorenew", item.autorenew, bool)
        self.validate_subscription_status(item.status, item.paused_from, f"{field_prefix}.paused_from")

        self.validate_list(
            f"{field_prefix}.usages", item.usages, self._usage_validator
        )

        self.validate_dates(
            (f"{field_prefix}.created_at", item.created_at),
            (f"{field_prefix}.updated_at", item.updated_at),
        )

        self.validate_dates(
            (f"{field_prefix}.created_at", item.created_at),
            (f"{field_prefix}.last_billing", item.last_billing),
        )

        self._json_validator.validate(item.fields, f"{field_prefix}.fields")

    def validate_subscription_create(self, item: SubscriptionCreate, field_prefix="SubscriptionCreate"):
        self.validate_field(field_prefix, item, SubscriptionCreate)
        self._plan_validator.validate(item.plan, f"{field_prefix}.plan")
        self.validate_field(f"{field_prefix}.subscriber_id", item.subscriber_id, str)
        self.validate_enum(f"{field_prefix}.status", item.status, SubscriptionStatus)
        self.validate_field(f"{field_prefix}.paused_from", item.paused_from, (datetime, NoneType))
        self.validate_field(f"{field_prefix}.autorenew", item.autorenew, bool)
        self.validate_subscription_status(item.status, item.paused_from, f"{field_prefix}.paused_from")
        self.validate_list(
            f"{field_prefix}.usages", item.usages, self._usage_validator
        )
        self._json_validator.validate(item.fields, f"{field_prefix}.fields")

    def validate(self, item: Union[Subscription, SubscriptionCreate], field_prefix=None):
        if isinstance(item, Subscription):
            field_prefix = field_prefix if field_prefix else "Subscription"
            self.validate_subscription(item, field_prefix)
        elif isinstance(item, SubscriptionCreate):
            field_prefix = field_prefix if field_prefix else "SubscriptionCreate"
            self.validate_subscription_create(item, field_prefix)
        else:
            raise TypeError(item)

        self.extend_errors(self._plan_validator.parse_errors())
        self.extend_errors(self._usage_validator.parse_errors())
        self.extend_errors(self._json_validator.parse_errors())


class WebhookValidator(BaseValidator):
    def validate_webhook(self, item: Webhook, field_prefix="Webhook"):
        self.validate_field(field_prefix, item, Webhook)
        self.validate_field(f"{field_prefix}.id", item.id, ID)
        self.validate_field(f"{field_prefix}.target_url", item.target_url, str)
        self.validate_enum(f"{field_prefix}.event_code", item.event_code, EventCode)
        self.validate_field(f"{field_prefix}.created_at", item.created_at, datetime)
        self.validate_field(f"{field_prefix}.updated_at", item.updated_at, datetime)
        self.validate_dates(
            (f"{field_prefix}.created_at", item.created_at),
            (f"{field_prefix}.updated_at", item.updated_at),
        )

    def validate_webhook_create(self, item: WebhookCreate, field_prefix="WebhookCreate"):
        self.validate_field(field_prefix, item, WebhookCreate)
        self.validate_enum(f"{field_prefix}.event_code", item.event_code, EventCode)
        self.validate_field(f"{field_prefix}.target_url", item.target_url, str)

    def validate_webhook_update(self, item: WebhookUpdate, field_prefix="WebhookUpdate"):
        self.validate_field(field_prefix, item, WebhookUpdate)
        self.validate_field(f"{field_prefix}.id", item.id, ID)
        self.validate_enum(f"{field_prefix}.event_code", item.event_code, EventCode)
        self.validate_field(f"{field_prefix}.target_url", item.target_url, str)
        self.validate_field(f"{field_prefix}.created_at", item.created_at, datetime)

    def validate(self, item: Union[Webhook, WebhookCreate, WebhookUpdate], field_prefix: str = None):
        if isinstance(item, Webhook):
            field_prefix = field_prefix if field_prefix else "Webhook"
            self.validate_webhook(item, field_prefix)
        elif isinstance(item, WebhookCreate):
            field_prefix = field_prefix if field_prefix else "WebhookCreate"
            self.validate_webhook_create(item, field_prefix)
        elif isinstance(item, WebhookUpdate):
            field_prefix = field_prefix if field_prefix else "WebhookUpdate"
            self.validate_webhook_update(item, field_prefix)
        else:
            raise TypeError(item)


ItemForValidation = Union[
    Plan,
    PlanCreate,
    Subscription,
    SubscriptionCreate,
    Webhook,
    WebhookCreate,
    WebhookUpdate,
    Usage,
    Discount,
]


def validate(items: Union[ItemForValidation, Iterable[ItemForValidation]]) -> None:
    selector = {
        Plan: PlanValidator(),
        PlanCreate: PlanValidator(),
        Subscription: SubscriptionValidator(),
        SubscriptionCreate: SubscriptionValidator(),
        Webhook: WebhookValidator(),
        WebhookCreate: WebhookValidator(),
        WebhookUpdate: WebhookValidator(),
        Usage: UsageValidator(),
        Discount: DiscountValidator(),
    }

    if not isinstance(items, Iterable):
        items = [items]

    errors = []
    for item in items:
        validator: Validator = selector.get(item.__class__)
        if not validator:
            raise TypeError(
                f"Cannot found validator for item with type: {items.__class__}. Available types are: {list(selector.keys())}"
            )
        validator.validate(item)
        errors.extend(validator.parse_errors())

    if errors:
        if len(errors) == 1:
            raise errors[0]
        else:
            raise MultipleError(exceptions=errors)
