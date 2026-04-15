from __future__ import annotations

import json
from datetime import date

from scripts.artifact_naming_lib import current_artifact_filename, dated_artifact_filename, slugify

from .support import ROOT, run_script


def test_artifact_naming_defaults_to_latest_pointer_and_dated_slug_records() -> None:
    assert current_artifact_filename("gather") == "latest.md"
    assert current_artifact_filename("handoff") == "handoff.md"
    assert slugify("Insane Search / Review!") == "insane-search-review"
    assert dated_artifact_filename("Insane Search / Review!", artifact_date=date(2026, 4, 15)) == (
        "2026-04-15-insane-search-review.md"
    )


def test_resolve_artifact_path_reports_record_and_current_paths() -> None:
    result = run_script(
        "scripts/resolve_artifact_path.py",
        "--repo-root",
        str(ROOT),
        "--skill-id",
        "gather",
        "--slug",
        "Insane Search / Review!",
        "--date",
        "2026-04-15",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["slug"] == "insane-search-review"
    assert payload["record_artifact_path"] == "charness-artifacts/gather/2026-04-15-insane-search-review.md"
    assert payload["current_artifact_path"] == "charness-artifacts/gather/latest.md"
    assert payload["frontmatter"]["artifact_kind"] == "record"


def test_handoff_current_path_remains_docs_handoff() -> None:
    result = run_script(
        "scripts/resolve_artifact_path.py",
        "--repo-root",
        str(ROOT),
        "--skill-id",
        "handoff",
        "--slug",
        "handoff refresh",
        "--date",
        "2026-04-15",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["record_artifact_path"] == "docs/2026-04-15-handoff-refresh.md"
    assert payload["current_artifact_path"] == "docs/handoff.md"
