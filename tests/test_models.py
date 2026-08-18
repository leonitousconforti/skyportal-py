"""Tests for the shared model base classes."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from skyportal_py import candidates, classifications, photometry, sources, spectra


def test_payload_models_forbid_unknown_fields() -> None:
    """A typo'd or unknown field in a request payload raises instead of being dropped."""
    with pytest.raises(ValidationError, match="magsystem"):
        photometry.PhotometryPost.model_validate(
            {
                "obj_id": "ZTF20abcdef",
                "mjd": 59000.0,
                "instrument_id": 1,
                "filter": "ztfg",
                "magsystem": "ab",  # typo of magsys
            }
        )
    with pytest.raises(ValidationError):
        sources.SourcePost.model_validate(
            {"id": "ZTF20abcdef", "ra": 10.5, "dec": -20.25, "group_id": [1]}
        )
    with pytest.raises(ValidationError):
        candidates.CandidatePost.model_validate(
            {
                "id": "ZTF20abcdef",
                "ra": 10.5,
                "dec": -20.25,
                "filter_ids": [1],
                "passed_at": "2020-01-01T00:00:00",
                "unknown": True,
            }
        )
    with pytest.raises(ValidationError):
        classifications.ClassificationPost.model_validate(
            {
                "obj_id": "ZTF20abcdef",
                "classification": "Ia",
                "taxonomy_id": 1,
                "prob": 0.9,  # typo of probability
            }
        )
    with pytest.raises(ValidationError):
        spectra.SpectrumPost.model_validate(
            {
                "obj_id": "ZTF20abcdef",
                "instrument_id": 1,
                "observed_at": "2020-01-01T00:00:00",
                "wavelengths": [6000.0],
                "fluxes": [1.0],
                "flux_err": [0.1],  # typo of errors
            }
        )


def test_response_models_keep_unknown_fields() -> None:
    """Response models still tolerate and preserve unmodeled server fields."""
    source = sources.Source.model_validate(
        {"id": "ZTF20abcdef", "tns_name": "SN 2020xyz"}
    )
    assert source.model_extra == {"tns_name": "SN 2020xyz"}
