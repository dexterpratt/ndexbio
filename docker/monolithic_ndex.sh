#!/usr/bin/env bash
# monolithic_ndex.sh — Launch the NDEx deploy image in monolithic mode.
#
# Usage: monolithic_ndex.sh [--config <path/to/config.toml>]
#
# All five services (NDEx, PostgreSQL, Keycloak, Solr, MailHog) run in a
# single container. Config and data directories for each service are
# bind-mounted from the host so state persists across container removals.
#
# Host directories are created under the directory containing this script
# if they do not already exist. Any existing container named 'ndex' is
# removed before starting a fresh one.
#
# --config <path>  Optional TOML file with a [[users]] array of tables.
#                  Required fields per entry: id, password.
#                  Optional fields: emailAddress, firstName, lastName.
#                  Users are idempotently seeded into NDEx after the
#                  container is ready.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

CONTAINER_NAME="ndex"
IMAGE="ndexbio/ndex-rest"
BASE_URL="http://localhost:8080"
CONFIG_FILE=""

# ── Parse arguments ───────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --config)
      shift
      [[ -z "${1:-}" ]] && { echo "ERROR: --config requires a file path" >&2; exit 1; }
      CONFIG_FILE="$1"
      ;;
    *) echo "ERROR: Unknown argument: $1" >&2; exit 1 ;;
  esac
  shift
done

if [[ -n "${CONFIG_FILE}" && ! -f "${CONFIG_FILE}" ]]; then
  echo "ERROR: config file not found: ${CONFIG_FILE}" >&2; exit 1
fi

# ── Host-side paths (relative to this script) ────────────────────────────────
NDEX_CONFIG="${SCRIPT_DIR}/ndex-config"
NDEX_DATA="${SCRIPT_DIR}/ndex-data"
POSTGRES_CONFIG="${SCRIPT_DIR}/postgres-config"
POSTGRES_DATA="${SCRIPT_DIR}/postgres-data"
KEYCLOAK_CONFIG="${SCRIPT_DIR}/keycloak-config"
KEYCLOAK_DATA="${SCRIPT_DIR}/keycloak-data"
SOLR_CONFIG="${SCRIPT_DIR}/solr-config"
SOLR_DATA="${SCRIPT_DIR}/solr-data"
MAILHOG_CONFIG="${SCRIPT_DIR}/mailhog-config"

# ── Remove any existing container ────────────────────────────────────────────
echo "==> Removing existing container '${CONTAINER_NAME}' (if any)..."
docker rm -f "${CONTAINER_NAME}" 2>/dev/null || true

# ── Create host directories if they don't exist ──────────────────────────────
echo "==> Ensuring host directories exist under ${SCRIPT_DIR}..."
for dir in \
  "${NDEX_CONFIG}" \
  "${NDEX_DATA}" \
  "${POSTGRES_CONFIG}" \
  "${POSTGRES_DATA}" \
  "${KEYCLOAK_CONFIG}" \
  "${KEYCLOAK_DATA}" \
  "${SOLR_CONFIG}" \
  "${SOLR_DATA}" \
  "${MAILHOG_CONFIG}"; do
  if [[ ! -d "${dir}" ]]; then
    mkdir -p "${dir}"
    echo "    created: ${dir}"
  fi
done

# ── Launch container ──────────────────────────────────────────────────────────
echo "==> Starting container '${CONTAINER_NAME}'..."
docker run --platform linux/amd64 -d \
  --name "${CONTAINER_NAME}" \
  -p 8080:8080 \
  -v "${NDEX_CONFIG}:/apps/ndex/config" \
  -v "${NDEX_DATA}:/apps/ndex/data" \
  -v "${POSTGRES_CONFIG}:/apps/postgres/config" \
  -v "${POSTGRES_DATA}:/apps/postgres/data" \
  -v "${KEYCLOAK_CONFIG}:/apps/keycloak/config" \
  -v "${KEYCLOAK_DATA}:/apps/keycloak/data" \
  -v "${SOLR_CONFIG}:/apps/solr/config" \
  -v "${SOLR_DATA}:/apps/solr/data" \
  -v "${MAILHOG_CONFIG}:/apps/mailhog/config" \
  "${IMAGE}" \
  --ndex --postgres --keycloak --solr --mailhog

# ── Wait for NDEx to be ready ─────────────────────────────────────────────────
echo "==> NDEx started ... waiting for active port ..."
MAX_WAIT=120
ELAPSED=0
until docker logs "${CONTAINER_NAME}" 2>&1 | grep -q "NDEx Deploy Container Ready"; do
  if [[ ${ELAPSED} -ge ${MAX_WAIT} ]]; then
    echo ""
    echo "  Last 30 lines of container log:"
    docker logs "${CONTAINER_NAME}" 2>&1 | tail -30
    echo "ERROR: Container did not reach Ready state within ${MAX_WAIT}s" >&2
    exit 1
  fi
  echo "    ... still initializing (${ELAPSED}s elapsed)"
  sleep 5
  ELAPSED=$((ELAPSED + 5))
done
echo "==> NDEx is ready!"
echo "    NDEx REST: ${BASE_URL}"

# ── Seed users from config (if provided) ─────────────────────────────────────
if [[ -n "${CONFIG_FILE}" ]]; then
  echo "==> Seeding users from ${CONFIG_FILE}..."

  # Parse [[users]] array-of-tables and upsert each user.
  # Uses a while-read loop (bash 3.2 compatible — no mapfile required).
  while IFS=$'\t' read -r uid upass uemail ufname ulname; do
    # Apply defaults for optional fields
    [[ -z "${uemail}" ]] && uemail="${uid}@ndex.local"
    [[ -z "${ufname}" ]] && ufname="NDEx"
    [[ -z "${ulname}" ]] && ulname="User"

    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/v2/user" \
      -H "Content-Type: application/json" \
      -d "{
        \"userName\": \"${uid}\",
        \"password\": \"${upass}\",
        \"emailAddress\": \"${uemail}\",
        \"firstName\": \"${ufname}\",
        \"lastName\": \"${ulname}\"
      }")
    HTTP_CODE=$(echo "${RESPONSE}" | tail -1)

    case "${HTTP_CODE}" in
      201) echo "    user '${uid}': created" ;;
      409) echo "    user '${uid}': exists" ;;
      *)
        BODY=$(echo "${RESPONSE}" | head -1)
        echo "ERROR: Failed to upsert user '${uid}' — HTTP ${HTTP_CODE}: ${BODY:0:200}" >&2
        exit 1
        ;;
    esac
  done < <(awk '
    /^\[\[users\]\]/ {
      if (id != "" && pass != "") print id "\t" pass "\t" email "\t" fname "\t" lname
      id = ""; pass = ""; email = ""; fname = ""; lname = ""
      in_users = 1; next
    }
    /^\[/ && !/^\[\[users\]\]/ { in_users = 0 }
    in_users && /^id[[:space:]]*=/ {
      v = $0; sub(/^id[[:space:]]*=[[:space:]]*"/, "", v); sub(/".*/, "", v); id = v
    }
    in_users && /^password[[:space:]]*=/ {
      v = $0; sub(/^password[[:space:]]*=[[:space:]]*"/, "", v); sub(/".*/, "", v); pass = v
    }
    in_users && /^emailAddress[[:space:]]*=/ {
      v = $0; sub(/^emailAddress[[:space:]]*=[[:space:]]*"/, "", v); sub(/".*/, "", v); email = v
    }
    in_users && /^firstName[[:space:]]*=/ {
      v = $0; sub(/^firstName[[:space:]]*=[[:space:]]*"/, "", v); sub(/".*/, "", v); fname = v
    }
    in_users && /^lastName[[:space:]]*=/ {
      v = $0; sub(/^lastName[[:space:]]*=[[:space:]]*"/, "", v); sub(/".*/, "", v); lname = v
    }
    END { if (id != "" && pass != "") print id "\t" pass "\t" email "\t" fname "\t" lname }
  ' "${CONFIG_FILE}")

  echo "==> User seeding complete."
fi
