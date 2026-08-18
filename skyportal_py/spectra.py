"""Typed endpoint functions for spectra."""

from __future__ import annotations

import httpx
from pydantic import Field

from skyportal_py._http import unwrap
from skyportal_py._models import Model


class Spectrum(Model):
    """A spectrum of a source."""

    id: int
    obj_id: str
    instrument_id: int
    wavelengths: list[float] = Field(default_factory=list)
    fluxes: list[float] = Field(default_factory=list)
    errors: list[float] | None = None
    observed_at: str | None = None
    origin: str | None = None


class SpectrumPost(Model):
    """Payload for posting a spectrum."""

    obj_id: str
    instrument_id: int
    observed_at: str
    wavelengths: list[float]
    fluxes: list[float]
    errors: list[float] | None = None
    origin: str | None = None
    group_ids: list[int] | None = None


class SpectrumPostResponse(Model):
    """Result of posting a spectrum."""

    id: int


class _SourceSpectra(Model):
    """Envelope of a source's spectra response."""

    obj_id: str | None = None
    spectra: list[Spectrum] = Field(default_factory=list)


def fetch_spectrum(client: httpx.Client, spectrum_id: int) -> Spectrum:
    """Retrieve a single spectrum by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    spectrum_id : int
        ID of the spectrum.
    """
    response = client.get(f"/api/spectrum/{spectrum_id}")
    return Spectrum.model_validate(unwrap(response))


def fetch_spectra(client: httpx.Client, obj_id: str) -> list[Spectrum]:
    """Retrieve the spectra of a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/sources/{obj_id}/spectra")
    return _SourceSpectra.model_validate(unwrap(response)).spectra


def post_spectrum(client: httpx.Client, payload: SpectrumPost) -> SpectrumPostResponse:
    """Post a spectrum.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SpectrumPost
        The spectrum to post. ``observed_at`` is an ISO-format (UTC)
        timestamp. If ``group_ids`` is omitted, the server applies its
        default visibility.
    """
    response = client.post("/api/spectrum", json=payload.model_dump(exclude_none=True))
    return SpectrumPostResponse.model_validate(unwrap(response))
