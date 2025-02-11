from typing import cast

import pytest

from subgatekit.v2_0.domain.exceptions import MultipleError, ValidationError
from tests.conftest import fake_plan, client, wrapper


@pytest.mark.asyncio
async def test_422(fake_plan, client):
    with pytest.raises(MultipleError) as err:
        _ = await wrapper(client.plan_client().create_plan(
            "AnyPlan",
            110,
            11,
            fields="incorrect data for fields",
        ))
    assert len(err.value.exceptions) == 2

    currency_err = cast(ValidationError, err.value.exceptions[0])
    assert currency_err.value == 11
    assert currency_err.value_type == int
    assert currency_err.field == "PlanCreate.currency"

    fields_err = cast(ValidationError, err.value.exceptions[1])
    assert fields_err.value == "incorrect data for fields"
    assert fields_err.value_type == str
    assert fields_err.field == "PlanCreate.fields"
