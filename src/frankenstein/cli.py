from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .contracts import CapabilityManifest
from .registry import Registry
from .runtime import execute
from .verifier import verify_issue_risk, verify_readiness, verify_release_normalize


ROOT = Path(__file__).resolve().parents[2]
FIXTURES_DIR = ROOT / "fixtures"
CAPABILITIES = {
    "repo.release_normalize": (
        ROOT / "capabilities/repo.release_normalize/1.0.0/manifest.json",
        verify_release_normalize,
    ),
    "repo.issue_risk": (
        ROOT / "capabilities/repo.issue_risk/1.0.0/manifest.json",
        verify_issue_risk,
    ),
    "release_readiness.compose": (
        ROOT / "capabilities/release_readiness.compose/1.0.0/manifest.json",
        verify_readiness,
    ),
}


def _database_path() -> Path:
    return Path(os.environ.get("FRANKENSTEIN_DB", ROOT / ".frankenstein/registry.db"))


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text())


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="frankenstein")
    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("inspect")

    capability = subcommands.add_parser("capability")
    operations = capability.add_subparsers(dest="operation", required=True)
    search = operations.add_parser("search")
    search.add_argument("query")
    describe = operations.add_parser("describe")
    describe.add_argument("id")
    build = operations.add_parser("build")
    build.add_argument("--request", required=True)
    verify = operations.add_parser("verify")
    verify.add_argument("id")
    listing = operations.add_parser("list")
    listing.add_argument("--status")
    run = operations.add_parser("execute")
    run.add_argument("id")
    run.add_argument("--input", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = Registry(_database_path())
    try:
        if args.command == "inspect":
            _print({"database": str(_database_path()), "capabilities": registry.list()})
            return 0
        if args.operation == "search":
            _print(registry.search(args.query))
        elif args.operation == "describe":
            _print(registry.get(args.id))
        elif args.operation == "list":
            _print(registry.list(args.status))
        elif args.operation == "build":
            request = _load_json(args.request)
            capability_id = request.get("capability_id")
            if capability_id not in CAPABILITIES:
                raise ValueError("no approved builder template satisfies this request")
            manifest_path, _ = CAPABILITIES[capability_id]
            manifest = CapabilityManifest.model_validate(_load_json(manifest_path))
            digest = registry.register_candidate(manifest)
            _print({"id": manifest.id, "version": manifest.version, "status": "candidate", "sha256": digest})
        elif args.operation == "verify":
            if args.id not in CAPABILITIES:
                raise ValueError("no independent verifier is registered for this capability")
            manifest_path, verifier = CAPABILITIES[args.id]
            manifest = CapabilityManifest.model_validate(_load_json(manifest_path))
            candidate = registry.get(args.id, manifest.version)
            if candidate["status"] != "candidate":
                raise ValueError("capability is not awaiting verification")
            verifier(FIXTURES_DIR)
            registry.mark_tested(args.id, manifest.version)
            registry.activate(args.id, manifest.version)
            _print({"id": args.id, "version": manifest.version, "status": "active", "verification": "passed"})
        elif args.operation == "execute":
            _print(execute(registry, args.id, _load_json(args.input)))
        return 0
    finally:
        registry.close()


if __name__ == "__main__":
    raise SystemExit(main())
