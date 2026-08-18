"""Typed endpoint functions for ``/api/internal/profile``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class UserProfile(BaseModel):
    """The user associated with the API token."""

    model_config = ConfigDict(extra="allow")

    username: str
    first_name: str | None = None
    last_name: str | None = None
    contact_email: str | None = None
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    acls: list[str] = Field(default_factory=list)
    preferences: dict[str, Any] = Field(default_factory=dict)
    gravatar_url: str | None = None


def fetch_profile(client: httpx.Client) -> UserProfile:
    """Retrieve the profile of the user associated with the token."""
    return UserProfile.model_validate(unwrap(client.get("/api/internal/profile")))
