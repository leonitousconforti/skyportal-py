"""Typed endpoint functions for ``/api/shifts``."""

from __future__ import annotations

import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.groups import Group
from skyportal_py.users import User


class ShiftUserMembership(BaseModel):
    """A user's membership in a shift (upstream ``ShiftUser``).

    ``username``, ``first_name`` and ``last_name`` are copied up from the
    nested ``user`` by the single-shift handler.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    shift_id: int | None = None
    user_id: int | None = None
    admin: bool | None = None
    needs_replacement: bool | None = None
    user: User | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None


class ShiftCommentAuthor(User):
    """A shift comment's author, with the gravatar URL the handler adds."""

    gravatar_url: str | None = None


class ShiftComment(BaseModel):
    """A comment posted about a shift (upstream ``CommentOnShift``).

    The handler strips ``attachment_bytes`` and tags each comment with
    ``resourceType``.
    """

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    text: str | None = None
    attachment_name: str | None = None
    origin: str | None = None
    bot: bool | None = None
    author_id: int | None = None
    shift_id: int | None = None
    author: ShiftCommentAuthor | None = None
    groups: list[Group] = Field(default_factory=list)
    resource_type: str | None = Field(alias="resourceType", default=None)


class ShiftGroupMember(BaseModel):
    """A member of a shift's group, as returned alongside a single shift."""

    model_config = ConfigDict(extra="forbid")

    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    expiration_date: datetime.datetime | None = None


class ShiftGroup(BaseModel):
    """A shift's group, as hand-assembled by the single-shift handler."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str | None = None
    has_admin_access: bool | None = None
    group_users: list[ShiftGroupMember] = Field(default_factory=list)


class Shift(BaseModel):
    """A group scanning shift (upstream ``Shift``).

    ``shift_users_ids`` is a column property (an aggregate of the shift's
    user IDs), so it is present even when no relationship is loaded.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    name: str | None = None
    description: str | None = None
    start_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None
    group_id: int | None = None
    required_users_number: int | None = None
    shift_users_ids: list[int] | None = None
    shift_users: list[ShiftUserMembership] = Field(default_factory=list)
    users: list[User] = Field(default_factory=list)
    comments: list[ShiftComment] = Field(default_factory=list)
    reminders: list[dict[str, Any]] = Field(default_factory=list)
    group: ShiftGroup | None = None


class ShiftPost(BaseModel):
    """Payload for creating a new shift."""

    model_config = ConfigDict(extra="forbid")

    name: str
    start_date: str
    end_date: str
    group_id: int
    description: str | None = None
    required_users_number: int | None = None
    shift_admins: list[int] | None = None


class ShiftPostResponse(BaseModel):
    """Result of creating a new shift."""

    model_config = ConfigDict(extra="forbid")

    id: int


class ShiftUserPostResponse(BaseModel):
    """Result of adding a user to a shift."""

    model_config = ConfigDict(extra="forbid")

    shift_id: int
    user_id: int
    admin: bool


class ShiftSummarySection(BaseModel):
    """One section (shifts or GCN events) of a shift summary report."""

    model_config = ConfigDict(extra="forbid")

    total: int | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)


class ShiftSummaryReport(BaseModel):
    """Summary of shift-user activity over a period."""

    model_config = ConfigDict(extra="forbid")

    shifts: ShiftSummarySection | None = None
    gcns: ShiftSummarySection | None = None


def fetch_shift(client: httpx.Client, shift_id: int) -> Shift:
    """Retrieve a single shift by ID.

    Includes the shift's users, comments, and group (with its members).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift.
    """
    response = client.get(f"/api/shifts/{shift_id}")
    return Shift.model_validate(unwrap(response))


def fetch_shifts(
    client: httpx.Client,
    *,
    group_id: int | None = None,
    start_date_limit: str | None = None,
    end_date_limit: str | None = None,
) -> list[Shift]:
    """Retrieve all shifts visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int, optional
        Restrict to shifts belonging to this group.
    start_date_limit : str, optional
        Only return shifts starting at or after this datetime, as an
        ISO-format string, e.g. ``"2024-01-01"``.
    end_date_limit : str, optional
        Only return shifts ending at or after this datetime, as an
        ISO-format string.
    """
    params: dict[str, str | int] = {}
    if group_id is not None:
        params["group_id"] = group_id
    if start_date_limit is not None:
        params["start_date_limit"] = start_date_limit
    if end_date_limit is not None:
        params["end_date_limit"] = end_date_limit
    response = client.get("/api/shifts", params=params)
    return [Shift.model_validate(shift) for shift in unwrap(response)]


def post_shift(client: httpx.Client, payload: ShiftPost) -> ShiftPostResponse:
    """Create a new shift.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : ShiftPost
        The shift to create. ``shift_admins`` lists the IDs of users to
        make admins of the new shift.
    """
    response = client.post("/api/shifts", json=payload.model_dump(exclude_none=True))
    return ShiftPostResponse.model_validate(unwrap(response))


def update_shift(
    client: httpx.Client,
    shift_id: int,
    *,
    name: str | None = None,
    description: str | None = None,
    required_users_number: int | None = None,
) -> None:
    """Update fields of an existing shift.

    Only the provided fields are sent; omitted fields are left unchanged.
    Only a shift admin or an admin of the shift's group can edit it.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift to update.
    name : str, optional
        New name; must be non-empty.
    description : str, optional
        New description.
    required_users_number : int, optional
        New number of users required for the shift to be considered full;
        must be at least 1 and at least the number of users already
        signed up.
    """
    fields = {
        "name": name,
        "description": description,
        "required_users_number": required_users_number,
    }
    payload = {key: value for key, value in fields.items() if value is not None}
    unwrap(client.patch(f"/api/shifts/{shift_id}", json=payload))


def delete_shift(client: httpx.Client, shift_id: int) -> None:
    """Delete a shift.

    Only a shift admin or an admin of the shift's group can delete it.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift to delete.
    """
    unwrap(client.delete(f"/api/shifts/{shift_id}"))


def post_shift_user(
    client: httpx.Client,
    shift_id: int,
    user_id: int,
    *,
    admin: bool = False,
    needs_replacement: bool = False,
) -> ShiftUserPostResponse:
    """Add a user to a shift.

    Fails if the user is already a member of the shift, or if the shift
    has reached its required number of users.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift.
    user_id : int
        ID of the user to add.
    admin : bool, optional
        Make the user an admin of the shift.
    needs_replacement : bool, optional
        Mark the user as needing a replacement for the shift.
    """
    payload = {
        "userID": user_id,
        "admin": admin,
        "needs_replacement": needs_replacement,
    }
    response = client.post(f"/api/shifts/{shift_id}/users", json=payload)
    return ShiftUserPostResponse.model_validate(unwrap(response))


def update_shift_user(
    client: httpx.Client,
    shift_id: int,
    user_id: int,
    *,
    admin: bool | None = None,
    needs_replacement: bool = False,
) -> None:
    """Update a shift user's admin or needs-replacement status.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift.
    user_id : int
        ID of the shift user to update.
    admin : bool, optional
        New admin status. If omitted, the current status is kept.
    needs_replacement : bool, optional
        Mark the user as needing a replacement; this notifies the other
        members of the shift's group. The server resets this flag to
        ``False`` when omitted.
    """
    payload: dict[str, bool] = {"needs_replacement": needs_replacement}
    if admin is not None:
        payload["admin"] = admin
    unwrap(client.patch(f"/api/shifts/{shift_id}/users/{user_id}", json=payload))


def delete_shift_user(client: httpx.Client, shift_id: int, user_id: int) -> None:
    """Remove a user from a shift.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int
        ID of the shift.
    user_id : int
        ID of the user to remove.
    """
    unwrap(client.delete(f"/api/shifts/{shift_id}/users/{user_id}"))


def fetch_shift_summary(
    client: httpx.Client,
    shift_id: int | None = None,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
) -> ShiftSummaryReport:
    """Retrieve a summary of shift-user activity over a period.

    Provide either ``shift_id``, or both ``start_date`` and ``end_date``
    (a period of at most four weeks). The report lists the matching
    shifts and the GCN events observed during them.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    shift_id : int, optional
        Summarize this single shift.
    start_date, end_date : str, optional
        Summarize shifts starting in this date range, as ISO-format date
        strings, e.g. ``"2024-01-01"``.
    """
    path = "/api/shifts/summary"
    if shift_id is not None:
        path = f"{path}/{shift_id}"
    params: dict[str, str] = {}
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    response = client.get(path, params=params)
    return ShiftSummaryReport.model_validate(unwrap(response))
