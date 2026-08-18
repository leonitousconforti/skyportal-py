"""Tests for the typed candidates endpoint functions."""

from __future__ import annotations

import json

import httpx
import respx

from skyportal_py import candidates

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_candidate(client: httpx.Client) -> None:
    """A candidate response validates into a Candidate model."""
    respx.get(f"{BASE_URL}/api/candidates/ZTF20abcdef").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {"id": "ZTF20abcdef", "ra": 10.5, "dec": -20.25},
            },
        )
    )
    candidate = candidates.fetch_candidate(client, "ZTF20abcdef")
    assert candidate.id == "ZTF20abcdef"
    assert candidate.ra == 10.5


@respx.mock
def test_fetch_candidates_pagination_and_filters(client: httpx.Client) -> None:
    """Query kwargs map to the endpoint's camelCase query parameters."""
    route = respx.get(f"{BASE_URL}/api/candidates").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": {
                    "candidates": [{"id": "ZTF20abcdef"}],
                    "totalMatches": 7,
                    "pageNumber": 2,
                    "numPerPage": 1,
                },
            },
        )
    )
    page = candidates.fetch_candidates(
        client,
        page_number=2,
        num_per_page=1,
        group_ids=[1, 2],
        saved_status="all",
    )
    assert page.total_matches == 7
    assert page.candidates[0].id == "ZTF20abcdef"
    params = route.calls[0].request.url.params
    assert params["pageNumber"] == "2"
    assert params["groupIDs"] == "1,2"
    assert params["savedStatus"] == "all"
    assert "startDate" not in params


@respx.mock
def test_post_candidate(client: httpx.Client) -> None:
    """The payload model is sent as-is and the created IDs come back."""
    route = respx.post(f"{BASE_URL}/api/candidates").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"ids": [12]}},
        )
    )
    result = candidates.post_candidate(
        client,
        candidates.CandidatePost(
            id="ZTF20abcdef",
            ra=10.5,
            dec=-20.25,
            filter_ids=[3],
            passed_at="2026-08-18T00:00:00",
        ),
    )
    assert result.ids == [12]
    body = json.loads(route.calls[0].request.content)
    assert body["filter_ids"] == [3]
    assert body["passed_at"] == "2026-08-18T00:00:00"
