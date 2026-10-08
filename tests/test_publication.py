import json

import pytest

from frankenstein.telemetry.publication import ALLOWED_FILES, validate_pages_tree


def create_valid_tree(root):
    for relative in ALLOWED_FILES:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}" if path.suffix == ".json" else "safe static content")


def test_exact_static_tree_is_accepted(tmp_path):
    create_valid_tree(tmp_path)
    validate_pages_tree(tmp_path)


@pytest.mark.parametrize("filename", ["agent.py", "deploy.sh", "raw.jsonl", "telemetry.sqlite", ".env"])
def test_backend_and_private_files_are_rejected(tmp_path, filename):
    create_valid_tree(tmp_path)
    (tmp_path / filename).write_text("private")

    with pytest.raises(ValueError, match="unexpected"):
        validate_pages_tree(tmp_path)


def test_secret_inside_approved_json_is_rejected(tmp_path):
    create_valid_tree(tmp_path)
    (tmp_path / "data/summary.json").write_text(json.dumps({"token": "ghp_abcdefghijklmnopqrstuvwxyz1234"}))

    with pytest.raises(ValueError, match="prohibited"):
        validate_pages_tree(tmp_path)
