"""Typed endpoint functions for ``/api/healpix``."""

from __future__ import annotations

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class HealpixCounts(BaseModel):
    """Counts of objects with and without a HEALPix index."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_without_healpix: int = Field(alias="totalWithoutHealpix", default=0)
    total_with_healpix: int = Field(alias="totalWithHealpix", default=0)


class HealpixUpdate(BaseModel):
    """Result of a HEALPix backfill batch."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_matches: int = Field(alias="totalMatches", default=0)
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


def fetch_healpix_counts(client: httpx.Client) -> HealpixCounts:
    """Count the objects with and without a HEALPix index.

    Requires the ``System admin`` ACL.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/healpix")
    return HealpixCounts.model_validate(unwrap(response))


def post_healpix_update(
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
) -> HealpixUpdate:
    """Compute HEALPix indices for one batch of objects that lack them.

    Requires the ``System admin`` ACL. ``total_matches`` in the response
    counts the objects still missing a HEALPix index before this batch ran.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls; the server defaults to page 1 and 100 per page,
        and caps ``num_per_page`` at 500.
    """
    params = {"pageNumber": page_number, "numPerPage": num_per_page}
    response = client.post("/api/healpix", params=params)
    return HealpixUpdate.model_validate(unwrap(response))
