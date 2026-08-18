"""Tests for the typed profile endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import profile

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_profile(client: httpx.Client) -> None:
    """The profile response validates into a UserProfile model."""
    respx.get(f"{BASE_URL}/api/internal/profile").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "username": "leo",
                    "first_name": "Leo",
                    "roles": ["Full user"],
                    "permissions": ["Comment"],
                    "acls": ["Comment"],
                    "preferences": {"theme": "dark"},
                },
            },
        )
    )
    user = profile.fetch_profile(client)
    assert user.username == "leo"
    assert user.roles == ["Full user"]
    assert user.preferences["theme"] == "dark"
    assert user.gravatar_url is None
