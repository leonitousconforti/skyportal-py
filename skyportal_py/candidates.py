"""Typed endpoint functions for ``/api/candidates``."""

from __future__ import annotations

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
