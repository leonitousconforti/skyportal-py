"""Typed endpoint functions for ``/api/groups``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class Group(BaseModel):
    """A SkyPortal group."""

    model_config = ConfigDict(extra="forbid")

    id: int
    name: str
    nickname: str | None = None
    single_user_group: bool = False


class GroupsResponse(BaseModel):
    """The groups visible to the token, split by relationship to the user."""

    model_config = ConfigDict(extra="forbid")

    user_groups: list[Group] = Field(default_factory=list)
    user_accessible_groups: list[Group] = Field(default_factory=list)
    all_groups: list[Group] | None = None


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
