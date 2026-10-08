# Telemetry Environment Audit

Audit date: 2026-10-08. Pi access used the approved unprivileged runtime account over the private administration link. No credentials were read, no services were changed, and no Pi files were modified.

## Repository

- Remote: `https://github.com/kovacoj/fr4nkiepi.git`.
- Visibility: public.
- Remote repository size: zero; no remote branches currently exist.
- GitHub reports `main` as the configured default branch, but it has no commit yet.
- Local `main` has no commit and contains the existing uncommitted Frankenstein implementation.
- No `gh-pages` branch exists, so there is no existing branch content to preserve.
- GitHub Pages API returns 404: Pages is not configured.
- GitHub CLI is authenticated to `github.com`; the active account has repository admin permission. No credential value was displayed or copied.
- The configured credential has broad `repo` scope. A narrower repository-scoped publisher credential is still recommended for the Pi.
- A stale, invalid authentication entry for a separate enterprise GitHub host exists locally and is unrelated to this repository.

## Raspberry Pi

- Ubuntu 26.04 LTS, ARM64, four cores.
- Memory: 3.7 GiB total, approximately 1.6 GiB available during this audit; no swap.
- Root filesystem: 28 GiB total, approximately 6.8 GiB available, 75% used.
- Hermes Agent `v0.21.6+140.g517b5e1`, upstream commit `517b5e10`, is installed from Git under `/home/frankenstein/.hermes/hermes-agent`.
- Hermes is not currently running and no Hermes user service is installed.
- Hermes has no sessions and its telemetry directory is empty, so there is no real agent usage to publish yet.
- Hermes configuration selects `anthropic/claude-opus-4.6` through an OpenRouter-compatible endpoint. This audit did not inspect or test credentials.
- Shared Hermes telemetry is disabled. Existing Hermes source includes per-call canonical token accounting, cache token buckets, reasoning tokens, estimated USD cost, pricing source/version, session persistence, `/usage`, `/insights`, API request hooks, stream hooks, and a Langfuse plugin.
- Hermes persists per-call token deltas to its session database when a session exists. Missing provider usage is explicitly represented as unavailable rather than zero.
- Existing integration seams should be used before modifying upstream Hermes: API request hooks, plugin hooks, session database usage counters, and the read-only usage/insights commands.

## Existing Pi Load

- Docker daemon is active.
- Three Uvicorn services are active; one Open WebUI process used roughly 654 MiB RSS during the audit.
- A system-level GitHub Actions runner is active under another account for a different repository. GitHub reports no runner registered to `kovacoj/fr4nkiepi`.
- These services must not be stopped or changed without operator approval. Frankie builds and tests remain on the laptop.

## Conclusions

1. Develop, test, and build on the laptop; deploy only lightweight runtime artifacts to ARM64.
2. Reuse Hermes usage accounting and hooks. Add a narrow adapter that emits phase and Frankenstein correlation IDs rather than replacing Hermes accounting.
3. Keep `/var/lib/frankenstein` as authoritative telemetry storage and publish allowlisted aggregates only.
4. Create `main` first, then create `gh-pages` as an orphan history in a separate worktree.
5. Do not report costs or live dashboard status until Hermes has produced real provider usage and the public URL has been verified.

## Current Blockers

- No Discord or confirmed working LLM session exists yet, so end-to-end usage telemetry cannot be verified.
- No narrow repository-scoped publication credential is installed on the Pi.
- GitHub Pages needs an initial `gh-pages` commit before branch-source configuration can be enabled.
- Adding swap is a privileged host change and requires explicit operator approval; it is not necessary for local development.
