from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from scripts.artifact_naming_lib import (
    current_artifact_filename,
    dated_artifact_filename,
    record_artifact_supported,
    slugify,
)

from .support import ROOT, run_script


def test_artifact_naming_defaults_to_latest_pointer_and_dated_slug_records() -> None:
    assert current_artifact_filename("gather") == "latest.md"
    assert current_artifact_filename("handoff") == "handoff.md"
    assert record_artifact_supported("gather") is True
    assert record_artifact_supported("find-skills") is False
    assert record_artifact_supported("handoff") is False
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
        "--intent",
        "record",
        "--date",
        "2026-04-15",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["slug"] == "insane-search-review"
    assert payload["record_artifact_path"] == "charness-artifacts/gather/2026-04-15-insane-search-review.md"
    assert payload["record_artifact_supported"] is True
    assert payload["current_artifact_path"] == "charness-artifacts/gather/latest.md"
    assert payload["write_artifact_path"] == "charness-artifacts/gather/2026-04-15-insane-search-review.md"
    assert payload["write_artifact_role"] == "durable_record"
    assert payload["update_current_pointer_after_write"] is True
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
    assert payload["record_artifact_path"] is None
    assert payload["record_artifact_supported"] is False
    assert payload["current_artifact_path"] == "docs/handoff.md"
    assert payload["write_artifact_path"] == "docs/handoff.md"
    assert payload["write_artifact_role"] == "current_pointer"


def write_minimal_resolver(repo: Path, skill_id: str, output_dir: str) -> None:
    resolver = repo / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                f"payload = {{'data': {{'output_dir': {output_dir!r}}}}}",
                "json.dump(payload, sys.stdout)",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_current_intent_resolves_symlinked_latest_to_write_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    target = artifact_dir / "history" / "current-quality.md"
    target.parent.mkdir()
    target.write_text("# Quality Review\n", encoding="utf-8")
    (artifact_dir / "latest.md").symlink_to(Path("history") / "current-quality.md")

    result = run_script(
        "scripts/resolve_artifact_path.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--slug",
        "quality review",
        "--intent",
        "current",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["current_artifact_path"] == "charness-artifacts/quality/latest.md"
    assert payload["current_pointer_is_symlink"] is True
    assert payload["current_pointer_target_path"] == "charness-artifacts/quality/history/current-quality.md"
    assert payload["write_artifact_path"] == "charness-artifacts/quality/history/current-quality.md"
    assert payload["write_artifact_role"] == "current_pointer_target"
    assert payload["update_current_pointer_after_write"] is False


def test_exported_resolver_uses_plugin_skill_resolver_for_consumer_repo(tmp_path: Path) -> None:
    export_root = tmp_path / "export"
    export_result = run_script(
        "scripts/export_plugin.py",
        "--repo-root",
        str(ROOT),
        "--host",
        "codex",
        "--output-root",
        str(export_root),
    )
    assert export_result.returncode == 0, export_result.stderr
    plugin_root = export_root / "plugins" / "charness"

    consumer = tmp_path / "consumer"
    (consumer / ".agents").mkdir(parents=True)
    (consumer / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(["version: 1", "repo: consumer", "language: en", "output_dir: charness-artifacts/quality", ""]),
        encoding="utf-8",
    )
    artifact_dir = consumer / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    target = artifact_dir / "history" / "current-quality.md"
    target.parent.mkdir()
    target.write_text("# Quality Review\n", encoding="utf-8")
    (artifact_dir / "latest.md").symlink_to(Path("history") / "current-quality.md")

    result = run_script(
        str(plugin_root / "scripts" / "resolve_artifact_path.py"),
        "--repo-root",
        str(consumer),
        "--skill-id",
        "quality",
        "--slug",
        "quality review",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["intent"] == "current"
    assert payload["write_artifact_path"] == "charness-artifacts/quality/history/current-quality.md"
    assert payload["write_artifact_role"] == "current_pointer_target"
