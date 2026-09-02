"""Work Item discovery is scoped to its Goal Run parent (c781e87d6).

Loaded by path, so the release changed-line lane can map these two skill scripts
to a standing test: `issue_tracker.py` reaches them through `_load_local`, which
no textual reference in the tracker tests names.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "public" / "issue" / "scripts"
REPO = "corca-ai/charness"
BACKEND = {"id": "gh", "binary": "gh", "commands": None}


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"{name}_discovery_test", SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


discovery = _load("issue_tracker_discovery")
relationships = _load("issue_tracker_relationships")


def _row(number: int, *, parent: int | None, body: str = "", pull_request: object = None) -> dict:
    row = {
        "id": 9000 + number,
        "number": number,
        "title": f"child {number}",
        "state": "open",
        "body": body,
        "url": f"https://api.github.com/repos/{REPO}/issues/{number}",
        "html_url": f"https://github.com/{REPO}/issues/{number}",
    }
    if parent is not None:
        row["parent_issue_url"] = f"https://api.github.com/repos/{REPO}/issues/{parent}"
    if pull_request is not None:
        row["pull_request"] = pull_request
    return row


@pytest.mark.parametrize(
    "value, expected",
    [
        ("https://api.github.com/repos/corca-ai/charness/issues/775", True),
        ("https://github.com/Corca-AI/Charness/issues/775/", True),
        ("https://api.github.com/repos/corca-ai/charness/issues/7750", False),
        ("https://api.github.com/repos/other/repo/issues/775", False),
        (None, False),
        (775, False),
    ],
)
def test_parent_url_matches_names_exactly_this_repo_and_number(value, expected) -> None:
    assert discovery.parent_url_matches(value, REPO, 775) is expected
    # The relationships module reads the same predicate rather than its own copy.
    assert relationships._parent_url_matches(value, REPO, 775) is expected


def test_discovery_reports_a_foreign_parent_and_keeps_an_unlinked_child(monkeypatch) -> None:
    marker = discovery.work_item_key_marker("integrated-closeout")
    rows = [
        _row(782, parent=775, body=f"{marker}\nthis run's child"),
        _row(772, parent=765, body=f"{marker}\nthe previous run's child"),
        _row(790, parent=None, body=f"{marker}\ncreated by an interrupted run, not linked yet"),
        _row(791, parent=775, body="no marker at all"),
        _row(792, parent=775, body=f"{marker}\na pull request", pull_request={"url": "x"}),
    ]
    monkeypatch.setattr(discovery, "_run_json", lambda argv, context: [rows])

    report = discovery.discover_managed_issues(
        REPO, "integrated-closeout", backend=BACKEND, parent_number=775
    )

    assert report["parent_number"] == 775
    assert [match["number"] for match in report["matches"]] == [782, 790]
    assert [match["number"] for match in report["foreign_parent"]] == [772]
    assert report["count"] == 2
    assert report["matches"][1]["parent_issue_url"] is None


def test_discovery_without_a_parent_counts_every_marked_issue(monkeypatch) -> None:
    marker = discovery.work_item_key_marker("integrated-closeout")
    rows = [_row(782, parent=775, body=marker), _row(772, parent=765, body=marker)]
    monkeypatch.setattr(discovery, "_run_json", lambda argv, context: [rows])

    report = discovery.discover_managed_issues(REPO, "integrated-closeout", backend=BACKEND)

    assert report["count"] == 2
    assert report["foreign_parent"] == []
