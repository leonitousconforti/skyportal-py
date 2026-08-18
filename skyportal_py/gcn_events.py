"""Typed endpoint functions for ``/api/gcn_event``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.localizations import Localization
from skyportal_py.mmadetectors import MMADetector
from skyportal_py.observation_plans import ObservationPlanRequest


class GcnNotice(BaseModel):
    """A GCN notice (VOEvent, JSON or dictionary) attached to an event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    ivorn: str | None = None
    notice_type: str | None = None
    notice_format: str | None = None
    stream: str | None = None
    date: str | None = None
    content: Any = None
    has_localization: bool | None = None
    localization_ingested: bool | None = None
    sent_by: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnProperty(BaseModel):
    """A set of properties parsed from a GCN event notice."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    data: dict[str, Any] | None = None
    sent_by: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnTag(BaseModel):
    """A tag on a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    text: str | None = None
    sent_by: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnSummary(BaseModel):
    """A human-readable summary of a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    group_id: int | None = None
    title: str | None = None
    text: str | None = None
    sent_by: dict[str, Any] | None = None
    group: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnReport(BaseModel):
    """A structured (publishable) report on a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    group_id: int | None = None
    report_name: str | None = None
    data: Any = None
    published: bool | None = None
    sent_by: dict[str, Any] | None = None
    group: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnTrigger(BaseModel):
    """Whether a GCN event triggered a given allocation."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    dateobs: str | None = None
    allocation_id: int | None = None
    triggered: bool | None = None
    allocation: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnEventUser(BaseModel):
    """A user assigned as an advocate for a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    gcnevent_id: int | None = None
    user_id: int | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    user: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnEventLocalization(Localization):
    """A localization as returned inside a GCN event payload."""

    tags: list[dict[str, Any]] | None = None
    properties: list[dict[str, Any]] | None = None
    center: Any = None


class GcnEventCrossmatchState(BaseModel):
    """Progress of the alert crossmatch for one event/filter/localization."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    gcnevent_id: int | None = None
    filter_id: int | None = None
    localization_id: int | None = None
    last_queried: str | None = None
    last_alert_jd: float | None = None
    status: str | None = None
    error: str | None = None
    archival_done: bool | None = None
    n_matches: int | None = None
    gcnevent: dict[str, Any] | None = None
    filter: dict[str, Any] | None = None
    localization: dict[str, Any] | None = None


class SurveyEfficiencyForObservations(BaseModel):
    """A survey efficiency analysis of executed observations for an event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    requester_id: int | None = None
    gcnevent_id: int | None = None
    localization_id: int | None = None
    instrument_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str | None = None
    lightcurves: Any = None
    number_of_transients: int | None = None
    number_in_covered: int | None = None
    number_detected: int | None = None
    efficiency: float | None = None
    requester: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None
    localization: dict[str, Any] | None = None
    instrument: dict[str, Any] | None = None
    groups: list[dict[str, Any]] | None = None


class GcnCatalogQuery(BaseModel):
    """A catalog query submitted for a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    requester_id: int | None = None
    allocation_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str | None = None
    requester: dict[str, Any] | None = None
    allocation: dict[str, Any] | None = None
    target_groups: list[dict[str, Any]] | None = None


class GcnEvent(BaseModel):
    """A GCN event, keyed by its UTC observation time (``dateobs``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    sent_by_id: int | None = None
    dateobs: str | None = None
    trigger_id: str | None = None
    aliases: list[str] | None = None
    tach_id: str | None = None
    circulars: dict[str, Any] | None = None
    gracedb_log: Any = None
    gracedb_labels: Any = None
    lightcurve: str | None = None
    event_users_ids: list[int] | None = None
    tags: list[str] | None = None
    localizations: list[GcnEventLocalization] | None = None
    gcn_notices: list[GcnNotice] | None = None
    properties: list[GcnProperty] | None = None
    summaries: list[GcnSummary] | None = None
    reports: list[GcnReport] | None = None
    comments: list[dict[str, Any]] | None = None
    reminders: list[dict[str, Any]] | None = None
    detectors: list[MMADetector] | None = None
    gcn_triggers: list[GcnTrigger] | None = None
    event_users: list[GcnEventUser] | None = None
    gcnevent_users: list[GcnEventUser] | None = None
    users: list[dict[str, Any]] | None = None
    groups: list[dict[str, Any]] | None = None
    sent_by: dict[str, Any] | None = None
    observationplan_requests: list[ObservationPlanRequest] | None = None
    survey_efficiency_analyses: list[SurveyEfficiencyForObservations] | None = None
    crossmatch_states: list[GcnEventCrossmatchState] | None = None


class GcnEventsPage(BaseModel):
    """One page of results from a GCN events query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    events: list[GcnEvent] = Field(default_factory=list)
    total_matches: int = Field(alias="totalMatches", default=0)


class GcnEventPost(BaseModel):
    """Payload for ingesting a GCN event."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    xml: str | None = None
    json_notice: dict[str, Any] | None = Field(default=None, alias="json")
    dateobs: str | None = None
    trigger_id: str | None = None
    aliases: list[str] | None = None
    group_ids: list[int] | None = None
    properties: dict[str, Any] | None = None
    tags: list[str] | None = None
    skymap: Any = None


class GcnEventPostResponse(BaseModel):
    """Result of ingesting a GCN event."""

    model_config = ConfigDict(extra="forbid")

    gcnevent_id: int | None = None
    dateobs: str | None = None
    notice_id: int | None = None


class GcnEventIdResponse(BaseModel):
    """A response carrying only the ID of the affected GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int


class GcnEventTagPostResponse(BaseModel):
    """Result of tagging a GCN event."""

    model_config = ConfigDict(extra="forbid")

    gcntag_id: int


class GcnEventTachInfo(BaseModel):
    """The TACH identifiers, aliases and circulars of a GCN event."""

    model_config = ConfigDict(extra="forbid")

    tach_id: str | None = None
    aliases: list[str] | None = None
    circulars: dict[str, Any] | None = None


class GcnEventCrossmatchRequeue(BaseModel):
    """Result of requeueing the alert crossmatch of a GCN event."""

    model_config = ConfigDict(extra="forbid")

    filters_requeued: int


class GcnEventInstrumentFields(BaseModel):
    """Instrument field probabilities for a GCN event localization."""

    model_config = ConfigDict(extra="forbid")

    field_ids: list[int] = Field(default_factory=list)
    probabilities: list[float] = Field(default_factory=list)


class GcnSummaryPost(BaseModel):
    """Payload for generating a GCN event summary."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    title: str
    group_id: int = Field(alias="groupId")
    number: int | None = None
    subject: str | None = None
    user_ids: list[int] | None = Field(default=None, alias="userIds")
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    localization_name: str | None = Field(default=None, alias="localizationName")
    localization_cumprob: float | None = Field(
        default=None, alias="localizationCumprob"
    )
    number_detections: int | None = Field(default=None, alias="numberDetections")
    number_observations: int | None = Field(default=None, alias="numberObservations")
    show_sources: bool | None = Field(default=None, alias="showSources")
    show_galaxies: bool | None = Field(default=None, alias="showGalaxies")
    show_observations: bool | None = Field(default=None, alias="showObservations")
    no_text: bool | None = Field(default=None, alias="noText")
    photometry_in_window: bool | None = Field(default=None, alias="photometryInWindow")
    stats_method: str | None = Field(default=None, alias="statsMethod")
    instrument_ids: list[int] | None = Field(default=None, alias="instrumentIds")
    acknowledgements: str | None = None


class GcnReportPost(BaseModel):
    """Payload for generating a GCN event report."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    report_name: str = Field(alias="reportName")
    group_id: int = Field(alias="groupId")
    start_date: str | None = Field(default=None, alias="startDate")
    end_date: str | None = Field(default=None, alias="endDate")
    localization_name: str | None = Field(default=None, alias="localizationName")
    localization_cumprob: float | None = Field(
        default=None, alias="localizationCumprob"
    )
    number_detections: int | None = Field(default=None, alias="numberDetections")
    show_sources: bool | None = Field(default=None, alias="showSources")
    show_observations: bool | None = Field(default=None, alias="showObservations")
    show_survey_efficiencies: bool | None = Field(
        default=None, alias="showSurveyEfficiencies"
    )
    photometry_in_window: bool | None = Field(default=None, alias="photometryInWindow")
    stats_method: str | None = Field(default=None, alias="statsMethod")
    instrument_ids: list[int] | None = Field(default=None, alias="instrumentIds")


class DefaultGcnTag(BaseModel):
    """A rule that automatically tags matching GCN events."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    requester_id: int | None = None
    default_tag_name: str | None = None
    filters: dict[str, Any] | None = None
    requester: dict[str, Any] | None = None


class DefaultGcnTagPost(BaseModel):
    """Payload for creating a default GCN tag."""

    model_config = ConfigDict(extra="forbid")

    default_tag_name: str
    filters: dict[str, Any] | None = None


class GcnEventObj(BaseModel):
    """An object's standing against a GCN event."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    obj_id: str | None = None
    dateobs: str | None = None
    status: str | None = None
    confirmer_id: int | None = None
    explanation: str | None = None
    notes: str | None = None
    obj: dict[str, Any] | None = None
    confirmer: dict[str, Any] | None = None
    gcnevent: dict[str, Any] | None = None


class GcnEventObjPost(BaseModel):
    """Payload for recording an object's standing against a GCN event."""

    model_config = ConfigDict(extra="forbid")

    source_id: str
    status: str
    localization_name: str
    localization_cumprob: float
    start_date: str
    end_date: str
    explanation: str | None = None
    notes: str | None = None


class GcnEventObjIdResponse(BaseModel):
    """Result of creating, updating or deleting a source-in-GCN record."""

    model_config = ConfigDict(extra="forbid")

    id: int


class GcnEventObjCrossmatchPost(BaseModel):
    """Payload for crossmatching an object against GCN events."""

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


def post_gcn_event(
    client: httpx.Client,
    payload: GcnEventPost,
) -> GcnEventPostResponse:
    """Ingest a GCN event from a VOEvent, a JSON notice or a dictionary.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : GcnEventPost
        The event to ingest. Provide ``xml`` (a VOEvent) or ``json_notice``
        (a GCN JSON notice); otherwise ``dateobs`` is required and the
        remaining fields describe the event. ``skymap`` accepts a
        multi-order map, a base64 FITS blob, a URL, or a cone/ellipse/polygon
        description. ``notice_id`` in the response is null for the
        dictionary form.
    """
    response = client.post(
        "/api/gcn_event",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return GcnEventPostResponse.model_validate(unwrap(response))


def fetch_gcn_event(
    client: httpx.Client,
    dateobs: str,
    *,
    exclude_notice_content: bool = False,
) -> GcnEvent:
    """Retrieve a single GCN event, with its localizations and summaries.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp, e.g. ``"2023-05-23T12:00:00"``.
    exclude_notice_content : bool, optional
        Omit the raw notice content from each entry of ``gcn_notices``.
        Defaults to false server-side.
    """
    response = client.get(
        f"/api/gcn_event/{dateobs}",
        params={"excludeNoticeContent": exclude_notice_content},
    )
    return GcnEvent.model_validate(unwrap(response))


def fetch_gcn_events(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 10,
    start_date: str | None = None,
    end_date: str | None = None,
    partial_dateobs: str | None = None,
    gcn_tag_keep: list[str] | None = None,
    gcn_tag_remove: list[str] | None = None,
    localization_tag_keep: list[str] | None = None,
    localization_tag_remove: list[str] | None = None,
    gcn_properties_filter: list[str] | None = None,
    localization_properties_filter: list[str] | None = None,
    group_ids: list[int] | None = None,
    sort_by: str | None = None,
    sort_order: str = "asc",
) -> GcnEventsPage:
    """Query GCN events, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls. The server caps the page size.
    start_date, end_date : str, optional
        Arrow-parseable bounds on ``dateobs``.
    partial_dateobs : str, optional
        Prefix of a ``dateobs`` (or a substring of an alias) to match.
        Cannot be combined with :func:`fetch_gcn_event`'s path lookup.
    gcn_tag_keep, gcn_tag_remove : list of str, optional
        Keep events carrying any of these GCN tags, or drop them.
    localization_tag_keep, localization_tag_remove : list of str, optional
        The same, applied to the tags of the events' localizations.
    gcn_properties_filter : list of str, optional
        Property filters, each ``"name"`` or ``"name: value: operator"``
        (operator in ``lt``, ``le``, ``eq``, ``ne``, ``ge``, ``gt``).
    localization_properties_filter : list of str, optional
        The same, applied to localization properties.
    group_ids : list of int, optional
        Return only events shared with at least one of these groups. This
        narrows what the token can already read, it does not widen it.
    sort_by : str, optional
        Only ``"dateobs"`` is supported. Defaults to newest first.
    sort_order : str, optional
        ``"asc"`` or ``"desc"``.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
        "sortOrder": sort_order,
    }
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    if partial_dateobs is not None:
        params["partialdateobs"] = partial_dateobs
    if gcn_tag_keep is not None:
        params["gcnTagKeep"] = ",".join(gcn_tag_keep)
    if gcn_tag_remove is not None:
        params["gcnTagRemove"] = ",".join(gcn_tag_remove)
    if localization_tag_keep is not None:
        params["localizationTagKeep"] = ",".join(localization_tag_keep)
    if localization_tag_remove is not None:
        params["localizationTagRemove"] = ",".join(localization_tag_remove)
    if gcn_properties_filter is not None:
        params["gcnPropertiesFilter"] = ",".join(gcn_properties_filter)
    if localization_properties_filter is not None:
        params["localizationPropertiesFilter"] = ",".join(
            localization_properties_filter
        )
    if group_ids is not None:
        params["groupIds"] = ",".join(str(gid) for gid in group_ids)
    if sort_by is not None:
        params["sortBy"] = sort_by
    response = client.get("/api/gcn_event", params=params)
    return GcnEventsPage.model_validate(unwrap(response))


def delete_gcn_event(client: httpx.Client, dateobs: str) -> None:
    """Delete a GCN event, along with its localizations, notices and tags.

    Requires the ``System admin`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event to delete.
    """
    unwrap(client.delete(f"/api/gcn_event/{dateobs}"))


def post_gcn_event_alias(client: httpx.Client, dateobs: str, alias: str) -> None:
    """Add an alias to a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    alias : str
        Alias to add. The server rejects an alias the event already has.
    """
    unwrap(client.post(f"/api/gcn_event/{dateobs}/alias", json={"alias": alias}))


def delete_gcn_event_alias(client: httpx.Client, dateobs: str, alias: str) -> None:
    """Remove an alias from a GCN event.

    Aliases containing ``LVC#`` or ``FERMI#`` cannot be removed.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    alias : str
        Alias to remove.
    """
    unwrap(
        client.request(
            "DELETE",
            f"/api/gcn_event/{dateobs}/alias",
            json={"alias": alias},
        )
    )


def fetch_gcn_event_tags(client: httpx.Client) -> list[str]:
    """Retrieve all distinct GCN event tags.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/gcn_event/tags")
    return [str(tag) for tag in unwrap(response)]


def post_gcn_event_tag(
    client: httpx.Client,
    dateobs: str,
    text: str,
) -> GcnEventTagPostResponse:
    """Tag a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event to tag.
    text : str
        The tag text.
    """
    response = client.post(
        "/api/gcn_event/tags",
        json={"dateobs": dateobs, "text": text},
    )
    return GcnEventTagPostResponse.model_validate(unwrap(response))


def delete_gcn_event_tag(client: httpx.Client, dateobs: str, tag: str) -> None:
    """Remove a tag from a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the tagged event.
    tag : str
        Text of the tag to remove.
    """
    unwrap(
        client.request(
            "DELETE",
            f"/api/gcn_event/tags/{dateobs}",
            json={"tag": tag},
        )
    )


def fetch_gcn_event_properties(client: httpx.Client) -> list[str]:
    """Retrieve all distinct GCN event property names, sorted.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/gcn_event/properties")
    return [str(name) for name in unwrap(response)]


def fetch_gcn_event_survey_efficiency(
    client: httpx.Client,
    gcnevent_id: int,
) -> list[SurveyEfficiencyForObservations]:
    """Retrieve the survey efficiency analyses of a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    gcnevent_id : int
        Numeric ID of the GCN event (not its ``dateobs``).
    """
    response = client.get(f"/api/gcn_event/{gcnevent_id}/survey_efficiency")
    return [
        SurveyEfficiencyForObservations.model_validate(analysis)
        for analysis in unwrap(response)
    ]


def fetch_gcn_event_observation_plan_requests(
    client: httpx.Client,
    gcnevent_id: int,
) -> list[ObservationPlanRequest]:
    """Retrieve the observation plan requests of a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    gcnevent_id : int
        Numeric ID of the GCN event (not its ``dateobs``).
    """
    response = client.get(f"/api/gcn_event/{gcnevent_id}/observation_plan_requests")
    return [
        ObservationPlanRequest.model_validate(request) for request in unwrap(response)
    ]


def fetch_gcn_event_catalog_queries(
    client: httpx.Client,
    gcnevent_id: int,
) -> list[GcnCatalogQuery]:
    """Retrieve the catalog queries submitted for a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    gcnevent_id : int
        Numeric ID of the GCN event (not its ``dateobs``).
    """
    response = client.get(f"/api/gcn_event/{gcnevent_id}/catalog_query")
    return [GcnCatalogQuery.model_validate(query) for query in unwrap(response)]


def post_gcn_event_user(client: httpx.Client, dateobs: str, user_id: int) -> None:
    """Add a user as an advocate for a GCN event.

    The user is notified in SkyPortal.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    user_id : int
        ID of the user to add.
    """
    unwrap(client.post(f"/api/gcn_event/{dateobs}/users", json={"userID": user_id}))


def delete_gcn_event_user(client: httpx.Client, dateobs: str, user_id: int) -> None:
    """Remove a user from the advocates of a GCN event.

    Only the user themselves (or a system admin) may be removed.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    user_id : int
        ID of the user to remove.
    """
    unwrap(client.delete(f"/api/gcn_event/{dateobs}/users/{user_id}"))


def fetch_gcn_event_notice_download(
    client: httpx.Client,
    dateobs: str,
    notice_id: int,
) -> bytes:
    """Download the raw content of a GCN notice.

    The payload is XML for VOEvent notices, JSON for JSON notices, and plain
    text otherwise.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event the notice belongs to.
    notice_id : int
        ID of the notice to download.
    """
    response = client.get(
        f"/api/gcn_event/{dateobs}/notice/{notice_id}/download",
    )
    return unwrap_content(response)


def post_gcn_event_gracedb(client: httpx.Client, dateobs: str) -> GcnEventIdResponse:
    """Scrape GraceDB for a gravitational-wave event's logs and labels.

    The scrape runs in the background; the event must already carry an
    ``LVC#`` alias. Requires the ``Manage GCNs`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.post(f"/api/gcn_event/{dateobs}/gracedb")
    return GcnEventIdResponse.model_validate(unwrap(response))


def post_gcn_event_tach(client: httpx.Client, dateobs: str) -> GcnEventIdResponse:
    """Scrape TACH for a GCN event's aliases and circulars.

    The scrape runs in the background. Requires the ``Manage GCNs``
    permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.post(f"/api/gcn_event/{dateobs}/tach")
    return GcnEventIdResponse.model_validate(unwrap(response))


def fetch_gcn_event_tach(client: httpx.Client, dateobs: str) -> GcnEventTachInfo:
    """Retrieve the TACH ID, aliases and circulars of a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.get(f"/api/gcn_event/{dateobs}/tach")
    return GcnEventTachInfo.model_validate(unwrap(response))


def fetch_gcn_event_crossmatch(
    client: httpx.Client,
    dateobs: str,
) -> list[GcnEventCrossmatchState]:
    """Retrieve the per-filter alert crossmatch progress of a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.get(f"/api/gcn_event/{dateobs}/crossmatch")
    return [GcnEventCrossmatchState.model_validate(state) for state in unwrap(response)]


def post_gcn_event_crossmatch(
    client: httpx.Client,
    dateobs: str,
) -> GcnEventCrossmatchRequeue:
    """Requeue the alert crossmatch of a GCN event.

    Every filter is re-queried from the start of the window, including the
    one-shot archival pass. Existing sources and annotations are refreshed in
    place rather than duplicated. Requires the ``Manage GCNs`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.post(f"/api/gcn_event/{dateobs}/crossmatch")
    return GcnEventCrossmatchRequeue.model_validate(unwrap(response))


def fetch_gcn_event_instrument_fields(
    client: httpx.Client,
    dateobs: str,
    instrument_id: int,
    *,
    localization_name: str | None = None,
    integrated_probability: float = 0.95,
) -> GcnEventInstrumentFields:
    """Compute an instrument's field probabilities for an event localization.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    instrument_id : int
        ID of the instrument whose fields are tiled against the skymap.
    localization_name : str, optional
        Name of the localization to use. Defaults to one of the event's
        localizations chosen by the server.
    integrated_probability : float, optional
        Cumulative probability threshold, defaults to 0.95.
    """
    params: dict[str, str | float] = {"integrated_probability": integrated_probability}
    if localization_name is not None:
        params["localization_name"] = localization_name
    response = client.get(
        f"/api/gcn_event/{dateobs}/instrument/{instrument_id}",
        params=params,
    )
    return GcnEventInstrumentFields.model_validate(unwrap(response))


def fetch_gcn_event_triggers(
    client: httpx.Client,
    dateobs: str,
    *,
    allocation_id: int | None = None,
) -> list[GcnTrigger]:
    """Retrieve the triggered status of a GCN event, per allocation.

    Requires the ``Manage allocations`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    allocation_id : int, optional
        Restrict to a single allocation.
    """
    path = f"/api/gcn_event/{dateobs}/triggered"
    if allocation_id is not None:
        path = f"{path}/{allocation_id}"
    response = client.get(path)
    return [GcnTrigger.model_validate(trigger) for trigger in unwrap(response)]


def update_gcn_event_trigger(
    client: httpx.Client,
    dateobs: str,
    allocation_id: int,
    *,
    triggered: bool,
) -> GcnTrigger:
    """Set whether a GCN event triggered an allocation.

    The record is created if it does not exist. Requires the
    ``Manage allocations`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    allocation_id : int
        ID of the allocation.
    triggered : bool
        The new triggered status.
    """
    response = client.put(
        f"/api/gcn_event/{dateobs}/triggered/{allocation_id}",
        json={"triggered": triggered},
    )
    return GcnTrigger.model_validate(unwrap(response))


def delete_gcn_event_trigger(
    client: httpx.Client,
    dateobs: str,
    allocation_id: int,
) -> GcnTrigger:
    """Delete the triggered status of a GCN event for an allocation.

    Returns the deleted record. Requires the ``Manage allocations``
    permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    allocation_id : int
        ID of the allocation.
    """
    response = client.delete(f"/api/gcn_event/{dateobs}/triggered/{allocation_id}")
    return GcnTrigger.model_validate(unwrap(response))


def post_gcn_summary(
    client: httpx.Client,
    dateobs: str,
    payload: GcnSummaryPost,
) -> GcnEventIdResponse:
    """Generate a summary of a GCN event.

    The summary is written in the background: the record is created
    immediately with the text ``"pending"`` and filled in later. Unless
    ``no_text`` is set, ``subject`` is required. A user may not have two
    summaries with the same title for the same event and group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    payload : GcnSummaryPost
        What to include in the summary. ``localization_cumprob`` defaults to
        0.95, ``number_detections`` to 2, ``number_observations`` to 1 and
        ``stats_method`` to ``"python"`` (``"db"`` is the alternative).
    """
    response = client.post(
        f"/api/gcn_event/{dateobs}/summary",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return GcnEventIdResponse.model_validate(unwrap(response))


def fetch_gcn_summary(
    client: httpx.Client,
    dateobs: str,
    summary_id: int,
) -> GcnSummary:
    """Retrieve a GCN event summary, including its text.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the summarized event.
    summary_id : int
        ID of the summary.
    """
    response = client.get(f"/api/gcn_event/{dateobs}/summary/{summary_id}")
    return GcnSummary.model_validate(unwrap(response))


def update_gcn_summary(
    client: httpx.Client,
    dateobs: str,
    summary_id: int,
    body: str,
) -> GcnSummary:
    """Replace the text of a GCN event summary.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the summarized event.
    summary_id : int
        ID of the summary to update.
    body : str
        The new summary text.
    """
    response = client.patch(
        f"/api/gcn_event/{dateobs}/summary/{summary_id}",
        json={"body": body},
    )
    return GcnSummary.model_validate(unwrap(response))


def delete_gcn_summary(
    client: httpx.Client,
    dateobs: str,
    summary_id: int,
) -> None:
    """Delete a GCN event summary.

    A summary that is still pending cannot be deleted within an hour of
    being created.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the summarized event.
    summary_id : int
        ID of the summary to delete.
    """
    unwrap(client.delete(f"/api/gcn_event/{dateobs}/summary/{summary_id}"))


def post_gcn_report(
    client: httpx.Client,
    dateobs: str,
    payload: GcnReportPost,
) -> GcnEventIdResponse:
    """Generate a report on a GCN event.

    The report is assembled in the background: the record is created
    immediately with pending data and filled in later. A user may not have
    two reports with the same name for the same event and group.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    payload : GcnReportPost
        What to include in the report. ``localization_cumprob`` defaults to
        0.95, ``number_detections`` to 2 and ``stats_method`` to
        ``"python"`` (``"db"`` is the alternative).
    """
    response = client.post(
        f"/api/gcn_event/{dateobs}/report",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return GcnEventIdResponse.model_validate(unwrap(response))


def fetch_gcn_reports(client: httpx.Client, dateobs: str) -> list[GcnReport]:
    """Retrieve the reports of a GCN event, newest first.

    The report data itself is omitted; use :func:`fetch_gcn_report` for it.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    """
    response = client.get(f"/api/gcn_event/{dateobs}/report")
    return [GcnReport.model_validate(report) for report in unwrap(response)]


def fetch_gcn_report(
    client: httpx.Client,
    dateobs: str,
    report_id: int,
) -> GcnReport:
    """Retrieve a single GCN event report, including its data.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    report_id : int
        ID of the report.
    """
    response = client.get(f"/api/gcn_event/{dateobs}/report/{report_id}")
    return GcnReport.model_validate(unwrap(response))


def update_gcn_report(
    client: httpx.Client,
    dateobs: str,
    report_id: int,
    *,
    data: dict[str, Any] | None = None,
    published: bool | None = None,
) -> GcnReport:
    """Update a GCN event report, or publish and unpublish it.

    Sources added to ``data`` are re-fetched from the database with their
    photometry; duplicates are rejected. When ``published`` is omitted the
    server regenerates the rendered report instead.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    report_id : int
        ID of the report to update.
    data : dict, optional
        The new report data.
    published : bool, optional
        Publish (true) or unpublish (false) the report.
    """
    payload: dict[str, Any] = {}
    if data is not None:
        payload["data"] = data
    if published is not None:
        payload["published"] = published
    response = client.patch(
        f"/api/gcn_event/{dateobs}/report/{report_id}",
        json=payload,
    )
    return GcnReport.model_validate(unwrap(response))


def delete_gcn_report(
    client: httpx.Client,
    dateobs: str,
    report_id: int,
) -> None:
    """Delete a GCN event report, unpublishing it first.

    A report that is still pending cannot be deleted within an hour of being
    created.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    report_id : int
        ID of the report to delete.
    """
    unwrap(client.delete(f"/api/gcn_event/{dateobs}/report/{report_id}"))


def post_default_gcn_tag(
    client: httpx.Client,
    payload: DefaultGcnTagPost,
) -> GcnEventIdResponse:
    """Create a rule that automatically tags matching GCN events.

    Requires the ``Manage GCNs`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : DefaultGcnTagPost
        The rule to create. ``default_tag_name`` must be unique. ``filters``
        accepts the keys ``gcn_tags``, ``notice_types`` and
        ``localization_tags``, each a list of strings.
    """
    response = client.post(
        "/api/default_gcn_tag",
        json=payload.model_dump(exclude_none=True),
    )
    return GcnEventIdResponse.model_validate(unwrap(response))


def fetch_default_gcn_tag(
    client: httpx.Client,
    default_gcn_tag_id: int,
) -> DefaultGcnTag:
    """Retrieve a single default GCN tag.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_gcn_tag_id : int
        ID of the default GCN tag.
    """
    response = client.get(f"/api/default_gcn_tag/{default_gcn_tag_id}")
    return DefaultGcnTag.model_validate(unwrap(response))


def fetch_default_gcn_tags(client: httpx.Client) -> list[DefaultGcnTag]:
    """Retrieve all default GCN tags.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/default_gcn_tag")
    return [DefaultGcnTag.model_validate(tag) for tag in unwrap(response)]


def delete_default_gcn_tag(
    client: httpx.Client,
    default_gcn_tag_id: int,
) -> None:
    """Delete a default GCN tag.

    Requires the ``Manage GCNs`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_gcn_tag_id : int
        ID of the default GCN tag to delete.
    """
    unwrap(client.delete(f"/api/default_gcn_tag/{default_gcn_tag_id}"))


def fetch_gcn_event_sources(
    client: httpx.Client,
    dateobs: str,
    *,
    source_ids: list[str] | None = None,
) -> list[GcnEventObj]:
    """Retrieve the objects vetted against a GCN event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    source_ids : list of str, optional
        Restrict to these object IDs. Defaults to every vetted object.
    """
    params: dict[str, str] = {}
    if source_ids is not None:
        params["sourcesIDList"] = ",".join(source_ids)
    response = client.get(f"/api/sources_in_gcn/{dateobs}", params=params)
    return [GcnEventObj.model_validate(source) for source in unwrap(response)]


def fetch_gcn_event_source(
    client: httpx.Client,
    dateobs: str,
    obj_id: str,
) -> list[GcnEventObj]:
    """Retrieve one object's standing against a GCN event.

    The server returns a list, empty when the object has not been vetted
    against the event.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    obj_id : str
        Object ID, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/sources_in_gcn/{dateobs}/{obj_id}")
    return [GcnEventObj.model_validate(source) for source in unwrap(response)]


def post_gcn_event_source(
    client: httpx.Client,
    dateobs: str,
    payload: GcnEventObjPost,
) -> GcnEventObjIdResponse:
    """Record an object's standing against a GCN event.

    An existing record for the object is updated instead. The server rejects
    a repost that changes neither status, explanation nor notes. Requires
    the ``Upload data`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    payload : GcnEventObjPost
        The object and its standing. ``status`` is one of ``"pending"``,
        ``"confirmed"``, ``"ambiguous"`` or ``"rejected"``.
    """
    response = client.post(
        f"/api/sources_in_gcn/{dateobs}",
        json=payload.model_dump(exclude_none=True),
    )
    return GcnEventObjIdResponse.model_validate(unwrap(response))


def update_gcn_event_source(  # noqa: PLR0913 -- mirrors the endpoint's request body
    client: httpx.Client,
    dateobs: str,
    obj_id: str,
    status: str,
    *,
    explanation: str | None = None,
    notes: str | None = None,
) -> GcnEventObjIdResponse:
    """Update an object's standing against a GCN event.

    Requires the ``Upload data`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    obj_id : str
        Object ID of the vetted object.
    status : str
        One of ``"pending"``, ``"confirmed"``, ``"ambiguous"`` or
        ``"rejected"``.
    explanation : str, optional
        Why the object was confirmed or rejected.
    notes : str, optional
        Extra information about the object.
    """
    payload: dict[str, str] = {"status": status}
    if explanation is not None:
        payload["explanation"] = explanation
    if notes is not None:
        payload["notes"] = notes
    response = client.patch(
        f"/api/sources_in_gcn/{dateobs}/{obj_id}",
        json=payload,
    )
    return GcnEventObjIdResponse.model_validate(unwrap(response))


def delete_gcn_event_source(
    client: httpx.Client,
    dateobs: str,
    obj_id: str,
) -> GcnEventObjIdResponse:
    """Remove an object's standing against a GCN event.

    The object's relation to the event becomes undefined again. Returns the
    ID of the deleted record. Requires the ``Upload data`` permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    dateobs : str
        UTC event timestamp of the event.
    obj_id : str
        Object ID of the vetted object.
    """
    response = client.delete(f"/api/sources_in_gcn/{dateobs}/{obj_id}")
    return GcnEventObjIdResponse.model_validate(unwrap(response))


def fetch_gcn_events_associated_with_source(
    client: httpx.Client,
    obj_id: str,
) -> list[str]:
    """Retrieve the ``dateobs`` of the GCN events an object is confirmed in.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/associated_gcns/{obj_id}")
    return [str(dateobs) for dateobs in unwrap(response)["gcns"]]


def post_gcn_event_obj_crossmatch(
    client: httpx.Client,
    obj_id: str,
    payload: GcnEventObjCrossmatchPost,
) -> None:
    """Crossmatch an object against the GCN events of a time window.

    The crossmatch runs in the background and records each containment as a
    pending object-in-event association, leaving decisions already made
    alone. The window may span at most 31 days.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID to crossmatch, e.g. ``"ZTF20abcdef"``.
    payload : GcnEventObjCrossmatchPost
        The window and filters. ``probability`` is the integrated
        probability contour to search within, defaulting to 0.95.
    """
    unwrap(
        client.post(
            f"/api/sources/{obj_id}/gcn_event",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )
    )
