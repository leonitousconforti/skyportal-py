"""Typed endpoint functions for ``/api/filters``."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Filter(BaseModel):
    """An alert-stream filter belonging to a group (upstream ``Filter``).

    ``stream``, ``group``, ``broker`` and ``candidates`` stay untyped: each of
    those upstream models owns a ``filters`` (or ``filter``) relationship, so
    typing them here would risk an import cycle.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    name: str | None = None
    stream_id: int | None = None
    group_id: int | None = None
    broker_id: int | None = None
    altdata: dict[str, Any] | None = None
    autosave: bool | None = None
    stream: dict[str, Any] | None = None
    group: dict[str, Any] | None = None
    broker: dict[str, Any] | None = None
    candidates: list[dict[str, Any]] | None = None


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


class FilterPost(BaseModel):
    """Payload for creating a filter."""

    model_config = ConfigDict(extra="forbid")

    name: str
    stream_id: int
    group_id: int
    broker_id: int | None = None
    altdata: dict[str, Any] | None = None


class FilterPatch(BaseModel):
    """Payload for updating a filter."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    altdata: dict[str, Any] | None = None
    group_id: int | None = None
    stream_id: int | None = None
    autosave: bool | None = None


class FilterPostResponse(BaseModel):
    """Result of creating a filter."""

    model_config = ConfigDict(extra="forbid")

    id: int


def post_filter(client: httpx.Client, payload: FilterPost) -> FilterPostResponse:
    """Create a filter.

    Requires the "Upload data" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : FilterPost
        The filter to create. ``broker_id`` identifies the broker the filter
        runs on, if any, and ``altdata`` holds arbitrary extra JSON.
    """
    response = client.post("/api/filters", json=payload.model_dump(exclude_none=True))
    return FilterPostResponse.model_validate(unwrap(response))


def update_filter(
    client: httpx.Client,
    filter_id: int,
    payload: FilterPatch,
) -> None:
    """Update a filter.

    Only the provided fields are sent; omitted fields are left unchanged.
    ``group_id`` and ``stream_id`` cannot be changed and are accepted only
    when they match the filter's current values. Renaming a filter that is
    attached to a broker also renames it on the broker, and fails if the
    broker rejects the rename. ``autosave`` controls whether objects passing
    the filter during broker ingestion are saved as sources to the filter's
    group. Requires the "Upload data" permission and group- or system-admin
    access to the filter's group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    filter_id : int
        ID of the filter to update.
    payload : FilterPatch
        The fields to change.
    """
    unwrap(
        client.patch(
            f"/api/filters/{filter_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def delete_filter(client: httpx.Client, filter_id: int) -> None:
    """Delete a filter.

    Requires the "Upload data" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    filter_id : int
        ID of the filter to delete.
    """
    unwrap(client.delete(f"/api/filters/{filter_id}"))
