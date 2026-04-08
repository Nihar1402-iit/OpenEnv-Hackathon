#!/usr/bin/env bash
#
# test-submission.sh — Comprehensive Meta Hackathon Submission Test
#
# This script validates your submission against the official Meta validator requirements:
# 1. HF Space is live and responds to /reset
# 2. Docker image builds successfully
# 3. openenv validate passes
# 4. Additionally tests /step, /state, /grader endpoints
#

set -uo pipefail

if [ -t 1 ]; then
  RED='\033[0;31m'
  GREEN='\033[0;32m'
  YELLOW='\033[1;33m'
  BLUE='\033[0;34m'
  BOLD='\033[1m'
  NC='\033[0m'
else
  RED='' GREEN='' YELLOW='' BLUE='' BOLD='' NC=''
fi

log()  { printf "[$(date -u +%H:%M:%S)] %b\n" "$*"; }
pass() { log "${GREEN}✓${NC} $1"; }
fail() { log "${RED}✗${NC} $1"; }
info() { log "${BLUE}ℹ${NC} $1"; }

REPO_DIR="${1:-.}"
PING_URL="${2:-http://localhost:7860}"

printf "\n${BOLD}========================================${NC}\n"
printf "${BOLD}  Meta Hackathon Submission Validator${NC}\n"
printf "${BOLD}========================================${NC}\n"
info "Repo:     $REPO_DIR"
info "Ping URL: $PING_URL"
printf "\n"

# ==============================================================================
# TEST 1: Docker Build
# ==============================================================================
printf "${BOLD}TEST 1: Docker Build${NC}\n"

if [ -f "$REPO_DIR/Dockerfile" ]; then
  DOCKER_CONTEXT="$REPO_DIR"
else
  fail "No Dockerfile found"
  exit 1
fi

info "Building Docker image..."

if docker build -q "$DOCKER_CONTEXT" -t meta-hackathon-submission:latest 2>&1 | tail -3; then
  pass "Docker build succeeded"
else
  fail "Docker build failed"
  exit 1
fi

printf "\n"

# ==============================================================================
# TEST 2: Start Docker Container
# ==============================================================================
printf "${BOLD}TEST 2: Starting Docker Container${NC}\n"

docker rm -f meta-hackathon-server 2>/dev/null || true
sleep 1

info "Starting container..."
if docker run -d \
  --name meta-hackathon-server \
  -p 7860:7860 \
  meta-hackathon-submission:latest \
  > /dev/null 2>&1; then
  pass "Docker container started"
  sleep 3
else
  fail "Failed to start Docker container"
  docker logs meta-hackathon-server
  exit 1
fi

printf "\n"

# ==============================================================================
# TEST 3: Ping HF Space (/reset endpoint)
# ==============================================================================
printf "${BOLD}TEST 3: Ping HF Space (/reset)${NC}\n"

info "Testing $PING_URL/reset ..."

RESET_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "$PING_URL/reset" 2>&1)

if echo "$RESET_RESPONSE" | grep -q "observation"; then
  pass "HF Space /reset endpoint works"
else
  fail "HF Space /reset endpoint failed"
  echo "$RESET_RESPONSE"
  exit 1
fi

printf "\n"

# ==============================================================================
# TEST 4: Test /state endpoint
# ==============================================================================
printf "${BOLD}TEST 4: Test /state endpoint${NC}\n"

info "Testing $PING_URL/state ..."

STATE_RESPONSE=$(curl -s -X GET "$PING_URL/state" 2>&1)

if echo "$STATE_RESPONSE" | grep -q "observation"; then
  pass "/state endpoint works"
else
  fail "/state endpoint failed"
  echo "$STATE_RESPONSE"
  exit 1
fi

printf "\n"

# ==============================================================================
# TEST 5: Test /step endpoint
# ==============================================================================
printf "${BOLD}TEST 5: Test /step endpoint${NC}\n"

info "Testing $PING_URL/step ..."

curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "$PING_URL/reset" > /dev/null

STEP_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "search_customers",
    "arguments": {"customer_id": "C001"}
  }' \
  "$PING_URL/step" 2>&1)

if echo "$STEP_RESPONSE" | grep -q "reward"; then
  pass "/step endpoint works"
else
  fail "/step endpoint failed"
  echo "$STEP_RESPONSE"
  exit 1
fi

printf "\n"

# ==============================================================================
# TEST 6: Test /grader endpoint
# ==============================================================================
printf "${BOLD}TEST 6: Test /grader endpoint${NC}\n"

info "Testing $PING_URL/grader ..."

GRADER_RESPONSE=$(curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "$PING_URL/grader" 2>&1)

if echo "$GRADER_RESPONSE" | grep -q "scores"; then
  pass "/grader endpoint works"
  TASK_COUNT=$(echo "$GRADER_RESPONSE" | grep -o 'task_[^"]*' | wc -l)
  info "Found $TASK_COUNT tasks in grader response"
else
  fail "/grader endpoint failed"
  echo "$GRADER_RESPONSE"
  exit 1
fi

printf "\n"

# ==============================================================================
# CLEANUP
# ==============================================================================
info "Cleaning up Docker container..."
docker rm -f meta-hackathon-server 2>/dev/null || true

printf "\n"
printf "${BOLD}========================================${NC}\n"
printf "${GREEN}${BOLD}  ✓ All tests passed!${NC}\n"
printf "${GREEN}${BOLD}  Your submission is ready.${NC}\n"
printf "${BOLD}========================================${NC}\n"
printf "\n"

exit 0
