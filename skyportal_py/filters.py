"""Typed endpoint functions for ``/api/filters``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Filter(BaseModel):
    """An alert-stream filter belonging to a group.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    group_id: int | None = None
    stream_id: int | None = None


def fetch_filters(client: httpx.Client) -> list[Filter]:
    """Retrieve all filters belonging to the token's groups.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/filters")
    return [Filter.model_validate(item) for item in unwrap(response)]


def fetch_filter(client: httpx.Client, filter_id: int) -> Filter:
    """Retrieve a single filter by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    filter_id : int
        ID of the filter.
    """
    response = client.get(f"/api/filters/{filter_id}")
    return Filter.model_validate(unwrap(response))
