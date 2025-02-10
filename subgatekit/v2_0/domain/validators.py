import datetime
import json
from abc import ABC, abstractmethod
from typing import Any, Self, Type, Union
from uuid import UUID

from subgatekit.v2_0.domain.enums import Period


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
