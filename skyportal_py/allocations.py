"""Typed endpoint functions for ``/api/allocation``."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.instruments import Instrument
from skyportal_py.telescopes import Ephemeris, Telescope
from skyportal_py.users import User


class AllocationUser(BaseModel):
    """A join row mapping a user to an allocation (upstream ``AllocationUser``).

    ``allocation`` stays untyped to avoid a recursive model.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    allocation_id: int | None = None
    user_id: int | None = None
    user: User | None = None
    allocation: dict[str, Any] | None = None


class Allocation(BaseModel):
    """An observing-time allocation on an instrument (upstream ``Allocation``).

    ``allocation_users`` is a list of plain users on the allocation endpoints
    (the handlers substitute ``allocation_user.user``) but a list of join rows
    when it arrives nested inside a telescope payload, so both are accepted.
    ``requests``, ``default_requests``, ``default_observation_plans``,
    ``catalog_queries``, ``observation_plans``, ``gcn_triggers`` and ``group``
    stay untyped: those upstream models point back at ``Allocation``, so typing
    them would risk an import cycle. ``requests``, ``ephemeris`` and
    ``telescope`` are injected by the single-allocation endpoint. The encrypted
    ``_altdata`` column is never serialized.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    pi: str | None = None
    proposal_id: str | None = None
    hours_allocated: float | None = None
    validity_ranges: list[dict[str, Any]] | None = None
    default_share_group_ids: list[int] | None = None
    types: (
        list[Literal["triggered", "forced_photometry", "observation_plan"]] | None
    ) = None
    group_id: int | None = None
    instrument_id: int | None = None
    instrument: Instrument | None = None
    allocation_users: list[User | AllocationUser] | None = None
    group: dict[str, Any] | None = None
    requests: list[dict[str, Any]] | None = None
    default_requests: list[dict[str, Any]] | None = None
    default_observation_plans: list[dict[str, Any]] | None = None
    catalog_queries: list[dict[str, Any]] | None = None
    observation_plans: list[dict[str, Any]] | None = None
    gcn_triggers: list[dict[str, Any]] | None = None
    ephemeris: Ephemeris | None = None
    telescope: Telescope | None = None


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


class AllocationPost(BaseModel):
    """Payload for creating an allocation."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    instrument_id: int
    group_id: int
    hours_allocated: float
    pi: str | None = None
    proposal_id: str | None = None
    types: list[str] | None = None
    validity_ranges: list[dict[str, Any]] | None = None
    default_share_group_ids: list[int] | None = None
    allocation_admin_ids: list[int] | None = None
    altdata: dict[str, Any] | None = Field(alias="_altdata", default=None)


class AllocationUpdate(BaseModel):
    """Payload for updating an allocation; every field is optional."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    instrument_id: int | None = None
    group_id: int | None = None
    hours_allocated: float | None = None
    pi: str | None = None
    proposal_id: str | None = None
    types: list[str] | None = None
    validity_ranges: list[dict[str, Any]] | None = None
    default_share_group_ids: list[int] | None = None
    allocation_admin_ids: list[int] | None = None
    altdata: dict[str, Any] | None = Field(alias="_altdata", default=None)
    replace_altdata: bool | None = None


class AllocationPostResponse(BaseModel):
    """Result of creating an allocation."""

    model_config = ConfigDict(extra="forbid")

    id: int


def post_allocation(
    client: httpx.Client,
    payload: AllocationPost,
) -> AllocationPostResponse:
    """Create an allocation on a robotic instrument.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : AllocationPost
        The allocation to create. ``altdata`` holds the instrument API
        credentials and is validated by the instrument's API class when it
        implements ``validate_altdata``. ``allocation_admin_ids`` lists the
        users allowed to administer the allocation. Requires the
        ``Manage allocations`` permission.
    """
    response = client.post(
        "/api/allocation",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return AllocationPostResponse.model_validate(unwrap(response))


def update_allocation(
    client: httpx.Client,
    allocation_id: int,
    payload: AllocationUpdate,
) -> None:
    """Update an allocation.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    allocation_id : int
        ID of the allocation to update.
    payload : AllocationUpdate
        Fields to change. ``altdata`` is merged into the stored value
        rather than replacing it. ``allocation_admin_ids`` is authoritative:
        any admin not listed is removed, so omitting it clears them all.
        Requires the ``Manage allocations`` permission.
    """
    unwrap(
        client.put(
            f"/api/allocation/{allocation_id}",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )
    )


def delete_allocation(client: httpx.Client, allocation_id: int) -> None:
    """Delete an allocation.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    allocation_id : int
        ID of the allocation to delete. Requires the ``Manage allocations``
        permission.
    """
    unwrap(client.delete(f"/api/allocation/{allocation_id}"))


def fetch_allocation_report(
    client: httpx.Client,
    instrument_id: int,
    *,
    output_format: str | None = None,
) -> bytes:
    """Retrieve a plotted report on an instrument's allocations.

    The report charts allocated hours, requests made, requests completed and
    the moon-phase distribution of completed requests, per allocation.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    instrument_id : int
        ID of the instrument to report on. The server errors unless it has
        at least one accessible allocation.
    output_format : str, optional
        ``"pdf"`` (the server default) or ``"png"``.

    Returns
    -------
    bytes
        The raw report file.
    """
    params = {} if output_format is None else {"output_format": output_format}
    response = client.get(f"/api/allocation/report/{instrument_id}", params=params)
    return unwrap_content(response)
