"""Typed endpoint functions for source comments."""

from __future__ import annotations

import httpx

from skyportal_py._http import unwrap
from skyportal_py._models import ResponseModel


class Comment(ResponseModel):
    """A comment on a source.

    Only commonly used fields are modeled; everything else the server
    returns is kept as extra attributes.
    """

    id: int
    text: str
    obj_id: str | None = None
    author_id: int | None = None
    created_at: str | None = None


class CommentPostResponse(ResponseModel):
    """Result of posting a comment."""

    comment_id: int


def fetch_comments(client: httpx.Client, obj_id: str) -> list[Comment]:
    """Retrieve the comments on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source, e.g. ``"ZTF20abcdef"``.
    """
    response = client.get(f"/api/sources/{obj_id}/comments")
    return [Comment.model_validate(comment) for comment in unwrap(response)]


def post_comment(
    client: httpx.Client,
    obj_id: str,
    text: str,
    *,
    group_ids: list[int] | None = None,
) -> CommentPostResponse:
    """Post a comment on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the source to comment on.
    text : str
        The comment text.
    group_ids : list of int, optional
        Restrict the comment's visibility to these groups. If omitted, the
        server applies its default visibility.
    """
    payload: dict[str, str | list[int]] = {"text": text}
    if group_ids is not None:
        payload["group_ids"] = group_ids
    response = client.post(f"/api/sources/{obj_id}/comments", json=payload)
    return CommentPostResponse.model_validate(unwrap(response))
