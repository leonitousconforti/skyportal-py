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


class ObservingRunUpdate(BaseModel):
    """Payload for updating an observing run; every field is optional."""

    model_config = ConfigDict(extra="forbid")

    instrument_id: int | None = None
    calendar_date: str | None = None
    pi: str | None = None
    observers: str | None = None
    duration: int | None = None
    group_id: int | None = None


def update_observing_run(
    client: httpx.Client,
    run_id: int,
    payload: ObservingRunUpdate,
) -> None:
    """Update an observing run.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    run_id : int
        ID of the observing run to update. Only the owner of a run may
        modify it.
    payload : ObservingRunUpdate
        Fields to change. The run's end time is recomputed server-side
        afterwards.
    """
    unwrap(
        client.put(
            f"/api/observing_run/{run_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def update_observing_run_not_observed(
    client: httpx.Client,
    run_id: int,
    current_status: str,
    new_status: str,
) -> None:
    """Bulk-restatus the assignments of an observing run.

    Every assignment on the run whose status equals ``current_status`` is
    moved to ``new_status``; the others are left alone.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    run_id : int
        ID of the observing run.
    current_status : str
        Status an assignment must currently have to be updated, e.g.
        ``"pending"``.
    new_status : str
        Status to apply, e.g. ``"not observed"``.
    """
    unwrap(
        client.put(
            f"/api/observing_run/{run_id}/not_observed",
            json={"current_status": current_status, "new_status": new_status},
        )
    )
