"""Typed endpoint functions for photometry."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class PhotometryPoint(BaseModel):
    """A single photometry point of a source.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(extra="allow")

    id: int
    obj_id: str
    mjd: float
    mag: float | None = None
    magerr: float | None = None
    limiting_mag: float | None = None
    filter: str | None = None
    magsys: str | None = None
    instrument_id: int | None = None
    origin: str | None = None


class PhotometryPost(BaseModel):
    """Payload for posting a photometry point.

    Provide either ``mag``/``magerr`` (magnitude space) or
    ``flux``/``fluxerr``/``zp`` (flux space). For non-detections, leave the
    measurement fields unset and provide ``limiting_mag``.
    """

    obj_id: str
    mjd: float
    instrument_id: int
    filter: str
    magsys: str = "ab"
    mag: float | None = None
    magerr: float | None = None
    limiting_mag: float | None = None
    flux: float | None = None
    fluxerr: float | None = None
    zp: float | None = None
    group_ids: list[int] | None = None


class PhotometryPostResponse(BaseModel):
    """Result of posting photometry."""

    model_config = ConfigDict(extra="allow")

    ids: list[int] = Field(default_factory=list)


def fetch_photometry(
    client: httpx.Client,
    obj_id: str,
    *,
    format: str = "mag",  # noqa: A002 -- mirrors the endpoint's query parameter
    magsys: str = "ab",
) -> list[PhotometryPoint]:
    """Retrieve the photometry of a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    format : str, optional
        Return photometry in ``"mag"`` or ``"flux"`` space.
    magsys : str, optional
        Magnitude system, ``"ab"`` or ``"vega"``.
    """
    response = client.get(
        f"/api/sources/{obj_id}/photometry",
        params={"format": format, "magsys": magsys},
    )
    return [PhotometryPoint.model_validate(point) for point in unwrap(response)]


def post_photometry(
    client: httpx.Client,
    payload: PhotometryPost,
) -> PhotometryPostResponse:
    """Post a photometry point.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : PhotometryPost
        The photometry point to post. If ``group_ids`` is omitted, the
        server applies its default visibility.
    """
    response = client.post(
        "/api/photometry", json=payload.model_dump(exclude_none=True)
    )
    return PhotometryPostResponse.model_validate(unwrap(response))
