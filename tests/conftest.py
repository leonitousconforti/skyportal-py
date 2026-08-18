"""Shared fixtures: clients for a live SkyPortal instance.

Start one with ``scripts/integration-up.sh`` (requires Docker); it prints
the environment variables these fixtures read. Tests skip when they are
unset.
"""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Iterator
from typing import Any

import httpx
import pytest

from skyportal_py import SkyPortal, create_client


def _base_url() -> str:
    url = os.environ.get("SKYPORTAL_TEST_URL")
    if not url:
        pytest.skip("SKYPORTAL_TEST_URL is not set")
    return url


def _pace(_request: httpx.Request) -> None:
    """Stay under the instance's nginx-level API rate limit."""
    time.sleep(0.3)


_PACE_HOOKS: dict[str, list[Callable[..., Any]]] = {"request": [_pace]}


@pytest.fixture(scope="session")
def live_client() -> Iterator[SkyPortal]:
    """Client for a live SkyPortal instance, or skip if none is configured."""
    token = os.environ.get("SKYPORTAL_TEST_TOKEN")
    if not token:
        pytest.skip("SKYPORTAL_TEST_TOKEN is not set")
    with create_client(_base_url(), token=token) as client:
        client.event_hooks = _PACE_HOOKS
        yield client


@pytest.fixture(scope="session")
def anonymous_client() -> Iterator[SkyPortal]:
    """Tokenless client for the same instance."""
    with create_client(_base_url()) as client:
        client.event_hooks = _PACE_HOOKS
        yield client
