"""Typed endpoint functions for ``/api/followup_request``."""

from __future__ import annotations

import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.allocations import Allocation
from skyportal_py.groups import Group
from skyportal_py.users import User


class FacilityTransaction(BaseModel):
    """A serialized exchange with a facility (upstream ``FacilityTransaction``).

    ``followup_request`` and ``observation_plan_request`` are the parent
    rows; they stay ``dict`` to avoid a circular import back into this
    module and into :mod:`skyportal_py.observation_plans`.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    request: dict[str, Any] | None = None
    response: dict[str, Any] | None = None
    followup_request_id: int | None = None
    observation_plan_request_id: int | None = None
    initiator_id: int | None = None
    initiator: User | None = None
    followup_request: dict[str, Any] | None = None
    observation_plan_request: dict[str, Any] | None = None


class FacilityTransactionRequest(BaseModel):
    """A queued facility call (upstream ``FacilityTransactionRequest``).

    ``followup_request`` and ``observation_plan_request`` are the parent
    rows; they stay ``dict`` to avoid a circular import back into this
    module and into :mod:`skyportal_py.observation_plans`.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    last_query: datetime.datetime | None = None
    method: str | None = None
    endpoint: str | None = None
    data: dict[str, Any] | None = None
    params: dict[str, Any] | None = None
    headers: dict[str, Any] | None = None
    status: str | None = None
    followup_request_id: int | None = None
    observation_plan_request_id: int | None = None
    initiator_id: int | None = None
    initiator: User | None = None
    followup_request: dict[str, Any] | None = None
    observation_plan_request: dict[str, Any] | None = None


class FollowupRequestWatcher(BaseModel):
    """A user watching a follow-up request (upstream ``FollowupRequestUser``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    followuprequest_id: int | None = None
    user_id: int | None = None


class FollowupRequest(BaseModel):
    """A follow-up observation request (upstream ``FollowupRequest``).

    ``obj`` stays ``dict`` because typing it as
    :class:`skyportal_py.sources.Source` would create an import cycle;
    the same applies to ``photometry``, ``photometric_series`` and
    ``spectra``, which all point back at the requesting object.
    """

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    obj_id: str | None = None
    allocation_id: int | None = None
    requester_id: int | None = None
    last_modified_by_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str | None = None
    comment: str | None = None
    obj: dict[str, Any] | None = None
    allocation: Allocation | None = None
    requester: User | None = None
    last_modified_by: User | None = None
    target_groups: list[Group] = Field(default_factory=list)
    watchers: list[FollowupRequestWatcher] = Field(default_factory=list)
    transactions: list[FacilityTransaction] = Field(default_factory=list)
    transaction_requests: list[FacilityTransactionRequest] = Field(default_factory=list)
    photometry: list[dict[str, Any]] = Field(default_factory=list)
    photometric_series: list[dict[str, Any]] = Field(default_factory=list)
    spectra: list[dict[str, Any]] = Field(default_factory=list)
    rise_time_utc: str | list[str] | None = None
    set_time_utc: str | list[str] | None = None


class FollowupRequestsPage(BaseModel):
    """One page of results from a follow-up requests query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    followup_requests: list[FollowupRequest] = Field(default_factory=list)
    total_matches: int = Field(alias="totalMatches", default=0)
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


class FollowupRequestPost(BaseModel):
    """Payload for submitting a follow-up request."""

    model_config = ConfigDict(extra="forbid")

    obj_id: str
    allocation_id: int
    payload: dict[str, Any]
    target_group_ids: list[int] | None = None


class FollowupRequestPostResponse(BaseModel):
    """Result of submitting a follow-up request."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_followup_request(
    client: httpx.Client,
    followup_request_id: int,
) -> FollowupRequest:
    """Retrieve a single follow-up request by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request.
    """
    response = client.get(f"/api/followup_request/{followup_request_id}")
    return FollowupRequest.model_validate(unwrap(response))


def fetch_followup_requests(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    source_id: str | None = None,
    instrument_id: int | None = None,
    allocation_id: int | None = None,
    status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> FollowupRequestsPage:
    """Query follow-up requests, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    source_id : str, optional
        Restrict to requests whose object ID contains this string.
    instrument_id : int, optional
        Restrict to requests on this instrument. Ignored if
        ``allocation_id`` is provided.
    allocation_id : int, optional
        Restrict to requests under this allocation.
    status : str, optional
        Restrict to requests whose status matches this string.
    start_date, end_date : str, optional
        Restrict to requests created in this date range, as ISO-format
        date strings, e.g. ``"2020-01-01"``.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if source_id is not None:
        params["sourceID"] = source_id
    if instrument_id is not None:
        params["instrumentID"] = instrument_id
    if allocation_id is not None:
        params["allocationID"] = allocation_id
    if status is not None:
        params["status"] = status
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    response = client.get("/api/followup_request", params=params)
    return FollowupRequestsPage.model_validate(unwrap(response))


def post_followup_request(
    client: httpx.Client,
    payload: FollowupRequestPost,
) -> FollowupRequestPostResponse:
    """Submit a follow-up request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : FollowupRequestPost
        The request to submit. ``payload`` holds the instrument-specific
        request parameters; the allocation's instrument API defines its
        schema. If ``target_group_ids`` is omitted, the server applies its
        default visibility to the results.
    """
    response = client.post(
        "/api/followup_request", json=payload.model_dump(exclude_none=True)
    )
    return FollowupRequestPostResponse.model_validate(unwrap(response))


def delete_followup_request(
    client: httpx.Client,
    followup_request_id: int,
) -> None:
    """Delete a follow-up request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request to delete.
    """
    unwrap(client.delete(f"/api/followup_request/{followup_request_id}"))


class DefaultFollowupRequest(BaseModel):
    """A default follow-up request (upstream ``DefaultFollowupRequest``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    requester_id: int | None = None
    allocation_id: int | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    default_followup_name: str | None = None
    source_filter: dict[str, Any] | str | None = None
    constraints: dict[str, Any] | None = None
    priority_order: str | None = None
    validity_days: int | None = None
    comment: str | None = None
    implements_update: bool | None = None
    allocation: Allocation | None = None
    requester: User | None = None
    target_groups: list[Group] = Field(default_factory=list)


class DefaultFollowupRequestPost(BaseModel):
    """Payload for creating a default follow-up request."""

    model_config = ConfigDict(extra="forbid")

    allocation_id: int
    payload: dict[str, Any]
    default_followup_name: str
    source_filter: dict[str, Any]
    target_group_ids: list[int] | None = None
    comment: str | None = None
    implements_update: bool | None = None
    priority_order: str | None = None
    validity_days: int | None = None
    radius: float | None = None
    not_if_duplicates: bool | None = None
    source_group_ids: list[int] | None = None
    ignore_source_group_ids: list[int] | None = None
    not_if_classified: bool | None = None
    not_if_spectra_exist: bool | None = None
    not_if_tns_classified: bool | None = None
    not_if_tns_reported: float | None = None
    not_if_assignment_exists: bool | None = None
    ignore_allocation_ids: list[int] | None = None


class DefaultFollowupRequestPostResponse(BaseModel):
    """Result of creating a default follow-up request."""

    model_config = ConfigDict(extra="forbid")

    id: int


class PhotometryRequestStatus(BaseModel):
    """Status of a follow-up request after a photometry retrieval."""

    model_config = ConfigDict(extra="forbid")

    id: int
    request_status: str | None = None


def update_followup_request(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    followup_request_id: int,
    *,
    status: str | None = None,
    obj_id: str | None = None,
    allocation_id: int | None = None,
    payload: dict[str, Any] | None = None,
    target_group_ids: list[int] | None = None,
) -> None:
    """Update a follow-up request.

    If ``status`` is given, the server updates the stored fields directly
    without contacting the instrument. Otherwise ``obj_id`` and
    ``allocation_id`` are required and the request is updated (or
    re-submitted, if it previously failed or was rejected) through the
    instrument's facility API.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request to update.
    status : str, optional
        New status for the request.
    obj_id : str, optional
        Object ID of the target. Required when ``status`` is omitted.
    allocation_id : int, optional
        Allocation for the request. Required when ``status`` is omitted.
    payload : dict, optional
        Instrument-specific request parameters; the allocation's
        instrument API defines its schema.
    target_group_ids : list of int, optional
        Restrict the results' visibility to these groups. If omitted, the
        visibility is left unchanged.
    """
    fields: dict[str, Any] = {
        "status": status,
        "obj_id": obj_id,
        "allocation_id": allocation_id,
        "payload": payload,
        "target_group_ids": target_group_ids,
    }
    body = {name: value for name, value in fields.items() if value is not None}
    unwrap(client.put(f"/api/followup_request/{followup_request_id}", json=body))


def post_followup_request_comment(
    client: httpx.Client,
    followup_request_id: int,
    comment: str | None,
) -> None:
    """Set the comment on a follow-up request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request.
    comment : str or None
        The comment text. Pass ``None`` (or an empty string) to clear the
        request's comment.
    """
    unwrap(
        client.put(
            f"/api/followup_request/{followup_request_id}/comment",
            json={"comment": comment},
        )
    )


def post_followup_request_watcher(
    client: httpx.Client,
    followup_request_id: int,
) -> None:
    """Add a follow-up request to the token user's watch list.

    The server rejects the call if the user is already watching the
    request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request to watch.
    """
    unwrap(client.post(f"/api/followup_request/watch/{followup_request_id}", json={}))


def delete_followup_request_watcher(
    client: httpx.Client,
    followup_request_id: int,
) -> None:
    """Remove a follow-up request from the token user's watch list.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request to stop watching.
    """
    unwrap(client.delete(f"/api/followup_request/watch/{followup_request_id}"))


def fetch_followup_request_schedule(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    instrument_id: int,
    *,
    output_format: str = "csv",
    source_id: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    status: str | None = None,
    priority_threshold: float | None = None,
    time_resolution: float | None = None,
    observation_start_date: str | None = None,
    observation_end_date: str | None = None,
    include_standards: bool = False,
    standards_only: bool = False,
    standard_type: str | None = None,
    magnitude_range: str | None = None,
) -> bytes:
    """Build an observation schedule for an instrument's follow-up requests.

    Returns the schedule file contents as bytes; the server needs at
    least one request (or standard) to schedule.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    instrument_id : int
        ID of the instrument to schedule.
    output_format : str, optional
        File format of the schedule: ``"csv"`` (default), ``"png"``, or
        ``"pdf"``.
    source_id : str, optional
        Restrict to requests whose object ID contains this string.
    start_date, end_date : str, optional
        Restrict to requests created in this date range, as ISO-format
        date strings, e.g. ``"2020-01-01"``.
    status : str, optional
        Restrict to requests whose status matches this string.
    priority_threshold : float, optional
        Restrict to requests with payload priority at or above this value.
    time_resolution : float, optional
        Scheduler time resolution in seconds. Server default is 20.
    observation_start_date, observation_end_date : str, optional
        Observation window, as ISO-format date strings. Server defaults
        are now and 12 hours from now.
    include_standards : bool, optional
        Include standard stars in the schedule.
    standards_only : bool, optional
        Schedule only standard stars, no follow-up requests.
    standard_type : str, optional
        Origin of the standard stars, as defined in the server config.
        Server default is ``"ESO"``.
    magnitude_range : str, optional
        Highest and lowest standard-star magnitude to include, e.g.
        ``"(12,9)"``.
    """
    params: dict[str, str | float] = {"output_format": output_format}
    if source_id is not None:
        params["sourceID"] = source_id
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    if status is not None:
        params["status"] = status
    if priority_threshold is not None:
        params["priorityThreshold"] = priority_threshold
    if time_resolution is not None:
        params["timeResolution"] = time_resolution
    if observation_start_date is not None:
        params["observationStartDate"] = observation_start_date
    if observation_end_date is not None:
        params["observationEndDate"] = observation_end_date
    if include_standards:
        params["includeStandards"] = "true"
    if standards_only:
        params["standardsOnly"] = "true"
    if standard_type is not None:
        params["standardType"] = standard_type
    if magnitude_range is not None:
        params["magnitudeRange"] = magnitude_range
    response = client.get(
        f"/api/followup_request/schedule/{instrument_id}", params=params
    )
    return unwrap_content(response)


def update_followup_request_prioritization(  # noqa: PLR0913 -- mirrors the endpoint's body parameters
    client: httpx.Client,
    *,
    request_ids: list[int],
    priority_type: str | None = None,
    magnitude_ordering: str | None = None,
    localization_id: int | None = None,
    minimum_priority: int | None = None,
    maximum_priority: int | None = None,
) -> None:
    """Automatically reprioritize a set of follow-up requests.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    request_ids : list of int
        IDs of the follow-up requests to reprioritize.
    priority_type : str, optional
        Priority source: ``"magnitude"`` (server default) or
        ``"localization"``.
    magnitude_ordering : str, optional
        Ordering for brightness-based prioritization: ``"ascending"``
        (brightest first, server default) or ``"descending"``.
    localization_id : int, optional
        Localization to weight by. Required when ``priority_type`` is
        ``"localization"``.
    minimum_priority, maximum_priority : int, optional
        Priority bounds for the instrument. Server defaults are 1 and 5.
    """
    body: dict[str, Any] = {"requestIds": request_ids}
    if priority_type is not None:
        body["priorityType"] = priority_type
    if magnitude_ordering is not None:
        body["magnitudeOrdering"] = magnitude_ordering
    if localization_id is not None:
        body["localizationId"] = localization_id
    if minimum_priority is not None:
        body["minimumPriority"] = minimum_priority
    if maximum_priority is not None:
        body["maximumPriority"] = maximum_priority
    unwrap(client.put("/api/followup_request/prioritization", json=body))


def fetch_default_followup_request(
    client: httpx.Client,
    default_followup_request_id: int,
) -> DefaultFollowupRequest:
    """Retrieve a single default follow-up request by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_followup_request_id : int
        ID of the default follow-up request.
    """
    response = client.get(
        f"/api/default_followup_request/{default_followup_request_id}"
    )
    return DefaultFollowupRequest.model_validate(unwrap(response))


def fetch_default_followup_requests(
    client: httpx.Client,
) -> list[DefaultFollowupRequest]:
    """Retrieve all default follow-up requests visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/default_followup_request")
    return [DefaultFollowupRequest.model_validate(item) for item in unwrap(response)]


def post_default_followup_request(
    client: httpx.Client,
    payload: DefaultFollowupRequestPost,
) -> DefaultFollowupRequestPostResponse:
    """Create a default follow-up request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : DefaultFollowupRequestPost
        The default request to create. ``payload`` holds the
        instrument-specific request parameters and must not contain
        ``start_date`` or ``end_date`` (the server fills the real window
        when the request fires on source save). ``source_filter`` decides
        which saved sources trigger the request and is required.
    """
    response = client.post(
        "/api/default_followup_request",
        json=payload.model_dump(exclude_none=True),
    )
    return DefaultFollowupRequestPostResponse.model_validate(unwrap(response))


def delete_default_followup_request(
    client: httpx.Client,
    default_followup_request_id: int,
) -> None:
    """Delete a default follow-up request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_followup_request_id : int
        ID of the default follow-up request to delete.
    """
    unwrap(
        client.delete(f"/api/default_followup_request/{default_followup_request_id}")
    )


def request_followup_photometry(
    client: httpx.Client,
    followup_request_id: int,
) -> PhotometryRequestStatus:
    """Retrieve photometry for a follow-up request from its facility.

    Asks the instrument's facility API to fetch the photometry produced
    by the request; the instrument must implement retrieval.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request.
    """
    response = client.get(f"/api/photometry_request/{followup_request_id}")
    return PhotometryRequestStatus.model_validate(unwrap(response))


def post_facility_message(
    client: httpx.Client,
    followup_request_id: int,
    message: dict[str, Any],
) -> None:
    """Post a message from a remote facility about a follow-up request.

    The request's instrument must have a Listener API; ``message`` must
    match that listener's schema, and the token needs the listener's ACL.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    followup_request_id : int
        ID of the follow-up request the message refers to.
    message : dict
        Listener-specific message content, merged into the request body
        alongside ``followup_request_id``.
    """
    body = {"followup_request_id": followup_request_id, **message}
    unwrap(client.post("/api/facility", json=body))
