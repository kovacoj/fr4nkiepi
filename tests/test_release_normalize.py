from pydantic import ValidationError
import pytest

from frankenstein.release_normalize import run


def test_normalizes_release_fields_and_change_lines():
    result = run(
        {
            "repository": "org/repo",
            "releases": [{"tag_name": "v1", "body": "## Changes\n- Fixed bug", "prerelease": True}],
        }
    )

    assert result["release_count"] == 1
    assert result["releases"][0] == {
        "tag": "v1",
        "title": "v1",
        "published_at": None,
        "url": None,
        "prerelease": True,
        "changes": ["Fixed bug"],
    }


def test_rejects_unknown_top_level_input():
    with pytest.raises(ValidationError):
        run({"repository": "org/repo", "releases": [], "secret_path": "/home/user/.ssh"})
