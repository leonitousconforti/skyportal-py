# skyportal-py

First-party Python client for the [SkyPortal](https://skyportal.io) API.

## Usage

```python
from skyportal_py import SkyPortal

client = SkyPortal("https://skyportal.example.com", token="your-api-token")

profile = client.whoami()
sources = client.get("sources", params={"numPerPage": 10})
client.post("comment", json={"obj_id": "ZTF20abcdef", "text": "interesting"})
```

Successful responses are unwrapped to their `data` field; error responses raise
`SkyPortalError` with the server's message and HTTP status code.

## Development

The dev environment is managed with [nix](https://nixos.org) and
[uv](https://docs.astral.sh/uv/):

```sh
nix develop  # or `direnv allow` with nix-direnv
uv run pytest
uv run ruff check
uv run ty check
```
