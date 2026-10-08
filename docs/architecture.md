# Architecture

The laptop is the development and test machine. The Raspberry Pi is the always-on ARM64 runtime. Hosted providers perform inference; external APIs provide discovery data. No model runs locally on the Pi.

`main` contains the control plane, telemetry implementation, tests, deployment definitions, and documentation. The orphan `gh-pages` branch has independent history and contains only static assets plus sanitized JSON snapshots.

The Pi is authoritative for operational telemetry. Append-only JSONL and SQLite live outside Git under the runtime account's local data directory. GitHub Pages is a delayed, read-only projection and has no route back to Hermes or the Pi.

Hermes remains upstream and supplies Discord, hosted model transports, usage normalization, pricing, sessions, and plugin hooks. Frankenstein supplies capability lifecycle, composition, qualification evidence, phase attribution, private telemetry persistence, and public aggregation.
