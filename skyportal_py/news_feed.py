"""Typed endpoint functions for ``/api/newsfeed``."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict

from skyportal_py._http import unwrap


class NewsFeedAuthorInfo(BaseModel):
    """Display information about the user behind a news feed item.

    Exactly the fields upstream's ``basic_user_display_info`` (and
    ``Comment.construct_author_info_dict``) copies off the ``User``.
    """

    model_config = ConfigDict(extra="forbid")

    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gravatar_url: str | None = None
    is_bot: bool | None = None


class NewsFeedItem(BaseModel):
    """One entry in the news feed (no upstream model; built by the handler).

    ``author`` is only set on comment items; ``author_info`` is absent on
    source items.
    """

    model_config = ConfigDict(extra="forbid")

    type: Literal[
        "source",
        "comment",
        "classification",
        "spectrum",
        "photometry",
    ]
    time: datetime | None = None
    message: str | None = None
    source_id: str | None = None
    classification: str | None = None
    author: str | None = None
    author_info: NewsFeedAuthorInfo | None = None


def fetch_news_feed(
    client: httpx.Client,
    *,
    num_items: int | None = None,
    team_id: int | None = None,
) -> list[NewsFeedItem]:
    """Retrieve a summary of recent activity, newest first.

    Items cover new sources, comments, classifications, spectra and follow-up
    photometry; which categories appear, and whether bot comments and ML
    classifications are included, follow the user's news feed preferences.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    num_items : int, optional
        Number of items to return. The server takes the larger of this and the
        user's preference, defaults to ``50`` when neither is set, and rejects
        values above ``1000``.
    team_id : int, optional
        Restrict the feed to sources saved to this team's groups; a view
        filter only, always intersected with the token's accessible groups.
    """
    params: dict[str, int] = {}
    if num_items is not None:
        params["numItems"] = num_items
    if team_id is not None:
        params["teamID"] = team_id
    response = client.get("/api/newsfeed", params=params)
    return [NewsFeedItem.model_validate(item) for item in unwrap(response)]
