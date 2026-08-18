"""Typed endpoint functions for ``/api/telescope``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Telescope(BaseModel):
    """A SkyPortal telescope."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    nickname: str | None = None
    lat: float | None = None
    lon: float | None = None
    elevation: float | None = None
    diameter: float | None = None
    robotic: bool = False


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
