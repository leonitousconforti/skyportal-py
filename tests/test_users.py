"""Tests for the typed user endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import users

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_users(client: httpx.Client) -> None:
    """A users response validates into a UsersPage model."""
    route = respx.get(f"{BASE_URL}/api/user").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "users": [
                        {
                            "id": 7,
                            "username": "leo",
                            "first_name": "Leo",
                            "contact_email": "leo@example.com",
                        }
                    ],
                    "totalMatches": 1,
                },
            },
        )
    )
    page = users.fetch_users(client, page_number=2, num_per_page=10)
    assert page.total_matches == 1
    assert page.users[0].username == "leo"
    params = route.calls[0].request.url.params
    assert params["pageNumber"] == "2"
    assert params["numPerPage"] == "10"


@respx.mock
def test_fetch_user(client: httpx.Client) -> None:
    """A user response validates into a User model."""
    respx.get(f"{BASE_URL}/api/user/7").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": 7, "username": "leo", "last_name": "Conforti"},
            },
        )
    )
    user = users.fetch_user(client, 7)
    assert user.id == 7
    assert user.last_name == "Conforti"
