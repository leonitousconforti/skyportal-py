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
