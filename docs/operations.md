# Operations

## Local Validation

```bash
uv sync --extra test
uv run pytest -q
uv run bash scripts/acceptance.sh
```

## Pi Deployment

```bash
bash scripts/deploy-rpi.sh
bash scripts/healthcheck.sh
```

The deploy script copies source and systemd definitions, creates an isolated venv, and starts one lightweight user timer. It does not overwrite `~/.hermes`, restart Hermes, use Docker, or alter networking.

## Service Checks

```bash
systemctl --user status frankenstein-telemetry.timer
systemctl --user status frankenstein-telemetry.service
journalctl --user -u frankenstein-telemetry.service -n 100 --no-pager
```

Structured telemetry is under `~/.local/share/frankenstein/telemetry`; SQLite is under `~/.local/share/frankenstein/database`. Remove or rollback the user units independently of Hermes. User services require lingering to survive the last logout; enabling it is an administrator action.
