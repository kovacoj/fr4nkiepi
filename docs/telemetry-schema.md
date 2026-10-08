# Capability Registry And Evidence Schema

## Capability Manifest

`CapabilityManifest` in `src/frankenstein/contracts.py` is the canonical registry contract.

| Field | Meaning |
| --- | --- |
| `id` | Stable namespaced identifier |
| `name` | Human-readable name safe for aggregate display |
| `version` | Immutable semantic version |
| `kind` | Skill, MCP proxy, executable tool, Python adapter, or workflow |
| `domain` | `task` or `capability_management`; required to prove harness evolution separately |
| `summary` | Bounded description |
| `entrypoint` | Runtime allowlist key; never dynamically imported |
| `input_schema` / `output_schema` | Typed composition boundary |
| `requires` | Exact `id@version` dependency pins |
| `permissions` | Declared network, filesystem, and secret requirements |
| `provenance` | Origin, source revision, artifact hash, license, and generating execution |
| `verification` | Independent suite and required regression/permission checks |
| `created_at` | UTC creation timestamp |

The registry computes a separate SHA-256 over the canonical manifest. The provenance artifact hash identifies implementation content, not the manifest itself.

## SQLite Tables

### `capability_versions`

One immutable manifest per `(id, version)`, lifecycle status, one-active-version constraint, manifest hash, and installation/activation timestamps.

### `lifecycle_events`

Append-only transitions with stable event ID, capability/version, prior state, next state, optional execution correlation, and timestamp.

### `verification_runs`

Independent suite, pass/fail result, tested artifact hash, optional execution correlation, and timestamp. Activation requires the registry state to be `tested`; a candidate cannot activate directly.

## Lifecycle

The current executable subset is `candidate -> tested -> active -> deprecated|revoked`. Public telemetry uses the richer vocabulary `discovered -> candidate -> testing -> verified -> installed -> active`, plus `rejected`, `deprecated`, and `rolled_back`. Mapping between internal atomic transitions and public states must be explicit in the aggregator.

## Invariants

1. One active version per capability ID.
2. Every dependency is pinned and active before workflow activation.
3. Dependency cycles are rejected.
4. Runtime entrypoints are selected from a server-owned allowlist.
5. Every node's permissions are checked during composed execution.
6. Generated management capabilities use `domain=capability_management` and cannot be substituted by an ordinary task capability for qualification.
7. Verification references the same artifact hash that is promoted.
8. Capability code is global; user/session data is not stored in capability metadata.

## Correlation IDs

Telemetry events will carry separate optional IDs for task, private session, agent execution, subagent execution, capability/version, tool invocation, LLM request, and evaluation. Public exports omit private session and user identifiers and expose only aggregate counts or pseudonymous demonstration scenario labels.
