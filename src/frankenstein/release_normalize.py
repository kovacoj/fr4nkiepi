from __future__ import annotations

import re
from typing import Any

from .contracts import ReleaseInput, ReleaseOutput


def run(raw: dict[str, Any]) -> dict[str, Any]:
    request = ReleaseInput.model_validate(raw)
    normalized = []

    for release in request.releases:
        tag = str(release.get("tag_name") or release.get("tag") or "").strip()
        if not tag:
            continue
        body = str(release.get("body") or "")
        changes = [
            cleaned
            for line in body.splitlines()
            if (cleaned := re.sub(r"^\s*(?:[-*+] |\d+[.)] )", "", line).strip())
            and not cleaned.startswith("#")
        ]
        normalized.append(
            {
                "tag": tag,
                "title": str(release.get("name") or tag).strip(),
                "published_at": release.get("published_at") or release.get("released_at"),
                "url": release.get("html_url") or release.get("url"),
                "prerelease": bool(release.get("prerelease", False)),
                "changes": changes,
            }
        )

    normalized.sort(key=lambda item: item["published_at"] or "", reverse=True)
    return ReleaseOutput(
        repository=request.repository,
        release_count=len(normalized),
        releases=normalized,
    ).model_dump(mode="json")
