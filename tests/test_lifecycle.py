import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from frankenstein.contracts import CapabilityManifest
from frankenstein.registry import Registry
from frankenstein.runtime import execute


ROOT = Path(__file__).resolve().parents[1]


def test_candidate_cannot_execute_before_activation(tmp_path):
    registry = Registry(tmp_path / "registry.db")
    manifest = CapabilityManifest.model_validate_json(
        (ROOT / "capabilities/repo.release_normalize/1.0.0/manifest.json").read_text()
    )
    registry.register_candidate(manifest)

    with pytest.raises(KeyError):
        execute(registry, manifest.id, {"repository": "x/y", "releases": []})
    registry.close()


def test_unapproved_entrypoint_is_denied(tmp_path):
    registry = Registry(tmp_path / "registry.db")
    raw = json.loads((ROOT / "capabilities/repo.release_normalize/1.0.0/manifest.json").read_text())
    raw["id"] = "malicious.capability"
    raw["entrypoint"] = "os:system"
    manifest = CapabilityManifest.model_validate(raw)
    registry.register_candidate(manifest)
    registry.mark_tested(manifest.id, manifest.version)
    registry.activate(manifest.id, manifest.version)

    with pytest.raises(PermissionError, match="not approved"):
        execute(registry, manifest.id, {})
    registry.close()


def test_candidate_cannot_bypass_verification(tmp_path):
    registry = Registry(tmp_path / "registry.db")
    manifest = CapabilityManifest.model_validate_json(
        (ROOT / "capabilities/repo.release_normalize/1.0.0/manifest.json").read_text()
    )
    registry.register_candidate(manifest)

    with pytest.raises(ValueError, match="verified candidate"):
        registry.activate(manifest.id, manifest.version)
    registry.close()


def test_fresh_process_reuses_active_capability(tmp_path):
    database = tmp_path / "registry.db"
    environment = {**os.environ, "FRANKENSTEIN_DB": str(database)}

    for arguments in [
        ["capability", "build", "--request", str(ROOT / "fixtures/alice_request.json")],
        ["capability", "verify", "repo.release_normalize"],
    ]:
        subprocess.run([sys.executable, "-m", "frankenstein.cli", *arguments], check=True, env=environment)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "frankenstein.cli",
            "capability",
            "execute",
            "repo.release_normalize",
            "--input",
            str(ROOT / "fixtures/releases.json"),
        ],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert json.loads(completed.stdout)["release_count"] == 2


def test_composition_requires_active_dependencies(tmp_path):
    registry = Registry(tmp_path / "registry.db")
    manifest = CapabilityManifest.model_validate_json(
        (ROOT / "capabilities/release_readiness.compose/1.0.0/manifest.json").read_text()
    )
    registry.register_candidate(manifest)
    registry.mark_tested(manifest.id, manifest.version)

    with pytest.raises(ValueError, match="missing dependency"):
        registry.activate(manifest.id, manifest.version)
    registry.close()


def test_fresh_process_executes_registered_composition(tmp_path):
    database = tmp_path / "registry.db"
    environment = {**os.environ, "FRANKENSTEIN_DB": str(database)}
    requests = ["alice_request.json", "bob_request.json", "charlie_request.json"]
    capability_ids = ["repo.release_normalize", "repo.issue_risk", "release_readiness.compose"]

    for request, capability_id in zip(requests, capability_ids, strict=True):
        subprocess.run(
            [sys.executable, "-m", "frankenstein.cli", "capability", "build", "--request", str(ROOT / "fixtures" / request)],
            check=True,
            capture_output=True,
            env=environment,
        )
        subprocess.run(
            [sys.executable, "-m", "frankenstein.cli", "capability", "verify", capability_id],
            check=True,
            capture_output=True,
            env=environment,
        )

    completed = subprocess.run(
        [sys.executable, "-m", "frankenstein.cli", "capability", "execute", "release_readiness.compose", "--input", str(ROOT / "fixtures/readiness.json")],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert json.loads(completed.stdout) == {
        "blocker_count": 1,
        "latest_release": "v1.1.0",
        "repository": "example/widgets",
        "status": "blocked",
        "summary": "Release blocked by 1 high-risk open issue(s).",
    }
