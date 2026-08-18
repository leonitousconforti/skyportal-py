"""Internal envelope unwrapping and error handling."""

from __future__ import annotations

from typing import Any

import httpx


class SkyPortalError(Exception):
    """Raised when the SkyPortal API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def unwrap(response: httpx.Response) -> Any:  # noqa: ANN401
    """Return the ``data`` field of a SkyPortal response envelope.

    Raises
    ------
    SkyPortalError
        If the response is an error envelope or not JSON.
    """
    try:
        payload = response.json()
    except ValueError:
        message = (
            f"SkyPortal returned a non-JSON response (HTTP {response.status_code})"
        )
        raise SkyPortalError(message, response.status_code) from None
    if response.is_success and payload.get("status") == "success":
        return payload.get("data")
    message = payload.get("message") or f"HTTP {response.status_code}"
    raise SkyPortalError(message, response.status_code)
