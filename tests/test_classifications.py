"""Tests for the typed classifications endpoint functions."""

from __future__ import annotations

import json

import httpx
import respx

from skyportal_py import classifications

BASE_URL = "https://skyportal.example.com"


@respx.mock
def test_fetch_classifications(client: httpx.Client) -> None:
    """A classifications response validates into a list of Classification."""
    respx.get(f"{BASE_URL}/api/sources/ZTF20abcdef/classifications").mock(
        return_value=httpx.Response(
            200,
            json={
                "status": "success",
                "data": [
                    {
                        "id": 9,
                        "obj_id": "ZTF20abcdef",
                        "classification": "Ia",
                        "taxonomy_id": 1,
                        "probability": 0.9,
                    }
                ],
            },
        )
    )
    result = classifications.fetch_classifications(client, "ZTF20abcdef")
    assert len(result) == 1
    assert result[0].classification == "Ia"
    assert result[0].probability == 0.9


@respx.mock
def test_post_classification(client: httpx.Client) -> None:
    """The payload model is sent with unset fields omitted."""
    route = respx.post(f"{BASE_URL}/api/classification").mock(
        return_value=httpx.Response(
            200,
            json={"status": "success", "data": {"classification_id": 9}},
        )
    )
    result = classifications.post_classification(
        client,
        classifications.ClassificationPost(
            obj_id="ZTF20abcdef",
            classification="Ia",
            taxonomy_id=1,
            probability=0.9,
        ),
    )
    assert result.classification_id == 9
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "obj_id": "ZTF20abcdef",
        "classification": "Ia",
        "taxonomy_id": 1,
        "probability": 0.9,
    }
