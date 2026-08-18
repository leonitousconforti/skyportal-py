"""Tests for the typed annotations endpoint functions."""

# No `from __future__ import annotations` here: it would shadow the
# `skyportal_py.annotations` module imported below.

import json

import httpx
import respx

from skyportal_py import annotations

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_annotations(client: httpx.Client) -> None:
    """An annotations response validates into a list of Annotation models."""
    respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/annotations").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 9,
                        "obj_id": "ZTF20abcdef",
                        "origin": "cross-match",
                        "data": {"gaia_parallax": 0.5},
                        "author_id": 7,
                    }
                ],
            },
        )
    )
    result = annotations.fetch_annotations(client, "ZTF20abcdef")
    assert len(result) == 1
    assert result[0].origin == "cross-match"
    assert result[0].data == {"gaia_parallax": 0.5}


@respx.mock
def test_post_annotation(client: httpx.Client) -> None:
    """The origin, data, and optional group IDs are sent as the payload."""
    route = respx.post(f"{BASE_URL}/api/sources/ZTF20abcdef/annotations").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"annotation_id": 9}},
        )
    )
    result = annotations.post_annotation(
        client,
        "ZTF20abcdef",
        "cross-match",
        {"gaia_parallax": 0.5},
        group_ids=[1],
    )
    assert result.annotation_id == 9
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "origin": "cross-match",
        "data": {"gaia_parallax": 0.5},
        "group_ids": [1],
    }


@respx.mock
def test_post_annotation_without_groups(client: httpx.Client) -> None:
    """Omitting group_ids leaves the key out of the payload."""
    route = respx.post(f"{BASE_URL}/api/sources/ZTF20abcdef/annotations").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"annotation_id": 10}},
        )
    )
    annotations.post_annotation(client, "ZTF20abcdef", "cross-match", {"a": 1})
    body = json.loads(route.calls[0].request.content)
    assert body == {"origin": "cross-match", "data": {"a": 1}}
