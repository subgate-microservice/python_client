from datetime import datetime


class Discount:
    def __init__(
            self,
            title: str,
            code: str,
            size: float,
            valid_until: datetime,
            description: str = None,
    ):
        self.title = title
        self.code = code
        self.description = description
        self.size = size
        self.valid_until = valid_until
