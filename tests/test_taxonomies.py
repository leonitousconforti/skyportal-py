"""Tests for the typed taxonomy endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import taxonomies

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_taxonomies(client: httpx.Client) -> None:
    """A taxonomy list response validates into Taxonomy models."""
    respx.get(f"{BASE_URL}/api/taxonomy").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 1,
                        "name": "Sitewide taxonomy",
                        "version": "1.2.0",
                        "provenance": "https://github.com/profjsb/timedomain-taxonomy",
                        "isLatest": True,
                        "hierarchy": {"class": "Time-domain Source"},
                    }
                ],
            },
        )
    )
    result = taxonomies.fetch_taxonomies(client)
    assert len(result) == 1
    assert result[0].is_latest is True
    assert result[0].hierarchy == {"class": "Time-domain Source"}


@respx.mock
def test_fetch_taxonomy(client: httpx.Client) -> None:
    """A taxonomy response validates into a Taxonomy model."""
    respx.get(f"{BASE_URL}/api/taxonomy/1").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": 1, "name": "Sitewide taxonomy", "isLatest": False},
            },
        )
    )
    taxonomy = taxonomies.fetch_taxonomy(client, 1)
    assert taxonomy.id == 1
    assert taxonomy.is_latest is False
