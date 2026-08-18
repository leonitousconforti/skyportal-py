"""Tests for the typed instrument endpoint functions."""

from __future__ import annotations

import httpx
import respx

from skyportal_py import instruments

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_instruments(client: httpx.Client) -> None:
    """An instrument list response validates into Instrument models."""
    respx.get(f"{BASE_URL}/api/instrument").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 3,
                        "name": "ZTF Camera",
                        "type": "imager",
                        "band": "optical",
                        "telescope_id": 1,
                        "filters": ["ztfg", "ztfr", "ztfi"],
                    }
                ],
            },
        )
    )
    result = instruments.fetch_instruments(client)
    assert len(result) == 1
    assert result[0].name == "ZTF Camera"
    assert result[0].filters == ["ztfg", "ztfr", "ztfi"]


@respx.mock
def test_fetch_instrument(client: httpx.Client) -> None:
    """An instrument response validates into an Instrument model."""
    respx.get(f"{BASE_URL}/api/instrument/3").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": 3, "name": "ZTF Camera", "telescope_id": 1},
            },
        )
    )
    instrument = instruments.fetch_instrument(client, 3)
    assert instrument.id == 3
    assert instrument.telescope_id == 1
