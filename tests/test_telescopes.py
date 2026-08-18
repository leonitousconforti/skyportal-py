"""Tests for the typed telescope endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import telescopes

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_telescopes(client: httpx.Client) -> None:
    """A telescope list response validates into Telescope models."""
    respx.get(f"{BASE_URL}/api/telescope").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 1,
                        "name": "Palomar 48 inch",
                        "nickname": "P48",
                        "lat": 33.36,
                        "lon": -116.86,
                        "elevation": 1712.0,
                        "diameter": 1.2,
                        "robotic": True,
                    }
                ],
            },
        )
    )
    result = telescopes.fetch_telescopes(client)
    assert len(result) == 1
    assert result[0].nickname == "P48"
    assert result[0].robotic is True


@respx.mock
def test_fetch_telescope(client: httpx.Client) -> None:
    """A telescope response validates into a Telescope model."""
    respx.get(f"{BASE_URL}/api/telescope/1").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": 1, "name": "Palomar 48 inch"},
            },
        )
    )
    telescope = telescopes.fetch_telescope(client, 1)
    assert telescope.id == 1
    assert telescope.robotic is False
