"""Tests for the typed spectra endpoint functions."""

from __future__ import annotations

import json

import httpx
import respx

from skyportal_py import spectra

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_spectrum(client: httpx.Client) -> None:
    """A spectrum response validates into a Spectrum model."""
    respx.get(f"{BASE_URL}/api/spectrum/12").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "id": 12,
                    "obj_id": "ZTF20abcdef",
                    "instrument_id": 3,
                    "wavelengths": [4000.0, 4001.0],
                    "fluxes": [1.2, 1.3],
                    "observed_at": "2026-08-18T00:00:00",
                },
            },
        )
    )
    spectrum = spectra.fetch_spectrum(client, 12)
    assert spectrum.id == 12
    assert spectrum.obj_id == "ZTF20abcdef"
    assert spectrum.wavelengths == [4000.0, 4001.0]


@respx.mock
def test_fetch_spectra(client: httpx.Client) -> None:
    """A source's spectra unwrap from the enclosing object."""
    respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/spectra").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "obj_id": "ZTF20abcdef",
                    "spectra": [
                        {
                            "id": 12,
                            "obj_id": "ZTF20abcdef",
                            "instrument_id": 3,
                            "wavelengths": [4000.0],
                            "fluxes": [1.2],
                        }
                    ],
                },
            },
        )
    )
    result = spectra.fetch_spectra(client, "ZTF20abcdef")
    assert len(result) == 1
    assert result[0].instrument_id == 3


@respx.mock
def test_fetch_spectra_bare_list(client: httpx.Client) -> None:
    """Older servers return the spectra as a bare list."""
    respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/spectra").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 12,
                        "obj_id": "ZTF20abcdef",
                        "instrument_id": 3,
                    }
                ],
            },
        )
    )
    result = spectra.fetch_spectra(client, "ZTF20abcdef")
    assert len(result) == 1
    assert result[0].id == 12


@respx.mock
def test_post_spectrum(client: httpx.Client) -> None:
    """The payload is serialized without unset optional fields."""
    route = respx.post(f"{BASE_URL}/api/spectrum").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"id": 12}},
        )
    )
    payload = spectra.SpectrumPost(
        obj_id="ZTF20abcdef",
        instrument_id=3,
        observed_at="2026-08-18T00:00:00",
        wavelengths=[4000.0],
        fluxes=[1.2],
    )
    result = spectra.post_spectrum(client, payload)
    assert result.id == 12
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "obj_id": "ZTF20abcdef",
        "instrument_id": 3,
        "observed_at": "2026-08-18T00:00:00",
        "wavelengths": [4000.0],
        "fluxes": [1.2],
    }
