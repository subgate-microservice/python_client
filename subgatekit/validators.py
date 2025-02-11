import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Self, Type, Union

from subgatekit.exceptions import MultipleError


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
            field: str,
            value: Any,
            **kwargs,
    ):
        self._errors = []
        self._field = field
        self._value = value

    @abstractmethod
    def validate(self) -> Self:
        raise NotImplemented

    def parse_errors(self) -> list[ValidationError]:
        result = self._errors
        self._errors = []
        return result


class TypeValidator(Validator):
    def __init__(
            self,
            field: str,
            value: Any,
            expected_type: Union[Type, tuple[Type]],
            optional=False,
    ):
        super().__init__(field, value)
        self._expected_type = expected_type
        self._optional = optional

    def validate(self) -> Self:
        if self._optional and self._value is None:
            return self
        if not isinstance(self._value, self._expected_type):
            self._errors.append(
                ValidationError(self._field, f"Must be of type {self._expected_type}", self._value)
            )
        return self


class BoundaryValidator(Validator):
    def __init__(
            self,
            field: str,
            value: Any,
            ge=None,
            lt=None,
    ):
        super().__init__(field, value)
        self._ge = ge
        self._lt = lt

    def validate(self) -> Self:
        if self._ge is not None and self._value < self._ge:
            self._errors.append(
                ValidationError(self._field, f"Must be >= {self._ge}", self._value)
            )
        if self._lt is not None and self._value >= self._lt:
            self._errors.append(
                ValidationError(self._field, f"Must be < {self._lt}", self._value)
            )
        return self


class EnumValidator(Validator):
    def __init__(
            self,
            field: str,
            value: Any,
            expected_type: Type[Enum],
    ):
        super().__init__(field, value)
        self._expected_type = expected_type

    def validate(self) -> Self:
        if self._value not in self._expected_type:
            self._errors.append(
                ValidationError(self._field, f"Must be of enum '{self._expected_type}'", self._value)
            )
        return self


class ListTypeValidator(TypeValidator):
    def validate(self) -> Self:
        if self._optional and self._value is None:
            return self

        if not isinstance(self._value, list):
            self._errors.append(
                ValidationError(self._field, "Must be a list", self._value)
            )
            return self

        for i, value in enumerate(self._value):
            if not isinstance(value, self._expected_type):
                self._errors.append(
                    ValidationError(f"{self._field}[{i}]", f"Must be of type {self._expected_type}", value)
                )
        return self


class FieldsValidator(Validator):
    def __init__(self, field: str, value: Any, optional=False, **kwargs):
        super().__init__(field, value, **kwargs)
        self._optional = optional

    def validate(self) -> Self:
        if self._optional and self._value is None:
            return self

        if not isinstance(self._value, dict):
            self._errors.append(
                ValidationError(self._field, f"Must be of type {dict}", self._value)
            )
        try:
            json.dumps(self._value)
        except TypeError:
            self._errors.append(
                ValidationError(
                    field=self._field,
                    value=self._value,
                    message="Is not json serializable"
                )
            )
        return self


def raise_errors_if_necessary(errors: list[ValidationError]) -> None:
    if errors:
        if len(errors) == 1:
            raise errors[0]
        else:
            raise MultipleError(errors)
