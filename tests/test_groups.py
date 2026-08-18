"""Tests for the typed groups endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import groups

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_groups(client: httpx.Client) -> None:
    """The groups response validates into a GroupsResponse model."""
    route = respx.get(f"{BASE_URL}/api/groups").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "user_groups": [{"id": 1, "name": "Program A"}],
                    "user_accessible_groups": [
                        {"id": 1, "name": "Program A"},
                        {"id": 2, "name": "Program B", "nickname": "progB"},
                    ],
                    "all_groups": None,
                },
            },
        )
    )
    result = groups.fetch_groups(client, include_single_user_groups=True)
    assert [g.id for g in result.user_groups] == [1]
    assert result.user_accessible_groups[1].nickname == "progB"
    assert result.all_groups is None
    params = route.calls[0].request.url.params
    assert params["includeSingleUserGroups"] == "true"


@respx.mock
def test_fetch_group(client: httpx.Client) -> None:
    """A group response validates into a Group model."""
    respx.get(f"{BASE_URL}/api/groups/1").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "id": 1,
                    "name": "Program A",
                    "single_user_group": False,
                },
            },
        )
    )
    group = groups.fetch_group(client, 1)
    assert group.id == 1
    assert group.name == "Program A"
    assert group.single_user_group is False
