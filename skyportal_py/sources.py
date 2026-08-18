"""Typed endpoint functions for ``/api/sources``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.groups import Group


class Source(BaseModel):
    """A SkyPortal source."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float | None = None
    dec: float | None = None
    redshift: float | None = None
    groups: list[Group] = Field(default_factory=list)


class SourcesPage(BaseModel):
    """One page of results from a sources query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    sources: list[Source]
    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


class SourcePost(BaseModel):
    """Payload for saving a new source."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float
    dec: float
    group_ids: list[int] | None = None


class SourcePostResponse(BaseModel):
    """Result of saving a new source."""

    model_config = ConfigDict(extra="forbid")

    id: str
    saved_to_groups: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def fetch_source(
    client: httpx.Client,
    obj_id: str,
    *,
    include_thumbnails: bool = False,
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
    """
    response = client.get(
        f"/api/sources/{obj_id}",
        params={"includeThumbnails": include_thumbnails},
    )
    return Source.model_validate(unwrap(response))


def fetch_sources(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    ra: float | None = None,
    dec: float | None = None,
    radius: float | None = None,
    group_ids: list[int] | None = None,
) -> SourcesPage:
    """Query saved sources, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    ra, dec, radius : float, optional
        Cone-search filter, all in degrees; provide all three together.
    group_ids : list of int, optional
        Restrict to sources saved to these groups.
    """
    params: dict[str, str | int | float] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if ra is not None:
        params["ra"] = ra
    if dec is not None:
        params["dec"] = dec
    if radius is not None:
        params["radius"] = radius
    if group_ids is not None:
        params["group_ids"] = ",".join(str(gid) for gid in group_ids)
    response = client.get("/api/sources", params=params)
    return SourcesPage.model_validate(unwrap(response))


def post_source(client: httpx.Client, payload: SourcePost) -> SourcePostResponse:
    """Save a new source (or update one the token could not previously see).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SourcePost
        The source to save. If ``group_ids`` is omitted, the server saves
        the source to all of the token's groups.
    """
    response = client.post("/api/sources", json=payload.model_dump(exclude_none=True))
    return SourcePostResponse.model_validate(unwrap(response))


def update_source(
    client: httpx.Client,
    obj_id: str,
    *,
    ra: float | None = None,
    dec: float | None = None,
    redshift: float | None = None,
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
    """
    fields = {"ra": ra, "dec": dec, "redshift": redshift}
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
    public_url_expires_at: str | None = None


class SourceSavedGroup(BaseModel):
    """A group a source is saved to."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    name: str | None = None
    nickname: str | None = None
    description: str | None = None
    private: bool | None = None
    auto_accept_requests: bool | None = None
    single_user_group: bool | None = None


class SourceColorMag(BaseModel):
    """A color and absolute magnitude derived from one catalog cross-match."""

    model_config = ConfigDict(extra="forbid")

    origin: str | None = None
    color: float | None = None
    abs_mag: float | None = None


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
    level: str
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


class PhotStat(BaseModel):
    """Aggregate photometry statistics for one object."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    last_update: str | None = None
    last_full_update: str | None = None
    last_phot_add_time: str | None = None
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
