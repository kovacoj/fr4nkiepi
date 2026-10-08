# Frankenstein Control Plane

Minimal local vertical slice for a persistent, test-gated capability registry. It proves that a missing capability can be registered as a candidate, independently verified, activated, and reused by a fresh process without gaining authority.

## Local Setup

```bash
uv sync --extra test
uv run pytest -q
uv run bash scripts/acceptance.sh
```

The acceptance flow uses a temporary SQLite database. Normal CLI use persists to `.frankenstein/registry.db`:

```bash
uv run python -m frankenstein.cli capability build --request fixtures/alice_request.json
uv run python -m frankenstein.cli capability verify repo.release_normalize
uv run python -m frankenstein.cli capability execute repo.release_normalize --input fixtures/releases.json
```

## Security Boundary

The current runtime executes only active registry versions and maps approved entrypoint names to functions in code. It never dynamically imports a manifest-provided entrypoint. The included capability requires no network, filesystem, or secret permissions; any non-empty requested permission is denied.

## Current Scope

Implemented: SQLite WAL registry, manifest validation, lifecycle gating, deterministic release normalization, held-out verification, search/describe/list/execute CLI operations, and fresh-process reuse.

Also implemented: deterministic issue-risk classification, a pinned dependency DAG for release-readiness composition, cycle/missing-dependency checks, and a fixed MCP server exposing only search, describe, list, and execute.

Run the stdio MCP dispatcher with:

```bash
FRANKENSTEIN_DB=/absolute/path/to/registry.db uv run frankenstein-mcp
```

Lifecycle mutations remain operator-only CLI operations and are deliberately absent from MCP. The SDK-level integration test connects an official MCP client directly to the server, lists its fixed tools, and executes a registered capability.

Deferred: Hermes configuration and live integration, Discord, external discovery, generated code sandboxing, multi-user queues, telemetry, and Pi deployment. These should follow only after this local slice remains green.
