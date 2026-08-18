"""Typed endpoint functions for ``/api/taxonomy``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py._models import ResponseModel


class Taxonomy(ResponseModel):
    """A classification taxonomy.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(validate_by_name=True)

    id: int
    name: str
    version: str | None = None
    provenance: str | None = None
    is_latest: bool = Field(alias="isLatest", default=True)
    hierarchy: dict[str, Any] | None = None


def fetch_taxonomies(client: httpx.Client) -> list[Taxonomy]:
    """Retrieve the taxonomies usable by the token's groups.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/taxonomy")
    return [Taxonomy.model_validate(item) for item in unwrap(response)]


def fetch_taxonomy(client: httpx.Client, taxonomy_id: int) -> Taxonomy:
    """Retrieve a single taxonomy by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    taxonomy_id : int
        ID of the taxonomy.
    """
    response = client.get(f"/api/taxonomy/{taxonomy_id}")
    return Taxonomy.model_validate(unwrap(response))
