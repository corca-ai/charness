from __future__ import annotations

import json
import os
import subprocess
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
    assert record_artifact_supported("history") is True
    assert record_artifact_supported("current") is False
    assert record_artifact_supported("rolling") is False
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
    assert payload["artifact_class"] == "history"
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
    assert payload["artifact_class"] == "rolling"
    assert payload["record_artifact_supported"] is False
    assert payload["current_artifact_path"] == "docs/handoff.md"
    assert payload["write_artifact_path"] == "docs/handoff.md"
    assert payload["write_artifact_role"] == "current_pointer"


def write_minimal_resolver(
    repo: Path, skill_id: str, output_dir: str, *, artifact_class: str = "history"
) -> None:
    resolver = repo / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text(
        "\n".join(
            [
                "#!/usr/bin/env python3",
                "import json",
                "import sys",
                "payload = {",
                f"  'data': {{'output_dir': {output_dir!r}, 'artifact_class': {artifact_class!r}}},",
                f"  'artifact_class': {artifact_class!r},",
                "}",
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


def test_refresh_current_pointer_copies_record_to_regular_current(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    record = artifact_dir / "2026-04-15-quality-review.md"
    record.write_text("# Quality Review\n\nFresh.\n", encoding="utf-8")
    current = artifact_dir / "latest.md"
    current.write_text("# Quality Review\n\nOld.\n", encoding="utf-8")

    dry_run = run_script(
        "scripts/refresh_current_pointer.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--record-artifact-path",
        "charness-artifacts/quality/2026-04-15-quality-review.md",
    )

    assert dry_run.returncode == 0, dry_run.stderr
    dry_payload = json.loads(dry_run.stdout)
    assert dry_payload["status"] == "planned"
    assert current.read_text(encoding="utf-8") == "# Quality Review\n\nOld.\n"

    result = run_script(
        "scripts/refresh_current_pointer.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--record-artifact-path",
        "charness-artifacts/quality/2026-04-15-quality-review.md",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "updated"
    assert current.read_text(encoding="utf-8") == record.read_text(encoding="utf-8")


def test_refresh_current_pointer_repoints_existing_symlink(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    old_record = artifact_dir / "2026-04-14-quality-review.md"
    new_record = artifact_dir / "2026-04-15-quality-review.md"
    old_record.write_text("# Quality Review\n\nOld.\n", encoding="utf-8")
    new_record.write_text("# Quality Review\n\nFresh.\n", encoding="utf-8")
    current = artifact_dir / "latest.md"
    current.symlink_to(old_record.name)

    result = run_script(
        "scripts/refresh_current_pointer.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--record-artifact-path",
        "charness-artifacts/quality/2026-04-15-quality-review.md",
        "--execute",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["status"] == "updated"
    assert os.readlink(current) == "2026-04-15-quality-review.md"


def test_refresh_current_pointer_blocks_current_class_records(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "find-skills", "charness-artifacts/find-skills", artifact_class="current")
    artifact_dir = repo / "charness-artifacts" / "find-skills"
    artifact_dir.mkdir(parents=True)
    record = artifact_dir / "2026-04-15-find-skills.md"
    record.write_text("# Find Skills\n", encoding="utf-8")

    result = run_script(
        "scripts/refresh_current_pointer.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "find-skills",
        "--record-artifact-path",
        "charness-artifacts/find-skills/2026-04-15-find-skills.md",
        "--execute",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "does not support dated records" in payload["reason"]


def test_invalid_artifact_class_fails_instead_of_defaulting_to_history(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality", artifact_class="typo")

    result = run_script(
        "scripts/resolve_artifact_path.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--slug",
        "quality review",
        "--intent",
        "record",
    )

    assert result.returncode == 1
    assert "artifact_class must be one of" in result.stderr


def test_simple_adapter_invalid_artifact_class_returns_invalid_payload(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "handoff-adapter.yaml").write_text(
        "version: 1\nrepo: repo\noutput_dir: docs\nartifact_class: typo\n",
        encoding="utf-8",
    )

    result = run_script(
        "skills/public/handoff/scripts/resolve_adapter.py",
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["valid"] is False
    assert payload["data"]["artifact_class"] == "rolling"
    assert "artifact_class must be one of: current, history, rolling" in payload["errors"]


def test_refresh_current_pointer_blocks_external_record_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "latest.md").write_text("# Quality Review\n", encoding="utf-8")
    outside_record = tmp_path / "outside.md"
    outside_record.write_text("# External\n", encoding="utf-8")

    result = run_script(
        "scripts/refresh_current_pointer.py",
        "--repo-root",
        str(repo),
        "--skill-id",
        "quality",
        "--record-artifact-path",
        str(outside_record),
        "--strategy",
        "symlink",
        "--execute",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["reason"] == "record artifact path is outside repo_root"


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

    record = artifact_dir / "2026-04-15-quality-review.md"
    record.write_text("# Quality Review\n\nFresh.\n", encoding="utf-8")
    record_result = run_script(
        str(plugin_root / "scripts" / "resolve_artifact_path.py"),
        "--repo-root",
        str(consumer),
        "--skill-id",
        "quality",
        "--slug",
        "quality review",
        "--intent",
        "record",
        "--date",
        "2026-04-15",
    )

    assert record_result.returncode == 0, record_result.stderr
    record_payload = json.loads(record_result.stdout)
    assert record_payload["refresh_current_pointer_argv"][1] == str(
        plugin_root / "scripts" / "refresh_current_pointer.py"
    )
    refresh_result = subprocess.run(
        record_payload["refresh_current_pointer_argv"],
        cwd=consumer,
        check=False,
        capture_output=True,
        text=True,
    )
    assert refresh_result.returncode == 0, refresh_result.stderr
    refresh_payload = json.loads(refresh_result.stdout)
    assert refresh_payload["status"] == "updated"
    assert os.readlink(artifact_dir / "latest.md") == "2026-04-15-quality-review.md"
