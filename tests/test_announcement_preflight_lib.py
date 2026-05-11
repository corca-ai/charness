from __future__ import annotations

import textwrap
from pathlib import Path

from scripts.announcement_preflight_lib import preflight_sources


def test_preflight_passes_when_no_sources_declared(tmp_path: Path) -> None:
    payload = preflight_sources({"in_progress_sources": []}, tmp_path / "missing.md")
    assert payload["ok"] is True
    assert payload["delivery_blocked"] is False
    assert payload["surfaces"] == []


def test_preflight_blocks_when_draft_missing_and_sources_declared(tmp_path: Path) -> None:
    adapter_data = {
        "in_progress_sources": [{"kind": "control_repo", "path": "/srv/ceal/control"}]
    }
    payload = preflight_sources(adapter_data, tmp_path / "missing.md")
    assert payload["ok"] is False
    assert payload["delivery_blocked"] is True
    assert payload["draft_exists"] is False
    assert payload["surfaces"][0]["status"] == "unverified"
    assert payload["surfaces"][0]["id"] == "control_repo:/srv/ceal/control"


def test_preflight_blocks_when_section_absent(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("# Announcement\n\n## Highlights\n- thing\n", encoding="utf-8")
    adapter_data = {"in_progress_sources": [{"kind": "handoff", "path": "docs/handoff.md"}]}
    payload = preflight_sources(adapter_data, draft)
    assert payload["section_present"] is False
    assert payload["delivery_blocked"] is True
    assert payload["surfaces"][0]["status"] == "unverified"


def test_preflight_marks_collected_or_unavailable_per_status_keyword(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        textwrap.dedent(
            """
            # Announcement

            ## Source surfaces
            - handoff:docs/handoff.md — collected: 12 commits since last record
            - control_repo:/srv/ceal — unavailable: stale instance root

            ## Highlights
            - thing
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    adapter_data = {
        "in_progress_sources": [
            {"kind": "handoff", "path": "docs/handoff.md"},
            {"kind": "control_repo", "path": "/srv/ceal"},
        ]
    }
    payload = preflight_sources(adapter_data, draft)
    assert payload["ok"] is True
    statuses = {item["kind"]: item["status"] for item in payload["surfaces"]}
    assert statuses == {"handoff": "collected", "control_repo": "unavailable"}


def test_preflight_blocks_when_one_source_unrecorded(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# x\n\n## Source surfaces\n- handoff:docs/handoff.md — collected: 0 commits\n",
        encoding="utf-8",
    )
    adapter_data = {
        "in_progress_sources": [
            {"kind": "handoff", "path": "docs/handoff.md"},
            {"kind": "control_repo", "path": "/srv/ceal"},
        ]
    }
    payload = preflight_sources(adapter_data, draft)
    assert payload["delivery_blocked"] is True
    statuses = {item["kind"]: item["status"] for item in payload["surfaces"]}
    assert statuses["handoff"] == "collected"
    assert statuses["control_repo"] == "unverified"


def test_preflight_keyword_match_uses_word_boundary_not_substring(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# x\n\n## Source surfaces\n- handoff:docs/handoff.md uncollected this run\n",
        encoding="utf-8",
    )
    adapter_data = {"in_progress_sources": [{"kind": "handoff", "path": "docs/handoff.md"}]}
    payload = preflight_sources(adapter_data, draft)
    assert payload["surfaces"][0]["status"] == "unverified"
    assert payload["delivery_blocked"] is True


def test_preflight_token_match_requires_kind_and_value_co_occurrence(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(
        "# x\n\n## Source surfaces\n- collected: handoff log noted but no path tag\n",
        encoding="utf-8",
    )
    adapter_data = {
        "in_progress_sources": [{"kind": "handoff", "path": "docs/handoff.md"}]
    }
    payload = preflight_sources(adapter_data, draft)
    assert payload["surfaces"][0]["status"] == "unverified"
