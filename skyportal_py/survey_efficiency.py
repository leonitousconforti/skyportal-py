"""Typed endpoint functions for ``/api/survey_efficiency``."""

from __future__ import annotations

import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap
from skyportal_py.groups import Group
from skyportal_py.instruments import Instrument
from skyportal_py.localizations import Localization
from skyportal_py.users import User


class SurveyEfficiencyForObservations(BaseModel):
    """An efficiency analysis (upstream ``SurveyEfficiencyForObservations``).

    ``gcnevent`` stays ``dict`` because :mod:`skyportal_py.gcn_events`
    already imports :mod:`skyportal_py.observation_plans`, which this
    module imports, so typing it would risk an import cycle.
    """

    # ``number_of_transients``, ``number_in_covered``, ``number_detected`` and
    # ``efficiency`` are Python properties derived from ``lightcurves``, not
    # columns: the ``/api/survey_efficiency`` handlers omit them, while the GCN
    # event and observation plan handlers add them to the serialized row.

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str | None = None
    lightcurves: str | None = None
    requester_id: int | None = None
    gcnevent_id: int | None = None
    localization_id: int | None = None
    instrument_id: int | None = None
    number_of_transients: int | None = None
    number_in_covered: int | None = None
    number_detected: int | None = None
    efficiency: float | None = None
    requester: User | None = None
    groups: list[Group] = Field(default_factory=list)
    gcnevent: dict[str, Any] | None = None
    localization: Localization | None = None
    instrument: Instrument | None = None


class SurveyEfficiencyForObservationPlan(BaseModel):
    """An efficiency analysis (upstream ``SurveyEfficiencyForObservationPlan``)."""

    # As above, the four count/efficiency keys are properties injected by the
    # observation plan handler rather than mapper columns.

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str | None = None
    lightcurves: str | None = None
    requester_id: int | None = None
    observation_plan_id: int | None = None
    number_of_transients: int | None = None
    number_in_covered: int | None = None
    number_detected: int | None = None
    efficiency: float | None = None
    requester: User | None = None
    groups: list[Group] = Field(default_factory=list)
    # ``observation_plan`` stays a dict: this module is the canonical home of
    # the survey-efficiency models, and ``observation_plans`` imports it.
    observation_plan: dict[str, Any] | None = None


class DefaultSurveyEfficiencyRequest(BaseModel):
    """A default efficiency request (upstream ``DefaultSurveyEfficiencyRequest``)."""

    model_config = ConfigDict(extra="forbid")

    id: int
    created_at: datetime.datetime | None = None
    modified: datetime.datetime | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    default_observationplan_request_id: int | None = None
    default_observationplan_request: dict[str, Any] | None = None


class DefaultSurveyEfficiencyPostResponse(BaseModel):
    """Result of creating a default survey efficiency request."""

    model_config = ConfigDict(extra="forbid")

    id: int


def fetch_survey_efficiency_for_observations(
    client: httpx.Client,
    survey_efficiency_analysis_id: int,
) -> SurveyEfficiencyForObservations:
    """Retrieve a single survey efficiency analysis of executed observations.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    survey_efficiency_analysis_id : int
        ID of the analysis, as returned by
        :func:`skyportal_py.observations.post_observation_simsurvey`.
    """
    response = client.get(
        f"/api/survey_efficiency/observations/{survey_efficiency_analysis_id}"
    )
    return SurveyEfficiencyForObservations.model_validate(unwrap(response))


def fetch_survey_efficiencies_for_observations(
    client: httpx.Client,
    *,
    gcnevent_id: int | None = None,
) -> list[SurveyEfficiencyForObservations]:
    """Retrieve the survey efficiency analyses of executed observations.

    Only analyses visible to the requesting user's groups are returned.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    gcnevent_id : int, optional
        Only return analyses for this GCN event. If omitted, analyses for
        all accessible events are returned.
    """
    params: dict[str, int] = {}
    if gcnevent_id is not None:
        params["gcnevent_id"] = gcnevent_id
    response = client.get("/api/survey_efficiency/observations", params=params)
    return [
        SurveyEfficiencyForObservations.model_validate(analysis)
        for analysis in unwrap(response)
    ]


def fetch_survey_efficiency_for_observation_plan(
    client: httpx.Client,
    survey_efficiency_analysis_id: int,
) -> SurveyEfficiencyForObservationPlan:
    """Retrieve a single survey efficiency analysis of an observation plan.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    survey_efficiency_analysis_id : int
        ID of the analysis, as returned by
        :func:`skyportal_py.observation_plans.fetch_observation_plan_simsurvey`.
    """
    response = client.get(
        f"/api/survey_efficiency/observation_plan/{survey_efficiency_analysis_id}"
    )
    return SurveyEfficiencyForObservationPlan.model_validate(unwrap(response))


def fetch_survey_efficiencies_for_observation_plan(
    client: httpx.Client,
    *,
    observation_plan_id: int | None = None,
) -> list[SurveyEfficiencyForObservationPlan]:
    """Retrieve the survey efficiency analyses of observation plans.

    Only analyses visible to the requesting user's groups are returned.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    observation_plan_id : int, optional
        Only return analyses for this event observation plan (the
        generated plan, not the observation plan request). If omitted,
        all accessible analyses are returned.
    """
    params: dict[str, int] = {}
    if observation_plan_id is not None:
        params["observation_plan_id"] = observation_plan_id
    response = client.get("/api/survey_efficiency/observation_plan", params=params)
    return [
        SurveyEfficiencyForObservationPlan.model_validate(analysis)
        for analysis in unwrap(response)
    ]


def post_default_survey_efficiency(
    client: httpx.Client,
    default_observationplan_request_id: int,
    *,
    payload: dict[str, Any] | None = None,
) -> DefaultSurveyEfficiencyPostResponse:
    """Create a default survey efficiency request.

    The analysis is run automatically whenever the referenced default
    observation plan generates a plan.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_observationplan_request_id : int
        ID of the default observation plan request to attach the analysis
        to. It must be readable by the requesting user.
    payload : dict, optional
        Content of the survey efficiency analysis (simulation parameters
        such as ``numberInjections``, ``numberDetections``,
        ``detectionThreshold`` and ``modelName``).
    """
    body: dict[str, Any] = {
        "default_observationplan_request_id": default_observationplan_request_id
    }
    if payload is not None:
        body["payload"] = payload
    response = client.post("/api/default_survey_efficiency", json=body)
    return DefaultSurveyEfficiencyPostResponse.model_validate(unwrap(response))


def fetch_default_survey_efficiency(
    client: httpx.Client,
    default_survey_efficiency_id: int,
) -> DefaultSurveyEfficiencyRequest:
    """Retrieve a single default survey efficiency request by ID.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_survey_efficiency_id : int
        ID of the default survey efficiency request.
    """
    response = client.get(
        f"/api/default_survey_efficiency/{default_survey_efficiency_id}"
    )
    return DefaultSurveyEfficiencyRequest.model_validate(unwrap(response))


def fetch_default_survey_efficiencies(
    client: httpx.Client,
) -> list[DefaultSurveyEfficiencyRequest]:
    """Retrieve all accessible default survey efficiency requests.

    Each request includes its parent default observation plan request
    under ``default_observationplan_request``.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/default_survey_efficiency")
    return [
        DefaultSurveyEfficiencyRequest.model_validate(request)
        for request in unwrap(response)
    ]


def delete_default_survey_efficiency(
    client: httpx.Client,
    default_survey_efficiency_id: int,
) -> None:
    """Delete a default survey efficiency request.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    default_survey_efficiency_id : int
        ID of the default survey efficiency request to delete.
    """
    unwrap(
        client.delete(f"/api/default_survey_efficiency/{default_survey_efficiency_id}")
    )
