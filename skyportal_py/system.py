"""Typed endpoint functions for the instance introspection endpoints."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class GitLogEntry(BaseModel):
    """One parsed commit from the deployed SkyPortal git log."""

    model_config = ConfigDict(extra="forbid")

    time: str | None = None
    sha: str | None = None
    email: str | None = None
    description: str | None = None
    pr_nr: str | None = None
    pr_url: str | None = None
    commit_url: str | None = None
    name: str | None = None


class SysInfo(BaseModel):
    """System and deployment information for the SkyPortal instance."""

    model_config = ConfigDict(extra="forbid")

    gitlog: list[GitLogEntry] = Field(default_factory=list)


def fetch_sysinfo(client: httpx.Client) -> SysInfo:
    """Retrieve system and deployment information.

    The git log is capped at the 100 most recent non-merge commits, with
    "bump" and "pin" commits filtered out.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/sysinfo")
    return SysInfo.model_validate(unwrap(response))


class DBInfo(BaseModel):
    """Basic health information about the instance's database."""

    model_config = ConfigDict(extra="forbid")

    source_table_empty: bool | None = None
    postgres_version: str | None = None


def fetch_dbinfo(client: httpx.Client) -> DBInfo:
    """Retrieve whether the sources table is empty and the Postgres version.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/internal/dbinfo")
    return DBInfo.model_validate(unwrap(response))


def fetch_config(client: httpx.Client) -> dict[str, Any]:
    """Retrieve the parts of the instance config exposed to clients.

    The response is an open-ended camelCase mapping whose keys vary with the
    deployed SkyPortal version, so it is returned unmodelled. Typical keys
    include ``"invitationsEnabled"``, ``"cosmology"``,
    ``"allowedSpectrumTypes"``, ``"defaultSpectrumType"``,
    ``"gcnNoticeTypes"``, ``"colorPalette"`` and ``"publicGroupName"``.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/config")
    return unwrap(response)


def fetch_db_stats(client: httpx.Client) -> dict[str, Any]:
    """Retrieve basic database statistics (requires "System admin").

    The response is an open-ended mapping keyed by human-readable phrases such
    as ``"Number of candidates"`` and ``"Latest cron job run times &
    statuses"``, so it is returned unmodelled. The photometry count is
    approximate, coming from ``pg_class.reltuples``.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/db_stats")
    return unwrap(response)


def fetch_enum_types(client: httpx.Client) -> dict[str, Any]:
    """Retrieve the enumerated value lists the instance accepts.

    The response is an open-ended mapping of upper-case names to lists of
    allowed values, and the set of names varies with the deployed SkyPortal
    version, so it is returned unmodelled. Typical keys include
    ``"ALLOWED_SPECTRUM_TYPES"``, ``"ALLOWED_MAGSYSTEMS"``,
    ``"ALLOWED_BANDPASSES"``, ``"THUMBNAIL_TYPES"``, ``"FOLLOWUP_PRIORITIES"``,
    ``"ALLOWED_API_CLASSNAMES"``, ``"ANALYSIS_TYPES"``,
    ``"ANALYSIS_INPUT_TYPES"`` and ``"AUTHENTICATION_TYPES"``.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/enum_types")
    return unwrap(response)
