"""Typed endpoint functions for photometry."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.annotations import AnnotationDetail
from skyportal_py.groups import Group
from skyportal_py.streams import Stream
from skyportal_py.users import User


class PhotometryValidation(BaseModel):
    """A validated/rejected mark on a photometry point."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    photometry_id: int | None = None
    validated: bool | None = None
    validator_id: int | None = None
    explanation: str | None = None
    notes: str | None = None


class _SerializedPhotometry(BaseModel):
    """A photometry point as built by the API's ``serialize`` helper."""

    # ``serialize`` never returns ``Photometry.to_dict()``: it hand-builds a
    # dict whose keys depend on the ``format`` query parameter. ``mag``,
    # ``magerr`` and ``limiting_mag`` are only present for ``format="mag"``,
    # ``flux``, ``fluxerr`` and ``zp`` only for ``format="flux"``, and both
    # sets for ``format="both"``. The ``ref_*``/``tot_*``/``mag(ref|tot)``
    # block is only present when the point has a reference flux, and the
    # ``extinction``/``mag_corr``/``flux_corr`` keys only when the caller
    # asked for extinction. ``groups``, ``annotations``, ``owner``,
    # ``streams`` and ``validations`` are each opt-in per endpoint, and the
    # ``owner``/``groups``/``streams`` entries are trimmed to a few columns.

    model_config = ConfigDict(extra="forbid")

    id: int
    obj_id: str | None = None
    ra: float | None = None
    dec: float | None = None
    ra_unc: float | None = None
    dec_unc: float | None = None
    filter: str | None = None
    mjd: float | None = None
    snr: float | None = None
    instrument_id: int | None = None
    instrument_name: str | None = None
    origin: str | None = None
    # The duplicate-resolution upload path can leave the literal string
    # "NaN" in place of a point's altdata dict.
    altdata: dict[str, Any] | str | None = None
    created_at: datetime | None = None
    groups: list[Group] = Field(default_factory=list)
    annotations: list[AnnotationDetail] = Field(default_factory=list)
    owner: User | None = None
    streams: list[Stream] = Field(default_factory=list)
    validations: list[PhotometryValidation] = Field(default_factory=list)
    magsys: str | None = None
    mag: float | None = None
    magerr: float | None = None
    limiting_mag: float | None = None
    flux: float | None = None
    fluxerr: float | None = None
    zp: float | None = None
    ref_flux: float | None = None
    ref_fluxerr: float | None = None
    tot_flux: float | None = None
    tot_fluxerr: float | None = None
    magref: float | None = None
    magtot: float | None = None
    e_magref: float | None = None
    e_magtot: float | None = None
    extinction: float | None = None
    mag_corr: float | None = None
    flux_corr: float | None = None


class PhotometryPoint(_SerializedPhotometry):
    """A single photometry point of a source (upstream ``Photometry``)."""

    # ``GET /api/sources/{obj_id}/photometry`` returns individual photometry
    # points *and* the rows of the object's photometric series in one list, so
    # this model also carries the extra keys a series row has: ``instrument``
    # and ``telescope`` (names, not objects) and, when the caller asked to
    # phase-fold, ``phase``. A series row can also carry arbitrary auxiliary
    # columns from the uploaded data file, which cannot be modelled.
    # ``format="plot"`` returns a strict subset of these keys.

    instrument: str | None = None
    telescope: str | None = None
    phase: float | None = None


class PhotometryPost(BaseModel):
    """Payload for posting one or many photometry points.

    Provide either ``mag``/``magerr`` (magnitude space) or
    ``flux``/``fluxerr``/``zp`` (flux space). For non-detections, leave the
    measurement fields unset and provide ``limiting_mag``. Every measurement
    field also accepts a 1D list to upload many points at once; scalars are
    broadcast across the lists, and a None entry inside a ``mag``/``flux``
    list marks that point as a non-detection.
    """

    model_config = ConfigDict(extra="forbid")

    obj_id: str | list[str]
    mjd: float | list[float]
    instrument_id: int | list[int]
    filter: str | list[str]
    magsys: str | list[str] = "ab"
    mag: float | list[float | None] | None = None
    magerr: float | list[float | None] | None = None
    limiting_mag: float | list[float | None] | None = None
    limiting_mag_nsigma: float | list[float | None] | None = None
    magref: float | list[float | None] | None = None
    e_magref: float | list[float | None] | None = None
    flux: float | list[float | None] | None = None
    fluxerr: float | list[float | None] | None = None
    zp: float | list[float | None] | None = None
    ref_flux: float | list[float | None] | None = None
    ref_fluxerr: float | list[float | None] | None = None
    ref_zp: float | list[float | None] | None = None
    ra: float | list[float | None] | None = None
    dec: float | list[float | None] | None = None
    ra_unc: float | list[float | None] | None = None
    dec_unc: float | list[float | None] | None = None
    origin: str | list[str | None] | None = None
    assignment_id: int | None = None
    altdata: dict[str, Any] | list[dict[str, Any] | None] | None = None
    extinction_corrected: bool | None = None
    group_ids: list[int] | Literal["all"] | None = None
    stream_ids: list[int] | None = None


class PhotometryPostResponse(BaseModel):
    """Result of posting photometry."""

    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(default_factory=list)
    upload_id: str | None = None


def fetch_photometry(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    format: str = "mag",  # noqa: A002 -- mirrors the endpoint's query parameter
    magsys: str = "ab",
    include_extinction: bool = False,
    include_validation_info: bool = False,
    include_annotation_info: bool = False,
    include_owner_info: bool = False,
    include_stream_info: bool = False,
    include_super_objs_photometry: bool = False,
    deduplicate_photometry: bool = False,
    individual_or_series: str = "both",
    phase_fold_data: bool = False,
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
    include_extinction : bool, optional
        Also return the Galactic extinction at each point and the corrected
        measurement, in ``extinction`` and ``mag_corr``/``flux_corr``.
    include_validation_info : bool, optional
        Also return each point's validation records in ``validations``.
    include_annotation_info : bool, optional
        Also return each point's annotations in ``annotations``.
    include_owner_info : bool, optional
        Also return the point's uploading user in ``owner``.
    include_stream_info : bool, optional
        Also return the streams each point belongs to in ``streams``.
    include_super_objs_photometry : bool, optional
        Aggregate photometry from every object linked through the source's
        SuperObj.
    deduplicate_photometry : bool, optional
        Drop duplicate ``(mjd, filter)`` points, keeping the most recently
        created one.
    individual_or_series : str, optional
        Return ``"individual"`` points, photometric ``"series"`` rows, or
        ``"both"``.
    phase_fold_data : bool, optional
        Phase-fold the photometry on the object's most recent ``period``
        annotation, in ``phase``. The server errors if the object has no
        period annotation.

    Notes
    -----
    The server returns the object's individual photometry points *and* the
    rows of its photometric series in the same list.
    """
    response = client.get(
        f"/api/sources/{obj_id}/photometry",
        params={
            "format": format,
            "magsys": magsys,
            "includeExtinction": include_extinction,
            "includeValidationInfo": include_validation_info,
            "includeAnnotationInfo": include_annotation_info,
            "includeOwnerInfo": include_owner_info,
            "includeStreamInfo": include_stream_info,
            "includeSuperObjsPhotometry": include_super_objs_photometry,
            "deduplicatePhotometry": deduplicate_photometry,
            "individualOrSeries": individual_or_series,
            "phaseFoldData": phase_fold_data,
        },
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
        server applies its default visibility. The response carries the
        ``upload_id`` of the batch, which
        :func:`bulk_delete_photometry` can undo.
    """
    response = client.post(
        "/api/photometry", json=payload.model_dump(exclude_none=True)
    )
    return PhotometryPostResponse.model_validate(unwrap(response))


def upsert_photometry(
    client: httpx.Client,
    payload: PhotometryPost,
    *,
    refresh: bool = False,
    duplicate_ignore_flux: bool = False,
    overwrite_flux: bool = False,
) -> PhotometryPostResponse:
    """Upload photometry, updating any points that already exist.

    Unlike :func:`post_photometry`, which fails on a duplicate, this
    resolves duplicates against the points already stored.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : PhotometryPost
        The photometry point to upload. If ``group_ids`` is omitted, the
        server applies its default visibility.
    refresh : bool, optional
        Ask the server to push a photometry refresh to any frontend that
        currently has the source open.
    duplicate_ignore_flux : bool, optional
        Match duplicates on ``mjd``, ``instrument_id``, ``filter`` and
        ``origin`` alone, ignoring flux. Reserved to super admins, since a
        loose match can overwrite data irrecoverably.
    overwrite_flux : bool, optional
        Replace the flux of matched duplicates with the uploaded values.
        Only applies together with ``duplicate_ignore_flux``, and only to
        points that already carry an origin.
    """
    params: dict[str, bool] = {
        "refresh": refresh,
        "duplicate_ignore_flux": duplicate_ignore_flux,
        "overwrite_flux": overwrite_flux,
    }
    response = client.put(
        "/api/photometry",
        params=params,
        json=payload.model_dump(exclude_none=True),
    )
    return PhotometryPostResponse.model_validate(unwrap(response))


def fetch_photometry_point(
    client: httpx.Client,
    photometry_id: int,
    *,
    format: str = "mag",  # noqa: A002 -- mirrors the endpoint's query parameter
    magsys: str = "ab",
) -> PhotometryPoint:
    """Retrieve a single photometry point by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point.
    format : str, optional
        Return the point in ``"mag"`` or ``"flux"`` space.
    magsys : str, optional
        Magnitude system, ``"ab"`` or ``"vega"``.
    """
    response = client.get(
        f"/api/photometry/{photometry_id}",
        params={"format": format, "magsys": magsys},
    )
    return PhotometryPoint.model_validate(unwrap(response))


def delete_photometry(client: httpx.Client, photometry_id: int) -> None:
    """Delete a photometry point.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point to delete.
    """
    unwrap(client.delete(f"/api/photometry/{photometry_id}"))


class PhotometryUpdate(BaseModel):
    """Payload for updating an existing photometry point.

    Every field is optional: the server loads the point, applies the given
    fields, and re-validates the result as either a flux-space
    (``flux``/``fluxerr``/``zp``) or magnitude-space (``mag``/``magerr``)
    measurement. Only the fields explicitly set on the payload are sent, so
    passing ``None`` explicitly (e.g. ``mag=None, magerr=None`` to turn a
    detection into a non-detection) sends a null, while omitting a field
    leaves it unchanged.
    """

    model_config = ConfigDict(extra="forbid")

    obj_id: str | None = None
    mjd: float | None = None
    instrument_id: int | None = None
    filter: str | None = None
    magsys: str | None = None
    mag: float | None = None
    magerr: float | None = None
    limiting_mag: float | None = None
    magref: float | None = None
    e_magref: float | None = None
    flux: float | None = None
    fluxerr: float | None = None
    zp: float | None = None
    ref_flux: float | None = None
    ref_fluxerr: float | None = None
    ref_zp: float | None = None
    ra: float | None = None
    dec: float | None = None
    ra_unc: float | None = None
    dec_unc: float | None = None
    origin: str | None = None
    alert_id: int | None = None
    assignment_id: int | None = None
    altdata: dict[str, Any] | None = None
    group_ids: list[int] | None = None
    stream_ids: list[int] | None = None


class PhotometryRangePoint(_SerializedPhotometry):
    """A photometry point as serialized by the date-range query."""

    # ``GET /api/photometry/range`` calls ``serialize`` with its defaults, so
    # this is the plain serialized point: same keys as
    # :class:`PhotometryPoint` minus the photometric-series extras.


class PhotometryValidationResponse(BaseModel):
    """Result of creating, updating or deleting a photometry validation."""

    model_config = ConfigDict(extra="forbid")

    id: int


def update_photometry(
    client: httpx.Client,
    photometry_id: int,
    payload: PhotometryUpdate,
    *,
    refresh: bool = False,
) -> None:
    """Update an existing photometry point.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point to update.
    payload : PhotometryUpdate
        Fields to apply. ``group_ids`` replaces the point's groups;
        ``stream_ids`` only adds streams, it never removes them. Updating
        requires being the point's owner or holding the ``Manage photometry``
        permission, which is stricter than read access.
    refresh : bool, optional
        Ask the server to push a source refresh to connected frontends. The
        parameter is only sent when true, because the server treats any
        value it receives as a request to refresh.
    """
    params = {"refresh": True} if refresh else {}
    unwrap(
        client.patch(
            f"/api/photometry/{photometry_id}",
            params=params,
            json=payload.model_dump(exclude_unset=True),
        )
    )


def fetch_photometry_range(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    instrument_ids: list[int] | None = None,
    min_date: str | None = None,
    max_date: str | None = None,
    format: str = "mag",  # noqa: A002 -- mirrors the endpoint's query parameter
    magsys: str = "ab",
) -> list[PhotometryRangePoint]:
    """Retrieve photometry taken by given instruments over a date range.

    This endpoint is a ``GET`` that carries its filters in a JSON request
    body rather than in the query string.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    instrument_ids : list of int, optional
        Only return photometry from these instruments. If omitted, all
        accessible instruments are queried.
    min_date : str, optional
        UT datetime string; return only photometry taken at or after it.
        Omit for an open-ended interval.
    max_date : str, optional
        UT datetime string; return only photometry taken at or before it.
        Omit for an open-ended interval.
    format : str, optional
        Return photometry in ``"mag"`` or ``"flux"`` space.
    magsys : str, optional
        Magnitude system of the output, e.g. ``"ab"`` or ``"vega"``.
    """
    body: dict[str, Any] = {}
    if instrument_ids is not None:
        body["instrument_ids"] = instrument_ids
    if min_date is not None:
        body["min_date"] = min_date
    if max_date is not None:
        body["max_date"] = max_date
    response = client.request(
        "GET",
        "/api/photometry/range",
        params={"format": format, "magsys": magsys},
        json=body,
    )
    return [PhotometryRangePoint.model_validate(point) for point in unwrap(response)]


def fetch_photometry_origins(client: httpx.Client) -> list[str]:
    """Retrieve the distinct photometry origins.

    This endpoint is deprecated upstream: the server currently answers every
    request with an error, so this call raises
    :class:`skyportal_py.SkyPortalError`.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    return list(unwrap(client.get("/api/photometry/origins")))


def bulk_delete_photometry(client: httpx.Client, upload_id: str) -> str:
    """Delete every photometry point from a bulk upload.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    upload_id : str
        The upload ID returned when the photometry was uploaded in bulk.
        Requires the ``Delete bulk photometry`` permission.
    """
    return str(unwrap(client.delete(f"/api/photometry/bulk_delete/{upload_id}")))


def post_photometry_validation(  # noqa: PLR0913 -- mirrors the endpoint's request body
    client: httpx.Client,
    photometry_id: int,
    *,
    validated: bool | None = None,
    explanation: str | None = None,
    notes: str | None = None,
    magsys: str | None = None,
) -> PhotometryValidationResponse:
    """Validate or reject a photometry point.

    Requires the server to be configured with ``misc.photometry_validation``
    enabled. If the point already has a validation, it is updated in place.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point.
    validated : bool, optional
        ``True`` to validate the point, ``False`` to reject it. Leave unset
        to record an undefined status.
    explanation : str, optional
        Why the point was validated or rejected.
    notes : str, optional
        Free-form notes about the validation.
    magsys : str, optional
        Magnitude system used in the refresh pushed to connected frontends.
    """
    payload: dict[str, Any] = {}
    if validated is not None:
        payload["validated"] = validated
    if explanation is not None:
        payload["explanation"] = explanation
    if notes is not None:
        payload["notes"] = notes
    if magsys is not None:
        payload["magsys"] = magsys
    response = client.post(f"/api/photometry/{photometry_id}/validation", json=payload)
    return PhotometryValidationResponse.model_validate(unwrap(response))


def update_photometry_validation(  # noqa: PLR0913 -- mirrors the endpoint's request body
    client: httpx.Client,
    photometry_id: int,
    *,
    validated: bool | None = None,
    explanation: str | None = None,
    notes: str | None = None,
    magsys: str | None = None,
) -> PhotometryValidationResponse:
    """Update the validated/rejected status of a photometry point.

    Requires the server to be configured with ``misc.photometry_validation``
    enabled, and fails if the point has no validation yet; use
    :func:`post_photometry_validation` to create one.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point.
    validated : bool, optional
        ``True`` to validate the point, ``False`` to reject it. Omitting it
        clears the status to undefined.
    explanation : str, optional
        Why the point was validated or rejected. Left unchanged if omitted.
    notes : str, optional
        Free-form notes about the validation. Left unchanged if omitted.
    magsys : str, optional
        Magnitude system used in the refresh pushed to connected frontends.
    """
    payload: dict[str, Any] = {}
    if validated is not None:
        payload["validated"] = validated
    if explanation is not None:
        payload["explanation"] = explanation
    if notes is not None:
        payload["notes"] = notes
    if magsys is not None:
        payload["magsys"] = magsys
    response = client.patch(f"/api/photometry/{photometry_id}/validation", json=payload)
    return PhotometryValidationResponse.model_validate(unwrap(response))


def delete_photometry_validation(
    client: httpx.Client,
    photometry_id: int,
) -> PhotometryValidationResponse:
    """Remove the validated/rejected status of a photometry point.

    The point's status becomes undefined again. Requires the server to be
    configured with ``misc.photometry_validation`` enabled.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    photometry_id : int
        ID of the photometry point.
    """
    response = client.delete(f"/api/photometry/{photometry_id}/validation")
    return PhotometryValidationResponse.model_validate(unwrap(response))
