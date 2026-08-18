"""Typed endpoint functions for source comments."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from skyportal_py._http import unwrap, unwrap_content
from skyportal_py.groups import Group


class Comment(BaseModel):
    """A comment on any commentable resource (upstream ``Comment``).

    Upstream splits comments across ``Comment``, ``CommentOnSpectrum``,
    ``CommentOnGCN``, ``CommentOnShift`` and ``CommentOnEarthquake``; this
    model is the union of that family, so each type-specific foreign key
    is optional and only the ones belonging to the comment's own table are
    ever set. ``author`` is the author's ``User.to_dict()`` (plus a
    ``gravatar_url`` key on the source endpoints), and ``obj``, ``gcn``,
    ``spectrum``, ``shift`` and ``earthquake`` stay ``dict`` to avoid
    importing in a circle from the modules that import this one.
    """

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    id: int
    created_at: datetime | None = None
    modified: datetime | None = None
    text: str | None = None
    attachment_name: str | None = None
    attachment_bytes: Any = None
    origin: str | None = None
    bot: bool | None = None
    author_id: int | None = None
    author: dict[str, Any] | None = None
    groups: list[Group] | None = None
    obj_id: str | None = None
    spectrum_id: int | None = None
    gcn_id: int | None = None
    earthquake_id: int | None = None
    shift_id: int | None = None
    obj: dict[str, Any] | None = None
    spectrum: dict[str, Any] | None = None
    gcn: dict[str, Any] | None = None
    shift: dict[str, Any] | None = None
    earthquake: dict[str, Any] | None = None
    dateobs: datetime | None = None
    resource_type: str | None = Field(alias="resourceType", default=None)


class CommentPostResponse(BaseModel):
    """Result of posting a comment."""

    model_config = ConfigDict(extra="forbid")

    comment_id: int
    message: str | None = None


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


def update_comment(
    client: httpx.Client,
    obj_id: str,
    comment_id: int,
    text: str,
    *,
    group_ids: list[int] | None = None,
) -> None:
    """Update a comment on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the commented source.
    comment_id : int
        ID of the comment to update.
    text : str
        The new comment text.
    group_ids : list of int, optional
        Restrict the comment's visibility to these groups. If omitted, the
        visibility is left unchanged.
    """
    payload: dict[str, str | list[int]] = {"text": text}
    if group_ids is not None:
        payload["group_ids"] = group_ids
    unwrap(client.put(f"/api/sources/{obj_id}/comments/{comment_id}", json=payload))


def delete_comment(client: httpx.Client, obj_id: str, comment_id: int) -> None:
    """Delete a comment on a source.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    obj_id : str
        Object ID of the commented source.
    comment_id : int
        ID of the comment to delete.
    """
    unwrap(client.delete(f"/api/sources/{obj_id}/comments/{comment_id}"))


class CommentDetail(Comment):
    """A single comment, as returned by the single-comment endpoint.

    The list and single-GET routes both return ``Comment.to_dict()`` plus
    ``resourceType``, so this is :class:`Comment` under the name the
    single-comment endpoint is documented with.
    """


class CommentAttachment(BaseModel):
    """The decoded contents of a comment attachment."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    comment_id: int = Field(alias="commentId")
    attachment: str | None = None
    attachment_name: str | None = Field(alias="attachmentName", default=None)


class CommentAttachmentCounts(BaseModel):
    """How many comments still hold their attachment in the database."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_without_attachment_bytes: int = Field(
        alias="totalWithoutAttachmentBytes", default=0
    )
    total_with_attachment_bytes: int = Field(
        alias="totalWithAttachmentBytes", default=0
    )


class CommentAttachmentBatch(BaseModel):
    """Result of moving one page of comment attachments to disk."""

    model_config = ConfigDict(extra="forbid", validate_by_name=True)

    total_matches: int = Field(alias="totalMatches", default=0)
    page_number: int = Field(alias="pageNumber", default=1)
    num_per_page: int = Field(alias="numPerPage", default=100)


def fetch_comment(
    client: httpx.Client,
    resource_id: str | int,
    comment_id: int,
    *,
    resource_type: str = "sources",
) -> CommentDetail:
    """Retrieve a single comment on any commentable resource.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the commented resource: an object ID for sources, otherwise
        an integer ID. It must match the comment's own resource.
    comment_id : int
        ID of the comment.
    resource_type : str, optional
        What the comment is on: ``"sources"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``.
    """
    response = client.get(f"/api/{resource_type}/{resource_id}/comments/{comment_id}")
    return CommentDetail.model_validate(unwrap(response))


def post_comment_with_attachment(  # noqa: PLR0913 -- mirrors the request body
    client: httpx.Client,
    resource_id: str | int,
    text: str,
    attachment_name: str,
    attachment_body: str,
    *,
    resource_type: str = "sources",
    group_ids: list[int] | None = None,
) -> CommentPostResponse:
    """Post a comment carrying a file attachment.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the resource to comment on: an object ID for sources,
        otherwise an integer ID.
    text : str
        The comment text.
    attachment_name : str
        Filename of the attachment; its extension decides whether the
        server can render a preview later.
    attachment_body : str
        Base64-encoded file contents, optionally still carrying a
        ``data:...;base64,`` prefix.
    resource_type : str, optional
        What to comment on: ``"sources"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``.
    group_ids : list of int, optional
        Restrict the comment's visibility to these groups. If omitted, the
        comment goes to the public group. Comments posted with a token are
        flagged as bot comments.
    """
    payload: dict[str, Any] = {
        "text": text,
        "attachment": {"name": attachment_name, "body": attachment_body},
    }
    if group_ids is not None:
        payload["group_ids"] = group_ids
    response = client.post(f"/api/{resource_type}/{resource_id}/comments", json=payload)
    return CommentPostResponse.model_validate(unwrap(response))


def fetch_comment_attachment(
    client: httpx.Client,
    resource_id: str | int,
    comment_id: int,
    *,
    resource_type: str = "sources",
    preview: bool = False,
) -> bytes:
    """Download a comment's attachment as raw bytes.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the commented resource; it must match the comment's own
        resource.
    comment_id : int
        ID of the comment holding the attachment.
    resource_type : str, optional
        What the comment is on: ``"sources"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``.
    preview : bool, optional
        Return a renderable preview instead of the raw file: FITS files
        come back as PNG, and other types must be in the server's list of
        previewable extensions.
    """
    params: dict[str, str] = (
        {"download": "", "preview": "true"} if preview else {"download": "true"}
    )
    response = client.get(
        f"/api/{resource_type}/{resource_id}/comments/{comment_id}/attachment",
        params=params,
    )
    return unwrap_content(response)


def fetch_comment_attachment_pdf(
    client: httpx.Client,
    resource_id: str | int,
    comment_id: int,
    *,
    resource_type: str = "sources",
    preview: bool = False,
) -> bytes:
    """Download a comment's attachment from the ``.pdf`` alias route.

    This serves exactly the same bytes as
    :func:`fetch_comment_attachment`; the suffixed URL exists only so that
    PDF viewers which key off the file extension can load it.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the commented resource; it must match the comment's own
        resource.
    comment_id : int
        ID of the comment holding the attachment.
    resource_type : str, optional
        What the comment is on: ``"sources"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``.
    preview : bool, optional
        Return the attachment inline rather than as a download.
    """
    params: dict[str, str] = (
        {"download": "", "preview": "true"} if preview else {"download": "true"}
    )
    response = client.get(
        f"/api/{resource_type}/{resource_id}/comments/{comment_id}/attachment.pdf",
        params=params,
    )
    return unwrap_content(response)


def fetch_comment_attachment_text(
    client: httpx.Client,
    resource_id: str | int,
    comment_id: int,
    *,
    resource_type: str = "sources",
) -> CommentAttachment:
    """Retrieve a comment's attachment decoded as text.

    Only useful for text-like attachments; binary files raise a decoding
    error on the server. Use :func:`fetch_comment_attachment` otherwise.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    resource_id : str or int
        ID of the commented resource; it must match the comment's own
        resource.
    comment_id : int
        ID of the comment holding the attachment.
    resource_type : str, optional
        What the comment is on: ``"sources"`` (the default), ``"spectra"``,
        ``"gcn_event"``, ``"shift"`` or ``"earthquake"``.
    """
    response = client.get(
        f"/api/{resource_type}/{resource_id}/comments/{comment_id}/attachment",
        params={"download": "", "preview": ""},
    )
    return CommentAttachment.model_validate(unwrap(response))


def fetch_comment_attachment_counts(
    client: httpx.Client,
) -> CommentAttachmentCounts:
    """Count comments whose attachment is still stored in the database.

    Requires the System admin ACL.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    """
    response = client.get("/api/comment_attachment")
    return CommentAttachmentCounts.model_validate(unwrap(response))


def post_comment_attachment_batch(
    client: httpx.Client,
    *,
    page_number: int = 1,
    num_per_page: int = 100,
) -> CommentAttachmentBatch:
    """Move one page of in-database comment attachments onto disk.

    Requires the System admin ACL. Because migrated comments drop out of
    the result set, repeated calls with ``page_number=1`` walk the whole
    backlog.

    Parameters
    ----------
    client : httpx.Client
        Client from :func:`skyportal_py.create_client`.
    page_number, num_per_page : int, optional
        Pagination controls over the comments that still hold attachment
        bytes. ``num_per_page`` is capped at 500 by the server.
    """
    response = client.post(
        "/api/comment_attachment",
        params={"pageNumber": page_number, "numPerPage": num_per_page},
    )
    return CommentAttachmentBatch.model_validate(unwrap(response))
