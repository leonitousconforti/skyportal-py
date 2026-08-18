"""Typed endpoint functions for source annotations."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class Annotation(BaseModel):
    """A machine-generated annotation on a source."""

    model_config = ConfigDict(extra="forbid")

    id: int
    obj_id: str | None = None
    origin: str
    data: dict[str, Any] = Field(default_factory=dict)
    author_id: int | None = None
    created_at: str | None = None


class AnnotationPostResponse(BaseModel):
    """Result of posting an annotation."""

    model_config = ConfigDict(extra="forbid")

    annotation_id: int


def fetch_annotations(client: httpx.Client, obj_id: str) -> list[Annotation]:
    """Retrieve the annotations on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/sources/{obj_id}/annotations")
    return [Annotation.model_validate(item) for item in unwrap(response)]


def post_annotation(
    client: httpx.Client,
    obj_id: str,
    origin: str,
    data: dict[str, Any],
    *,
    group_ids: list[int] | None = None,
) -> AnnotationPostResponse:
    """Post an annotation on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to annotate.
    origin : str
        Name of the process that produced the annotation, e.g. a pipeline
        or cross-match service. A source can hold one annotation per
        origin.
    data : dict
        The annotation payload, a JSON-serializable mapping.
    group_ids : list of int, optional
        Restrict the annotation's visibility to these groups. If omitted,
        the server applies its default visibility.
    """
    payload: dict[str, Any] = {"origin": origin, "data": data}
    if group_ids is not None:
        payload["group_ids"] = group_ids
    response = client.post(f"/api/sources/{obj_id}/annotations", json=payload)
    return AnnotationPostResponse.model_validate(unwrap(response))


def update_annotation(
    client: httpx.Client,
    obj_id: str,
    annotation_id: int,
    data: dict[str, Any],
    *,
    group_ids: list[int] | None = None,
) -> None:
    """Update an annotation on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the annotated source.
    annotation_id : int
        ID of the annotation to update.
    data : dict
        The new annotation payload, a JSON-serializable mapping.
    group_ids : list of int, optional
        Restrict the annotation's visibility to these groups. If omitted,
        the visibility is left unchanged.
    """
    payload: dict[str, Any] = {"data": data}
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(
        client.put(f"/api/sources/{obj_id}/annotations/{annotation_id}", json=payload)
    )


def delete_annotation(client: httpx.Client, obj_id: str, annotation_id: int) -> None:
    """Delete an annotation on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the annotated source.
    annotation_id : int
        ID of the annotation to delete.
    """
    unwrap(client.delete(f"/api/sources/{obj_id}/annotations/{annotation_id}"))
