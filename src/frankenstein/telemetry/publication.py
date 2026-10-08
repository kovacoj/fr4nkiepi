from __future__ import annotations

import re
from pathlib import Path


ALLOWED_FILES = {
    ".nojekyll",
    "index.html",
    "assets/style.css",
    "assets/app.js",
    "data/summary.json",
    "data/timeseries.json",
    "data/models.json",
    "data/capabilities.json",
    "data/executions.json",
    "data/evolution.json",
    "data/system.json",
}
PROHIBITED_PATTERNS = (
    re.compile(r"(?i)(^|/)(\.env|id_rsa|id_ed25519|SKILL\.md|memory|raw)(/|$)"),
    re.compile(r"(?i)\.(py|sh|sqlite|db|jsonl|pem|key|log|yaml|yml)$"),
    re.compile(r"(?i)(gh[pousr]_[a-z0-9]{20,}|sk-[a-z0-9_-]{16,}|discord[_-]?bot[_-]?token)"),
)


def validate_pages_tree(root: Path) -> None:
    files = {
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    unexpected = sorted(files - ALLOWED_FILES)
    missing = sorted(ALLOWED_FILES - files)
    if unexpected or missing:
        raise ValueError(f"invalid Pages tree; unexpected={unexpected}, missing={missing}")
    for relative in sorted(files):
        path = root / relative
        content = path.read_text(errors="replace")
        for pattern in PROHIBITED_PATTERNS:
            if pattern.search(relative) or pattern.search(content):
                raise ValueError(f"prohibited content in Pages tree: {relative}")
