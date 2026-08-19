"""Typed endpoint functions for ``/api/sources``."""

from __future__ import annotations

import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.analysis import ObjAnalysis
from skyportal_py.annotations import Annotation
from skyportal_py.assignments import Assignment
from skyportal_py.candidates import CandidateRecord
from skyportal_py.classifications import Classification
from skyportal_py.comments import Comment
from skyportal_py.filters import Filter
from skyportal_py.followup_requests import FollowupRequest
from skyportal_py.galaxies import Galaxy
from skyportal_py.groups import Group
from skyportal_py.photometry import PhotometryPoint
from skyportal_py.tags import ObjTag
from skyportal_py.thumbnails import Thumbnail
from skyportal_py.users import User


class SourceSavedGroup(Group):
    """A group a source is saved to, with its ``sources`` join-table record."""

    active: bool | None = None
    requested: bool | None = None
    saved_at: datetime.datetime | None = None
    saved_by: User | None = None


class SourceAnnotation(Annotation):
    """An annotation as returned on a source (upstream ``Annotation``)."""

    # ``get_source`` tags every annotation with the resource it belongs to.
    type: str | None = None


class SourceDuplicate(BaseModel):
    """Another saved source within 4 arcsec of this one (upstream ``Obj``)."""

    model_config = ConfigDict(extra="forbid")

    obj_id: str
    ra: float | None = None
    dec: float | None = None
    separation: float | None = None


class SourceAssociatedObj(BaseModel):
    """An object linked to this source through a ``SuperObj``."""

    model_config = ConfigDict(extra="forbid")

    obj_id: str
    ra: float | None = None
    dec: float | None = None
    separation: float | None = None
    super_obj_id: int | None = None
    super_obj_name: str | None = None


GcnNoteStatus = Literal["highlighted", "rejected", "ambiguous", "pending", "not vetted"]
"""How a source stands against a GCN event, as the source handler words it."""


class SourceGcnNote(BaseModel):
    """A source's vetting note for one GCN event (upstream ``GcnEventObj``)."""

    model_config = ConfigDict(extra="forbid")

    dateobs: datetime.datetime | None = None
    explanation: str | None = None
    notes: str | None = None
    status: GcnNoteStatus | None = None


class SourceCandidate(CandidateRecord):
    """A filter passage as returned on a source (upstream ``Candidate``)."""

    filter: Filter | None = None


class SourceFollowupRequest(FollowupRequest):
    """A follow-up request as returned on a source (upstream ``FollowupRequest``)."""

    # ``get_source`` replaces the transaction rows with the decoded JSON
    # bodies of their responses, and only for admins.
    transactions: list[Any] = Field(default_factory=list)


class SourceColorMag(BaseModel):
    """A color and absolute magnitude derived from one catalog cross-match."""

    model_config = ConfigDict(extra="forbid")

    origin: str | None = None
    color: float | None = None
    abs_mag: float | None = None


class PhotStat(BaseModel):
    """Aggregate photometry statistics for one object (upstream ``PhotStat``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    last_update: datetime.datetime | None = None
    last_full_update: datetime.datetime | None = None
    # Not a column: set on the instance by ``PhotStatHandler.get``.
    last_phot_add_time: datetime.datetime | None = None
    obj_id: str | None = None
    num_obs_global: int | None = None
    num_obs_per_filter: dict[str, Any] | None = None
    num_det_global: int | None = None
    num_det_no_forced_phot_global: int | None = None
    num_det_per_filter: dict[str, Any] | None = None
    first_detected_mjd: float | None = None
    first_detected_mag: float | None = None
    first_detected_filter: str | None = None
    last_detected_mjd: float | None = None
    last_detected_mag: float | None = None
    last_detected_filter: str | None = None
    first_detected_no_forced_phot_mjd: float | None = None
    first_detected_no_forced_phot_mag: float | None = None
    first_detected_no_forced_phot_filter: str | None = None
    last_detected_no_forced_phot_mjd: float | None = None
    last_detected_no_forced_phot_mag: float | None = None
    last_detected_no_forced_phot_filter: str | None = None
    recent_obs_mjd: float | None = None
    predetection_mjds: list[float] | None = None
    last_non_detection_mjd: float | None = None
    time_to_non_detection: float | None = None
    mean_mag_global: float | None = None
    mean_mag_per_filter: dict[str, Any] | None = None
    mean_color: dict[str, Any] | None = None
    peak_mjd_global: float | None = None
    peak_mjd_per_filter: dict[str, Any] | None = None
    peak_mag_global: float | None = None
    peak_mag_per_filter: dict[str, Any] | None = None
    faintest_mag_global: float | None = None
    faintest_mag_per_filter: dict[str, Any] | None = None
    deepest_limit_global: float | None = None
    deepest_limit_per_filter: dict[str, Any] | None = None
    rise_rate: float | None = None
    decay_rate: float | None = None
    mag_rms_global: float | None = None
    mag_rms_per_filter: dict[str, Any] | None = None


class Source(BaseModel):
    """A SkyPortal source (upstream ``Obj``)."""

    model_config = ConfigDict(extra="forbid")

    # -- Mapper columns of ``Obj`` -------------------------------------------
    id: str
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    ra: float | None = None
    dec: float | None = None
    ra_dis: float | None = None
    dec_dis: float | None = None
    ra_err: float | None = None
    dec_err: float | None = None
    offset: float | None = None
    t0: float | None = None
    redshift: float | None = None
    redshift_error: float | None = None
    redshift_origin: str | None = None
    redshift_history: list[dict[str, Any]] | None = None
    host_id: int | None = None
    summary: str | None = None
    summary_history: list[dict[str, Any]] | None = None
    altdata: dict[str, Any] | None = None
    dist_nearest_source: float | None = None
    mag_nearest_source: float | None = None
    e_mag_nearest_source: float | None = None
    transient: bool | None = None
    varstar: bool | None = None
    is_roid: bool | None = None
    mpc_name: str | None = None
    tns_name: str | None = None
    tns_info: dict[str, Any] | None = None
    score: float | None = None
    origin: str | None = None
    alias: list[str] | None = None
    healpix: int | None = None
    detect_photometry_count: int | None = None
    # ``Obj.to_dict`` strips this; the source handlers add it back by hand.
    internal_key: str | None = None

    # -- Values the handlers compute and inject -------------------------------
    gal_lat: float | None = None
    gal_lon: float | None = None
    luminosity_distance: float | None = None
    dm: float | None = None
    angular_diameter_distance: float | None = None
    ebv: float | None = None
    first_detected: datetime.datetime | None = None
    last_detected: datetime.datetime | None = None
    host_offset: float | None = None
    host_distance: float | None = None
    # ``period_exists`` on a single source, ``period`` in a sources listing.
    period_exists: bool | None = None
    period: bool | None = None
    photometry_exists: bool | None = None
    spectrum_exists: bool | None = None
    comment_exists: bool | None = None
    # Names of galaxies within 10 arcsec; ``None`` for moving objects.
    galaxies: list[str] | None = None
    duplicates: list[SourceDuplicate] = Field(default_factory=list)
    associated_objs: list[SourceAssociatedObj] = Field(default_factory=list)
    color_magnitude: list[SourceColorMag] = Field(default_factory=list)
    gcn_notes: list[SourceGcnNote] = Field(default_factory=list)
    tags: list[ObjTag] = Field(default_factory=list)

    # -- Nested records ------------------------------------------------------
    groups: list[SourceSavedGroup] = Field(default_factory=list)
    thumbnails: list[Thumbnail] = Field(default_factory=list)
    photstats: list[PhotStat] = Field(default_factory=list)
    annotations: list[SourceAnnotation] = Field(default_factory=list)
    classifications: list[Classification] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)
    photometry: list[PhotometryPoint] = Field(default_factory=list)
    host: Galaxy | None = None
    followup_requests: list[SourceFollowupRequest] = Field(default_factory=list)
    assignments: list[Assignment] = Field(default_factory=list)
    analyses: list[ObjAnalysis] = Field(default_factory=list)
    candidates: list[SourceCandidate] = Field(default_factory=list)
    # ``GcnEvent`` rows with an added ``dateobs_mjd``; left free-form because
    # ``gcn_events`` cannot import ``sources`` without a cycle.
    gcn_crossmatch: list[dict[str, Any]] = Field(default_factory=list)
    # Users on a single source, ``SourceLabel`` rows in a sources listing.
    labellers: list[dict[str, Any]] = Field(default_factory=list)


class SourcesPage(BaseModel):
    """One page of results from a sources query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    sources: list[Source]
    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)
    # Echoed back when exactly one group was queried for.
    group_id: int | None = None
    # Returned when ``useCache`` is set; pass it back to replay the query.
    query_id: str | None = Field(alias="queryID", default=None)
    geojson: dict[str, Any] | None = None


class SourcePost(BaseModel):
    """Payload for saving a new source (upstream ``ObjPost``)."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float | None = None
    dec: float | None = None
    ra_dis: float | None = None
    dec_dis: float | None = None
    ra_err: float | None = None
    dec_err: float | None = None
    offset: float | None = None
    t0: float | None = None
    redshift: float | None = None
    redshift_error: float | None = None
    redshift_origin: str | None = None
    host_id: int | None = None
    summary: str | None = None
    summary_history: list[dict[str, Any]] | None = None
    altdata: dict[str, Any] | None = None
    dist_nearest_source: float | None = None
    mag_nearest_source: float | None = None
    e_mag_nearest_source: float | None = None
    transient: bool | None = None
    varstar: bool | None = None
    is_roid: bool | None = None
    mpc_name: str | None = None
    tns_name: str | None = None
    tns_info: dict[str, Any] | None = None
    score: float | None = None
    origin: str | None = None
    alias: list[str] | None = None
    detect_photometry_count: int | None = None
    group_ids: list[int] | None = None
    refresh_source: bool | None = None
    ignore_if_in_group_ids: dict[str, list[int]] | None = None
    saver_per_group_id: dict[str, int] | None = None


class SourcePostResponse(BaseModel):
    """Result of saving a new source."""

    model_config = ConfigDict(extra="forbid")

    id: str
    saved_to_groups: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def fetch_source(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    include_thumbnails: bool = False,
    include_photometry: bool = False,
    include_color_magnitude: bool = False,
    include_photometry_exists: bool = False,
    include_detection_stats: bool = False,
    include_period_exists: bool = False,
    include_labellers: bool = False,
    include_gcn_crossmatches: bool = False,
    include_analyses: bool = False,
    deduplicate_photometry: bool = False,
) -> Source:
    """Retrieve a single source by object ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    include_thumbnails : bool, optional
        Include thumbnail data in the response.
    include_photometry : bool, optional
        Include the source's photometry in ``photometry``.
    include_color_magnitude : bool, optional
        Include the source's color/absolute-magnitude data in
        ``color_magnitude``.
    include_photometry_exists : bool, optional
        Include whether any photometry exists, in ``photometry_exists``.
    include_detection_stats : bool, optional
        Include the aggregate photometry statistics in ``photstats``.
    include_period_exists : bool, optional
        Include whether a period annotation exists, in ``period_exists``.
    include_labellers : bool, optional
        Include the users who labelled the source, in ``labellers``.
    include_gcn_crossmatches : bool, optional
        Include the source's GCN event crossmatches, in ``gcn_crossmatch``.
    include_analyses : bool, optional
        Include the source's analyses in ``analyses``.
    deduplicate_photometry : bool, optional
        With ``include_photometry``, drop photometry points duplicated
        within a short time window.
    """
    response = client.get(
        f"/api/sources/{obj_id}",
        params={
            "includeThumbnails": include_thumbnails,
            "includePhotometry": include_photometry,
            "includeColorMagnitude": include_color_magnitude,
            "includePhotometryExists": include_photometry_exists,
            "includeDetectionStats": include_detection_stats,
            "includePeriodExists": include_period_exists,
            "includeLabellers": include_labellers,
            "includeGCNCrossmatches": include_gcn_crossmatches,
            "includeAnalyses": include_analyses,
            "deduplicatePhotometry": deduplicate_photometry,
        },
    )
    return Source.model_validate(unwrap(response))


def source_exists(client: httpx.Client, obj_id: str) -> bool:
    """Check whether a source with this object ID is accessible.

    Uses the endpoint's HEAD form, which carries no body.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID to check.
    """
    return client.head(f"/api/sources/{obj_id}").is_success


def fetch_sources(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    source_id: str | None = None,
    ra: float | None = None,
    dec: float | None = None,
    radius: float | None = None,
    group_ids: list[int] | None = None,
    spatial_catalog_name: str | None = None,
    spatial_catalog_entry_name: str | None = None,
    localization_dateobs: str | None = None,
    localization_name: str | None = None,
    localization_cumprob: float | None = None,
    remove_nested: bool | None = None,
    saved_before: str | None = None,
    saved_after: str | None = None,
    saved_by_current_user: bool | None = None,
    created_or_modified_after: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    has_spectrum: bool | None = None,
    has_spectrum_before: str | None = None,
    has_spectrum_after: str | None = None,
    has_tns_name: bool | None = None,
    has_followup_request: bool | None = None,
    simbad_class: str | None = None,
    classifications: list[str] | None = None,
    nonclassifications: list[str] | None = None,
    unclassified: bool | None = None,
    min_redshift: float | None = None,
    max_redshift: float | None = None,
    min_peak_magnitude: float | None = None,
    max_peak_magnitude: float | None = None,
    min_latest_magnitude: float | None = None,
    max_latest_magnitude: float | None = None,
    annotations_filter: str | None = None,
    annotations_filter_origin: str | None = None,
    comments_filter: str | None = None,
    rejected_source_ids: list[str] | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> SourcesPage:
    """Query saved sources, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    source_id : str, optional
        Keep sources whose object ID contains this (partial-match) string.
    ra, dec, radius : float, optional
        Cone-search filter, all in degrees; provide all three together.
    group_ids : list of int, optional
        Restrict to sources saved to these groups.
    spatial_catalog_name, spatial_catalog_entry_name : str, optional
        Keep sources inside this entry of this spatial catalog; provide
        both together.
    localization_dateobs, localization_name : str, optional
        Keep sources inside a GCN localization, identified by its event
        time and map name.
    localization_cumprob : float, optional
        Cumulative probability level of the localization region to keep
        sources within.
    remove_nested : bool, optional
        Strip the nested ``thumbnails``/``annotations``/``groups`` payloads
        from each source.
    saved_before, saved_after : str, optional
        Keep sources saved in this ISO-format (UTC) time range.
    saved_by_current_user : bool, optional
        Keep only sources the token's user saved.
    created_or_modified_after : str, optional
        Keep sources created or modified after this ISO-format time.
    start_date, end_date : str, optional
        Keep sources last detected in this ISO-format time range.
    has_spectrum : bool, optional
        Keep only sources with at least one spectrum.
    has_spectrum_before, has_spectrum_after : str, optional
        Keep sources with a spectrum observed before/after this ISO time.
    has_tns_name : bool, optional
        Keep only sources with a TNS name.
    has_followup_request : bool, optional
        Keep only sources with a follow-up request.
    simbad_class : str, optional
        Keep sources with this Simbad class.
    classifications, nonclassifications : list of str, optional
        Keep sources carrying / not carrying one of these
        ``"taxonomy: classification"`` strings.
    unclassified : bool, optional
        Keep only sources without any classification.
    min_redshift, max_redshift : float, optional
        Redshift range filter.
    min_peak_magnitude, max_peak_magnitude : float, optional
        Peak-magnitude range filter.
    min_latest_magnitude, max_latest_magnitude : float, optional
        Latest-magnitude range filter.
    annotations_filter : str, optional
        Comma-separated ``key[:value:operator]`` annotation constraints.
    annotations_filter_origin : str, optional
        Comma-separated origins the annotations must come from.
    comments_filter : str, optional
        Partial-match filter on comment text.
    rejected_source_ids : list of str, optional
        Object IDs to exclude from the results.
    sort_by, sort_order : str, optional
        Sort column (a source column, ``"saved_at"``, ``"altdata.<key>"``
        or ``"annotation.<origin>.<key>"``) and direction ("asc"/"desc").
    """
    params: dict[str, str | int | float | bool] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
        **_sources_filter_params(
            source_id=source_id,
            ra=ra,
            dec=dec,
            radius=radius,
            group_ids=group_ids,
            spatial_catalog_name=spatial_catalog_name,
            spatial_catalog_entry_name=spatial_catalog_entry_name,
            localization_dateobs=localization_dateobs,
            localization_name=localization_name,
            localization_cumprob=localization_cumprob,
            remove_nested=remove_nested,
            saved_before=saved_before,
            saved_after=saved_after,
            saved_by_current_user=saved_by_current_user,
            created_or_modified_after=created_or_modified_after,
            start_date=start_date,
            end_date=end_date,
            has_spectrum=has_spectrum,
            has_spectrum_before=has_spectrum_before,
            has_spectrum_after=has_spectrum_after,
            has_tns_name=has_tns_name,
            has_followup_request=has_followup_request,
            simbad_class=simbad_class,
            classifications=classifications,
            nonclassifications=nonclassifications,
            unclassified=unclassified,
            min_redshift=min_redshift,
            max_redshift=max_redshift,
            min_peak_magnitude=min_peak_magnitude,
            max_peak_magnitude=max_peak_magnitude,
            min_latest_magnitude=min_latest_magnitude,
            max_latest_magnitude=max_latest_magnitude,
            annotations_filter=annotations_filter,
            annotations_filter_origin=annotations_filter_origin,
            comments_filter=comments_filter,
            rejected_source_ids=rejected_source_ids,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    }
    response = client.get("/api/sources", params=params)
    return SourcesPage.model_validate(unwrap(response))


# Wire names of the sources-list filters, keyed by keyword-argument name.
_SOURCES_FILTER_WIRE_NAMES = {
    "source_id": "sourceID",
    "ra": "ra",
    "dec": "dec",
    "radius": "radius",
    "spatial_catalog_name": "spatialCatalogName",
    "spatial_catalog_entry_name": "spatialCatalogEntryName",
    "localization_dateobs": "localizationDateobs",
    "localization_name": "localizationName",
    "localization_cumprob": "localizationCumprob",
    "remove_nested": "removeNested",
    "saved_before": "savedBefore",
    "saved_after": "savedAfter",
    "saved_by_current_user": "savedByCurrentUser",
    "created_or_modified_after": "createdOrModifiedAfter",
    "start_date": "startDate",
    "end_date": "endDate",
    "has_spectrum": "hasSpectrum",
    "has_spectrum_before": "hasSpectrumBefore",
    "has_spectrum_after": "hasSpectrumAfter",
    "has_tns_name": "hasTNSname",
    "has_followup_request": "hasFollowupRequest",
    "simbad_class": "simbadClass",
    "unclassified": "unclassified",
    "min_redshift": "minRedshift",
    "max_redshift": "maxRedshift",
    "min_peak_magnitude": "minPeakMagnitude",
    "max_peak_magnitude": "maxPeakMagnitude",
    "min_latest_magnitude": "minLatestMagnitude",
    "max_latest_magnitude": "maxLatestMagnitude",
    "annotations_filter": "annotationsFilter",
    "annotations_filter_origin": "annotationsFilterOrigin",
    "comments_filter": "commentsFilter",
    "sort_by": "sortBy",
    "sort_order": "sortOrder",
}


def _sources_filter_params(
    **kwargs: Any,  # noqa: ANN401 -- values are the caller's typed keyword arguments
) -> dict[str, str | int | float | bool]:
    """Map provided sources-list keyword arguments to wire query params."""
    group_ids = kwargs.pop("group_ids", None)
    classifications = kwargs.pop("classifications", None)
    nonclassifications = kwargs.pop("nonclassifications", None)
    rejected_source_ids = kwargs.pop("rejected_source_ids", None)
    params: dict[str, str | int | float | bool] = {
        _SOURCES_FILTER_WIRE_NAMES[name]: value
        for name, value in kwargs.items()
        if value is not None
    }
    if group_ids is not None:
        params["group_ids"] = ",".join(str(gid) for gid in group_ids)
    if classifications is not None:
        params["classifications"] = ",".join(classifications)
    if nonclassifications is not None:
        params["nonclassifications"] = ",".join(nonclassifications)
    if rejected_source_ids is not None:
        params["rejectedSourceIDs"] = ",".join(rejected_source_ids)
    return params


class SavedSource(BaseModel):
    """A row of the save-summary form of the sources query.

    The upstream ``Source`` join-table record between an object and the
    group it is saved to, rather than the object itself.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    obj_id: str
    group_id: int | None = None
    saved_by_id: int | None = None
    saved_at: datetime.datetime | None = None
    active: bool | None = None
    requested: bool | None = None
    unsaved_by_id: int | None = None
    unsaved_at: datetime.datetime | None = None


class SourcesSaveSummaryPage(BaseModel):
    """One page of results from a save-summary sources query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    sources: list[SavedSource] = Field(default_factory=list)
    total_matches: int | None = Field(alias="totalMatches", default=None)
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)
    group_id: int | None = None
    query_id: str | None = Field(alias="queryID", default=None)


def fetch_sources_save_summary(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    group_ids: list[int] | None = None,
    saved_before: str | None = None,
    saved_after: str | None = None,
    sort_by: str | None = None,
    sort_order: str | None = None,
) -> SourcesSaveSummaryPage:
    """Query when and by whom sources were saved, one page at a time.

    The ``saveSummary`` form of the sources query returns the save records
    (object ID, group, saver, time) instead of the objects themselves.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    group_ids : list of int, optional
        Restrict to sources saved to these groups.
    saved_before, saved_after : str, optional
        Keep sources saved in this ISO-format (UTC) time range.
    sort_by, sort_order : str, optional
        Sort column (e.g. ``"saved_at"``) and direction ("asc"/"desc").
    """
    params: dict[str, str | int | float | bool] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
        "saveSummary": True,
        **_sources_filter_params(
            group_ids=group_ids,
            saved_before=saved_before,
            saved_after=saved_after,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    }
    response = client.get("/api/sources", params=params)
    return SourcesSaveSummaryPage.model_validate(unwrap(response))


def post_source(client: httpx.Client, payload: SourcePost) -> SourcePostResponse:
    """Save a new source (or update one the token could not previously see).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SourcePost
        The source to save. ``ra`` and ``dec`` are required for an object
        that does not exist yet; for one that does, any field given is
        applied as an update. If ``group_ids`` is omitted, the server saves
        the source to all of the token's groups.
    """
    response = client.post("/api/sources", json=payload.model_dump(exclude_none=True))
    return SourcePostResponse.model_validate(unwrap(response))


def update_source(  # noqa: PLR0913 -- mirrors the endpoint's body parameters
    client: httpx.Client,
    obj_id: str,
    *,
    ra: float | None = None,
    dec: float | None = None,
    redshift: float | None = None,
    transient: bool | None = None,
    ra_dis: float | None = None,
    altdata: dict[str, Any] | None = None,
    summary: str | None = None,
) -> None:
    """Update fields of an existing source.

    Only the provided fields are sent; omitted fields are left unchanged.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to update.
    ra, dec : float, optional
        New coordinates, in degrees.
    redshift : float, optional
        New redshift.
    transient : bool, optional
        Whether the source is an astrophysical transient.
    ra_dis, altdata : optional
        Discovery right ascension and misc. metadata stored as JSON.
    summary : str, optional
        New human-readable summary of the source.
    """
    fields = {
        "ra": ra,
        "dec": dec,
        "redshift": redshift,
        "transient": transient,
        "ra_dis": ra_dis,
        "altdata": altdata,
        "summary": summary,
    }
    payload = {name: value for name, value in fields.items() if value is not None}
    unwrap(client.patch(f"/api/sources/{obj_id}", json=payload))


class SourceOffsetStar(BaseModel):
    """One line of an offset-star starlist."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    line: str = Field(alias="str")
    name: str | None = None
    ra: float | None = None
    dec: float | None = None
    dras: str | None = None
    ddecs: str | None = None
    mag: float | None = None
    pa: float | None = None


class SourceOffsets(BaseModel):
    """Offset stars for a source, in a facility's starlist format."""

    model_config = ConfigDict(extra="forbid")

    facility: str | None = None
    starlist_str: str | None = None
    starlist_info: list[SourceOffsetStar] = Field(default_factory=list)
    ra: float | None = None
    dec: float | None = None
    noffsets: int | None = None
    queries_issued: int | None = None
    query: str | None = None
    used_ztfref: bool | None = None
    gaia_available: bool | None = None


class FinderChartFacility(BaseModel):
    """Default offset-star parameters for one finding-chart facility."""

    model_config = ConfigDict(extra="forbid")

    radius_degrees: float | None = None
    mag_limit: float | None = None
    mag_min: float | None = None
    min_sep_arcsec: float | None = None


class SourceFinderChart(BaseModel):
    """A finding chart returned as JSON rather than as a file."""

    model_config = ConfigDict(extra="forbid")

    finding_chart: str
    starlist: list[SourceOffsetStar] = Field(default_factory=list)
    public_url: str | None = None
    public_url_expires_at: datetime.datetime | None = None


class SourceGcnEventCrossmatchPost(BaseModel):
    """Payload for crossmatching a source against GCN events."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    start_date: str = Field(alias="startDate")
    end_date: str = Field(alias="endDate")
    probability: float | None = None
    before_first_detection: bool | None = Field(
        default=None, alias="beforeFirstDetection"
    )
    gcn_tag_keep: list[str] | None = Field(default=None, alias="gcnTagKeep")
    gcn_tag_remove: list[str] | None = Field(default=None, alias="gcnTagRemove")
    localization_tag_keep: list[str] | None = Field(
        default=None, alias="localizationTagKeep"
    )
    localization_tag_remove: list[str] | None = Field(
        default=None, alias="localizationTagRemove"
    )
    gcn_properties_filter: list[str] | None = Field(
        default=None, alias="gcnPropertiesFilter"
    )
    localization_properties_filter: list[str] | None = Field(
        default=None, alias="localizationPropertiesFilter"
    )


class SourceMpcQueryPost(BaseModel):
    """Payload for a Minor Planet Center crossmatch."""

    model_config = ConfigDict(extra="forbid")

    obscode: str | None = None
    date: str | None = None
    limiting_magnitude: float | None = None
    search_radius: float | None = None


class SourceNotificationPost(BaseModel):
    """Payload for sending a source notification."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    source_id: str = Field(alias="sourceId")
    group_ids: list[int] = Field(alias="groupIds")
    level: Literal["soft", "hard"]
    additional_notes: str | None = Field(default=None, alias="additionalNotes")


class SourceNotificationPostResponse(BaseModel):
    """Result of sending a source notification."""

    model_config = ConfigDict(extra="forbid")

    id: int


class SourceExists(BaseModel):
    """Whether a source already exists by name or by position."""

    model_config = ConfigDict(extra="forbid")

    source_exists: bool
    message: str | None = None


class PhotStatCounts(BaseModel):
    """Counts of objects with and without photometry statistics."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_with_phot_stats: int = Field(alias="totalWithPhotStats")
    total_without_phot_stats: int = Field(alias="totalWithoutPhotStats")


class PhotStatsBatch(BaseModel):
    """Pagination summary of a batch photometry-statistics update."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


class PhotStatAggregateField(BaseModel):
    """A photometry-statistics field that can be plotted."""

    model_config = ConfigDict(extra="forbid")

    value: str
    label: str | None = None


class PhotStatAggregatePoint(BaseModel):
    """One source's photometry statistics, ready for plotting."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float | None = None
    dec: float | None = None
    redshift: float | None = None
    classification: str | None = None
    first_detected_mjd: float | None = None
    peak_mjd: float | None = None
    tns_discovery_date: str | None = None
    x: float | None = None
    y: float | None = None
    z: float | None = None


class PhotStatAggregate(BaseModel):
    """Bulk photometry statistics across many sources."""

    model_config = ConfigDict(extra="forbid")

    fields: list[PhotStatAggregateField] = Field(default_factory=list)
    points: list[PhotStatAggregatePoint] = Field(default_factory=list)
    count: int = 0
    truncated: bool = False


def delete_source(client: httpx.Client, obj_id: str, group_id: int) -> None:
    """Unsave a source from one group.

    The source is deactivated for that group rather than deleted outright;
    the token must have access to the group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to unsave.
    group_id : int
        Group to unsave the source from. Sent in the request body.
    """
    unwrap(
        client.request(
            "DELETE",
            f"/api/sources/{obj_id}",
            json={"group_id": group_id},
        )
    )


def delete_source_photometry(client: httpx.Client, obj_id: str) -> str:
    """Delete all of a source's photometry points.

    Requires the "Delete bulk photometry" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source whose photometry is deleted.
    """
    return str(unwrap(client.delete(f"/api/sources/{obj_id}/photometry")))


def fetch_source_offsets(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    facility: str = "Keck",
    num_offset_stars: int = 3,
    obstime: str | None = None,
    use_ztfref: bool = True,
    observing_run_id: int | None = None,
) -> SourceOffsets:
    """Retrieve offset stars for a source, to aid in spectroscopy.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    facility : str, optional
        Starlist format, one of ``"Keck"``, ``"Shane"``, ``"P200"``, or
        ``"P200-NGPS"``. Defaults to ``"Keck"``.
    num_offset_stars : int, optional
        Number of offset stars requested, in [0, 10]. Zero returns a
        starlist of just the source. Defaults to 3.
    obstime : str, optional
        Observation time in ISO format, e.g. ``"2020-12-30T12:34:10"``.
        Defaults to now.
    use_ztfref : bool, optional
        Use the ZTFref catalog for offset-star positions instead of Gaia
        DR3. Defaults to True.
    observing_run_id : int, optional
        Observing run whose assignment priority and comment should be
        folded into the starlist.
    """
    params: dict[str, str | int | bool] = {
        "facility": facility,
        "num_offset_stars": num_offset_stars,
        "use_ztfref": use_ztfref,
    }
    if obstime is not None:
        params["obstime"] = obstime
    if observing_run_id is not None:
        params["observing_run_id"] = observing_run_id
    response = client.get(f"/api/sources/{obj_id}/offsets", params=params)
    return SourceOffsets.model_validate(unwrap(response))


def _source_finder_params(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    *,
    imsize: float,
    facility: str,
    image_source: str,
    use_ztfref: bool,
    obstime: str | None,
    output_type: str,
    num_offset_stars: int,
    mag_min: float | None,
    mag_limit: float | None,
    use_cache: bool,
) -> dict[str, str | float | int | bool]:
    params: dict[str, str | float | int | bool] = {
        "imsize": imsize,
        "facility": facility,
        "image_source": image_source,
        "use_ztfref": use_ztfref,
        "type": output_type,
        "num_offset_stars": num_offset_stars,
        "use_cache": use_cache,
    }
    if obstime is not None:
        params["obstime"] = obstime
    if mag_min is not None:
        params["mag_min"] = mag_min
    if mag_limit is not None:
        params["mag_limit"] = mag_limit
    return params


def fetch_source_finder(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    imsize: float = 4.0,
    facility: str = "Keck",
    image_source: str = "ps1",
    use_ztfref: bool = True,
    obstime: str | None = None,
    output_type: str = "pdf",
    num_offset_stars: int = 3,
    mag_min: float | None = None,
    mag_limit: float | None = None,
    use_cache: bool = True,
) -> bytes:
    """Generate a finding chart for a source, as a PDF or PNG file.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    imsize : float, optional
        Square image size in arcmin, in [2, 15]. Defaults to 4.0.
    facility : str, optional
        Starlist format, one of ``"Keck"``, ``"Shane"``, ``"P200"``, or
        ``"P200-NGPS"``. Defaults to ``"Keck"``.
    image_source : str, optional
        Chart image source, one of ``"ps1"``, ``"desi"``, ``"dss"``, or
        ``"ztfref"``. Defaults to ``"ps1"``.
    use_ztfref : bool, optional
        Use the ZTFref catalog for offset-star positions instead of Gaia
        DR3. Defaults to True.
    obstime : str, optional
        Observation time in ISO format. Defaults to now.
    output_type : str, optional
        Output file type, ``"pdf"`` or ``"png"``. Defaults to ``"pdf"``.
    num_offset_stars : int, optional
        Number of offset stars to show, in [0, 4]. Defaults to 3.
    mag_min, mag_limit : float, optional
        Brightest and faintest offset-star magnitudes to allow. Each
        defaults to the facility value.
    use_cache : bool, optional
        Reuse a cached chart when one is available. Defaults to True.
    """
    params = _source_finder_params(
        imsize=imsize,
        facility=facility,
        image_source=image_source,
        use_ztfref=use_ztfref,
        obstime=obstime,
        output_type=output_type,
        num_offset_stars=num_offset_stars,
        mag_min=mag_min,
        mag_limit=mag_limit,
        use_cache=use_cache,
    )
    response = client.get(f"/api/sources/{obj_id}/finder", params=params)
    return unwrap_content(response)


def fetch_source_finder_json(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    imsize: float = 4.0,
    facility: str = "Keck",
    image_source: str = "ps1",
    use_ztfref: bool = True,
    obstime: str | None = None,
    output_type: str = "pdf",
    num_offset_stars: int = 3,
    mag_min: float | None = None,
    mag_limit: float | None = None,
    use_cache: bool = True,
) -> SourceFinderChart:
    """Generate a finding chart and return it as base64 JSON with its starlist.

    Same endpoint as :func:`fetch_source_finder`, called with ``as_json``.
    ``public_url`` is only present when the chart was cached.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    imsize : float, optional
        Square image size in arcmin, in [2, 15]. Defaults to 4.0.
    facility : str, optional
        Starlist format, one of ``"Keck"``, ``"Shane"``, ``"P200"``, or
        ``"P200-NGPS"``. Defaults to ``"Keck"``.
    image_source : str, optional
        Chart image source, one of ``"ps1"``, ``"desi"``, ``"dss"``, or
        ``"ztfref"``. Defaults to ``"ps1"``.
    use_ztfref : bool, optional
        Use the ZTFref catalog for offset-star positions instead of Gaia
        DR3. Defaults to True.
    obstime : str, optional
        Observation time in ISO format. Defaults to now.
    output_type : str, optional
        Chart file type, ``"pdf"`` or ``"png"``. Defaults to ``"pdf"``.
    num_offset_stars : int, optional
        Number of offset stars to show, in [0, 4]. Defaults to 3.
    mag_min, mag_limit : float, optional
        Brightest and faintest offset-star magnitudes to allow. Each
        defaults to the facility value.
    use_cache : bool, optional
        Reuse a cached chart when one is available. Defaults to True.
    """
    params = _source_finder_params(
        imsize=imsize,
        facility=facility,
        image_source=image_source,
        use_ztfref=use_ztfref,
        obstime=obstime,
        output_type=output_type,
        num_offset_stars=num_offset_stars,
        mag_min=mag_min,
        mag_limit=mag_limit,
        use_cache=use_cache,
    )
    params["as_json"] = True
    response = client.get(f"/api/sources/{obj_id}/finder", params=params)
    return SourceFinderChart.model_validate(unwrap(response))


def fetch_finder_chart_facilities(
    client: httpx.Client,
) -> dict[str, FinderChartFacility]:
    """Retrieve the per-facility default finding-chart parameters.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/finder_chart/facilities")
    return {
        name: FinderChartFacility.model_validate(parameters)
        for name, parameters in unwrap(response).items()
    }


def post_source_host(client: httpx.Client, obj_id: str, galaxy_name: str) -> None:
    """Set a source's host galaxy.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    galaxy_name : str
        Name of an existing galaxy to associate with the object.
    """
    unwrap(
        client.post(
            f"/api/sources/{obj_id}/host",
            json={"galaxyName": galaxy_name},
        )
    )


def delete_source_host(client: httpx.Client, obj_id: str) -> None:
    """Clear a source's host galaxy.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    unwrap(client.delete(f"/api/sources/{obj_id}/host"))


def fetch_source_saved_groups(
    client: httpx.Client, obj_id: str
) -> list[SourceSavedGroup]:
    """Retrieve the groups a source is saved to or requested for.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    response = client.get(f"/api/sources/{obj_id}/groups")
    return [SourceSavedGroup.model_validate(group) for group in unwrap(response)]


def post_source_labels(client: httpx.Client, obj_id: str, group_ids: list[int]) -> None:
    """Record that the calling user has labelled a source for some groups.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    group_ids : list of int
        Groups to record labelling for. Labels already present are left
        untouched.
    """
    unwrap(
        client.post(
            f"/api/sources/{obj_id}/labels",
            json={"groupIds": group_ids},
        )
    )


def delete_source_labels(
    client: httpx.Client, obj_id: str, group_ids: list[int]
) -> None:
    """Remove the calling user's labels on a source for some groups.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    group_ids : list of int
        Groups to remove labels for. Sent in the request body.
    """
    unwrap(
        client.request(
            "DELETE",
            f"/api/sources/{obj_id}/labels",
            json={"groupIds": group_ids},
        )
    )


def fetch_source_color_mag(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    apparent_mag_key: str | None = None,
    parallax_key: str | None = None,
    absorption_key: str | None = None,
    absolute_mag_key: str | None = None,
    blue_mag_key: str | None = None,
    red_mag_key: str | None = None,
    color_key: str | None = None,
) -> list[SourceColorMag]:
    """Retrieve a source's color and absolute magnitude from cross-match annotations.

    All key arguments are matched against annotation keys ignoring case and
    underscores.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    catalog : str, optional
        Partial match on the annotation origin. Defaults to ``"GAIA"``.
    apparent_mag_key : str, optional
        Annotation key holding the apparent magnitude. Defaults to
        ``"Mag_G"``.
    parallax_key : str, optional
        Annotation key holding the parallax, used with the apparent
        magnitude to derive the absolute magnitude. Defaults to ``"Plx"``.
    absorption_key : str, optional
        Annotation key holding the absorption term added to the derived
        absolute magnitude. Defaults to ``"A_G"``.
    absolute_mag_key : str, optional
        Annotation key holding the absolute magnitude directly; overrides
        ``apparent_mag_key``, ``parallax_key`` and ``absorption_key``.
    blue_mag_key, red_mag_key : str, optional
        Annotation keys differenced to form the color. Default to
        ``"Mag_Bp"`` and ``"Mag_Rp"``.
    color_key : str, optional
        Annotation key holding the color directly; overrides
        ``blue_mag_key`` and ``red_mag_key``.
    """
    params: dict[str, str] = {}
    optional = {
        "catalog": catalog,
        "apparentMagKey": apparent_mag_key,
        "parallaxKey": parallax_key,
        "absorptionKey": absorption_key,
        "absoluteMagKey": absolute_mag_key,
        "blueMagKey": blue_mag_key,
        "redMagKey": red_mag_key,
        "colorKey": color_key,
    }
    params.update(
        {name: value for name, value in optional.items() if value is not None}
    )
    response = client.get(f"/api/sources/{obj_id}/color_mag", params=params)
    return [SourceColorMag.model_validate(entry) for entry in unwrap(response)]


def post_source_gcn_event_crossmatch(
    client: httpx.Client,
    obj_id: str,
    payload: SourceGcnEventCrossmatchPost,
) -> None:
    """Crossmatch a source against GCN events in a date range.

    The crossmatch runs in the background; the call returns as soon as it
    is queued. ``start_date`` and ``end_date`` are required and must be
    within 31 days of each other.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    payload : SourceGcnEventCrossmatchPost
        Date range, probability contour, and GCN/localization filters.
    """
    unwrap(
        client.post(
            f"/api/sources/{obj_id}/gcn_event",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )
    )


def post_source_mpc_query(
    client: httpx.Client,
    obj_id: str,
    payload: SourceMpcQueryPost | None = None,
) -> None:
    """Query the Minor Planet Center for known minor planets at a source's position.

    The query runs in the background; on a match the object is flagged as
    a solar system object and its MPC name and alias are stored.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    payload : SourceMpcQueryPost, optional
        Query settings. The server defaults to observatory code ``"500"``
        (geocentric), the current time, a limiting magnitude of 24.0, and a
        search radius of 1 arcmin.
    """
    body = {} if payload is None else payload.model_dump(exclude_none=True)
    unwrap(client.post(f"/api/sources/{obj_id}/mpc", json=body))


def fetch_source_tns(
    client: httpx.Client,
    obj_id: str,
    *,
    radius: float = 2.0,
) -> None:
    """Look up a source on the Transient Name Server.

    The lookup runs in the background and stores the result on the object;
    the call returns as soon as it is queued.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    radius : float, optional
        Cone-search radius in arcseconds; must be non-negative. Defaults
        to 2.0.
    """
    unwrap(client.get(f"/api/sources/{obj_id}/tns", params={"radius": radius}))


def fetch_source_observability(
    client: httpx.Client,
    obj_id: str,
    *,
    max_airmass: float = 2.5,
    twilight: str = "astronomical",
) -> bytes:
    """Generate an observability plot for a source, as a PDF file.

    The plot covers the next 24 hours for every fixed-location telescope
    the token can see.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    max_airmass : float, optional
        Maximum airmass to consider. Defaults to 2.5.
    twilight : str, optional
        Twilight definition, one of ``"astronomical"`` (-18 degrees),
        ``"nautical"`` (-12 degrees), or ``"civil"`` (-6 degrees).
        Defaults to ``"astronomical"``.
    """
    response = client.get(
        f"/api/sources/{obj_id}/observability",
        params={"maxAirmass": max_airmass, "twilight": twilight},
    )
    return unwrap_content(response)


def post_source_photometry_copy(
    client: httpx.Client,
    obj_id: str,
    origin_id: str,
    group_ids: list[int],
) -> None:
    """Copy every photometry point from one source onto another.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the target source, which the photometry is copied to.
    origin_id : str
        Object ID of the source the photometry is copied from.
    group_ids : list of int
        Groups to give access to the copied photometry.
    """
    unwrap(
        client.post(
            f"/api/sources/{obj_id}/copy_photometry",
            json={"origin_id": origin_id, "group_ids": group_ids},
        )
    )


def fetch_source_phot_stat(client: httpx.Client, obj_id: str) -> PhotStat:
    """Retrieve the photometry statistics of a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    response = client.get(f"/api/sources/{obj_id}/phot_stat")
    return PhotStat.model_validate(unwrap(response))


def post_source_phot_stat(client: httpx.Client, obj_id: str) -> None:
    """Calculate and store photometry statistics for a source.

    Requires system admin permissions, and fails if statistics already
    exist for the object.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    unwrap(client.post(f"/api/sources/{obj_id}/phot_stat"))


def update_source_phot_stat(client: httpx.Client, obj_id: str) -> None:
    """Recalculate a source's photometry statistics, creating them if absent.

    Requires system admin permissions.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    unwrap(client.put(f"/api/sources/{obj_id}/phot_stat"))


def delete_source_phot_stat(client: httpx.Client, obj_id: str) -> None:
    """Delete a source's photometry statistics.

    Requires system admin permissions.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source.
    """
    unwrap(client.delete(f"/api/sources/{obj_id}/phot_stat"))


def fetch_phot_stats_counts(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    created_at_start_time: str | None = None,
    created_at_end_time: str | None = None,
    quick_update_start_time: str | None = None,
    quick_update_end_time: str | None = None,
    full_update_start_time: str | None = None,
    full_update_end_time: str | None = None,
) -> PhotStatCounts:
    """Count the objects with and without photometry statistics.

    Requires system admin permissions.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    created_at_start_time, created_at_end_time : str, optional
        Arrow-parseable times bounding object creation.
    quick_update_start_time, quick_update_end_time : str, optional
        Arrow-parseable times bounding the last statistics update of any
        kind.
    full_update_start_time, full_update_end_time : str, optional
        Arrow-parseable times bounding the last full statistics update.
    """
    params: dict[str, str] = {}
    optional = {
        "createdAtStartTime": created_at_start_time,
        "createdAtEndTime": created_at_end_time,
        "quickUpdateStartTime": quick_update_start_time,
        "quickUpdateEndTime": quick_update_end_time,
        "fullUpdateStartTime": full_update_start_time,
        "fullUpdateEndTime": full_update_end_time,
    }
    params.update(
        {name: value for name, value in optional.items() if value is not None}
    )
    response = client.get("/api/phot_stats", params=params)
    return PhotStatCounts.model_validate(unwrap(response))


def post_phot_stats(
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    created_at_start_time: str | None = None,
    created_at_end_time: str | None = None,
) -> PhotStatsBatch:
    """Calculate photometry statistics for a page of objects that lack them.

    Requires system admin permissions.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls over the objects without statistics;
        ``num_per_page`` is capped server-side at 500.
    created_at_start_time, created_at_end_time : str, optional
        Arrow-parseable times bounding object creation.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if created_at_start_time is not None:
        params["createdAtStartTime"] = created_at_start_time
    if created_at_end_time is not None:
        params["createdAtEndTime"] = created_at_end_time
    response = client.post("/api/phot_stats", params=params)
    return PhotStatsBatch.model_validate(unwrap(response))


def update_phot_stats(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    created_at_start_time: str | None = None,
    created_at_end_time: str | None = None,
    quick_update_start_time: str | None = None,
    quick_update_end_time: str | None = None,
    full_update_start_time: str | None = None,
    full_update_end_time: str | None = None,
) -> PhotStatsBatch:
    """Recalculate photometry statistics for a page of objects that have them.

    Requires system admin permissions.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls; ``num_per_page`` is capped server-side at 500.
    created_at_start_time, created_at_end_time : str, optional
        Arrow-parseable times bounding object creation.
    quick_update_start_time, quick_update_end_time : str, optional
        Arrow-parseable times bounding the last statistics update of any
        kind.
    full_update_start_time, full_update_end_time : str, optional
        Arrow-parseable times bounding the last full statistics update.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    optional = {
        "createdAtStartTime": created_at_start_time,
        "createdAtEndTime": created_at_end_time,
        "quickUpdateStartTime": quick_update_start_time,
        "quickUpdateEndTime": quick_update_end_time,
        "fullUpdateStartTime": full_update_start_time,
        "fullUpdateEndTime": full_update_end_time,
    }
    params.update(
        {name: value for name, value in optional.items() if value is not None}
    )
    response = client.patch("/api/phot_stats", params=params)
    return PhotStatsBatch.model_validate(unwrap(response))


def fetch_phot_stats_aggregate(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    x_field: str | None = None,
    y_field: str | None = None,
    z_field: str | None = None,
    classifications: list[str] | None = None,
    classification_prob_threshold: float | None = None,
    group_id: int | None = None,
    obj_ids: list[str] | None = None,
    max_matches: int | None = None,
) -> PhotStatAggregate:
    """Retrieve photometry statistics across many sources, for bulk plotting.

    Called without ``x_field`` and ``y_field``, the response holds only the
    list of plottable fields.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    x_field, y_field : str, optional
        Photometry-statistics fields for the x and y axes; both are
        required to get any points back.
    z_field : str, optional
        Optional third axis.
    classifications : list of str, optional
        Restrict to sources carrying any of these classification names.
    classification_prob_threshold : float, optional
        Only count classifications at or above this probability.
    group_id : int, optional
        Restrict to sources saved to this group.
    obj_ids : list of str, optional
        Restrict to these objects.
    max_matches : int, optional
        Maximum number of points to return. Defaults to 20000 server-side
        and is capped at 100000; the response flags truncation.
    """
    params: dict[str, str | int | float] = {}
    if x_field is not None:
        params["xField"] = x_field
    if y_field is not None:
        params["yField"] = y_field
    if z_field is not None:
        params["zField"] = z_field
    if classifications is not None:
        params["classifications"] = ",".join(classifications)
    if classification_prob_threshold is not None:
        params["classificationProbThreshold"] = classification_prob_threshold
    if group_id is not None:
        params["group_id"] = group_id
    if obj_ids is not None:
        params["obj_ids"] = ",".join(obj_ids)
    if max_matches is not None:
        params["maxMatches"] = max_matches
    response = client.get("/api/phot_stats/aggregate", params=params)
    return PhotStatAggregate.model_validate(unwrap(response))


def fetch_source_exists(
    client: httpx.Client,
    obj_id: str | None = None,
    *,
    ra: float | None = None,
    dec: float | None = None,
    radius: float | None = None,
) -> SourceExists:
    """Check whether a source already exists by name or by position.

    Provide ``obj_id``, or all of ``ra``, ``dec`` and ``radius``, or both:
    with both, a name match short-circuits and a position match is tried
    otherwise.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str, optional
        Object ID to look for.
    ra, dec, radius : float, optional
        Cone search in decimal degrees; provide all three together.
    """
    params: dict[str, float] = {}
    if ra is not None:
        params["ra"] = ra
    if dec is not None:
        params["dec"] = dec
    if radius is not None:
        params["radius"] = radius
    path = "/api/source_exists" if obj_id is None else f"/api/source_exists/{obj_id}"
    response = client.get(path, params=params)
    return SourceExists.model_validate(unwrap(response))


def post_source_notification(
    client: httpx.Client, payload: SourceNotificationPost
) -> SourceNotificationPostResponse:
    """Notify the members of some groups about a source.

    Requires notifications to be enabled on the deployment, and the token
    must belong to every group the source is being announced to.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SourceNotificationPost
        Source, recipient groups, and notification level: ``"soft"`` sends
        an email, ``"hard"`` sends an email and an SMS.
    """
    response = client.post(
        "/api/source_notifications",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return SourceNotificationPostResponse.model_validate(unwrap(response))
