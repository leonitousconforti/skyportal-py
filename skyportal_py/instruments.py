"""Typed endpoint functions for ``/api/instrument``."""

from __future__ import annotations

import httpx
from pydantic import Field

from skyportal_py._http import unwrap
from skyportal_py._models import ResponseModel


class Instrument(ResponseModel):
    """A SkyPortal instrument.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    id: int
    name: str
    type: str | None = None
    band: str | None = None
    telescope_id: int | None = None
    filters: list[str] = Field(default_factory=list)


def fetch_instruments(client: httpx.Client) -> list[Instrument]:
    """Retrieve all instruments visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/instrument")
    return [Instrument.model_validate(item) for item in unwrap(response)]


def fetch_instrument(client: httpx.Client, instrument_id: int) -> Instrument:
    """Retrieve a single instrument by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    instrument_id : int
        ID of the instrument.
    """
    response = client.get(f"/api/instrument/{instrument_id}")
    return Instrument.model_validate(unwrap(response))
