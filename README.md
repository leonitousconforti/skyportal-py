# skyportal-py

First-party Python client for the [SkyPortal](https://skyportal.io) API.

## Usage

Each endpoint is a plain function with explicit types for path parameters,
query arguments, payloads, and responses (pydantic models). `create_client`
returns a `SkyPortal` client: an
[httpx](https://www.python-httpx.org)`.Client` subclass preconfigured with
the instance's base URL and token header, with every endpoint function bound
as a method.

```python
from skyportal_py import create_client, sources

client = create_client("https://skyportal.example.com", token="your-api-token")
# or, for instances that allow anonymous viewing:
anon = create_client("https://skyportal.example.com")

me = client.fetch_profile()  # -> UserProfile
page = client.fetch_sources(num_per_page=10)  # -> SourcesPage
source = client.fetch_source("ZTF20abcdef")  # -> Source
client.post_source(sources.SourcePost(id="ZTF20abcdef", ra=10.5, dec=-20.25))

my_groups = client.fetch_groups()  # -> GroupsResponse
candidates_page = client.fetch_candidates(group_ids=[1])  # -> CandidatesPage
lightcurve = client.fetch_photometry("ZTF20abcdef")  # -> list[PhotometryPoint]
notes = client.fetch_comments("ZTF20abcdef")  # -> list[Comment]
labels = client.fetch_classifications("ZTF20abcdef")  # -> list[Classification]
spectra_list = client.fetch_spectra("ZTF20abcdef")  # -> list[Spectrum]
notes_auto = client.fetch_annotations("ZTF20abcdef")  # -> list[Annotation]
client.post_comment("ZTF20abcdef", "spectrum looks like a SN Ia")

scopes = client.fetch_telescopes()  # -> list[Telescope]
cameras = client.fetch_instruments()  # -> list[Instrument]
schemes = client.fetch_taxonomies()  # -> list[Taxonomy]
alert_filters = client.fetch_filters()  # -> list[Filter]
people = client.fetch_users()  # -> UsersPage

# equivalently, call the functions directly with any httpx.Client:
source = sources.fetch_source(client, "ZTF20abcdef")
```

All models use `extra="forbid"`: unknown fields in request payloads and
server responses raise a validation error. Error responses raise `SkyPortalError`
with the server's message and HTTP status code. For endpoints without a typed
function yet, use the httpx client directly and `unwrap` the envelope:

```python
from skyportal_py import unwrap

unwrap(client.get("/api/streams"))
```

## Development

The dev environment is managed with [nix](https://nixos.org) and
[uv](https://docs.astral.sh/uv/):

```sh
nix develop  # or `direnv allow` with nix-direnv
uv run pytest
uv run ruff check
uv run ty check
```

### Tests

The tests run against a real SkyPortal instance and skip when none is
configured. CI boots one per job with `scripts/integration-up.sh` (a
pinned checkout of skyportal's own compose stack: web app, PostgreSQL,
and Valkey), caching the built image in GHCR keyed on the pinned ref in
the script. To run them yourself, point them at an instance and an
admin API token:

```sh
SKYPORTAL_TEST_URL=... SKYPORTAL_TEST_TOKEN=... uv run pytest
```
