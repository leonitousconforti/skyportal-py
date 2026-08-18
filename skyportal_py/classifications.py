"""Typed endpoint functions for classifications."""

from __future__ import annotations

import httpx

from skyportal_py._http import unwrap
from skyportal_py._models import Model


class Classification(Model):
    """A classification of a source."""

    id: int
    obj_id: str
    classification: str
    taxonomy_id: int
    probability: float | None = None
    author_name: str | None = None


class ClassificationPost(Model):
    """Payload for posting a classification."""

    obj_id: str
    classification: str
    taxonomy_id: int
    probability: float | None = None
    group_ids: list[int] | None = None


class ClassificationPostResponse(Model):
    """Result of posting a classification."""

    classification_id: int


def fetch_classifications(client: httpx.Client, obj_id: str) -> list[Classification]:
    """Retrieve the classifications of a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/sources/{obj_id}/classifications")
    return [Classification.model_validate(item) for item in unwrap(response)]


def post_classification(
    client: httpx.Client,
    payload: ClassificationPost,
) -> ClassificationPostResponse:
    """Post a classification of a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : ClassificationPost
        The classification to post. ``classification`` must be a class in
        the taxonomy identified by ``taxonomy_id``. If ``group_ids`` is
        omitted, the server applies its default visibility.
    """
    response = client.post(
        "/api/classification", json=payload.model_dump(exclude_none=True)
    )
    return ClassificationPostResponse.model_validate(unwrap(response))
