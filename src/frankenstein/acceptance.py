from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Gate:
    id: str
    description: str
    points: int
    required_events: frozenset[str]


GATES = (
    Gate("DOD-01", "Missing capability detected after registry search", 8, frozenset({"capability_gap_detected", "registry_searched"})),
    Gate("DOD-02", "Reusable implementation artifact generated", 10, frozenset({"capability_generated"})),
    Gate("DOD-03", "Failed verification prevents promotion", 8, frozenset({"capability_test_failed", "promotion_denied"})),
    Gate("DOD-04", "Capability independently verified and registered", 10, frozenset({"capability_verified", "capability_registered"})),
    Gate("DOD-05", "Original task completed using generated capability", 10, frozenset({"capability_invoked", "task_completed"})),
    Gate("DOD-06", "Capability-management infrastructure generated", 10, frozenset({"management_capability_generated"})),
    Gate("DOD-07", "Management extension verified, registered, and used", 10, frozenset({"management_capability_verified", "management_capability_registered", "management_capability_invoked"})),
    Gate("DOD-08", "Registry survives process restart", 8, frozenset({"process_restarted", "registry_reloaded"})),
    Gate("DOD-09", "Fresh session discovers generated capabilities", 8, frozenset({"fresh_session_started", "capabilities_rediscovered"})),
    Gate("DOD-10", "Different task composes two capabilities without rebuild", 10, frozenset({"capabilities_composed", "composition_task_completed", "no_rebuild_confirmed"})),
    Gate("DOD-11", "Installed capability does not expand authority", 8, frozenset({"permission_escalation_denied", "ordinary_execution_succeeded"})),
)


def score_evidence(events: list[dict[str, Any]]) -> dict[str, Any]:
    event_types = {str(event.get("type")) for event in events}
    results = []
    for gate in GATES:
        missing = sorted(gate.required_events - event_types)
        passed = not missing
        results.append(
            {
                "id": gate.id,
                "description": gate.description,
                "points": gate.points if passed else 0,
                "possible_points": gate.points,
                "passed": passed,
                "missing_events": missing,
            }
        )
    score = sum(result["points"] for result in results)
    return {
        "qualified": all(result["passed"] for result in results),
        "score": score,
        "possible_score": sum(gate.points for gate in GATES),
        "gates": results,
    }
