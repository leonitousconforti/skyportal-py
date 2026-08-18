"""Typed endpoint functions for ``/api/summary_query``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class SummaryQueryPost(BaseModel):
    """Payload for a source summary similarity search."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    q: str | None = None
    obj_id: str | None = Field(alias="objID", default=None)
    k: int | None = None
    z_min: float | None = None
    z_max: float | None = None
    classification_types: list[str] | None = Field(
        alias="classificationTypes", default=None
    )


class SummaryQueryMatch(BaseModel):
    """One vector-store hit for a summary query (not a SkyPortal model).

    The shape is defined by the Pinecone client, not by SkyPortal: when
    ``q`` is used the handler rebuilds each hit as exactly ``id``,
    ``score`` and ``metadata``, but when ``obj_id`` is used it passes the
    raw ``matches`` of the Pinecone query response straight through, so
    the remaining fields are Pinecone's ``ScoredVector`` attributes
    (``values``, ``sparse_values``, serialized as ``sparseValues``) and
    may change with the Pinecone SDK version rather than with SkyPortal.
    ``metadata`` holds whatever SkyPortal indexed alongside the summary
    (``redshift``, ``class``, ...), so it stays free-form.
    """

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    id: str
    score: float | None = None
    values: list[float] | None = None
    sparse_values: dict[str, Any] | None = Field(alias="sparseValues", default=None)
    metadata: dict[str, Any] | None = None


class SummaryQueryResults(BaseModel):
    """Results of a source summary similarity search."""

    model_config = ConfigDict(extra="forbid")

    query_results: list[SummaryQueryMatch] = Field(default_factory=list)


def post_summary_query(
    client: httpx.Client,
    payload: SummaryQueryPost,
) -> SummaryQueryResults:
    """Search for sources whose summaries match a query.

    The search runs against the vector store of source summaries, so it
    requires the server to be configured with an embeddings store and an
    OpenAI key (globally or in the requesting user's preferences).

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    payload : SummaryQueryPost
        The query. Exactly one of ``q`` (a free-text query) and
        ``obj_id`` (find sources similar to that source's summary) must
        be given. ``k`` is the maximum number of sources to return and
        must satisfy ``1 <= k <= 100``; server default 5. ``z_min`` and
        ``z_max`` bound the redshift of the returned sources and
        ``classification_types`` restricts them to those
        classifications; omitting them applies no restriction.
    """
    response = client.post(
        "/api/summary_query",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return SummaryQueryResults.model_validate(unwrap(response))
