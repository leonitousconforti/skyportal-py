"""Typed endpoint functions for ``/api/sources``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.groups import Group


class Source(BaseModel):
    """A SkyPortal source.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    ra: float | None = None
    dec: float | None = None
    redshift: float | None = None
    groups: list[Group] = Field(default_factory=list)


class SourcesPage(BaseModel):
    """One page of results from a sources query."""

    model_config = ConfigDict(extra="allow", validate_by_name=True)

    sources: list[Source]
    total_matches: int = Field(alias="totalMatches")
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


class SourcePost(BaseModel):
    """Payload for saving a new source."""

    id: str
    ra: float
    dec: float
    group_ids: list[int] | None = None


class SourcePostResponse(BaseModel):
    """Result of saving a new source."""

    model_config = ConfigDict(extra="allow")

    id: str
    saved_to_groups: list[int] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


def fetch_source(
    client: httpx.Client,
    obj_id: str,
    *,
    include_thumbnails: bool = False,
) -> Source:
    """Retrieve a single source by object ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    include_thumbnails : bool, optional
        Include thumbnail data in the response.
    """
    response = client.get(
        f"/api/sources/{obj_id}",
        params={"includeThumbnails": include_thumbnails},
    )
    return Source.model_validate(unwrap(response))


def fetch_sources(  # noqa: PLR0913 -- mirrors the endpoint's query parameters
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
    ra: float | None = None,
    dec: float | None = None,
    radius: float | None = None,
    group_ids: list[int] | None = None,
) -> SourcesPage:
    """Query saved sources, one page at a time.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls.
    ra, dec, radius : float, optional
        Cone-search filter, all in degrees; provide all three together.
    group_ids : list of int, optional
        Restrict to sources saved to these groups.
    """
    params: dict[str, str | int | float] = {
        "pageNumber": page_number,
        "numPerPage": num_per_page,
    }
    if ra is not None:
        params["ra"] = ra
    if dec is not None:
        params["dec"] = dec
    if radius is not None:
        params["radius"] = radius
    if group_ids is not None:
        params["group_ids"] = ",".join(str(gid) for gid in group_ids)
    response = client.get("/api/sources", params=params)
    return SourcesPage.model_validate(unwrap(response))


def post_source(client: httpx.Client, payload: SourcePost) -> SourcePostResponse:
    """Save a new source (or update one the token could not previously see).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SourcePost
        The source to save. If ``group_ids`` is omitted, the server saves
        the source to all of the token's groups.
    """
    response = client.post("/api/sources", json=payload.model_dump(exclude_none=True))
    return SourcePostResponse.model_validate(unwrap(response))
