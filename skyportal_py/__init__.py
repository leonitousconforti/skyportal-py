"""First-party Python client for the SkyPortal API."""

from skyportal_py import (
    annotations,
    candidates,
    classifications,
    comments,
    filters,
    groups,
    instruments,
    photometry,
    profile,
    sources,
    spectra,
    taxonomies,
    telescopes,
    users,
)
from skyportal_py._http import SkyPortalError, unwrap
from skyportal_py.client import SkyPortal, create_client

__all__ = [
    "SkyPortal",
    "SkyPortalError",
    "annotations",
    "candidates",
    "classifications",
    "comments",
    "create_client",
    "filters",
    "groups",
    "instruments",
    "photometry",
    "profile",
    "sources",
    "spectra",
    "taxonomies",
    "telescopes",
    "unwrap",
    "users",
]
