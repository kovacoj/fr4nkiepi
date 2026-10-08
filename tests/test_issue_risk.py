from frankenstein.issue_risk import run


def test_classifies_and_orders_open_issue_risks():
    result = run(
        {
            "repository": "org/repo",
            "issues": [
                {"number": 2, "title": "Minor", "labels": []},
                {"number": 1, "title": "Exploit", "labels": ["security"]},
                {"number": 3, "title": "Done", "state": "closed", "labels": ["blocker"]},
            ],
        }
    )

    assert result["issue_count"] == 2
    assert result["high_risk_count"] == 1
    assert [issue["id"] for issue in result["issues"]] == ["1", "2"]
