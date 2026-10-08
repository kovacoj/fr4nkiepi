#!/usr/bin/env bash
set -euo pipefail

TARGET="${FRANKENSTEIN_SSH_TARGET:-frankenstein@10.42.0.152}"
REMOTE_ROOT="${FRANKENSTEIN_REMOTE_ROOT:-.local/share/frankenstein}"

ssh "$TARGET" "mkdir -p \"\$HOME/$REMOTE_ROOT/runtime\" \"\$HOME/.config/systemd/user\""
rsync -az --delete \
  --exclude .git --exclude .venv --exclude .env --exclude __pycache__ \
  pyproject.toml uv.lock src deploy/systemd \
  "$TARGET:$REMOTE_ROOT/runtime/"
ssh "$TARGET" "python3 -m venv \"\$HOME/$REMOTE_ROOT/runtime/.venv\" && \"\$HOME/$REMOTE_ROOT/runtime/.venv/bin/pip\" install --disable-pip-version-check --no-cache-dir \"\$HOME/$REMOTE_ROOT/runtime\""
ssh "$TARGET" "cp \"\$HOME/$REMOTE_ROOT/runtime/systemd/\"* \"\$HOME/.config/systemd/user/\" && systemctl --user daemon-reload && systemctl --user enable --now frankenstein-telemetry.timer && systemctl --user start frankenstein-telemetry.service"
