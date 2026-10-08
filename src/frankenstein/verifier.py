from __future__ import annotations

import json
from pathlib import Path
from typing import Callable

from .issue_risk import run as run_issue_risk
from .release_normalize import run
from .release_readiness import run as run_release_readiness


def verify_release_normalize(fixtures_dir: Path) -> None:
    verify_cases(fixtures_dir / "release_normalize_held_out.json", run)


def verify_cases(path: Path, function: Callable[[dict], dict]) -> None:
    cases = json.loads(path.read_text())
    for case in cases:
        actual = function(case["input"])
        if actual != case["expected"]:
            raise AssertionError(f"held-out case failed: {case['name']}")


def verify_issue_risk(fixtures_dir: Path) -> None:
    verify_cases(fixtures_dir / "issue_risk_held_out.json", run_issue_risk)


def verify_readiness(fixtures_dir: Path) -> None:
    cases = json.loads((fixtures_dir / "readiness_held_out.json").read_text())
    for case in cases:
        actual = run_release_readiness(case["input"], case["dependencies"])
        if actual != case["expected"]:
            raise AssertionError(f"held-out case failed: {case['name']}")
