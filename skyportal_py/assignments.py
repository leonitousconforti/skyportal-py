"""Typed endpoint functions for ``/api/assignment``."""

from __future__ import annotations

import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.users import User

FollowupPriority = Literal["1", "2", "3", "4", "5"]
"""Allowed follow-up priorities, lowest (``"1"``) to highest (``"5"``)."""


class Assignment(BaseModel):
    """A target assignment on an observing run (upstream ``ClassicalAssignment``).

    ``obj`` stays ``dict`` because typing it as
    :class:`skyportal_py.sources.Source` would create an import cycle.
    ``/api/assignment`` serializes through the auto-generated marshmallow
    schema, so relationships other than ``obj`` and ``requester`` dump as
    bare primary keys; ``/api/observing_run/<id>`` instead returns
    ``to_dict()`` output plus the last-detection and rise/set extras.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    obj_id: str | None = None
    run_id: int | None = None
    requester_id: int | None = None
    last_modified_by_id: int | None = None
    status: str | None = None
    priority: FollowupPriority | None = None
    comment: str | None = None
    obj: dict[str, Any] | None = None
    requester: User | None = None
    last_modified_by: int | None = None
    run: int | None = None
    spectra: list[int] = Field(default_factory=list)
    photometry: list[int] = Field(default_factory=list)
    photometric_series: list[int] = Field(default_factory=list)
    rise_time_utc: str | None = None
    set_time_utc: str | None = None
    accessible_group_names: list[str] = Field(default_factory=list)
    last_detected_mag: float | None = None
    last_detected_filter: str | None = None
    last_detected_mjd: float | None = None


class AssignmentPost(BaseModel):
    """Payload for assigning a target to an observing run."""

    model_config = ConfigDict(extra="forbid")

    run_id: int
    obj_id: str
    priority: FollowupPriority
    status: str | None = None
    comment: str | None = None


class AssignmentPostResponse(BaseModel):
    """Result of posting an assignment."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_assignment(client: httpx.Client, assignment_id: int) -> Assignment:
    """Retrieve a single observing-run assignment by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    assignment_id : int
        ID of the assignment.
    """
    response = client.get(f"/api/assignment/{assignment_id}")
    return Assignment.model_validate(unwrap(response))


def fetch_assignments(client: httpx.Client) -> list[Assignment]:
    """Retrieve all observing-run assignments visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/assignment")
    return [Assignment.model_validate(item) for item in unwrap(response)]


def post_assignment(
    client: httpx.Client,
    payload: AssignmentPost,
) -> AssignmentPostResponse:
    """Assign a target to a classical observing run.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : AssignmentPost
        The assignment to create. ``priority`` is a string from ``"1"``
        (lowest) to ``"5"`` (highest). The server rejects the assignment
        if the object is already assigned to the run.
    """
    response = client.post(
        "/api/assignment", json=payload.model_dump(exclude_none=True)
    )
    return AssignmentPostResponse.model_validate(unwrap(response))


def update_assignment(
    client: httpx.Client,
    assignment_id: int,
    *,
    comment: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> None:
    """Update an observing-run assignment.

    Only the provided fields are sent; omitted fields are left unchanged.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    assignment_id : int
        ID of the assignment to update.
    comment : str, optional
        New comment on the assignment.
    status : str, optional
        New status, e.g. ``"done"``, ``"not done"``, or ``"pending"``.
    priority : str, optional
        New priority, from ``"1"`` (lowest) to ``"5"`` (highest).
    """
    fields = {"comment": comment, "status": status, "priority": priority}
    payload = {name: value for name, value in fields.items() if value is not None}
    unwrap(client.put(f"/api/assignment/{assignment_id}", json=payload))


def delete_assignment(client: httpx.Client, assignment_id: int) -> None:
    """Delete an observing-run assignment.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    assignment_id : int
        ID of the assignment to delete.
    """
    unwrap(client.delete(f"/api/assignment/{assignment_id}"))
