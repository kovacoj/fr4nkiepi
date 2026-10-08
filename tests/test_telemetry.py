from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import pytest

from frankenstein.telemetry.events import TelemetryEvent
from frankenstein.telemetry.export import build_public_snapshots, validate_public_snapshots
from frankenstein.telemetry.storage import TelemetryStore


def llm_event(**overrides):
    values = {
        "type": "llm_request_completed",
        "phase": "execution",
        "timestamp": datetime.now(timezone.utc),
        "llm_request_id": uuid4(),
        "provider": "example",
        "model": "small-model",
        "input_tokens": 100,
        "output_tokens": 20,
        "cost_usd": Decimal("0.00125"),
        "cost_status": "estimated",
        "pricing_source": "fixture",
        "pricing_version": "2026-10-08",
        "success": True,
    }
    values.update(overrides)
    return TelemetryEvent(**values)


def test_duplicate_event_does_not_inflate_cost(tmp_path):
    store = TelemetryStore(tmp_path)
    event = llm_event()

    assert store.ingest(event) is True
    assert store.ingest(event) is False
    snapshots = build_public_snapshots(store.events())

    assert snapshots["summary.json"]["total_known_cost_usd"] == "0.00125"
    store.close()


def test_phase_costs_remain_separate(tmp_path):
    store = TelemetryStore(tmp_path)
    store.ingest(llm_event(phase="build", cost_usd=Decimal("0.2")))
    store.ingest(llm_event(phase="evaluation", cost_usd=Decimal("0.1")))
    store.ingest(llm_event(phase="execution", cost_usd=Decimal("0.05")))

    costs = build_public_snapshots(store.events())["summary.json"]["cost_usd"]

    assert costs == {"build": "0.2", "evaluation": "0.1", "execution": "0.05"}
    store.close()


def test_unknown_cost_is_not_zero():
    event = llm_event(cost_usd=None, cost_status="unknown")
    summary = build_public_snapshots([event])["summary.json"]

    assert summary["unknown_cost_events"] == 1
    assert summary["total_known_cost_usd"] == "0"


def test_public_export_rejects_synthetic_secret():
    snapshots = build_public_snapshots([])
    snapshots["evolution.json"]["events"] = [{"type": "capability", "capability_id": "sk-secretsecretsecretsecret"}]

    with pytest.raises(ValueError, match="sensitive"):
        validate_public_snapshots(snapshots)
