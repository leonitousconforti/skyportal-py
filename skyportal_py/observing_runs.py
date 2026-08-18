"""Typed endpoint functions for ``/api/observing_run``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class ObservingRun(BaseModel):
    """A classical observing run on an instrument."""

    model_config = ConfigDict(extra="forbid")

    id: int
    instrument_id: int
    calendar_date: str | None = None
    pi: str | None = None
    observers: str | None = None
    group_id: int | None = None


class ObservingRunPost(BaseModel):
    """Payload for creating an observing run."""

    model_config = ConfigDict(extra="forbid")

    instrument_id: int
    calendar_date: str
    pi: str | None = None
    observers: str | None = None
    duration: int | None = None
    group_id: int | None = None


class ObservingRunPostResponse(BaseModel):
    """Result of creating an observing run."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_observing_runs(client: httpx.Client) -> list[ObservingRun]:
    """Retrieve all observing runs.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/observing_run")
    return [ObservingRun.model_validate(item) for item in unwrap(response)]


def fetch_observing_run(client: httpx.Client, run_id: int) -> ObservingRun:
    """Retrieve a single observing run by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    run_id : int
        ID of the observing run.
    """
    response = client.get(f"/api/observing_run/{run_id}")
    return ObservingRun.model_validate(unwrap(response))


def post_observing_run(
    client: httpx.Client,
    payload: ObservingRunPost,
) -> ObservingRunPostResponse:
    """Create an observing run.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : ObservingRunPost
        The run to create. ``calendar_date`` is the local calendar date of
        the run in ISO format, e.g. ``"2026-09-01"``; ``duration`` is the
        number of nights.
    """
    response = client.post(
        "/api/observing_run", json=payload.model_dump(exclude_none=True)
    )
    return ObservingRunPostResponse.model_validate(unwrap(response))


def delete_observing_run(client: httpx.Client, run_id: int) -> None:
    """Delete an observing run.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    run_id : int
        ID of the observing run to delete.
    """
    unwrap(client.delete(f"/api/observing_run/{run_id}"))
