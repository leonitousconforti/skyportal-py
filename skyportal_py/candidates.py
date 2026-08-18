"""Typed endpoint functions for ``/api/candidates``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class Candidate(BaseModel):
    """A SkyPortal candidate."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float | None = None
    dec: float | None = None
    redshift: float | None = None


class CandidatesPage(BaseModel):
    """One page of results from a candidates query."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    candidates: list[Candidate]
    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=25)


class CandidatePost(BaseModel):
    """Payload for posting a new candidate."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ra: float
    dec: float
    filter_ids: list[int]
    passed_at: str


class CandidatePostResponse(BaseModel):
    """Result of posting a new candidate."""

    model_config = ConfigDict(extra="forbid")

    ids: list[int] = Field(default_factory=list)


def fetch_candidate(client: httpx.Client, obj_id: str) -> Candidate:
    """Retrieve a single candidate by object ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the candidate, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/candidates/{obj_id}")
    return Candidate.model_validate(unwrap(response))


def fetch_candidates(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 25,
    group_ids: list[int] | None = None,
    saved_status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> CandidatesPage:
    """Query candidates, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    group_ids : list of int, optional
        Restrict to candidates passing filters belonging to these groups.
    saved_status : str, optional
        Filter on whether candidates are saved as sources, e.g. ``"all"``
        or ``"savedToAllSelected"``.
    start_date, end_date : str, optional
        Restrict to candidates that passed a filter in this ISO-format
        (UTC) time range.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if group_ids is not None:
        params["groupIDs"] = ",".join(str(gid) for gid in group_ids)
    if saved_status is not None:
        params["savedStatus"] = saved_status
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    response = client.get("/api/candidates", params=params)
    return CandidatesPage.model_validate(unwrap(response))


def post_candidate(
    client: httpx.Client,
    payload: CandidatePost,
) -> CandidatePostResponse:
    """Post a new candidate.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : CandidatePost
        The candidate to post, including the filters it passed
        (``filter_ids``) and when it passed them (``passed_at``).
    """
    response = client.post(
        "/api/candidates", json=payload.model_dump(exclude_none=True)
    )
    return CandidatePostResponse.model_validate(unwrap(response))


class CandidateRecord(BaseModel):
    """One row of the ``candidates`` table: an Obj that passed a Filter."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    obj_id: str | None = None
    filter_id: int | None = None
    passed_at: str | None = None
    passing_alert_id: int | None = None
    uploader_id: int | None = None


class CandidateFilterPage(BaseModel):
    """One page of raw candidate rows from ``/api/candidates_filter``."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    candidates: list[CandidateRecord] = Field(default_factory=list)
    total_matches: int | None = Field(alias="totalMatches", default=None)


class BulkCandidateDeleteResponse(BaseModel):
    """Result of a bulk deletion of old, unsaved candidate objects."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    deleted: int
    remaining: int
    dry_run: bool = Field(alias="dryRun")


class ScanReportPassedFiltersRange(BaseModel):
    """Time range over which candidates must have passed a filter."""

    model_config = ConfigDict(extra="forbid")

    start_date: str
    end_date: str


class ScanReportSavedCandidatesRange(BaseModel):
    """Time range over which candidates must have been saved as sources."""

    model_config = ConfigDict(extra="forbid")

    start_saved_date: str
    end_saved_date: str


class ScanReportPost(BaseModel):
    """Payload for generating a candidate scanning report."""

    model_config = ConfigDict(extra="forbid")

    group_ids: list[int]
    passed_filters_range: ScanReportPassedFiltersRange | None = None
    saved_candidates_range: ScanReportSavedCandidatesRange | None = None
    passed_filters_window_hours: float | None = None
    saved_candidates_window_hours: float | None = None
    gcn_event_dateobs: str | None = None


class ScanReport(BaseModel):
    """A candidate scanning report."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    author_id: int | None = None
    author: str | None = None
    options: dict[str, Any] | None = None
    groups: list[dict[str, Any]] | None = None


class ScanReportsPage(BaseModel):
    """One page of candidate scanning reports."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    reports: list[ScanReport] = Field(default_factory=list)
    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=10)


class ScanReportItem(BaseModel):
    """One saved candidate listed in a scanning report."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    obj_id: str | None = None
    scan_report_id: int | None = None
    data: dict[str, Any] | None = None


def delete_candidate(client: httpx.Client, obj_id: str, filter_id: int) -> None:
    """Delete the candidate entries for an object on a given filter.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the candidate, e.g. ``"ZTF20abcdef"``.
    filter_id : int
        ID of the filter the candidate passed. The server errors if no
        candidate matches this ``(obj_id, filter_id)`` pairing.
    """
    unwrap(client.delete(f"/api/candidates/{obj_id}/{filter_id}"))


def bulk_delete_candidates(
    client: httpx.Client,
    *,
    max_age_months: int | None = None,
    batch_size: int | None = None,
    dry_run: bool | None = None,
) -> BulkCandidateDeleteResponse:
    """Bulk-delete old, unsaved candidate objects.

    Deletes objects that appear as candidates, are not saved as an active
    source in any group, and whose most recent ``passed_at`` is older than
    ``max_age_months``. Deleting an object cascades to its candidates,
    photometry, annotations and thumbnails. Requires the ``System admin``
    permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    max_age_months : int, optional
        Age threshold in months. Server default is 6.
    batch_size : int, optional
        Maximum number of objects deleted in this call, oldest first.
        Server default is 1000; must be between 1 and 10000.
    dry_run : bool, optional
        If true, only report how many objects would be deleted. Server
        default is false.
    """
    payload: dict[str, int | bool] = {}
    if max_age_months is not None:
        payload["maxAgeMonths"] = max_age_months
    if batch_size is not None:
        payload["batchSize"] = batch_size
    if dry_run is not None:
        payload["dryRun"] = dry_run
    response = client.post("/api/candidates/bulk_delete", json=payload)
    return BulkCandidateDeleteResponse.model_validate(unwrap(response))


def fetch_candidates_filter(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 25,
    group_ids: list[int] | None = None,
    filter_ids: list[int] | None = None,
    saved_status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> CandidateFilterPage:
    """Query the raw candidate rows, rather than the objects behind them.

    This is the lighter counterpart of :func:`fetch_candidates`: it returns
    ``candidates`` table rows, including ``passing_alert_id`` (the alert
    candid), which is what maps a candidate back to the upstream alert.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls. Rows are ordered by ``passed_at`` ascending.
        ``total_matches`` is only computed for page 1; keep it client-side
        while paginating.
    group_ids, filter_ids : list of int, optional
        Restrict to these groups and filters. Both default to everything
        accessible to the token.
    saved_status : str, optional
        Filter on whether candidates are saved as sources, e.g. ``"all"``
        (the server default) or ``"savedToAllSelected"``.
    start_date, end_date : str, optional
        Restrict to candidates that passed a filter in this ISO-format
        (UTC) time range.
    """
    params: dict[str, str | int] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if group_ids is not None:
        params["groupIDs"] = ",".join(str(gid) for gid in group_ids)
    if filter_ids is not None:
        params["filterIDs"] = ",".join(str(fid) for fid in filter_ids)
    if saved_status is not None:
        params["savedStatus"] = saved_status
    if start_date is not None:
        params["startDate"] = start_date
    if end_date is not None:
        params["endDate"] = end_date
    response = client.get("/api/candidates_filter", params=params)
    return CandidateFilterPage.model_validate(unwrap(response))


def post_scan_report(client: httpx.Client, payload: ScanReportPost) -> None:
    """Generate a candidate scanning report.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : ScanReportPost
        Groups owning the report plus the two time ranges it covers. Each
        range may instead be given as a rolling window in hours ending
        now (``passed_filters_window_hours``,
        ``saved_candidates_window_hours``); the explicit ranges win when
        both are supplied. The server errors if a report already exists
        for the same groups and options, or if no saved sources match.
    """
    unwrap(
        client.post(
            "/api/candidates/scan_reports",
            json=payload.model_dump(exclude_none=True),
        )
    )


def fetch_scan_reports(
    client: httpx.Client,
    *,
    page: int = 1,
    num_per_page: int = 10,
) -> ScanReportsPage:
    """Retrieve candidate scanning reports, newest first.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page, num_per_page : int, optional
        Pagination controls.
    """
    params = {"page": page, "numPerPage": num_per_page}
    response = client.get("/api/candidates/scan_reports", params=params)
    return ScanReportsPage.model_validate(unwrap(response))


def fetch_scan_report_items(
    client: httpx.Client,
    report_id: int,
) -> list[ScanReportItem]:
    """Retrieve every item of a candidate scanning report.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    report_id : int
        ID of the scanning report.
    """
    response = client.get(f"/api/candidates/scan_reports/{report_id}/items")
    return [ScanReportItem.model_validate(item) for item in unwrap(response)]


def update_scan_report_item(
    client: httpx.Client,
    report_id: int,
    item_id: int,
    *,
    comment: str | None = None,
) -> None:
    """Set the comment on one item of a candidate scanning report.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    report_id : int
        ID of the scanning report holding the item.
    item_id : int
        ID of the report item to update.
    comment : str, optional
        The comment to store. Passing ``None`` clears it, since the server
        overwrites the item's ``comment`` key with whatever is sent.
    """
    unwrap(
        client.patch(
            f"/api/candidates/scan_reports/{report_id}/items/{item_id}",
            json={"comment": comment},
        )
    )
