"""Tests for the typed comments endpoint functions."""

from __future__ import annotations

import json

import httpx
import respx

from skyportal_py import comments

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_comments(client: httpx.Client) -> None:
    """A comments response validates into a list of Comment models."""
    respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/comments").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 5,
                        "text": "spectrum looks like a SN Ia",
                        "obj_id": "ZTF20abcdef",
                        "author_id": 7,
                        "created_at": "2026-08-18T00:00:00",
                    }
                ],
            },
        )
    )
    result = comments.fetch_comments(client, "ZTF20abcdef")
    assert len(result) == 1
    assert result[0].id == 5
    assert result[0].text == "spectrum looks like a SN Ia"


@respx.mock
def test_post_comment(client: httpx.Client) -> None:
    """The comment text and optional group IDs are sent as the payload."""
    route = respx.post(f"{BASE_URL}/api/sources/ZTF20abcdef/comments").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"comment_id": 5}},
        )
    )
    result = comments.post_comment(client, "ZTF20abcdef", "hi", group_ids=[1])
    assert result.comment_id == 5
    body = json.loads(route.calls[0].request.content)
    assert body == {"text": "hi", "group_ids": [1]}


@respx.mock
def test_post_comment_without_groups(client: httpx.Client) -> None:
    """Omitting group_ids leaves the key out of the payload."""
    route = respx.post(f"{BASE_URL}/api/sources/ZTF20abcdef/comments").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"comment_id": 6}},
        )
    )
    comments.post_comment(client, "ZTF20abcdef", "hi")
    body = json.loads(route.calls[0].request.content)
    assert body == {"text": "hi"}
