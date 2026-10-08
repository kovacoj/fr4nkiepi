from __future__ import annotations

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any

from .events import TelemetryEvent


PUBLIC_FILES = {
    "summary.json", "timeseries.json", "models.json", "capabilities.json",
    "executions.json", "evolution.json", "system.json",
}
SENSITIVE = re.compile(
    r"(?i)(gh[pousr]_[a-z0-9]{20,}|sk-[a-z0-9_-]{16,}|api[_-]?key|discord[_-]?bot[_-]?token|"
    r"/home/|/root/|\.ssh|10\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)"
)


def build_public_snapshots(events: list[TelemetryEvent]) -> dict[str, Any]:
    generated_at = datetime.now(timezone.utc).isoformat()
    costs = defaultdict(Decimal)
    unknown_cost_events = 0
    models: dict[tuple[str, str], dict[str, Any]] = {}
    capabilities: dict[tuple[str, str], dict[str, Any]] = {}
    event_counts = Counter(event.type for event in events)

    for event in events:
        if event.cost_status == "unknown":
            unknown_cost_events += 1
        elif event.cost_usd is not None:
            costs[event.phase] += event.cost_usd
        if event.provider and event.model:
            key = (event.provider, event.model)
            item = models.setdefault(key, {"provider": key[0], "model": key[1], "requests": 0, "cost_usd": Decimal(0), "input_tokens": 0, "output_tokens": 0})
            item["requests"] += 1
            item["cost_usd"] += event.cost_usd or Decimal(0)
            item["input_tokens"] += event.input_tokens or 0
            item["output_tokens"] += event.output_tokens or 0
        if event.capability_id and event.capability_version:
            key = (event.capability_id, event.capability_version)
            item = capabilities.setdefault(key, {"id": key[0], "version": key[1], "invocations": 0, "successes": 0, "failures": 0})
            if event.type == "capability_invoked":
                item["invocations"] += 1
                item["successes" if event.success else "failures"] += 1

    total_known = sum(costs.values(), Decimal(0))
    snapshots = {
        "summary.json": {
            "generated_at": generated_at,
            "cost_usd": {phase: str(costs[phase]) for phase in ("build", "evaluation", "execution")},
            "total_known_cost_usd": str(total_known),
            "unknown_cost_events": unknown_cost_events,
            "installed_capabilities": event_counts["capability_registered"],
            "completed_tasks": event_counts["task_completed"] + event_counts["composition_task_completed"],
        },
        "timeseries.json": {"generated_at": generated_at, "points": []},
        "models.json": {"generated_at": generated_at, "models": list(models.values())},
        "capabilities.json": {"generated_at": generated_at, "capabilities": list(capabilities.values())},
        "executions.json": {"generated_at": generated_at, "executions": []},
        "evolution.json": {
            "generated_at": generated_at,
            "events": [
                {"timestamp": event.timestamp.isoformat(), "type": event.type, "capability_id": event.capability_id, "capability_version": event.capability_version}
                for event in events[-100:]
                if event.type.startswith("capability_") or event.type.startswith("management_")
            ],
        },
        "system.json": {"generated_at": generated_at, "samples": []},
    }
    return json.loads(json.dumps(snapshots, default=str))


def validate_public_snapshots(snapshots: dict[str, Any]) -> None:
    if set(snapshots) != PUBLIC_FILES:
        raise ValueError("public snapshot file set does not match allowlist")
    encoded = json.dumps(snapshots, sort_keys=True)
    if SENSITIVE.search(encoded):
        raise ValueError("public snapshots contain sensitive-looking content")


def write_public_snapshots(snapshots: dict[str, Any], destination: Path) -> None:
    validate_public_snapshots(snapshots)
    destination.mkdir(parents=True, exist_ok=True)
    for filename, value in snapshots.items():
        temporary = destination / f".{filename}.tmp"
        temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
        os.replace(temporary, destination / filename)
