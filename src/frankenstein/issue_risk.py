from __future__ import annotations

from typing import Any

from .contracts import IssueInput, IssueRiskOutput


HIGH_RISK_LABELS = {"blocker", "critical", "security"}
MEDIUM_RISK_LABELS = {"bug", "regression", "performance"}


def run(raw: dict[str, Any]) -> dict[str, Any]:
    request = IssueInput.model_validate(raw)
    normalized = []

    for issue in request.issues:
        if issue.get("state", "open") != "open":
            continue
        labels = {
            str(label.get("name") if isinstance(label, dict) else label).strip().lower()
            for label in issue.get("labels", [])
        }
        reasons = []
        if matched := sorted(labels & HIGH_RISK_LABELS):
            risk = "high"
            reasons.append(f"high-risk labels: {', '.join(matched)}")
        elif matched := sorted(labels & MEDIUM_RISK_LABELS):
            risk = "medium"
            reasons.append(f"risk labels: {', '.join(matched)}")
        else:
            risk = "low"
            reasons.append("no known release-risk label")
        normalized.append(
            {
                "id": str(issue.get("id") or issue.get("iid") or issue.get("number") or "unknown"),
                "title": str(issue.get("title") or "Untitled issue").strip(),
                "url": issue.get("html_url") or issue.get("web_url") or issue.get("url"),
                "risk": risk,
                "reasons": reasons,
            }
        )

    order = {"high": 0, "medium": 1, "low": 2}
    normalized.sort(key=lambda item: (order[item["risk"]], item["id"]))
    return IssueRiskOutput(
        repository=request.repository,
        issue_count=len(normalized),
        high_risk_count=sum(issue["risk"] == "high" for issue in normalized),
        issues=normalized,
    ).model_dump(mode="json")
