"""Tests for the SkyPortal client."""

from __future__ import annotations

import pytest
import responses

from skyportal_py import SkyPortal, SkyPortalError

BASE_URL = "https://skyportal.example.com"


@pytest.fixture
def client() -> SkyPortal:
    """Return a client pointed at a fake instance."""
    return SkyPortal(BASE_URL, token="abc123")


@responses.activate
def test_get_unwraps_data(client: SkyPortal) -> None:
    """A successful response returns only the data field."""
    responses.get(
        f"{BASE_URL}/api/sources",
        json={"status": "success", "data": {"sources": [], "totalMatches": 0}},
    )
    assert client.get("sources") == {"sources": [], "totalMatches": 0}


@responses.activate
def test_token_header_and_api_prefix(client: SkyPortal) -> None:
    """The token header is sent and the api/ prefix is optional."""
    route = responses.get(
        f"{BASE_URL}/api/internal/profile",
        json={"status": "success", "data": {"username": "leo"}},
    )
    assert client.whoami() == {"username": "leo"}
    assert route.calls[0].request.headers["Authorization"] == "token abc123"


@responses.activate
def test_error_raises(client: SkyPortal) -> None:
    """An error envelope raises SkyPortalError with the server message."""
    responses.get(
        f"{BASE_URL}/api/sources/ZTF20abcdef",
        json={"status": "error", "message": "Invalid source ID"},
        status=400,
    )
    with pytest.raises(SkyPortalError, match="Invalid source ID") as excinfo:
        client.get("/sources/ZTF20abcdef")
    assert excinfo.value.status_code == 400


@responses.activate
def test_non_json_response_raises(client: SkyPortal) -> None:
    """A non-JSON response raises SkyPortalError instead of ValueError."""
    responses.get(
        f"{BASE_URL}/api/sources", body="<html>proxy error</html>", status=502
    )
    with pytest.raises(SkyPortalError, match="non-JSON"):
        client.get("sources")


@responses.activate
def test_post_sends_json_body(client: SkyPortal) -> None:
    """POST forwards the JSON body."""
    route = responses.post(
        f"{BASE_URL}/api/comment",
        json={"status": "success", "data": {"comment_id": 1}},
    )
    assert client.post("comment", json={"text": "hi"}) == {"comment_id": 1}
    assert route.calls[0].request.body == b'{"text": "hi"}'
