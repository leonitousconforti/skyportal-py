"""Shared Pydantic base class for endpoint models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    """Base class for all skyportal-py models; unknown fields are rejected."""

    model_config = ConfigDict(extra="forbid")
