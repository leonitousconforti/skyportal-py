"""Typed endpoint functions for ``/api/moving_object``."""

from __future__ import annotations

import datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap


class MovingObjectFollowupPost(BaseModel):
    """Payload for scheduling follow-up of a moving object."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    instrument_id: int
    exposure_count: int
    exposure_time: float
    start_time: str
    end_time: str
    band: str = Field(alias="filter")
    primary_only: bool | None = None
    airmass_limit: float | None = None
    moon_distance_limit: float | None = None
    sun_altitude_limit: float | None = None
    references_only: bool | None = None


class MovingObjectObservation(BaseModel):
    """A scheduled exposure from ``find_observable_sequence``.

    This is not a database model: the handler returns the plain dicts
    built by ``skyportal.utils.moving_objects.find_observable_sequence``,
    nothing is persisted, and the keys below are the complete set.
    """

    model_config = ConfigDict(extra="forbid")

    start_time: datetime.datetime | None = None
    end_time: datetime.datetime | None = None
    band: str | None = None
    field_id: int | None = None
    airmass: float | None = None
    sun_altitude: float | None = None
    moon_distance: float | None = None


def post_moving_object_followup(
    client: httpx.Client,
    obj_name: str,
    payload: MovingObjectFollowupPost,
) -> list[MovingObjectObservation]:
    """Find a continuous sequence of observations for a moving object.

    The object's ephemeris is looked up by name and matched against the
    instrument's fields; ``exposure_count`` exposures are then scheduled
    at the optimal times inside the requested window. An empty list is
    returned when no observable sequence long enough exists.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_name : str
        Name of the moving object, e.g. ``"2024 YR4"``.
    payload : MovingObjectFollowupPost
        The request. ``start_time`` and ``end_time`` are ISO-format
        datetimes less than 7 days apart. ``band`` is sent as the
        endpoint's ``filter`` field. ``primary_only`` restricts the
        search to the instrument's primary field grid (server default
        true), and ``airmass_limit``, ``moon_distance_limit`` and
        ``sun_altitude_limit`` default server-side to 2.5, 30 degrees
        and -18 degrees respectively.
    """
    response = client.post(
        f"/api/moving_object/{obj_name}/followup",
        json=payload.model_dump(by_alias=True, exclude_none=True),
    )
    return [
        MovingObjectObservation.model_validate(observation)
        for observation in unwrap(response)
    ]
