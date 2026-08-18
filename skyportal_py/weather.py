"""Typed endpoint functions for ``/api/weather``."""

from __future__ import annotations

from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class Weather(BaseModel):
    """Cached OpenWeather data for a telescope site."""

    model_config = ConfigDict(extra="forbid")

    weather: dict[str, Any] | None = None
    weather_retrieved_at: str | None = None
    weather_fetch_at: str | None = None
    weather_link: str | None = None
    telescope_name: str | None = None
    telescope_nickname: str | None = None
    telescope_id: int | None = None
    message: str | None = None


def fetch_weather(
    client: httpx.Client,
    *,
    telescope_id: int | None = None,
) -> Weather:
    """Retrieve the weather at a telescope site.

    The server refreshes the cached OpenWeather data only once the configured
    refresh interval has elapsed, and reports upstream failures in
    ``message`` rather than as an error. When no telescope can be resolved at
    all, every field except ``weather`` is absent.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    telescope_id : int, optional
        Telescope to report on. If omitted the server falls back to the user's
        weather preference, then to the first telescope the token can access.
    """
    params: dict[str, int] = {}
    if telescope_id is not None:
        params["telescope_id"] = telescope_id
    response = client.get("/api/weather", params=params)
    return Weather.model_validate(unwrap(response))
