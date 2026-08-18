"""Shared Pydantic base classes for endpoint models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Model(BaseModel):
    """Base class for all skyportal-py models.

    Unknown fields are rejected, so a typo in a request payload raises a
    validation error instead of being silently dropped.
    """

    model_config = ConfigDict(extra="forbid")


class ResponseModel(Model):
    """Base class for models validated from server responses.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    model_config = ConfigDict(extra="allow")
