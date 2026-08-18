"""Typed endpoint functions for ``/api/streams``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Stream(BaseModel):
    """An alert stream, e.g. a survey's public alerts.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(extra="allow")

    id: int
    name: str
    altdata: dict[str, Any] | None = None


def fetch_streams(client: httpx.Client) -> list[Stream]:
    """Retrieve the alert streams visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/streams")
    return [Stream.model_validate(item) for item in unwrap(response)]


def fetch_stream(client: httpx.Client, stream_id: int) -> Stream:
    """Retrieve a single alert stream by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    stream_id : int
        ID of the stream.
    """
    response = client.get(f"/api/streams/{stream_id}")
    return Stream.model_validate(unwrap(response))
