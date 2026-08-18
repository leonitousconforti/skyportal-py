"""Client construction."""

from __future__ import annotations

import httpx

from skyportal_py import profile, sources


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
