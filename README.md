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

# equivalently, call the functions directly with any httpx.Client:
source = sources.fetch_source(client, "ZTF20abcdef")
```

Response models validate the fields they declare and keep everything else the
server returns as extra attributes. Error responses raise `SkyPortalError`
with the server's message and HTTP status code. For endpoints without a typed
function yet, use the httpx client directly and `unwrap` the envelope:

```python
from skyportal_py import unwrap

unwrap(client.post("/api/comment", json={"obj_id": "ZTF20abcdef", "text": "hi"}))
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
