"""Tests for the typed photometry endpoint functions."""

from __future__ import annotations

import json

import httpx
import respx

from skyportal_py import photometry

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_photometry(client: httpx.Client) -> None:
    """A photometry response validates into a list of PhotometryPoint."""
    route = respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/photometry").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 100,
                        "obj_id": "ZTF20abcdef",
                        "mjd": 59000.5,
                        "mag": 18.2,
                        "magerr": 0.05,
                        "filter": "ztfg",
                        "instrument_id": 1,
                    },
                    {
                        "id": 101,
                        "obj_id": "ZTF20abcdef",
                        "mjd": 59001.5,
                        "mag": None,
                        "limiting_mag": 20.5,
                        "filter": "ztfr",
                    },
                ],
            },
        )
    )
    points = photometry.fetch_photometry(client, "ZTF20abcdef", format="mag")
    assert [p.id for p in points] == [100, 101]
    assert points[0].mag == 18.2
    assert points[1].mag is None
    assert points[1].limiting_mag == 20.5
    params = route.calls[0].request.url.params
    assert params["format"] == "mag"
    assert params["magsys"] == "ab"


@respx.mock
def test_post_photometry(client: httpx.Client) -> None:
    """The payload model is sent with unset fields omitted."""
    route = respx.post(f"{BASE_URL}/api/photometry").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"ids": [100]}},
        )
    )
    result = photometry.post_photometry(
        client,
        photometry.PhotometryPost(
            obj_id="ZTF20abcdef",
            mjd=59000.5,
            instrument_id=1,
            filter="ztfg",
            mag=18.2,
            magerr=0.05,
            limiting_mag=20.5,
        ),
    )
    assert result.ids == [100]
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "obj_id": "ZTF20abcdef",
        "mjd": 59000.5,
        "instrument_id": 1,
        "filter": "ztfg",
        "magsys": "ab",
        "mag": 18.2,
        "magerr": 0.05,
        "limiting_mag": 20.5,
    }
