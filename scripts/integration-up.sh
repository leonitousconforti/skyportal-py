#!/usr/bin/env bash
# Boot a real SkyPortal instance for the CI test jobs.
#
# Usage (from GitHub Actions):
#   scripts/integration-up.sh image   # only ensure the docker image exists
#   scripts/integration-up.sh         # boot SkyPortal and export env vars
#
# Writes SKYPORTAL_IMAGE and SKYPORTAL_IMAGE_BUILT (image step) plus
# SKYPORTAL_TEST_URL and SKYPORTAL_TEST_TOKEN (boot step) to $GITHUB_ENV.
# SKYPORTAL_IMAGE_REPO selects the image repo for pull-through caching,
# e.g. ghcr.io/<owner>/<repo>/skyportal-web.
set -euo pipefail

: "${GITHUB_ENV:?this script is meant to run in GitHub Actions}"

SKYPORTAL_REF="aca4d4a3851c7112965e2d1b74c5e18111974429"
SKYPORTAL_DIR=".skyportal"
SKYPORTAL_IMAGE="${SKYPORTAL_IMAGE_REPO:-skyportal-web}:$SKYPORTAL_REF"
BASE_URL="http://localhost:9000"

compose() {
    (cd "$SKYPORTAL_DIR" &&
        docker compose -f docker-compose.yaml -f docker-compose.integration.yaml "$@")
}

fail() {
    echo "==> $1; recent logs:"
    compose logs --tail 100 db-init web || true
    exit 1
}

echo "==> Fetching skyportal/skyportal @ $SKYPORTAL_REF"
git init -q "$SKYPORTAL_DIR"
git -C "$SKYPORTAL_DIR" fetch -q --depth 1 https://github.com/skyportal/skyportal "$SKYPORTAL_REF"
git -C "$SKYPORTAL_DIR" checkout -q --force FETCH_HEAD

SKYPORTAL_IMAGE_BUILT=false
if ! docker pull -q "$SKYPORTAL_IMAGE"; then
    echo "==> No cached image; building $SKYPORTAL_IMAGE (~25 min)"
    (cd "$SKYPORTAL_DIR" && make docker-local DOCKER_IMAGENAME="$SKYPORTAL_IMAGE")
    SKYPORTAL_IMAGE_BUILT=true
fi
{
    echo "SKYPORTAL_IMAGE=$SKYPORTAL_IMAGE"
    echo "SKYPORTAL_IMAGE_BUILT=$SKYPORTAL_IMAGE_BUILT"
} >> "$GITHUB_ENV"
if [ "${1:-up}" = "image" ]; then
    exit 0
fi

# The upstream compose file builds `web`/`db-init` from source with no
# image name; point both at our tag instead.
cat > "$SKYPORTAL_DIR/docker-compose.integration.yaml" << EOF
services:
  web:
    image: $SKYPORTAL_IMAGE
  db-init:
    image: $SKYPORTAL_IMAGE
EOF

echo "==> Starting containers (web + postgres + valkey)"
compose up -d

echo "==> Waiting for SkyPortal at $BASE_URL"
status=000
for _ in $(seq 1 120); do
    status=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/api/sysinfo" || echo 000)
    if [ "$status" != "000" ] && [ "$status" -lt 500 ]; then
        break
    fi
    sleep 5
done
if [ "$status" = "000" ] || [ "$status" -ge 500 ]; then
    fail "SkyPortal did not come up"
fi

# On first boot the app provisions an admin user and writes their API
# token to .tokens.yaml in the app root inside the container.
echo "==> Waiting for the provisioned admin token"
TOKEN=""
for _ in $(seq 1 60); do
    TOKEN=$(compose exec -T web cat .tokens.yaml 2> /dev/null |
        awk -F': *' 'NF==2 {print $2; exit}')
    if [ -n "$TOKEN" ]; then
        break
    fi
    sleep 2
done
if [ -z "$TOKEN" ]; then
    fail "No admin token appeared in .tokens.yaml"
fi

# The app answers requests (and even writes the token) while it is still
# provisioning, returning errors like "System provisioning" or HTTP 405
# in the meantime. Only an authenticated success envelope means ready.
echo "==> Waiting for the API to finish provisioning"
ready=""
for _ in $(seq 1 120); do
    body=$(curl -s -H "Authorization: token $TOKEN" "$BASE_URL/api/internal/profile" || true)
    if printf '%s' "$body" | grep -q '"status": *"success"'; then
        ready=1
        break
    fi
    sleep 5
done
if [ -z "$ready" ]; then
    fail "The API never returned a success envelope"
fi

echo "==> SkyPortal is up at $BASE_URL"
{
    echo "SKYPORTAL_TEST_URL=$BASE_URL"
    echo "SKYPORTAL_TEST_TOKEN=$TOKEN"
} >> "$GITHUB_ENV"
