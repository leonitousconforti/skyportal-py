"""Typed endpoint functions for ``/api/{resource_type}/{id}/reminders``."""

from __future__ import annotations

from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.groups import Group

ReminderResourceType = Literal[
    "source",
    "spectra",
    "gcn_event",
    "shift",
    "earthquake",
]


class Reminder(BaseModel):
    """A reminder attached to a source, spectrum, GCN event, shift or earthquake."""

    model_config = ConfigDict(extra="forbid")

    id: int
    text: str | None = None
    origin: str | None = None
    bot: bool | None = None
    next_reminder: str | None = None
    reminder_delay: float | None = None
    number_of_reminders: int | None = None
    user_id: int | None = None
    obj_id: str | None = None
    spectrum_id: int | None = None
    gcn_id: int | None = None
    earthquake_id: int | None = None
    shift_id: int | None = None
    created_at: str | None = None
    modified: str | None = None
    groups: list[Group] | None = None
    user: dict[str, Any] | None = None


class RemindersResponse(BaseModel):
    """All reminders attached to one resource."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    resource_id: str = Field(alias="resourceId")
    resource_type: str = Field(alias="resourceType")
    reminders: list[Reminder] = Field(default_factory=list)


class ReminderPost(BaseModel):
    """Payload for creating reminders on a resource."""

    model_config = ConfigDict(extra="forbid")

    text: str
    next_reminder: str
    reminder_delay: float | None = None
    number_of_reminders: int | None = None
    group_ids: list[int] | None = None
    user_ids: list[int] | None = None


class ReminderPostResponse(BaseModel):
    """IDs of the reminders created by a post."""

    model_config = ConfigDict(extra="forbid")

    reminder_ids: list[int] = Field(default_factory=list)


class ReminderUpdate(BaseModel):
    """Payload for updating an existing reminder."""

    model_config = ConfigDict(extra="forbid")

    text: str | None = None
    origin: str | None = None
    bot: bool | None = None
    next_reminder: str | None = None
    reminder_delay: float | None = None
    number_of_reminders: int | None = None
    group_ids: list[int] | None = None
    user_ids: list[int] | None = None


def fetch_reminders(
    client: httpx.Client,
    resource_id: str,
    *,
    resource_type: ReminderResourceType = "source",
) -> RemindersResponse:
    """Retrieve every reminder attached to one resource.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str
        ID of the resource the reminders are on: an object ID for
        ``"source"``, otherwise the integer ID of the spectrum, GCN event,
        shift or earthquake.
    resource_type : str, optional
        What the reminders are on: ``"source"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``. Note the route uses
        the singular ``"source"``.
    """
    response = client.get(f"/api/{resource_type}/{resource_id}/reminders")
    return RemindersResponse.model_validate(unwrap(response))


def fetch_reminder(
    client: httpx.Client,
    resource_id: str,
    reminder_id: int,
    *,
    resource_type: ReminderResourceType = "source",
) -> Reminder:
    """Retrieve a single reminder by ID.

    The server rejects the request if the reminder is not attached to
    ``resource_id``.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str
        ID of the resource the reminder is on.
    reminder_id : int
        ID of the reminder to retrieve.
    resource_type : str, optional
        What the reminder is on; see :func:`fetch_reminders`.
    """
    path = f"/api/{resource_type}/{resource_id}/reminders/{reminder_id}"
    return Reminder.model_validate(unwrap(client.get(path)))


def post_reminder(
    client: httpx.Client,
    resource_id: str,
    payload: ReminderPost,
    *,
    resource_type: ReminderResourceType = "source",
) -> ReminderPostResponse:
    """Create reminders on a resource, one per target user.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str
        ID of the resource to attach the reminders to.
    payload : ReminderPost
        The reminder to create. If ``user_ids`` is omitted the reminder is
        created for the requesting user only, and if ``group_ids`` is omitted
        it is visible to all of the requesting user's groups. The server
        defaults ``reminder_delay`` and ``number_of_reminders`` to ``1``.
    resource_type : str, optional
        What the reminder is on; see :func:`fetch_reminders`.
    """
    response = client.post(
        f"/api/{resource_type}/{resource_id}/reminders",
        json=payload.model_dump(exclude_none=True),
    )
    return ReminderPostResponse.model_validate(unwrap(response))


def update_reminder(
    client: httpx.Client,
    resource_id: str,
    reminder_id: int,
    payload: ReminderUpdate,
    *,
    resource_type: ReminderResourceType = "source",
) -> None:
    """Update an existing reminder.

    Only the provided fields are sent; omitted fields are left unchanged.
    Omitting ``group_ids`` resets visibility to all of the requesting user's
    groups, and omitting ``user_ids`` resets the reminder to the requesting
    user.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str
        ID of the resource the reminder is on.
    reminder_id : int
        ID of the reminder to update.
    payload : ReminderUpdate
        The fields to change.
    resource_type : str, optional
        What the reminder is on; see :func:`fetch_reminders`.
    """
    unwrap(
        client.patch(
            f"/api/{resource_type}/{resource_id}/reminders/{reminder_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def delete_reminder(
    client: httpx.Client,
    resource_id: str,
    reminder_id: int,
    *,
    resource_type: ReminderResourceType = "source",
) -> None:
    """Delete a reminder.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str
        ID of the resource the reminder is on.
    reminder_id : int
        ID of the reminder to delete.
    resource_type : str, optional
        What the reminder is on; see :func:`fetch_reminders`.
    """
    path = f"/api/{resource_type}/{resource_id}/reminders/{reminder_id}"
    unwrap(client.delete(path))
