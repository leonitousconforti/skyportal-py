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


class AnnotationDetail(BaseModel):
    """An annotation on any resource type, with every stored field."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: str | None = None
    modified: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    origin: str | None = None
    author_id: int | None = None
    author: dict[str, Any] | None = None
    groups: list[dict[str, Any]] = Field(default_factory=list)
    obj_id: str | None = None
    spectrum_id: int | None = None
    photometry_id: int | None = None


def fetch_annotation(
    client: httpx.Client,
    resource_id: str | int,
    annotation_id: int,
    *,
    resource_type: str = "sources",
) -> AnnotationDetail:
    """Retrieve a single annotation on any annotatable resource.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the annotated resource: an object ID for sources, otherwise
        an integer ID. It must match the annotation's own resource.
    annotation_id : int
        ID of the annotation.
    resource_type : str, optional
        What the annotation is on: ``"sources"`` (the default),
        ``"spectra"`` or ``"photometry"``.
    """
    response = client.get(
        f"/api/{resource_type}/{resource_id}/annotations/{annotation_id}"
    )
    return AnnotationDetail.model_validate(unwrap(response))


def post_gaia_annotation(  # noqa: PLR0913 -- mirrors the endpoint's request body
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    crossmatch_radius: float | None = None,
    crossmatch_limmag: float | None = None,
    crossmatch_number: int | None = None,
    group_ids: list[int] | None = None,
) -> None:
    """Cross-match a source against Gaia and save the result as annotations.

    One annotation is created per Gaia match, holding the parallax, proper
    motion, magnitudes and RUWE. Nothing is returned; read the annotations
    back with :func:`fetch_annotations`.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to cross-match.
    catalog : str, optional
        Catalog key to record as the annotation origin. Defaults to
        ``"gaiadr3.gaia_source"``.
    crossmatch_radius : float, optional
        Cross-match radius in arcseconds. Defaults to the server config.
    crossmatch_limmag : float, optional
        Ignore Gaia sources fainter than this G magnitude. Defaults to the
        server config; pass ``0`` to keep sources of any magnitude.
    crossmatch_number : int, optional
        Maximum number of matches to keep, closest first after correcting
        for proper motion. Defaults to the server config.
    group_ids : list of int, optional
        Restrict the annotations' visibility to these groups. If omitted,
        they go to the public group.
    """
    payload: dict[str, Any] = {}
    if catalog is not None:
        payload["catalog"] = catalog
    if crossmatch_radius is not None:
        payload["crossmatchRadius"] = crossmatch_radius
    if crossmatch_limmag is not None:
        payload["crossmatchLimmag"] = crossmatch_limmag
    if crossmatch_number is not None:
        payload["crossmatchNumber"] = crossmatch_number
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.post(f"/api/sources/{obj_id}/annotations/gaia", json=payload))


def post_irsa_annotation(
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    crossmatch_radius: float | None = None,
    group_ids: list[int] | None = None,
) -> None:
    """Cross-match a source against an IRSA WISE catalog as annotations.

    One annotation is created per WISE match, holding the W1-W4 profile
    magnitudes and their uncertainties.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to cross-match.
    catalog : str, optional
        IRSA catalog to query. Defaults to ``"allwise_p3as_psd"``.
    crossmatch_radius : float, optional
        Cross-match radius in arcseconds. Defaults to 2.
    group_ids : list of int, optional
        Restrict the annotations' visibility to these groups. If omitted,
        they go to the public group.
    """
    payload: dict[str, Any] = {}
    if catalog is not None:
        payload["catalog"] = catalog
    if crossmatch_radius is not None:
        payload["crossmatchRadius"] = crossmatch_radius
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.post(f"/api/sources/{obj_id}/annotations/irsa", json=payload))


def post_vizier_annotation(
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    crossmatch_radius: float | None = None,
    group_ids: list[int] | None = None,
) -> None:
    """Cross-match a source against a Vizier catalog as annotations.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to cross-match.
    catalog : str, optional
        Vizier catalog identifier. Defaults to ``"VII/290"``, the million
        quasar catalog. The query must resolve to exactly one table.
    crossmatch_radius : float, optional
        Cross-match radius in arcseconds. Defaults to 2.
    group_ids : list of int, optional
        Restrict the annotations' visibility to these groups. If omitted,
        they go to the public group.
    """
    payload: dict[str, Any] = {}
    if catalog is not None:
        payload["catalog"] = catalog
    if crossmatch_radius is not None:
        payload["crossmatchRadius"] = crossmatch_radius
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.post(f"/api/sources/{obj_id}/annotations/vizier", json=payload))


def post_datalab_annotation(
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    crossmatch_radius: float | None = None,
    group_ids: list[int] | None = None,
) -> None:
    """Cross-match a source against an Astro Data Lab catalog.

    One annotation is created per match, holding photometric redshifts, or
    spectroscopic redshifts for DESI catalogs (any ``catalog`` starting
    with ``"desi_"``, which use a different schema).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to cross-match.
    catalog : str, optional
        Data Lab catalog to query. Defaults to ``"ls_dr10"``.
    crossmatch_radius : float, optional
        Cross-match radius in arcseconds. Defaults to 2.
    group_ids : list of int, optional
        Restrict the annotations' visibility to these groups. If omitted,
        they go to the public group.
    """
    payload: dict[str, Any] = {}
    if catalog is not None:
        payload["catalog"] = catalog
    if crossmatch_radius is not None:
        payload["crossmatchRadius"] = crossmatch_radius
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.post(f"/api/sources/{obj_id}/annotations/datalab", json=payload))


def post_ps1_annotation(  # noqa: PLR0913 -- mirrors the endpoint's request body
    client: httpx.Client,
    obj_id: str,
    *,
    catalog: str | None = None,
    crossmatch_radius: float | None = None,
    crossmatch_min_detections: int | None = None,
    crossmatch_number: int | None = None,
    group_ids: list[int] | None = None,
) -> None:
    """Cross-match a source against Pan-STARRS1 DR2 as annotations.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to cross-match.
    catalog : str, optional
        Catalog key to record as the annotation origin. Defaults to
        ``"ps1.dr2"``; the query itself always runs against DR2.
    crossmatch_radius : float, optional
        Cross-match radius in arcseconds. Defaults to 2 and must be
        between 0 and 5.
    crossmatch_min_detections : int, optional
        Ignore PS1 sources with fewer detections than this. Defaults to 1
        and must be at least 1.
    crossmatch_number : int, optional
        Maximum number of matches to keep. Defaults to 5 and must be
        between 1 and 5.
    group_ids : list of int, optional
        Restrict the annotations' visibility to these groups. If omitted,
        they go to the public group.
    """
    payload: dict[str, Any] = {}
    if catalog is not None:
        payload["catalog"] = catalog
    if crossmatch_radius is not None:
        payload["crossmatchRadius"] = crossmatch_radius
    if crossmatch_min_detections is not None:
        payload["crossmatchMinDetections"] = crossmatch_min_detections
    if crossmatch_number is not None:
        payload["crossmatchNumber"] = crossmatch_number
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.post(f"/api/sources/{obj_id}/annotations/ps1", json=payload))
