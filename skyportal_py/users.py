"""Typed endpoint functions for ``/api/user``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class User(BaseModel):
    """A SkyPortal user."""

    model_config = ConfigDict(extra="forbid")

    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None
    contact_email: str | None = None


class UsersPage(BaseModel):
    """One page of results from a users query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    users: list[User]
    total_matches: int = Field(alias="totalMatches")


def fetch_users(
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 25,
) -> UsersPage:
    """Query users, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    """
    response = client.get(
        "/api/user",
        params={"pageNumber": page_number, "numPerPage": num_per_page},
    )
    return UsersPage.model_validate(unwrap(response))


def fetch_user(client: httpx.Client, user_id: int) -> User:
    """Retrieve a single user by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    user_id : int
        ID of the user.
    """
    response = client.get(f"/api/user/{user_id}")
    return User.model_validate(unwrap(response))


class UserPost(BaseModel):
    """Payload for adding a new user."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    username: str
    first_name: str | None = None
    last_name: str | None = None
    affiliations: list[str] | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    oauth_uid: str | None = None
    roles: list[str] | None = None
    group_ids_and_admin: list[list[int | bool]] | None = Field(
        alias="groupIDsAndAdmin", default=None
    )


class UserPostResponse(BaseModel):
    """Result of adding a new user."""

    model_config = ConfigDict(extra="forbid")

    id: int


def post_user(client: httpx.Client, payload: UserPost) -> UserPostResponse:
    """Add a new user (requires the "Manage users" ACL).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : UserPost
        The user to add. If ``roles`` is omitted, the server assigns its
        configured default role; if ``group_ids_and_admin`` (pairs of
        ``[group_id, admin]``) is omitted, the server adds the user to its
        default groups.
    """
    response = client.post(
        "/api/user",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return UserPostResponse.model_validate(unwrap(response))


def update_user(
    client: httpx.Client,
    user_id: int,
    *,
    expiration_date: str | None = None,
) -> None:
    """Update a user record (requires the "Manage users" ACL).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    user_id : int
        ID of the user to update.
    expiration_date : str, optional
        Arrow-parseable date string (e.g. ``"2020-01-01"``). After this
        date the account is deactivated and cannot access the application.
    """
    payload: dict[str, str] = {}
    if expiration_date is not None:
        payload["expirationDate"] = expiration_date
    unwrap(client.patch(f"/api/user/{user_id}", json=payload))


def delete_user(client: httpx.Client, user_id: int) -> None:
    """Delete a user (requires the "Manage users" ACL).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    user_id : int
        ID of the user to delete.
    """
    unwrap(client.delete(f"/api/user/{user_id}"))
