from typing import NamedTuple

from subgatekit.v2_0.domain.enums import Period


class Cycle(NamedTuple):
    title: str
    code: Period
    cycle_in_days: int

    @classmethod
    def from_code(cls, code: Period):
        if code == Period.Daily:
            return cls("Daily", code, 1)
        elif code == Period.Weekly:
            return cls("Weekly", code, 7)
        elif code == Period.Monthly:
            return cls("Monthly", code, 30)
        elif code == Period.Quarterly:
            return cls("Quarterly", code, 92)
        elif code == Period.Semiannual:
            return cls("Semiannual", code, 183)
        elif code == Period.Annual:
            return cls("Annual", code, 365)
        elif code == Period.Lifetime:
            return cls("Lifetime", code, 365_000)
        raise ValueError(code)
