from __future__ import annotations

import argparse
import os
from pathlib import Path

from .export import build_public_snapshots, write_public_snapshots
from .storage import TelemetryStore
from .system import collect_system_event


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("sample-system", "export"))
    parser.add_argument("--root", default=os.environ.get("FRANKENSTEIN_STATE", str(Path.home() / ".local/share/frankenstein")))
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    root = Path(args.root)
    store = TelemetryStore(root)
    try:
        if args.command == "sample-system":
            store.ingest(collect_system_event(root / "state"))
        else:
            if not args.output:
                parser.error("export requires --output")
            write_public_snapshots(build_public_snapshots(store.events()), Path(args.output))
    finally:
        store.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
