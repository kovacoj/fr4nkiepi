from frankenstein.acceptance import GATES, score_evidence


def test_all_mandatory_evidence_is_required_even_with_high_score():
    events = [
        {"type": event_type}
        for gate in GATES[:-1]
        for event_type in gate.required_events
    ]

    report = score_evidence(events)

    assert report["score"] == 92
    assert report["qualified"] is False
    assert report["gates"][-1]["missing_events"]


def test_complete_evidence_qualifies_at_100_points():
    events = [
        {"type": event_type}
        for gate in GATES
        for event_type in gate.required_events
    ]

    report = score_evidence(events)

    assert report["score"] == report["possible_score"] == 100
    assert report["qualified"] is True
