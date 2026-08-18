"""HTTP client for a SkyPortal instance."""

from __future__ import annotations

from typing import Any

import requests


class SkyPortalError(Exception):
    """Raised when the SkyPortal API returns an error response."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class SkyPortal:
    """Client for a SkyPortal instance's HTTP API.

    Parameters
    ----------
    base_url : str
        Root URL of the SkyPortal instance, e.g. ``https://fritz.science``.
    token : str
        API token from your SkyPortal profile page.
    timeout : float, optional
        Timeout in seconds applied to every request.
    session : requests.Session, optional
        Session to reuse; a new one is created if not given.

    Examples
    --------
    >>> client = SkyPortal("https://skyportal.example.com", token="abc123")
    >>> client.get("sources", params={"numPerPage": 10})  # doctest: +SKIP
    """

    def __init__(
        self,
        base_url: str,
        token: str,
        *,
        timeout: float = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()
        self._session.headers["Authorization"] = f"token {token}"

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Send a request and return the ``data`` field of the response.

        Parameters
        ----------
        method : str
            HTTP method, e.g. ``"GET"``.
        path : str
            API path relative to the instance root, with or without the
            leading ``/api/`` prefix.
        params : dict, optional
            Query parameters.
        json : Any, optional
            JSON-serializable request body.

        Returns
        -------
        Any
            The ``data`` field of the SkyPortal response envelope.

        Raises
        ------
        SkyPortalError
            If the response is not a success.
        """
        path = path.lstrip("/")
        if not path.startswith("api/"):
            path = f"api/{path}"
        response = self._session.request(
            method,
            f"{self.base_url}/{path}",
            params=params,
            json=json,
            timeout=self.timeout,
        )
        try:
            payload = response.json()
        except ValueError:
            message = (
                f"SkyPortal returned a non-JSON response (HTTP {response.status_code})"
            )
            raise SkyPortalError(message, response.status_code) from None
        if response.ok and payload.get("status") == "success":
            return payload.get("data")
        message = payload.get("message") or f"HTTP {response.status_code}"
        raise SkyPortalError(message, response.status_code)

    def get(self, path: str, *, params: dict[str, Any] | None = None) -> Any:  # noqa: ANN401
        """Send a GET request."""
        return self.request("GET", path, params=params)

    def post(self, path: str, *, json: Any = None) -> Any:  # noqa: ANN401
        """Send a POST request."""
        return self.request("POST", path, json=json)

    def put(self, path: str, *, json: Any = None) -> Any:  # noqa: ANN401
        """Send a PUT request."""
        return self.request("PUT", path, json=json)

    def patch(self, path: str, *, json: Any = None) -> Any:  # noqa: ANN401
        """Send a PATCH request."""
        return self.request("PATCH", path, json=json)

    def delete(self, path: str) -> Any:  # noqa: ANN401
        """Send a DELETE request."""
        return self.request("DELETE", path)

    def whoami(self) -> dict[str, Any]:
        """Return the profile of the user associated with the token."""
        return self.get("internal/profile")
