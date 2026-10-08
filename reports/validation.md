# Validation Log

## 2026-10-08: Local Lifecycle Vertical Slice

Environment: laptop, CPython 3.13.6 managed by uv.

Commands:

```bash
uv sync --extra test
uv run pytest -q
uv run bash scripts/acceptance.sh
uv run python -m compileall -q src tests
```

Results:

- Unit/integration suite: 6 passed in 1.24 seconds.
- Python bytecode compilation: passed.
- Candidate registration: passed; manifest SHA-256 recorded by registry.
- Held-out deterministic verification: passed.
- Candidate-to-active bypass test: passed; direct activation is denied.
- Unapproved dynamic entrypoint test: passed; execution is denied.
- Active capability search and execution: passed.
- Fresh interpreter process reused the SQLite-registered active capability: passed.
- Capability permissions are empty; no network, filesystem, or secret authority was added.

This first run validated the local registry-backed lifecycle only. The subsequent run below adds local composition and an MCP protocol surface.

## 2026-10-08: Composition and MCP Dispatcher

Commands:

```bash
uv sync --extra test
uv run pytest -q
uv run bash scripts/acceptance.sh
uv run python -m compileall -q src tests
```

Results:

- Unit/integration suite: 10 passed in 5.08 seconds.
- Two deterministic adapters and one workflow passed separate held-out fixtures.
- Missing active dependencies prevent workflow activation.
- Dependency versions are pinned and checked again during execution.
- A fresh interpreter resolved and executed the active release-readiness DAG without direct calls from the demo script.
- The composed permission check is deny-by-default at every DAG node.
- Official MCP Python SDK 2.3.0 client connected in process, listed exactly four fixed tools, and executed an active capability with structured output.
- MCP exposes search, describe, list, and execute only. Build, verify, activation, and rollback are not remotely exposed.

The MCP protocol surface is locally tested, but Hermes has not yet been configured to launch it. Discord, live repository discovery, telemetry, generated-code isolation, and Pi deployment remain unimplemented.

## 2026-10-08: Telemetry And Pages Foundation

- Automated suite: 24 passed.
- Static Pages tree validator: passed.
- JavaScript syntax check: passed.
- All seven public feeds parsed as valid JSON.
- `main` and `gh-pages` were created as independent root histories.
- Remote `gh-pages` tree contains only the eleven approved static files.
- GitHub Pages branch source is `gh-pages` at `/`, with HTTPS enforced.
- Initial live page and relative summary feed returned HTTP 200.
- Pi system telemetry timer deployed and active; collection service exited successfully with approximately 21 MiB peak memory.
- Pi JSONL and SQLite telemetry files exist outside Git.
- A sanitized snapshot containing real Pi load, memory, disk, temperature, uptime, and Hermes-running state was exported and pushed.

Still unverified: Hermes provider calls and costs, Discord, autonomous capability generation, management-layer self-extension, automatic Pi-to-GitHub publication, retention/log rotation, logout/reboot recovery, and the mandatory end-to-end qualification gates.
