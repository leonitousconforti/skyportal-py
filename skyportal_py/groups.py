"""Typed endpoint functions for ``/api/groups``."""

from __future__ import annotations

import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.filters import Filter
from skyportal_py.streams import Stream


class GroupMember(BaseModel):
    """A group member as assembled by the ``GET /api/groups/{id}`` handler."""

    # The handler hand-builds this dict from a ``GroupUser`` and its ``User``
    # rather than serializing either model, so it is not a 1:1 upstream model.

    model_config = ConfigDict(extra="forbid")

    id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    oauth_uid: str | None = None
    admin: bool | None = None
    can_save: bool | None = None
    can_share_photometry: bool | None = None


class Group(BaseModel):
    """A SkyPortal group (upstream ``Group``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    name: str
    nickname: str | None = None
    description: str | None = None
    private: bool | None = None
    auto_accept_requests: bool | None = None
    single_user_group: bool = False
    streams: list[Stream] | None = None
    filters: list[Filter] | None = None
    group_users: list[GroupUser] | None = None
    users: list[GroupMember] | None = None


class GroupUser(BaseModel):
    """A user's membership of a group (upstream ``GroupUser`` join model)."""

    # ``user`` stays ``dict[str, Any]``: typing it as ``users.User`` would make
    # groups -> users -> groups a circular import.

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    group_id: int | None = None
    user_id: int | None = None
    admin: bool | None = None
    can_save: bool | None = None
    can_share_photometry: bool | None = None
    user: dict[str, Any] | None = None
    group: Group | None = None


Group.model_rebuild()


class GroupsResponse(BaseModel):
    """The groups visible to the token, split by relationship to the user."""

    model_config = ConfigDict(extra="forbid")

    user_groups: list[Group] = Field(default_factory=list)
    user_accessible_groups: list[Group] = Field(default_factory=list)
    all_groups: list[Group] | None = None


class GroupPost(BaseModel):
    """Payload for creating a group."""

    model_config = ConfigDict(extra="forbid")

    name: str
    nickname: str | None = None
    description: str | None = None
    auto_accept_requests: bool | None = None
    group_admins: list[int] | None = None


class GroupPostResponse(BaseModel):
    """Result of creating a group."""

    model_config = ConfigDict(extra="forbid")

    id: int


class GroupStreamPostResponse(BaseModel):
    """Result of granting a group access to a stream."""

    model_config = ConfigDict(extra="forbid")

    group_id: int
    stream_id: int


class GroupUserPostResponse(BaseModel):
    """Result of adding a user to a group."""

    model_config = ConfigDict(extra="forbid")

    group_id: int
    user_id: int
    admin: bool


def fetch_groups(
    client: httpx.Client,
    *,
    include_single_user_groups: bool = False,
) -> GroupsResponse:
    """Retrieve the groups the token's user belongs to or can access.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    include_single_user_groups : bool, optional
        Also include each user's implicit single-user group.
    """
    response = client.get(
        "/api/groups",
        params={"includeSingleUserGroups": include_single_user_groups},
    )
    return GroupsResponse.model_validate(unwrap(response))


def fetch_group(client: httpx.Client, group_id: int) -> Group:
    """Retrieve a single group by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    """
    response = client.get(f"/api/groups/{group_id}")
    return Group.model_validate(unwrap(response))


def post_group(client: httpx.Client, payload: GroupPost) -> GroupPostResponse:
    """Create a new group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : GroupPost
        The group to create. ``name`` must not collide with an existing
        group. ``group_admins`` lists user IDs to make group admins; the
        current user is added as an admin automatically.
    """
    response = client.post("/api/groups", json=payload.model_dump(exclude_none=True))
    return GroupPostResponse.model_validate(unwrap(response))


def update_group(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    group_id: int,
    name: str,
    *,
    nickname: str | None = None,
    description: str | None = None,
    private: bool | None = None,
    auto_accept_requests: bool | None = None,
) -> None:
    """Update an existing group.

    Only the provided fields are sent; omitted fields are left unchanged.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group to update.
    name : str
        The group name; required by the server even if unchanged.
    nickname, description : str, optional
        New nickname and description.
    private : bool, optional
        Whether the group is private.
    auto_accept_requests : bool, optional
        Whether admission requests to the group are accepted automatically.
    """
    fields = {
        "nickname": nickname,
        "description": description,
        "private": private,
        "auto_accept_requests": auto_accept_requests,
    }
    payload: dict[str, str | bool] = {"name": name}
    payload.update({key: value for key, value in fields.items() if value is not None})
    unwrap(client.put(f"/api/groups/{group_id}", json=payload))


def delete_group(client: httpx.Client, group_id: int) -> None:
    """Delete a group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group to delete.
    """
    unwrap(client.delete(f"/api/groups/{group_id}"))


def fetch_public_group(client: httpx.Client) -> Group:
    """Retrieve the server's configured public group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/groups/public")
    return Group.model_validate(unwrap(response))


def post_group_stream(
    client: httpx.Client,
    group_id: int,
    stream_id: int,
) -> GroupStreamPostResponse:
    """Grant a group access to an alert stream.

    Every member of the group must already have access to the stream.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    stream_id : int
        ID of the stream to associate with the group.
    """
    response = client.post(
        f"/api/groups/{group_id}/streams", json={"stream_id": stream_id}
    )
    return GroupStreamPostResponse.model_validate(unwrap(response))


def delete_group_stream(client: httpx.Client, group_id: int, stream_id: int) -> None:
    """Remove an alert stream from a group.

    Fails if one of the group's filters still operates on the stream.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    stream_id : int
        ID of the stream to remove from the group.
    """
    unwrap(client.delete(f"/api/groups/{group_id}/streams/{stream_id}"))


def post_group_user(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    group_id: int,
    user_id: int,
    *,
    admin: bool = False,
    can_save: bool = True,
    can_share_photometry: bool = False,
) -> GroupUserPostResponse:
    """Add a user to a group.

    The user must already have access to every stream of the group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    user_id : int
        ID of the user to add.
    admin : bool, optional
        Make the user a group admin.
    can_save : bool, optional
        Allow the user to save sources to the group.
    can_share_photometry : bool, optional
        Allow the user to share the group's photometry with other groups.
    """
    response = client.post(
        f"/api/groups/{group_id}/users",
        json={
            "userID": user_id,
            "admin": admin,
            "canSave": can_save,
            "canSharePhotometry": can_share_photometry,
        },
    )
    return GroupUserPostResponse.model_validate(unwrap(response))


def update_group_user(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    group_id: int,
    user_id: int,
    *,
    admin: bool | None = None,
    can_save: bool | None = None,
    can_share_photometry: bool | None = None,
) -> None:
    """Update a group member's admin or save-access status.

    At least one of ``admin``, ``can_save``, or ``can_share_photometry``
    must be provided; omitted flags are left unchanged.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    user_id : int
        ID of the group member to update.
    admin : bool, optional
        Whether the user is a group admin.
    can_save : bool, optional
        Whether the user can save sources to the group.
    can_share_photometry : bool, optional
        Whether the user can share the group's photometry with other groups.
    """
    fields = {
        "admin": admin,
        "canSave": can_save,
        "canSharePhotometry": can_share_photometry,
    }
    payload: dict[str, int | bool] = {"userID": user_id}
    payload.update({key: value for key, value in fields.items() if value is not None})
    unwrap(client.patch(f"/api/groups/{group_id}/users", json=payload))


def delete_group_user(client: httpx.Client, group_id: int, user_id: int) -> None:
    """Remove a user from a group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group.
    user_id : int
        ID of the group member to remove.
    """
    unwrap(client.delete(f"/api/groups/{group_id}/users/{user_id}"))


def post_group_users_from_groups(
    client: httpx.Client,
    group_id: int,
    from_group_ids: list[int],
) -> None:
    """Add all members of other groups to the specified group.

    Users already in the target group are skipped.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    group_id : int
        ID of the group to add users to.
    from_group_ids : list of int
        IDs of the groups whose members should be added.
    """
    unwrap(
        client.post(
            f"/api/groups/{group_id}/usersFromGroups",
            json={"fromGroupIDs": from_group_ids},
        )
    )
