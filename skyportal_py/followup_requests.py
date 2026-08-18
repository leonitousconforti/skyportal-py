"""Typed endpoint functions for ``/api/followup_request``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class FollowupRequest(BaseModel):
    """A follow-up observation request."""

    model_config = ConfigDict(extra="forbid")

    id: int
    obj_id: str
    allocation_id: int
    status: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    requester_id: int | None = None
    created_at: str | None = None


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
