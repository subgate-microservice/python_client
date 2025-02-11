from datetime import datetime

from subgatekit.v2_0.domain.validators import TypeValidator, raise_errors_if_necessary, BoundaryValidator


class Discount:
    def __init__(
            self,
            title: str,
            code: str,
            size: float,
            valid_until: datetime,
            description: str = None,
    ):
        self._validate(title, code, size, valid_until, description)
        self.title = title
        self.code = code
        self.description = description
        self.size = size
        self.valid_until = valid_until

    @staticmethod
    def _validate(
            title: str,
            code: str,
            size: float,
            valid_until: datetime,
            description: str,
    ):
        validators = [
            TypeValidator("Discount.title", title, str),
            TypeValidator("Discount.code", code, str),
            TypeValidator("Discount.size", size, float),
            BoundaryValidator("Discount.size", size, ge=0, lt=1),
            TypeValidator("Discount.valid_until", valid_until, datetime),
            TypeValidator("Discount.description", description, str, True),
        ]
        errors = []
        for validator in validators:
            errors.extend(validator.validate().parse_errors())
        raise_errors_if_necessary(errors)
