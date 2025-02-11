import datetime
import logging
from typing import Optional, Iterable, Literal

import httpx

from subgatekit.v2_0.domain.enums import SubscriptionStatus
from subgatekit.v2_0.domain.exceptions import ItemNotExist, ItemAlreadyExist, ActiveStatusConflict
from subgatekit.v2_0.domain.utils import ID


def processing_response(response: httpx.Response):
    if response.status_code == 404:
        data = response.json()
        if data.get("exception_code") == "item_not_exist":
            raise ItemNotExist.from_json(data)
        response.raise_for_status()

    if response.status_code == 409:
        data = response.json()
        if data["exception_code"] == "active_status_conflict":
            raise ActiveStatusConflict.from_json(data)
        raise ItemAlreadyExist.from_json(data)

    if response.status_code == 422:
        logger.error(response.json())
        raise Exception("HttpStatusCode422")

    if response.status_code >= 400:
        response.raise_for_status()

    if response.status_code == 204:
        return None
    return response.json()


OrderBy = list[tuple[str, Literal[1, -1]]]

logger = logging.getLogger(__name__)


def _to_iterable[T](data: T | Iterable[T]) -> Iterable[T]:
    if not isinstance(data, Iterable) or isinstance(data, str):
        data = [data]
    return data


def build_query_params(
        ids: Optional[Iterable[ID]] = None,
        subscriber_ids: Optional[Iterable[str]] = None,
        statuses: Optional[Iterable[SubscriptionStatus]] = None,
        expiration_date_gte: Optional[datetime.datetime] = None,
        expiration_date_gt: Optional[datetime.datetime] = None,
        expiration_date_lte: Optional[datetime.datetime] = None,
        expiration_date_lt: Optional[datetime.datetime] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        order_by: Optional[OrderBy] = None,
) -> dict:
    params = {}
    if ids is not None:
        ids = _to_iterable(ids)
        params["ids"] = [str(x) for x in ids]
    if subscriber_ids is not None:
        subscriber_ids = _to_iterable(subscriber_ids)
        params["subscriber_ids"] = list(subscriber_ids)
    if statuses is not None:
        statuses = _to_iterable(statuses)
        params["statuses"] = [statuses] if isinstance(statuses, str) else list(statuses)
    if expiration_date_gte:
        params["expiration_date_gte"] = expiration_date_gte.isoformat()
    if expiration_date_gt:
        params["expiration_date_gt"] = expiration_date_gt.isoformat()
    if expiration_date_lte:
        params["expiration_date_lte"] = expiration_date_lte.isoformat()
    if expiration_date_lt:
        params["expiration_date_lt"] = expiration_date_lt.isoformat()
    if skip is not None:
        params["skip"] = skip
    if limit is not None:
        params["limit"] = limit
    if order_by is not None:
        params["order_by"] = [f"{col},{asc}" for col, asc in order_by]
    return params
