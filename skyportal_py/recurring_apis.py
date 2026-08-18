"""Typed endpoint functions for ``/api/recurring_api``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class RecurringAPI(BaseModel):
    """A recurring API call scheduled by a user."""

    model_config = ConfigDict(extra="forbid")

    id: int
    endpoint: str | None = None
    method: str | None = None
    payload: Any = None
    next_call: str | None = None
    call_delay: float | None = None
    number_of_retries: int | None = None
    active: bool | None = None
    owner_id: int | None = None
    owner: dict[str, Any] | None = None
    created_at: str | None = None
    modified: str | None = None


class RecurringAPIPost(BaseModel):
    """Payload for scheduling a recurring API call."""

    model_config = ConfigDict(extra="forbid")

    endpoint: str
    method: str
    next_call: str
    call_delay: float
    payload: str
    number_of_retries: int | None = None


class RecurringAPIPostResponse(BaseModel):
    """Result of scheduling a recurring API call."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_recurring_apis(client: httpx.Client) -> list[RecurringAPI]:
    """Retrieve every recurring API call the token can access.

    The server decodes each ``payload`` from its stored JSON string, so
    ``payload`` is a mapping here even though it is a string on creation.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/recurring_api")
    return [RecurringAPI.model_validate(item) for item in unwrap(response)]


def fetch_recurring_api(client: httpx.Client, recurring_api_id: int) -> RecurringAPI:
    """Retrieve a single recurring API call by ID.

    Unlike :func:`fetch_recurring_apis`, the server returns ``payload``
    exactly as stored.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    recurring_api_id : int
        ID of the recurring API call to retrieve.
    """
    response = client.get(f"/api/recurring_api/{recurring_api_id}")
    return RecurringAPI.model_validate(unwrap(response))


def post_recurring_api(
    client: httpx.Client,
    payload: RecurringAPIPost,
) -> RecurringAPIPostResponse:
    """Schedule a recurring API call (requires "Manage Recurring APIs").

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : RecurringAPIPost
        The call to schedule. ``method`` is upper-cased by the server and must
        end up as ``"GET"`` or ``"POST"``, ``payload`` must be a valid JSON
        string, ``next_call`` is any arrow-parseable timestamp, ``call_delay``
        is in days, and ``number_of_retries`` may not exceed ``10``.
    """
    response = client.post(
        "/api/recurring_api",
        json=payload.model_dump(exclude_none=True),
    )
    return RecurringAPIPostResponse.model_validate(unwrap(response))


def delete_recurring_api(client: httpx.Client, recurring_api_id: int) -> None:
    """Delete a recurring API call (requires "Manage Recurring APIs").

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    recurring_api_id : int
        ID of the recurring API call to delete; only its owner may delete it.
    """
    unwrap(client.delete(f"/api/recurring_api/{recurring_api_id}"))
