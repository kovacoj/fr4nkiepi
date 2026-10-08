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

## Hermes Gateway

```bash
hermes gateway status
journalctl --user -u hermes-gateway.service -n 100 --no-pager
```

The gateway is managed by Hermes' generated user service and systemd lingering is enabled. Do not launch a second foreground gateway while this service is active.

Voice-channel playback additionally needs system Opus on the Pi:

```bash
sudo apt-get install -y libopus0
hermes gateway restart
```

Hermes already supplies its managed ARM64 FFmpeg binary. Do not install unrelated desktop audio packages.
