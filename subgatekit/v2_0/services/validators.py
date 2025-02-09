import datetime
import json
from abc import ABC, abstractmethod
from typing import Any, Self, Type, Union, cast
from uuid import UUID

from subgatekit.v2_0.domain.cycle import Cycle
from subgatekit.v2_0.domain.discount import Discount
from subgatekit.v2_0.domain.enums import Period, SubscriptionStatus
from subgatekit.v2_0.domain.plan import Plan
from subgatekit.v2_0.domain.subscription import Subscription
from subgatekit.v2_0.domain.usage import UsageRate, Usage


class ValidationError(Exception):
    def __init__(self, field: str, message: str, value: Any):
        self.field = field
        self.value = value
        self.message = message
        self.value_type = type(value)

    def __str__(self):
        return (
            f"Validation error on field '{self.field}': {self.message}. "
            f"Received value: {self.value}. Value type: {self.value_type}"
        )


class Validator(ABC):
    def __init__(
            self,
            value: Any,
            field_name: str = None,
            optional=False,
    ):
        self.errors = []
        self.field_name = field_name
        self.value = value
        self._optional = optional

    def validate_type(self, expected_type: Union[Type, tuple[Type, ...]]):
        if self._optional and self.value is None:
            return
        if not isinstance(self.value, expected_type):
            self.errors.append(
                ValidationError(self.field_name, f"Must be of type {expected_type}", self.value)
            )

    @abstractmethod
    def validate(self) -> Self:
        raise NotImplemented

    def parse_errors(self) -> list[ValidationError]:
        result = self.errors
        self.errors = []
        return result


class BoundaryValidator(Validator, ABC):
    def __init__(
            self,
            value: Any,
            field_name: str = None,
            optional=False,
            ge=None,
            lt=None,
    ):
        super().__init__(value, field_name, optional)
        self._ge = ge
        self._lt = lt

    def validate_boundaries(self):
        if self._ge is not None and self.value < self._ge:
            self.errors.append(ValidationError(self.field_name, f"Must be ≥ {self._ge}", self.value))
        if self._lt is not None and self.value >= self._lt:
            self.errors.append(ValidationError(self.field_name, f"Must be < {self._lt}", self.value))


class StringValidator(Validator):
    def validate(self) -> Self:
        self.validate_type(str)
        return self


class IntegerValidator(BoundaryValidator):
    def validate(self) -> Self:
        self.validate_type(int)
        if not self.errors:
            self.validate_boundaries()
        return self


class NumberValidator(BoundaryValidator):
    def validate(self) -> Self:
        self.validate_type((int, float))
        if not self.errors:
            self.validate_boundaries()
        return self


class BooleanValidator(Validator):
    def validate(self) -> Self:
        self.validate_type(bool)
        return self


class AwareDatetimeValidator(BoundaryValidator):
    def validate(self) -> Self:
        self.validate_type(datetime.datetime)
        if not self.errors:
            self.validate_boundaries()
        return self


class UUIDValidator(Validator):
    def validate(self) -> Self:
        self.validate_type(UUID)
        return self


class FieldsValidator(Validator):
    def validate(self) -> Self:
        self.validate_type(dict)
        try:
            json.dumps(self.value)
        except TypeError:
            self.errors.append(
                ValidationError(
                    field=self.field_name,
                    value=self.value,
                    message="Is not json serializable"
                )
            )
        return self


class DatesValidator(Validator):
    def __init__(
            self,
            earlier_value: Any,
            later_value: Any,
            earlier_field_name: str,
            later_field_name: str,
    ):
        super().__init__(earlier_value, earlier_field_name)
        self.later_field_name = later_field_name
        self.later_value = later_value

    def validate(self) -> Self:
        if not isinstance(self.value, datetime.datetime):
            self.errors.append(
                ValidationError(
                    self.field_name,
                    f"{self.field_name} should be datetime with tz_info",
                    self.value,
                )
            )
        if not isinstance(self.later_value, datetime.datetime):
            self.errors.append(
                ValidationError(
                    self.later_field_name,
                    f"{self.later_field_name} should be datetime with tz_info",
                    self.later_value,
                )
            )
        if not self.errors:
            if self.value > self.later_value:
                self.errors.append(
                    ValidationError(
                        field=self.field_name,
                        value=self.value,
                        message=f"{self.field_name} ({self.value}) "
                                f"must be ≤ {self.later_field_name} ({self.later_value})",
                    )
                )
        return self


class ListValidator(Validator):
    def __init__(
            self,
            value: Any,
            item_validator: Type[Validator],
            field_name: str,
    ):
        super().__init__(value, field_name)
        self._item_validator_type = item_validator

    def validate(self) -> Self:
        if not isinstance(self.value, list):
            self.errors.append(
                ValidationError(self.field_name, "Must be a list", self.value)
            )
        else:
            for i, item in enumerate(self.value):
                validator = self._item_validator_type(f"{self.field_name}[{i}]", item)
                validator.validate()
                self.errors.extend(validator.parse_errors())
        return self


class PeriodValidator(Validator):
    def validate(self) -> Self:
        if self.value not in Period:
            self.errors.append(
                ValidationError(
                    self.field_name,
                    f"Must be one of {[x for x in Period]}",
                    self.value
                ))
        return self


class SubscriptionStatusValidator(Validator):
    def validate(self) -> Self:
        if self.value not in SubscriptionStatus:
            self.errors.append(
                ValidationError(
                    self.field_name,
                    f"Must be one of {[x for x in SubscriptionStatus]}",
                    self.value
                ))
        return self


class CycleValidator(Validator):
    def __init__(self, value: Cycle, field_name: str = "Cycle"):
        super().__init__(value, field_name)

    def validate(self) -> Self:
        self.validate_type(Cycle)
        if not self.errors:
            self.errors.extend(
                StringValidator(self.value.title, f"{self.field_name}.title").validate().parse_errors() +
                PeriodValidator(self.value.code, f"{self.field_name}.code", ).validate().parse_errors() +
                IntegerValidator(self.value.cycle_in_days, f"{self.field_name}.cycle_in_days").validate().parse_errors()
            )
        return self


class UsageRateValidator(Validator):
    def __init__(self, value: Any, field_name: str = "UsageRate"):
        super().__init__(value, field_name)

    def validate(self) -> Self:
        self.validate_type(UsageRate)
        if not self.errors:
            self.errors.extend(
                StringValidator(self.value.title, f"{self.field_name}.title").validate().parse_errors() +
                StringValidator(self.value.code, f"{self.field_name}.code").validate().parse_errors() +
                StringValidator(self.value.unit, f"{self.field_name}.unit").validate().parse_errors() +
                NumberValidator(self.value.available_units,
                                f"{self.field_name}.available_units").validate().parse_errors() +
                CycleValidator(self.value.renew_cycle, f"{self.field_name}.renew_cycle").validate().parse_errors()
            )
        return self


class UsageValidator(Validator):
    def __init__(self, value: Any, field_name: str = "Usage"):
        super().__init__(value, field_name)

    def validate(self) -> Self:
        self.validate_type(Usage)
        if not self.errors:
            self.errors.extend(
                StringValidator(self.value.title, f"{self.field_name}.title").validate().parse_errors() +
                StringValidator(self.value.code, f"{self.field_name}.code").validate().parse_errors() +
                StringValidator(self.value.unit, f"{self.field_name}.unit").validate().parse_errors() +
                NumberValidator(self.value.available_units,
                                f"{self.field_name}.available_units").validate().parse_errors() +
                CycleValidator(self.value.renew_cycle, f"{self.field_name}.renew_cycle").validate().parse_errors() +
                NumberValidator(self.value.used_units, f"{self.field_name}.used_units").validate().parse_errors()
            )
        return self


class DiscountValidator(Validator):
    def __init__(self, value: Any, field_name: str = "Discount"):
        super().__init__(value, field_name)

    def validate(self) -> Self:
        self.validate_type(Discount)
        if not self.errors:
            self.errors.extend(
                StringValidator(self.value.title, f"{self.field_name}.title").validate().parse_errors() +
                StringValidator(self.value.code, f"{self.field_name}.code").validate().parse_errors() +
                StringValidator(self.value.description, f"{self.field_name}.description",
                                True).validate().parse_errors() +
                NumberValidator(self.value.size, f"{self.field_name}.size", ge=0, lt=1).validate().parse_errors() +
                AwareDatetimeValidator(self.value.valid_until,
                                       f"{self.field_name}.valid_until").validate().parse_errors()

            )
        return self


class PlanValidator(Validator):
    def __init__(self, value: Any, field_name: str = "Plan"):
        super().__init__(value, field_name)

    def validate(self) -> Self:
        self.validate_type(Plan)
        value = cast(Plan, self.value)
        field = self.field_name
        if not self.errors:
            self.errors.extend(
                UUIDValidator(value.id, f"{field}.id").validate().parse_errors() +
                StringValidator(value.title, f"{field}.title").validate().parse_errors() +
                NumberValidator(value.price, f"{field}.price").validate().parse_errors() +
                StringValidator(value.currency, f"{field}.currency").validate().parse_errors() +
                StringValidator(value.description, f"{field}.description", optional=True).validate().parse_errors() +
                IntegerValidator(value.level, f"{field}.level").validate().parse_errors() +
                StringValidator(value.features, f"{field}.features", True).validate().parse_errors() +
                FieldsValidator(value.fields, f"{field}.fields").validate().parse_errors() +
                DatesValidator(value.created_at, value.updated_at, f"{field}.created_at",
                               f"{field}.updated_at").validate().parse_errors() +
                ListValidator(value.usage_rates, UsageRateValidator, f"{field}.usage_rates").validate().parse_errors() +
                ListValidator(value.discounts, DiscountValidator, f"{field}.discounts").validate().parse_errors() +
                CycleValidator(value.billing_cycle, f"{field}.billing_cycle").validate().parse_errors()
            )
        return self


class SubscriptionValidator(Validator):
    def __init__(self, value: Any, field_name: str = "Subscription"):
        super().__init__(value, field_name)

    def validate_subscription_status(self):
        status, paused_from = self.value.status, self.value.paused_from
        if status == SubscriptionStatus.Paused:
            if paused_from is None:
                self.errors.append(
                    ValidationError(
                        field=f"{self.field_name}.paused_from",
                        value=paused_from,
                        message="'paused_from' is required when status is 'Paused'"
                    )
                )
        else:
            if paused_from is not None:
                self.errors.append(
                    ValidationError(
                        field=f"{self.field_name}.paused_from",
                        value=paused_from,
                        message="'paused_from' must be None when status is not 'Paused'",
                    )
                )

    def validate(self) -> Self:
        self.validate_type(Subscription)
        value = cast(Subscription, self.value)
        field = self.field_name
        if not self.errors:
            self.validate_subscription_status()
            self.errors.extend(
                UUIDValidator(value.id, f"{field}.id").validate().parse_errors() +
                StringValidator(value.subscriber_id, f"{field}.subscriber_id`").validate().parse_errors() +
                PlanValidator(value.plan, f"{field}.plan").validate().parse_errors() +
                SubscriptionStatusValidator(value.status, f"{field}.status").validate().parse_errors() +
                DatesValidator(value.created_at, value.updated_at, f"{field}.created_at",
                               f"{field}.updated_at").validate().parse_errors() +
                DatesValidator(value.created_at, value.last_billing, f"{field}.created_at",
                               f"{field}.last_billing").validate().parse_errors() +
                AwareDatetimeValidator(value.last_billing, f"{field}.last_billing").validate().parse_errors() +
                BooleanValidator(value.autorenew, f"{field}.autorenew").validate().parse_errors() +
                ListValidator(value.usages, UsageValidator, f"{field}.usages").validate().parse_errors() +
                FieldsValidator(value.fields, f"{field}.fields").validate().parse_errors()
            )
        return self
