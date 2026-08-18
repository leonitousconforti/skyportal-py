"""Typed endpoint functions for ``/api/telescope``."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Ephemeris(BaseModel):
    """Sun/twilight times computed for a telescope's site.

    Returned by the single-allocation endpoint. Every value is ``None`` when
    the telescope has no usable observer (no fixed location, or missing
    coordinates), in which case the server sends an empty object instead.
    """

    model_config = ConfigDict(extra="forbid")

    sunset_utc: str | None = None
    sunrise_utc: str | None = None
    twilight_morning_astronomical_utc: str | None = None
    twilight_evening_astronomical_utc: str | None = None
    twilight_morning_nautical_utc: str | None = None
    twilight_evening_nautical_utc: str | None = None
    utc_offset_hours: float | None = None
    sunset_unix_ms: float | None = None
    sunrise_unix_ms: float | None = None
    twilight_morning_astronomical_unix_ms: float | None = None
    twilight_evening_astronomical_unix_ms: float | None = None
    twilight_morning_nautical_unix_ms: float | None = None
    twilight_evening_nautical_unix_ms: float | None = None


class Telescope(BaseModel):
    """A SkyPortal telescope (upstream ``Telescope``).

    ``instruments`` and ``allocations`` stay untyped: typing them with
    ``instruments.Instrument`` / ``allocations.Allocation`` would create an
    import cycle, as both of those models point back at ``Telescope``.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    name: str | None = None
    nickname: str | None = None
    lat: float | None = None
    lon: float | None = None
    elevation: float | None = None
    mpc_obscode: str | None = None
    diameter: float | None = None
    skycam_link: str | None = None
    weather_link: str | None = None
    robotic: bool | None = None
    fixed_location: bool | None = None
    instruments: list[dict[str, Any]] | None = None
    allocations: list[dict[str, Any]] | None = None
    is_night_astronomical: bool | None = None
    morning: str | bool | None = None
    evening: str | bool | None = None


def fetch_telescopes(client: httpx.Client) -> list[Telescope]:
    """Retrieve all telescopes.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/telescope")
    return [Telescope.model_validate(item) for item in unwrap(response)]


def fetch_telescope(client: httpx.Client, telescope_id: int) -> Telescope:
    """Retrieve a single telescope by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    telescope_id : int
        ID of the telescope.
    """
    response = client.get(f"/api/telescope/{telescope_id}")
    return Telescope.model_validate(unwrap(response))


class TelescopePost(BaseModel):
    """Payload for creating a telescope."""

    model_config = ConfigDict(extra="forbid")

    name: str
    nickname: str
    diameter: float
    lat: float | None = None
    lon: float | None = None
    elevation: float | None = None
    skycam_link: str | None = None
    weather_link: str | None = None
    robotic: bool = False
    fixed_location: bool | None = None


class TelescopePostResponse(BaseModel):
    """Result of creating a telescope."""

    model_config = ConfigDict(extra="forbid")

    id: int


class TelescopePut(BaseModel):
    """Payload for updating a telescope."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    nickname: str | None = None
    diameter: float | None = None
    lat: float | None = None
    lon: float | None = None
    elevation: float | None = None
    skycam_link: str | None = None
    weather_link: str | None = None
    robotic: bool | None = None
    fixed_location: bool | None = None


def post_telescope(
    client: httpx.Client,
    payload: TelescopePost,
) -> TelescopePostResponse:
    """Create a telescope.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : TelescopePost
        The telescope to create. ``name`` is the unabbreviated facility
        name, ``nickname`` the abbreviated one, and ``diameter`` is in
        meters. ``fixed_location`` defaults to true server-side, in which
        case ``lat``, ``lon``, and ``elevation`` are required.
    """
    response = client.post("/api/telescope", json=payload.model_dump(exclude_none=True))
    return TelescopePostResponse.model_validate(unwrap(response))


def update_telescope(
    client: httpx.Client,
    telescope_id: int,
    payload: TelescopePut,
) -> None:
    """Update a telescope.

    Only the provided fields are sent; omitted fields are left unchanged.
    Requires the "Manage telescopes" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    telescope_id : int
        ID of the telescope to update.
    payload : TelescopePut
        The fields to change.
    """
    unwrap(
        client.put(
            f"/api/telescope/{telescope_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def delete_telescope(client: httpx.Client, telescope_id: int) -> None:
    """Delete a telescope.

    Requires the "Manage telescopes" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    telescope_id : int
        ID of the telescope to delete.
    """
    unwrap(client.delete(f"/api/telescope/{telescope_id}"))
