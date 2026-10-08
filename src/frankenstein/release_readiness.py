from __future__ import annotations

from typing import Any

from .contracts import ReadinessInput, ReadinessOutput


def run(raw: dict[str, Any], dependencies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    request = ReadinessInput.model_validate(raw)
    releases = dependencies["repo.release_normalize"]
    issue_risks = dependencies["repo.issue_risk"]
    blocker_count = issue_risks["high_risk_count"]
    latest_release = releases["releases"][0]["tag"] if releases["releases"] else None

    if blocker_count:
        status = "blocked"
        summary = f"Release blocked by {blocker_count} high-risk open issue(s)."
    elif issue_risks["issue_count"]:
        status = "caution"
        summary = f"No blockers found; review {issue_risks['issue_count']} open issue(s)."
    else:
        status = "ready"
        summary = "No open issue risks found."

    return ReadinessOutput(
        repository=request.repository,
        status=status,
        latest_release=latest_release,
        blocker_count=blocker_count,
        summary=summary,
    ).model_dump(mode="json")
