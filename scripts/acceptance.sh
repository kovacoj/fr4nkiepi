#!/usr/bin/env bash
set -euo pipefail

ROOT="$(realpath "$(dirname "${BASH_SOURCE[0]}")/..")"
DB="$(mktemp --suffix=.db)"
trap 'rm -f "$DB" "$DB-shm" "$DB-wal"' EXIT
export FRANKENSTEIN_DB="$DB"

python -m frankenstein.cli capability build --request "$ROOT/fixtures/alice_request.json"
python -m frankenstein.cli capability verify repo.release_normalize
python -m frankenstein.cli capability build --request "$ROOT/fixtures/bob_request.json"
python -m frankenstein.cli capability verify repo.issue_risk
python -m frankenstein.cli capability build --request "$ROOT/fixtures/charlie_request.json"
python -m frankenstein.cli capability verify release_readiness.compose
python -m frankenstein.cli capability search 'release'
python -m frankenstein.cli capability execute repo.release_normalize --input "$ROOT/fixtures/releases.json"

# Separate interpreters prove registry-backed cross-process composition and reuse.
python -m frankenstein.cli capability execute release_readiness.compose --input "$ROOT/fixtures/readiness.json"
python -m frankenstein.cli capability list --status active
