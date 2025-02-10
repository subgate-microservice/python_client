import json
from abc import ABC, abstractmethod
from typing import Any, Self, Type, Union


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


class ListValidator(Validator):
    def __init__(
            self,
            field: str,
            value: Any,
            item_validator: Type[Validator],
            **kwargs,
    ):
        super().__init__(field, value)
        self._item_validator_type = item_validator
        self._kwargs = kwargs

    def validate(self) -> Self:
        if not isinstance(self._value, list):
            self._errors.append(
                ValidationError(self._field, "Must be a list", self._value)
            )
        else:
            for i, item in enumerate(self._value):
                validator = self._item_validator_type(f"{self._field}[{i}]", item, **self._kwargs)
                validator.validate()
                self._errors.extend(validator.parse_errors())
        return self


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
            return
        if not isinstance(self._value, self._expected_type):
            self._errors.append(
                ValidationError(self._field, f"Must be of type {self._expected_type}", self._value)
            )


class FieldsValidator(Validator):
    def validate(self) -> Self:
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
