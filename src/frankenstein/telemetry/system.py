from __future__ import annotations

import json
import os
from decimal import Decimal
from pathlib import Path

from .events import TelemetryEvent


def _memory() -> dict[str, int]:
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, value = line.split(":", 1)
        values[key] = int(value.strip().split()[0]) * 1024
    return values


def _cpu_percent(state_path: Path) -> Decimal | None:
    fields = [int(value) for value in Path("/proc/stat").read_text().splitlines()[0].split()[1:]]
    idle = fields[3] + fields[4]
    total = sum(fields)
    previous = None
    if state_path.exists():
        try:
            previous = json.loads(state_path.read_text())
        except (json.JSONDecodeError, OSError):
            previous = None
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps({"idle": idle, "total": total}))
    os.replace(temporary, state_path)
    if not previous or total <= previous["total"]:
        return None
    total_delta = total - previous["total"]
    idle_delta = idle - previous["idle"]
    return (Decimal(100) * Decimal(total_delta - idle_delta) / Decimal(total_delta)).quantize(Decimal("0.1"))


def collect_system_event(state_dir: Path) -> TelemetryEvent:
    state_dir.mkdir(parents=True, exist_ok=True)
    memory = _memory()
    total_memory = memory["MemTotal"]
    available_memory = memory["MemAvailable"]
    swap_total = memory.get("SwapTotal", 0)
    swap_free = memory.get("SwapFree", 0)
    disk = os.statvfs("/")
    disk_total = disk.f_blocks * disk.f_frsize
    disk_free = disk.f_bavail * disk.f_frsize
    temperature_path = Path("/sys/class/thermal/thermal_zone0/temp")
    temperature = Decimal(temperature_path.read_text().strip()) / 1000 if temperature_path.exists() else None
    hermes_running = False
    for path in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            arguments = path.read_bytes().split(b"\0")
        except (OSError, PermissionError):
            continue
        if any(Path(argument.decode(errors="ignore")).name == "hermes" for argument in arguments if argument):
            hermes_running = True
            break
    return TelemetryEvent(
        type="system_sample",
        phase="system",
        cpu_percent=_cpu_percent(state_dir / "cpu.json"),
        load_1m=Decimal(str(os.getloadavg()[0])).quantize(Decimal("0.01")),
        memory_used_percent=(Decimal(100) * Decimal(total_memory - available_memory) / Decimal(total_memory)).quantize(Decimal("0.1")),
        memory_available_bytes=available_memory,
        swap_used_percent=(Decimal(100) * Decimal(swap_total - swap_free) / Decimal(swap_total)).quantize(Decimal("0.1")) if swap_total else Decimal(0),
        disk_used_percent=(Decimal(100) * Decimal(disk_total - disk_free) / Decimal(disk_total)).quantize(Decimal("0.1")),
        disk_free_bytes=disk_free,
        temperature_c=temperature,
        uptime_seconds=int(float(Path("/proc/uptime").read_text().split()[0])),
        hermes_running=hermes_running,
    )
