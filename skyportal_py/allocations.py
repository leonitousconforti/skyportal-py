"""Typed endpoint functions for ``/api/allocation``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Allocation(BaseModel):
    """An observing-time allocation on an instrument."""

    model_config = ConfigDict(extra="forbid")

    id: int
    pi: str | None = None
    proposal_id: str | None = None
    hours_allocated: float | None = None
    group_id: int | None = None
    instrument_id: int | None = None


def fetch_allocations(
    client: httpx.Client,
    *,
    instrument_id: int | None = None,
) -> list[Allocation]:
    """Retrieve the allocations visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    instrument_id : int, optional
        Restrict to allocations on this instrument.
    """
    params = {} if instrument_id is None else {"instrument_id": instrument_id}
    response = client.get("/api/allocation", params=params)
    return [Allocation.model_validate(item) for item in unwrap(response)]


def fetch_allocation(client: httpx.Client, allocation_id: int) -> Allocation:
    """Retrieve a single allocation by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    allocation_id : int
        ID of the allocation.
    """
    response = client.get(f"/api/allocation/{allocation_id}")
    return Allocation.model_validate(unwrap(response)["allocation"])
