"""Round-trip tests against a live SkyPortal instance.

These run only when ``SKYPORTAL_TEST_URL`` and ``SKYPORTAL_TEST_TOKEN``
point at a running instance; see ``scripts/integration-up.sh``. They use
the provisioned admin token and create everything they need (groups,
sources, telescopes, streams, taxonomies, ...), so no demo data is
required.
"""

from __future__ import annotations

import uuid

import pytest

from skyportal_py import (
    SkyPortal,
    SkyPortalError,
    candidates,
    classifications,
    photometry,
    sources,
    spectra,
    unwrap,
)

SUFFIX = uuid.uuid4().hex[:12]


@pytest.fixture(scope="session")
def group_id(live_client: SkyPortal) -> int:
    """Create a fresh group to save test data to."""
    response = live_client.post(
        "/api/groups", json={"name": f"skyportal-py fixtures {SUFFIX}"}
    )
    return unwrap(response)["id"]


@pytest.fixture(scope="session")
def obj_id(live_client: SkyPortal, group_id: int) -> str:
    """Save a source to the fixture group."""
    obj_id = f"skyportal-py-fix-{SUFFIX}"
    live_client.post_source(
        sources.SourcePost(id=obj_id, ra=31.5, dec=-16.25, group_ids=[group_id])
    )
    return obj_id


@pytest.fixture(scope="session")
def telescope_id(live_client: SkyPortal) -> int:
    """Create a fresh telescope."""
    return unwrap(
        live_client.post(
            "/api/telescope",
            json={
                "name": f"skyportal-py telescope {SUFFIX}",
                "nickname": f"sp-{SUFFIX}",
                "lat": 33.36,
                "lon": -116.86,
                "elevation": 1706.0,
                "diameter": 1.2,
            },
        )
    )["id"]


@pytest.fixture(scope="session")
def instrument_id(live_client: SkyPortal, telescope_id: int) -> int:
    """Create an imaging instrument on the fixture telescope."""
    return unwrap(
        live_client.post(
            "/api/instrument",
            json={
                "name": f"skyportal-py instrument {SUFFIX}",
                "type": "imager",
                "band": "optical",
                "telescope_id": telescope_id,
                "filters": ["ztfg"],
            },
        )
    )["id"]


@pytest.fixture(scope="session")
def filter_id(live_client: SkyPortal, group_id: int) -> int:
    """Create an alert filter on a fresh stream the fixture group can access."""
    stream_id = unwrap(
        live_client.post("/api/streams", json={"name": f"skyportal-py {SUFFIX}"})
    )["id"]
    unwrap(
        live_client.post(
            f"/api/groups/{group_id}/streams", json={"stream_id": stream_id}
        )
    )
    return unwrap(
        live_client.post(
            "/api/filters",
            json={
                "name": f"skyportal-py filter {SUFFIX}",
                "stream_id": stream_id,
                "group_id": group_id,
            },
        )
    )["id"]


@pytest.fixture(scope="session")
def taxonomy_id(live_client: SkyPortal, group_id: int) -> int:
    """Create a minimal taxonomy shared with the fixture group."""
    return unwrap(
        live_client.post(
            "/api/taxonomy",
            json={
                "name": f"skyportal-py taxonomy {SUFFIX}",
                "hierarchy": {
                    "class": "skyportal-py root",
                    "subclasses": [{"class": "Kilonova"}],
                },
                "version": "1.0.0",
                "group_ids": [group_id],
            },
        )
    )["taxonomy_id"]


def test_fetch_profile(live_client: SkyPortal) -> None:
    """The provisioned admin token resolves to a real user profile."""
    user = live_client.fetch_profile()
    assert user.username


def test_source_roundtrip(live_client: SkyPortal) -> None:
    """Create a group, save a source to it, and read both back."""
    suffix = uuid.uuid4().hex[:12]
    group_id = unwrap(
        live_client.post("/api/groups", json={"name": f"skyportal-py test {suffix}"})
    )["id"]

    obj_id = f"skyportal-py-{suffix}"
    result = live_client.post_source(
        sources.SourcePost(id=obj_id, ra=10.5, dec=-20.25, group_ids=[group_id])
    )
    assert result.id == obj_id

    source = live_client.fetch_source(obj_id)
    assert source.id == obj_id
    assert source.ra == pytest.approx(10.5)
    assert source.dec == pytest.approx(-20.25)
    assert any(group.id == group_id for group in source.groups)

    page = live_client.fetch_sources(group_ids=[group_id])
    assert page.total_matches == 1
    assert page.sources[0].id == obj_id

    cone = live_client.fetch_sources(ra=10.5, dec=-20.25, radius=0.5)
    assert obj_id in [s.id for s in cone.sources]


def test_groups_roundtrip(live_client: SkyPortal, group_id: int) -> None:
    """The fixture group appears in group queries."""
    group = live_client.fetch_group(group_id)
    assert group.id == group_id
    assert group.name == f"skyportal-py fixtures {SUFFIX}"
    assert not group.single_user_group

    groups = live_client.fetch_groups()
    assert group_id in [g.id for g in groups.user_accessible_groups]


def test_comment_roundtrip(live_client: SkyPortal, obj_id: str) -> None:
    """A posted comment comes back in the source's comments."""
    posted = live_client.post_comment(obj_id, "posted by skyportal-py tests")
    comments = live_client.fetch_comments(obj_id)
    match = [c for c in comments if c.id == posted.comment_id]
    assert len(match) == 1
    assert match[0].text == "posted by skyportal-py tests"
    assert match[0].obj_id == obj_id


def test_photometry_roundtrip(
    live_client: SkyPortal, obj_id: str, instrument_id: int, group_id: int
) -> None:
    """A posted photometry point comes back in the source's lightcurve."""
    result = live_client.post_photometry(
        photometry.PhotometryPost(
            obj_id=obj_id,
            mjd=59000.0,
            instrument_id=instrument_id,
            filter="ztfg",
            mag=18.1,
            magerr=0.05,
            limiting_mag=20.5,
            group_ids=[group_id],
        )
    )
    assert result.ids

    points = live_client.fetch_photometry(obj_id)
    match = [p for p in points if p.id == result.ids[0]]
    assert len(match) == 1
    assert match[0].mjd == pytest.approx(59000.0)
    assert match[0].mag == pytest.approx(18.1)
    assert match[0].filter == "ztfg"
    assert match[0].instrument_id == instrument_id


def test_candidate_roundtrip(
    live_client: SkyPortal, filter_id: int, group_id: int
) -> None:
    """A posted candidate comes back individually and in queries."""
    cand_id = f"skyportal-py-cand-{uuid.uuid4().hex[:12]}"
    result = live_client.post_candidate(
        candidates.CandidatePost(
            id=cand_id,
            ra=40.0,
            dec=-10.0,
            filter_ids=[filter_id],
            passed_at="2026-08-18T00:00:00",
        )
    )
    assert result.ids

    candidate = live_client.fetch_candidate(cand_id)
    assert candidate.id == cand_id
    assert candidate.ra == pytest.approx(40.0)

    page = live_client.fetch_candidates(group_ids=[group_id])
    assert cand_id in [c.id for c in page.candidates]


def test_classification_roundtrip(
    live_client: SkyPortal, obj_id: str, taxonomy_id: int, group_id: int
) -> None:
    """A posted classification comes back on the source."""
    posted = live_client.post_classification(
        classifications.ClassificationPost(
            obj_id=obj_id,
            classification="Kilonova",
            taxonomy_id=taxonomy_id,
            probability=0.9,
            group_ids=[group_id],
        )
    )
    labels = live_client.fetch_classifications(obj_id)
    match = [c for c in labels if c.id == posted.classification_id]
    assert len(match) == 1
    assert match[0].classification == "Kilonova"
    assert match[0].taxonomy_id == taxonomy_id
    assert match[0].probability == pytest.approx(0.9)


def test_telescope_and_instrument_roundtrip(
    live_client: SkyPortal, telescope_id: int, instrument_id: int
) -> None:
    """The fixture telescope and instrument appear in queries."""
    telescope = live_client.fetch_telescope(telescope_id)
    assert telescope.name == f"skyportal-py telescope {SUFFIX}"
    assert telescope.diameter == pytest.approx(1.2)
    assert telescope_id in [t.id for t in live_client.fetch_telescopes()]

    instrument = live_client.fetch_instrument(instrument_id)
    assert instrument.name == f"skyportal-py instrument {SUFFIX}"
    assert instrument.telescope_id == telescope_id
    assert instrument.filters == ["ztfg"]
    assert instrument_id in [i.id for i in live_client.fetch_instruments()]


def test_filter_roundtrip(
    live_client: SkyPortal, filter_id: int, group_id: int
) -> None:
    """The fixture filter appears in filter queries."""
    filter_ = live_client.fetch_filter(filter_id)
    assert filter_.name == f"skyportal-py filter {SUFFIX}"
    assert filter_.group_id == group_id
    assert filter_id in [f.id for f in live_client.fetch_filters()]


def test_taxonomy_roundtrip(live_client: SkyPortal, taxonomy_id: int) -> None:
    """The fixture taxonomy appears in taxonomy queries."""
    taxonomy = live_client.fetch_taxonomy(taxonomy_id)
    assert taxonomy.name == f"skyportal-py taxonomy {SUFFIX}"
    assert taxonomy.version == "1.0.0"
    assert taxonomy.hierarchy is not None
    assert taxonomy_id in [t.id for t in live_client.fetch_taxonomies()]


def test_spectrum_roundtrip(
    live_client: SkyPortal, obj_id: str, instrument_id: int, group_id: int
) -> None:
    """A posted spectrum comes back individually and on the source."""
    posted = live_client.post_spectrum(
        spectra.SpectrumPost(
            obj_id=obj_id,
            instrument_id=instrument_id,
            observed_at="2026-08-18T00:00:00",
            wavelengths=[400.0, 500.0, 600.0],
            fluxes=[1.0, 1.1, 0.9],
            group_ids=[group_id],
        )
    )

    spectrum = live_client.fetch_spectrum(posted.id)
    assert spectrum.obj_id == obj_id
    assert spectrum.instrument_id == instrument_id
    assert spectrum.wavelengths == pytest.approx([400.0, 500.0, 600.0])
    assert spectrum.fluxes == pytest.approx([1.0, 1.1, 0.9])

    assert posted.id in [s.id for s in live_client.fetch_spectra(obj_id)]


def test_annotation_roundtrip(
    live_client: SkyPortal, obj_id: str, group_id: int
) -> None:
    """A posted annotation comes back on the source."""
    origin = f"skyportal-py-{SUFFIX}"
    posted = live_client.post_annotation(
        obj_id, origin, {"score": 0.97}, group_ids=[group_id]
    )
    annotations = live_client.fetch_annotations(obj_id)
    match = [a for a in annotations if a.id == posted.annotation_id]
    assert len(match) == 1
    assert match[0].origin == origin
    assert match[0].data == {"score": 0.97}


def test_users_roundtrip(live_client: SkyPortal) -> None:
    """The user listing pages and individual users can be fetched."""
    page = live_client.fetch_users(num_per_page=10)
    assert page.total_matches >= 1
    assert page.users

    user = live_client.fetch_user(page.users[0].id)
    assert user.id == page.users[0].id
    assert user.username == page.users[0].username


def test_fetch_missing_source_raises(live_client: SkyPortal) -> None:
    """Fetching a nonexistent source surfaces the server's error."""
    with pytest.raises(SkyPortalError) as excinfo:
        live_client.fetch_source(f"skyportal-py-missing-{uuid.uuid4().hex[:12]}")
    assert excinfo.value.status_code is not None
    assert str(excinfo.value)


def test_anonymous_client_is_rejected(anonymous_client: SkyPortal) -> None:
    """Without a token, authenticated endpoints raise SkyPortalError."""
    with pytest.raises(SkyPortalError):
        anonymous_client.fetch_profile()
