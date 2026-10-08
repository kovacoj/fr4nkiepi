from frankenstein.telemetry.export import build_public_snapshots
from frankenstein.telemetry.system import collect_system_event


def test_system_sample_uses_public_aggregate_fields(tmp_path):
    event = collect_system_event(tmp_path)
    sample = build_public_snapshots([event])["system.json"]["samples"][0]

    assert 0 <= event.memory_used_percent <= 100
    assert 0 <= event.disk_used_percent <= 100
    assert set(sample) == {
        "timestamp", "cpu_percent", "load_1m", "memory_used_percent",
        "disk_used_percent", "disk_free_gib", "temperature_c",
        "uptime_seconds", "hermes_running",
    }
