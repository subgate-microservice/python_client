from typing import Hashable, Any


class MultipleError(Exception):
    def __init__(self, exceptions: list[Exception]):
        self.exceptions = exceptions

    def __str__(self):
        if not self.exceptions:
            return "No errors."
        error_messages = "\n".join(
            [f"{i + 1}. {str(exc)}" for i, exc in enumerate(self.exceptions)]
        )
        return f"Multiple errors occurred ({len(self.exceptions)}):\n{error_messages}"


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


class ItemNotExist(Exception):
    def __init__(self, item_type: str, lookup_field_value: Hashable, lookup_field_key: str):
        self.item_type = item_type
        self.lookup_field_value = lookup_field_value
        self.lookup_field_key = lookup_field_key

    def __str__(self):
        return f"The item of type '{self.item_type}' with {self.lookup_field_key} '{self.lookup_field_value}' does not exist."

    @classmethod
    def from_json(cls, data):
        return cls(
            item_type=data["item_type"],
            lookup_field_value=data["lookup_field_value"],
            lookup_field_key=data["lookup_field_key"],
        )


class ItemAlreadyExist(Exception):
    def __init__(self, item_type: str, index_value: Hashable, index_key: str):
        self.item_type = item_type
        self.index_value = index_value
        self.index_key = index_key

    def __str__(self):
        return f"The item of type '{self.item_type}' with {self.index_key} '{self.index_value}' already exists."

    @classmethod
    def from_json(cls, data):
        return cls(
            item_type=data["item_type"],
            index_value=data["index_value"],
            index_key=data["index_key"],
        )
