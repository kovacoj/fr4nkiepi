#!/usr/bin/env python3
import sys
from pathlib import Path

from frankenstein.telemetry.publication import validate_pages_tree


if len(sys.argv) != 2:
    raise SystemExit("usage: validate-pages.py PATH_TO_GH_PAGES_WORKTREE")

validate_pages_tree(Path(sys.argv[1]).resolve())
print("Pages tree validated")
