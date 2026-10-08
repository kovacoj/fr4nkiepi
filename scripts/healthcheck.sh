#!/usr/bin/env bash
set -euo pipefail

TARGET="${FRANKENSTEIN_SSH_TARGET:-frankenstein@10.42.0.152}"
ssh "$TARGET" 'systemctl --user --no-pager status frankenstein-telemetry.timer; systemctl --user --no-pager status frankenstein-telemetry.service; test -s "$HOME/.local/share/frankenstein/telemetry/system.jsonl"; test -s "$HOME/.local/share/frankenstein/database/telemetry.sqlite"'
