"""Typed endpoint functions for ``/api/analysis_service`` and ``/api/obj/analysis``."""

from __future__ import annotations

import datetime
from typing import Any, Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.groups import Group
from skyportal_py.users import User

AnalysisType = Literal["lightcurve_fitting", "spectrum_fitting", "meta_analysis"]
AnalysisInputType = Literal[
    "photometry",
    "spectra",
    "redshift",
    "annotations",
    "comments",
    "classifications",
]
AuthenticationType = Literal[
    "none",
    "header_token",
    "api_key",
    "HTTPBasicAuth",
    "HTTPDigestAuth",
    "OAuth1",
]
WebhookStatus = Literal[
    "queued",
    "pending",
    "completed",
    "failure",
    "cancelled",
    "timed_out",
]


class AnalysisService(BaseModel):
    """An external analysis service (upstream ``AnalysisService``)."""

    # ``_authinfo`` is an underscore-prefixed column and so is never part of
    # ``to_dict()``; the ``obj_analyses`` and ``default_analyses`` backrefs are
    # never eager-loaded by the handlers.

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    version: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    url: str | None = None
    optional_analysis_parameters: dict[str, Any] | str | None = None
    authentication_type: AuthenticationType | None = None
    enabled: bool | None = None
    analysis_type: AnalysisType | None = None
    input_data_types: list[AnalysisInputType] = Field(default_factory=list)
    timeout: float | None = None
    upload_only: bool | None = None
    display_on_resource_dropdown: bool | None = None
    is_summary: bool | None = None
    groups: list[Group] = Field(default_factory=list)


class AnalysisServicePost(BaseModel):
    """Payload for registering a new analysis service."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    name: str
    url: str
    authentication_type: AuthenticationType
    analysis_type: AnalysisType
    input_data_types: list[AnalysisInputType]
    display_name: str | None = None
    description: str | None = None
    version: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    optional_analysis_parameters: str | None = None
    authinfo: str | None = Field(alias="_authinfo", default=None)
    enabled: bool | None = None
    timeout: float | None = None
    upload_only: bool | None = None
    is_summary: bool | None = None
    display_on_resource_dropdown: bool | None = None
    group_ids: list[int] | None = None


class AnalysisServiceUpdate(BaseModel):
    """Payload for a partial update of an analysis service."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    url: str | None = None
    authentication_type: AuthenticationType | None = None
    analysis_type: AnalysisType | None = None
    input_data_types: list[AnalysisInputType] | None = None
    display_name: str | None = None
    description: str | None = None
    version: str | None = None
    contact_name: str | None = None
    contact_email: str | None = None
    optional_analysis_parameters: str | None = None
    authinfo: dict[str, Any] | None = None
    enabled: bool | None = None
    timeout: float | None = None
    upload_only: bool | None = None
    is_summary: bool | None = None
    display_on_resource_dropdown: bool | None = None
    group_ids: list[int] | None = None


class AnalysisServicePostResponse(BaseModel):
    """Result of registering an analysis service."""

    model_config = ConfigDict(extra="forbid")

    id: int


class ObjAnalysis(BaseModel):
    """An analysis run on an object (upstream ``ObjAnalysis``)."""

    # ``_unique_id`` and ``_full_name`` are underscore-prefixed columns and so
    # never appear in ``to_dict()``; ``_full_name`` is surfaced separately as
    # ``filename`` when ``includeFilename`` is set. ``obj`` stays untyped-out
    # because :mod:`skyportal_py.sources` imports this module, and it is never
    # eager-loaded anyway.
    #
    # ``analysis_service_name``, ``analysis_service_description``,
    # ``num_plots``, ``filename``, ``data``, ``model_lightcurve``,
    # ``model_lightcurves``, ``model_name`` and ``n_detections`` are injected by
    # the handler rather than being columns. The listing endpoint without
    # ``objID`` returns only ``id``, ``obj_id``, ``status``, ``status_message``,
    # ``created_at``, ``last_activity`` and ``analysis_service_id`` (plus the
    # two service-name keys).

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    obj_id: str | None = None
    author_id: int | None = None
    analysis_service_id: int | None = None
    hash: str | None = None
    show_parameters: bool | None = None
    show_plots: bool | None = None
    show_corner: bool | None = None
    analysis_parameters: dict[str, Any] | None = None
    input_filters: dict[str, Any] | None = None
    invalid_after: datetime.datetime | None = None
    token: str | None = None
    handled_by_url: str | None = None
    status: WebhookStatus | None = None
    status_message: str | None = None
    duration: float | None = None
    last_activity: datetime.datetime | None = None
    analysis_service_name: str | None = None
    analysis_service_description: str | None = None
    num_plots: int | None = None
    filename: str | None = None
    groups: list[Group] = Field(default_factory=list)
    data: dict[str, Any] | None = None
    model_lightcurve: Any = None
    model_lightcurves: Any = None
    model_name: str | None = None
    n_detections: int | None = None


class AnalysisPost(BaseModel):
    """Payload for starting an analysis run."""

    model_config = ConfigDict(extra="forbid")

    analysis_parameters: dict[str, Any] | None = None
    show_parameters: bool | None = None
    show_plots: bool | None = None
    show_corner: bool | None = None
    input_filters: dict[str, Any] | None = None
    group_ids: list[int] | None = None


class AnalysisPostResponse(BaseModel):
    """Result of starting an analysis run."""

    model_config = ConfigDict(extra="forbid")

    id: int


class AnalysisUploadPost(BaseModel):
    """Payload for uploading results to an upload-only analysis service."""

    model_config = ConfigDict(extra="forbid")

    analysis: dict[str, Any] | None = None
    message: str | None = None
    show_parameters: bool | None = None
    show_plots: bool | None = None
    show_corner: bool | None = None
    group_ids: list[int] | None = None


class AnalysisUploadResponse(BaseModel):
    """Result of uploading an upload-only analysis."""

    model_config = ConfigDict(extra="forbid")

    id: int
    message: str | None = None


class DefaultAnalysis(BaseModel):
    """A default analysis (upstream ``DefaultAnalysis``)."""

    # The handler eager-loads ``groups``, ``author`` and ``analysis_service``.

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    analysis_service_id: int | None = None
    author_id: int | None = None
    show_parameters: bool | None = None
    show_plots: bool | None = None
    show_corner: bool | None = None
    default_analysis_parameters: dict[str, Any] | None = None
    source_filter: dict[str, Any] | None = None
    stats: dict[str, Any] | None = None
    groups: list[Group] = Field(default_factory=list)
    author: User | None = None
    analysis_service: AnalysisService | None = None


class DefaultAnalysisPost(BaseModel):
    """Payload for creating or updating a default analysis."""

    model_config = ConfigDict(extra="forbid")

    default_analysis_parameters: dict[str, Any] | None = None
    source_filter: dict[str, Any] | None = None
    daily_limit: int | None = None
    show_parameters: bool | None = None
    show_plots: bool | None = None
    show_corner: bool | None = None
    group_ids: list[int] | None = None


class DefaultAnalysisPostResponse(BaseModel):
    """Result of creating a default analysis."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_analysis_service(
    client: httpx.Client,
    analysis_service_id: int,
) -> AnalysisService:
    """Retrieve a single analysis service by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service.
    """
    response = client.get(f"/api/analysis_service/{analysis_service_id}")
    return AnalysisService.model_validate(unwrap(response))


def fetch_analysis_services(client: httpx.Client) -> list[AnalysisService]:
    """Retrieve all analysis services visible to the token.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/analysis_service")
    return [AnalysisService.model_validate(service) for service in unwrap(response)]


def post_analysis_service(
    client: httpx.Client,
    payload: AnalysisServicePost,
) -> AnalysisServicePostResponse:
    """Register a new analysis service.

    Requires the "Manage Analysis Services" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : AnalysisServicePost
        The service to register. ``optional_analysis_parameters`` and
        ``authinfo`` (sent as ``_authinfo``) must be JSON-encoded strings;
        ``authinfo`` is required unless ``authentication_type`` is
        ``"none"``. If ``group_ids`` is omitted, the service is made
        accessible to all of the token's groups.
    """
    response = client.post(
        "/api/analysis_service",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return AnalysisServicePostResponse.model_validate(unwrap(response))


def update_analysis_service(
    client: httpx.Client,
    analysis_service_id: int,
    payload: AnalysisServiceUpdate,
) -> None:
    """Update an analysis service.

    Only the provided fields are sent; omitted fields are left unchanged.
    Requires the "Manage Analysis Services" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service to update.
    payload : AnalysisServiceUpdate
        The fields to update.
    """
    unwrap(
        client.patch(
            f"/api/analysis_service/{analysis_service_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def delete_analysis_service(client: httpx.Client, analysis_service_id: int) -> None:
    """Delete an analysis service.

    Requires the "Manage Analysis Services" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service to delete.
    """
    unwrap(client.delete(f"/api/analysis_service/{analysis_service_id}"))


def fetch_default_analysis(
    client: httpx.Client,
    analysis_service_id: int,
    default_analysis_id: int,
) -> DefaultAnalysis:
    """Retrieve a single default analysis by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service the default analysis belongs to.
    default_analysis_id : int
        ID of the default analysis.
    """
    response = client.get(
        f"/api/analysis_service/{analysis_service_id}"
        f"/default_analysis/{default_analysis_id}"
    )
    return DefaultAnalysis.model_validate(unwrap(response))


def fetch_default_analyses(
    client: httpx.Client,
    analysis_service_id: int,
) -> list[DefaultAnalysis]:
    """Retrieve the default analyses of an analysis service.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service.
    """
    response = client.get(
        f"/api/analysis_service/{analysis_service_id}/default_analysis"
    )
    return [DefaultAnalysis.model_validate(default) for default in unwrap(response)]


def post_default_analysis(
    client: httpx.Client,
    analysis_service_id: int,
    payload: DefaultAnalysisPost,
) -> DefaultAnalysisPostResponse:
    """Create a default analysis for an analysis service.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service to attach the default analysis to.
    payload : DefaultAnalysisPost
        The default analysis to create. ``daily_limit`` defaults to 10 and
        must be between 1 and 1000. If ``group_ids`` is omitted, the server
        uses all of the token's groups.
    """
    response = client.post(
        f"/api/analysis_service/{analysis_service_id}/default_analysis",
        json=payload.model_dump(exclude_none=True),
    )
    return DefaultAnalysisPostResponse.model_validate(unwrap(response))


def update_default_analysis(
    client: httpx.Client,
    analysis_service_id: int,
    default_analysis_id: int,
    payload: DefaultAnalysisPost,
) -> None:
    """Update a default analysis.

    Only the provided fields are sent; omitted fields are left unchanged.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service the default analysis belongs to.
    default_analysis_id : int
        ID of the default analysis to update.
    payload : DefaultAnalysisPost
        The fields to update.
    """
    unwrap(
        client.patch(
            f"/api/analysis_service/{analysis_service_id}"
            f"/default_analysis/{default_analysis_id}",
            json=payload.model_dump(exclude_none=True),
        )
    )


def delete_default_analysis(
    client: httpx.Client,
    analysis_service_id: int,
    default_analysis_id: int,
) -> None:
    """Delete a default analysis.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_service_id : int
        ID of the analysis service the default analysis belongs to.
    default_analysis_id : int
        ID of the default analysis to delete.
    """
    unwrap(
        client.delete(
            f"/api/analysis_service/{analysis_service_id}"
            f"/default_analysis/{default_analysis_id}"
        )
    )


def post_analysis(
    client: httpx.Client,
    obj_id: str,
    analysis_service_id: int,
    payload: AnalysisPost | None = None,
) -> AnalysisPostResponse:
    """Start an analysis run on an object.

    Requires the "Run Analyses" permission. The server assembles the input
    data, calls the external service asynchronously, and returns the new
    analysis ID immediately; poll :func:`fetch_analysis` for the status.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID to analyze.
    analysis_service_id : int
        ID of the analysis service to run. Must not be an upload-only
        service (use :func:`post_analysis_upload` for those).
    payload : AnalysisPost, optional
        Run options. ``analysis_parameters`` keys must be declared by the
        service's ``optional_analysis_parameters``. If ``group_ids`` is
        omitted, results are visible to all of the token's groups.
    """
    body = payload.model_dump(exclude_none=True) if payload is not None else {}
    response = client.post(
        f"/api/obj/{obj_id}/analysis/{analysis_service_id}", json=body
    )
    return AnalysisPostResponse.model_validate(unwrap(response))


def fetch_analysis(
    client: httpx.Client,
    analysis_id: int,
    *,
    include_analysis_data: bool = False,
    include_filename: bool = False,
) -> ObjAnalysis:
    """Retrieve a single analysis by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_id : int
        ID of the analysis.
    include_analysis_data : bool, optional
        Include the analysis data in the response; can be large.
    include_filename : bool, optional
        Include the server-side filename of the analysis data.
    """
    response = client.get(
        f"/api/obj/analysis/{analysis_id}",
        params={
            "includeAnalysisData": include_analysis_data,
            "includeFilename": include_filename,
        },
    )
    return ObjAnalysis.model_validate(unwrap(response))


def fetch_analyses(
    client: httpx.Client,
    *,
    obj_id: str | None = None,
    analysis_service_id: int | None = None,
    summary_only: bool = False,
    include_filename: bool = False,
) -> list[ObjAnalysis]:
    """Retrieve analyses, optionally restricted to one object.

    Without ``obj_id``, the server returns a minimal record per analysis
    (IDs, status, and timestamps only).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str, optional
        Restrict to analyses whose object ID contains this string.
    analysis_service_id : int, optional
        Restrict to analyses run with this analysis service.
    summary_only : bool, optional
        Only return analyses from services with ``is_summary`` set.
    include_filename : bool, optional
        Include the server-side filename of the analysis data. Only
        applies when ``obj_id`` is provided.
    """
    params: dict[str, str | int | bool] = {
        "summaryOnly": summary_only,
        "includeFilename": include_filename,
    }
    if obj_id is not None:
        params["objID"] = obj_id
    if analysis_service_id is not None:
        params["analysisServiceID"] = analysis_service_id
    response = client.get("/api/obj/analysis", params=params)
    return [ObjAnalysis.model_validate(analysis) for analysis in unwrap(response)]


def delete_analysis(client: httpx.Client, analysis_id: int) -> None:
    """Delete an analysis and its stored data.

    Requires the "Run Analyses" permission.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_id : int
        ID of the analysis to delete.
    """
    unwrap(client.delete(f"/api/obj/analysis/{analysis_id}"))


def post_analysis_upload(
    client: httpx.Client,
    obj_id: str,
    analysis_service_id: int,
    payload: AnalysisUploadPost,
) -> AnalysisUploadResponse:
    """Upload results for an upload-only analysis service.

    Requires the "Run Analyses" permission. The analysis is stored as
    completed without calling any external service.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID the analysis belongs to.
    analysis_service_id : int
        ID of the analysis service; must be an upload-only service.
    payload : AnalysisUploadPost
        The results to store. ``analysis`` holds the results data (e.g.
        ``{"results": ...}``); ``message`` becomes the status message. If
        ``group_ids`` is omitted, results are visible to all of the
        token's groups.
    """
    response = client.post(
        f"/api/obj/{obj_id}/analysis_upload/{analysis_service_id}",
        json=payload.model_dump(exclude_none=True),
    )
    return AnalysisUploadResponse.model_validate(unwrap(response))


def fetch_analysis_results(
    client: httpx.Client,
    analysis_id: int,
    *,
    download: bool = False,
) -> Any:  # noqa: ANN401
    """Retrieve the results data of a completed analysis.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_id : int
        ID of the analysis.
    download : bool, optional
        Retrieve the results as a JSON file download instead of the usual
        response envelope; the return value is then the raw file bytes.
    """
    response = client.get(
        f"/api/obj/analysis/{analysis_id}/results",
        params={"download": "true"} if download else {},
    )
    if download:
        return unwrap_content(response)
    return unwrap(response)


def fetch_analysis_plot(
    client: httpx.Client,
    analysis_id: int,
    *,
    plot_number: int = 0,
) -> bytes:
    """Download one plot produced by an analysis.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    analysis_id : int
        ID of the analysis.
    plot_number : int, optional
        Which plot to download, starting at 0. The number of available
        plots is the ``num_plots`` field of :func:`fetch_analysis`.
    """
    response = client.get(f"/api/obj/analysis/{analysis_id}/plots/{plot_number}")
    return unwrap_content(response)
