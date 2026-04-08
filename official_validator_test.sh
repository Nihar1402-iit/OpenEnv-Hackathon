#!/usr/bin/env bash
#
# official-validator-test.sh — Run the official Meta validator checks
#
# This script replicates the exact Meta validator requirements:
# 1. HF Space ping (/reset endpoint)
# 2. Docker build
# 3. openenv validate
#

set -uo pipefail

DOCKER_BUILD_TIMEOUT=600

if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' BOLD='' NC=''
fi

run_with_timeout() {
  local secs="$1"; shift
  if command -v timeout &>/dev/null; then
    timeout "$secs" "$@"
  elif command -v gtimeout &>/dev/null; then
    gtimeout "$secs" "$@"
  else
    "$@" &
    local pid=$!
    ( sleep "$secs" && kill "$pid" 2>/dev/null ) &
    local watcher=$!
    wait "$pid" 2>/dev/null
    local rc=$?
    kill "$watcher" 2>/dev/null
    wait "$watcher" 2>/dev/null
    return $rc
  fi
}

CLEANUP_FILES=()
cleanup() { rm -f "${CLEANUP_FILES[@]+"${CLEANUP_FILES[@]}"}"; }
trap cleanup EXIT

PING_URL="${1:-http://localhost:7860}"
REPO_DIR="${2:-.}"

if ! REPO_DIR="$(cd "$REPO_DIR" 2>/dev/null && pwd)"; then
  printf "Error: directory '%s' not found\n" "${2:-.}"
  exit 1
fi

PING_URL="${PING_URL%/}"
export PING_URL
PASS=0

log()  { printf "[%s] %b\n" "$(date -u +%H:%M:%S)" "$*"; }
pass() { log "${GREEN}✓ PASSED${NC} -- $1"; PASS=$((PASS + 1)); }
fail() { log "${RED}✗ FAILED${NC} -- $1"; }
hint() { printf "  ${YELLOW}→${NC} %b\n" "$1"; }
stop_at() {
  printf "\n"
  printf "${RED}${BOLD}Validation stopped at %s.${NC}\n" "$1"
  exit 1
}

printf "\n"
printf "${BOLD}========================================${NC}\n"
printf "${BOLD}  Official Meta Validator Test${NC}\n"
printf "${BOLD}========================================${NC}\n"
log "Repo:     $REPO_DIR"
log "Ping URL: $PING_URL"
printf "\n"

# ==============================================================================
# STEP 1: Ping HF Space (/reset endpoint)
# ==============================================================================
log "${BOLD}Step 1/3: Pinging HF Space${NC} ($PING_URL/reset) ..."

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
  -H "Content-Type: application/json" -d '{}' \
  "$PING_URL/reset" --max-time 30 2>/dev/null || printf "000")

if [ "$HTTP_CODE" = "200" ]; then
  pass "HF Space is live and responds to /reset"
elif [ "$HTTP_CODE" = "000" ]; then
  fail "HF Space not reachable (connection failed or timed out)"
  hint "Is the container running? Try: docker ps"
  hint "Or start it: docker run -d --name crm-env -p 7860:7860 <image>"
  stop_at "Step 1"
else
  fail "HF Space /reset returned HTTP $HTTP_CODE (expected 200)"
  hint "Check if the server is responding correctly"
  stop_at "Step 1"
fi

printf "\n"

# ==============================================================================
# STEP 2: Docker Build
# ==============================================================================
log "${BOLD}Step 2/3: Running docker build${NC} ..."

if ! command -v docker &>/dev/null; then
  fail "docker command not found"
  hint "Install Docker: https://docs.docker.com/get-docker/"
  stop_at "Step 2"
fi

if [ -f "$REPO_DIR/Dockerfile" ]; then
  DOCKER_CONTEXT="$REPO_DIR"
elif [ -f "$REPO_DIR/server/Dockerfile" ]; then
  DOCKER_CONTEXT="$REPO_DIR/server"
else
  fail "No Dockerfile found in repo root or server/ directory"
  stop_at "Step 2"
fi

log "  Found Dockerfile in $DOCKER_CONTEXT"

BUILD_OK=false
BUILD_OUTPUT=$(run_with_timeout "$DOCKER_BUILD_TIMEOUT" docker build -q "$DOCKER_CONTEXT" 2>&1) && BUILD_OK=true

if [ "$BUILD_OK" = true ]; then
  pass "Docker build succeeded"
else
  fail "Docker build failed (timeout=${DOCKER_BUILD_TIMEOUT}s)"
  printf "%s\n" "$BUILD_OUTPUT" | tail -10
  stop_at "Step 2"
fi

printf "\n"

# ==============================================================================
# STEP 3: openenv validate
# ==============================================================================
log "${BOLD}Step 3/3: Running openenv validate${NC} ..."

if ! command -v openenv &>/dev/null; then
  fail "openenv command not found"
  hint "Install it: pip install openenv-core"
  stop_at "Step 3"
fi

VALIDATE_OK=false
VALIDATE_OUTPUT=$(cd "$REPO_DIR" && openenv validate 2>&1) && VALIDATE_OK=true

if [ "$VALIDATE_OK" = true ]; then
  pass "openenv validate passed"
  if [ -n "$VALIDATE_OUTPUT" ]; then
    log "  $VALIDATE_OUTPUT"
  fi
else
  fail "openenv validate failed"
  printf "%s\n" "$VALIDATE_OUTPUT"
  stop_at "Step 3"
fi

printf "\n"

# ==============================================================================
# Summary
# ==============================================================================
printf "${BOLD}========================================${NC}\n"
printf "${GREEN}${BOLD}  ✓ All 3/3 checks passed!${NC}\n"
printf "${GREEN}${BOLD}  ✓ Your submission is ready to submit.${NC}\n"
printf "${BOLD}========================================${NC}\n"
printf "\n"

exit 0
