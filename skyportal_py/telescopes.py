"""Typed endpoint functions for ``/api/telescope``."""

from __future__ import annotations

import httpx

from skyportal_py._http import unwrap
from skyportal_py._models import ResponseModel


class Telescope(ResponseModel):
    """A SkyPortal telescope.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

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
