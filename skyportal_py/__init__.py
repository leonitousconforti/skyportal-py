"""First-party Python client for the SkyPortal API."""

from skyportal_py import (
    allocations,
    annotations,
    candidates,
    classifications,
    comments,
    filters,
    followup_requests,
    groups,
    instruments,
    observing_runs,
    photometry,
    profile,
    sources,
    spectra,
    streams,
    taxonomies,
    telescopes,
    users,
)
from skyportal_py._http import SkyPortalError, unwrap
from skyportal_py.client import SkyPortal, create_client

__all__ = [
    "SkyPortal",
    "SkyPortalError",
    "allocations",
    "annotations",
    "candidates",
    "classifications",
    "comments",
    "create_client",
    "filters",
    "followup_requests",
    "groups",
    "instruments",
    "observing_runs",
    "photometry",
    "profile",
    "sources",
    "spectra",
    "streams",
    "taxonomies",
    "telescopes",
    "unwrap",
    "users",
]
