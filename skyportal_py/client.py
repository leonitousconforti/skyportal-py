"""Client construction."""

from __future__ import annotations

import httpx

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


class SkyPortal(httpx.Client):
    """An ``httpx.Client`` with the typed endpoint functions bound as methods.

    Endpoint functions take the client as their first argument, so assigning
    them here turns them into methods (``self`` is the client). Both spellings
    work: ``client.fetch_source("ZTF...")`` and
    ``sources.fetch_source(client, "ZTF...")``.
    """

    fetch_source = sources.fetch_source
    fetch_sources = sources.fetch_sources
    post_source = sources.post_source
    fetch_profile = profile.fetch_profile
    fetch_group = groups.fetch_group
    fetch_groups = groups.fetch_groups
    fetch_candidate = candidates.fetch_candidate
    fetch_candidates = candidates.fetch_candidates
    post_candidate = candidates.post_candidate
    fetch_photometry = photometry.fetch_photometry
    post_photometry = photometry.post_photometry
    fetch_comments = comments.fetch_comments
    post_comment = comments.post_comment
    fetch_classifications = classifications.fetch_classifications
    post_classification = classifications.post_classification
    fetch_spectrum = spectra.fetch_spectrum
    fetch_spectra = spectra.fetch_spectra
    post_spectrum = spectra.post_spectrum
    fetch_instrument = instruments.fetch_instrument
    fetch_instruments = instruments.fetch_instruments
    fetch_telescope = telescopes.fetch_telescope
    fetch_telescopes = telescopes.fetch_telescopes
    fetch_taxonomy = taxonomies.fetch_taxonomy
    fetch_taxonomies = taxonomies.fetch_taxonomies
    fetch_filter = filters.fetch_filter
    fetch_filters = filters.fetch_filters
    fetch_annotations = annotations.fetch_annotations
    post_annotation = annotations.post_annotation
    fetch_user = users.fetch_user
    fetch_users = users.fetch_users


def create_client(
    base_url: str,
    token: str | None = None,
    *,
    timeout: float = 30.0,
) -> SkyPortal:
    """Create a client configured for a SkyPortal instance.

    Reuse one client per instance: it pools connections, so repeated
    requests skip the TCP/TLS handshake.

    Parameters
    ----------
    base_url : str
        Root URL of the SkyPortal instance, e.g. ``https://fritz.science``.
    token : str, optional
        API token from your SkyPortal profile page. Omit for anonymous
        access to instances that allow it.
    timeout : float, optional
        Timeout in seconds applied to every request.
    """
    headers = {} if token is None else {"Authorization": f"token {token}"}
    return SkyPortal(base_url=base_url, headers=headers, timeout=timeout)
