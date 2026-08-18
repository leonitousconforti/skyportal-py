"""Tests for the typed filter endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import filters

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_filters(client: httpx.Client) -> None:
    """A filter list response validates into Filter models."""
    respx.get(f"{BASE_URL}/api/filters").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 4,
                        "name": "Bright transients",
                        "group_id": 1,
                        "stream_id": 2,
                    }
                ],
            },
        )
    )
    result = filters.fetch_filters(client)
    assert len(result) == 1
    assert result[0].name == "Bright transients"
    assert result[0].stream_id == 2


@respx.mock
def test_fetch_filter(client: httpx.Client) -> None:
    """A filter response validates into a Filter model."""
    respx.get(f"{BASE_URL}/api/filters/4").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": 4, "name": "Bright transients", "group_id": 1},
            },
        )
    )
    result = filters.fetch_filter(client, 4)
    assert result.id == 4
    assert result.group_id == 1
