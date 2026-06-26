from __future__ import annotations

import importlib.util
import json
import os
import runpy
import subprocess
import sys
from datetime import date
from pathlib import Path

from scripts.artifact_naming_lib import (
    current_artifact_filename,
    dated_artifact_filename,
    record_artifact_supported,
    slugify,
)
from scripts.resolve_artifact_path import payload_for as resolve_artifact_payload_for

from .support import ROOT, run_script

INVENTORY_SPEC = importlib.util.spec_from_file_location(
    "inventory_current_pointer_layouts", ROOT / "scripts" / "inventory_current_pointer_layouts.py"
)
assert INVENTORY_SPEC is not None and INVENTORY_SPEC.loader is not None
INVENTORY = importlib.util.module_from_spec(INVENTORY_SPEC)
sys.modules[INVENTORY_SPEC.name] = INVENTORY
INVENTORY_SPEC.loader.exec_module(INVENTORY)


def _load_quality_resolver():
    spec = importlib.util.spec_from_file_location(
        "resolve_quality_artifact", ROOT / "skills" / "public" / "quality" / "scripts" / "resolve_quality_artifact.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    payload = resolve_artifact_payload_for(
        ROOT,
        "gather",
        "Insane Search / Review!",
        intent="record",
        artifact_date=date(2026, 4, 15),
        adapter={
            "data": {"output_dir": "charness-artifacts/gather", "artifact_class": "history"},
            "artifact_class": "history",
        },
    )

    assert payload["slug"] == "insane-search-review"
    assert payload["artifact_class"] == "history"
    assert payload["artifact_path"] == "charness-artifacts/gather/latest.md"
    assert payload["record_artifact_path"] == "charness-artifacts/gather/2026-04-15-insane-search-review.md"
    assert payload["record_artifact_supported"] is True
    assert payload["current_artifact_path"] == "charness-artifacts/gather/latest.md"
    assert payload["write_artifact_path"] == "charness-artifacts/gather/2026-04-15-insane-search-review.md"
    assert payload["write_artifact_role"] == "durable_record"
    assert payload["update_current_pointer_after_write"] is True
    assert payload["frontmatter"]["artifact_kind"] == "record"


def test_handoff_current_path_remains_docs_handoff() -> None:
    payload = resolve_artifact_payload_for(
        ROOT,
        "handoff",
        "handoff refresh",
        artifact_date=date(2026, 4, 15),
        adapter={
            "data": {"output_dir": "docs", "artifact_class": "rolling"},
            "artifact_class": "rolling",
        },
    )

    assert payload["record_artifact_path"] is None
    assert payload["artifact_class"] == "rolling"
    assert payload["artifact_path"] == "docs/handoff.md"
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


def write_unmanaged_resolver(repo: Path, skill_id: str) -> None:
    resolver = repo / "skills" / "public" / skill_id / "scripts" / "resolve_adapter.py"
    resolver.parent.mkdir(parents=True)
    resolver.write_text(
        "import json, sys\njson.dump({'data': {}, 'artifact_class': 'history'}, sys.stdout)\n",
        encoding="utf-8",
    )


def test_inventory_current_pointer_layouts_reports_adapter_and_disk_shapes(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    write_minimal_resolver(
        repo,
        "find-skills",
        "charness-artifacts/find-skills",
        artifact_class="current",
    )
    write_minimal_resolver(repo, "handoff", "docs", artifact_class="rolling")
    write_unmanaged_resolver(repo, "issue")
    (repo / "skills" / "public" / "create-cli").mkdir(parents=True)

    quality_dir = repo / "charness-artifacts" / "quality"
    quality_dir.mkdir(parents=True)
    target = quality_dir / "2026-06-16-current-quality.md"
    target.write_text("# Quality\n", encoding="utf-8")
    (quality_dir / "latest.md").symlink_to(target.name)
    find_skills_dir = repo / "charness-artifacts" / "find-skills"
    find_skills_dir.mkdir(parents=True)
    (find_skills_dir / "latest.md").write_text("# Find Skills\n", encoding="utf-8")
    cautilus_dir = repo / "charness-artifacts" / "cautilus"
    cautilus_dir.mkdir(parents=True)
    (cautilus_dir / "latest.md").write_text("# Cautilus\n", encoding="utf-8")
    docs = repo / "docs"
    docs.mkdir()
    (docs / "handoff.md").write_text("# Handoff\n", encoding="utf-8")

    items = INVENTORY.inventory(
        repo,
        selected=["quality", "find-skills", "handoff", "issue", "create-cli", "cautilus"],
        day=date(2026, 6, 16),
    )

    by_skill = {item.skill_id: item for item in items}
    assert by_skill["quality"].artifact_class == "history"
    assert by_skill["quality"].on_disk_layout == "symlink_current_pointer"
    assert by_skill["quality"].write_artifact_path == (
        "charness-artifacts/quality/2026-06-16-current-quality.md"
    )
    assert by_skill["find-skills"].artifact_class == "current"
    assert by_skill["find-skills"].on_disk_layout == "regular_current_pointer"
    assert by_skill["handoff"].artifact_class == "rolling"
    assert by_skill["handoff"].on_disk_layout == "rolling_file"
    assert by_skill["issue"].status == "adapter_unmanaged"
    assert by_skill["issue"].on_disk_layout == "adapter_unmanaged"
    assert by_skill["create-cli"].status == "adapter_unmanaged"
    assert by_skill["create-cli"].on_disk_layout == "adapter_unmanaged"
    assert by_skill["cautilus"].status == "adapter_unmanaged"
    assert by_skill["cautilus"].discovery_source == "artifact_family"
    assert by_skill["cautilus"].artifact_path == "charness-artifacts/cautilus/latest.md"
    assert by_skill["cautilus"].on_disk_layout == "regular_current_pointer"


def test_inventory_current_pointer_layouts_default_discovery_and_format_helpers(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "skills" / "public" / "quality").mkdir(parents=True)
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "latest.md").write_text("# Quality\n", encoding="utf-8")
    (repo / "charness-artifacts" / "cautilus").mkdir(parents=True)
    (repo / "charness-artifacts" / "cautilus" / "latest.md").write_text("# Cautilus\n", encoding="utf-8")

    assert INVENTORY._skill_ids(repo, None) == ["cautilus", "quality"]
    assert INVENTORY._skill_ids(repo, ["zeta", "alpha", "alpha"]) == ["alpha", "zeta"]
    assert INVENTORY._discovery_source(repo, "quality") == "public_skill+artifact_family"
    assert INVENTORY._discovery_source(repo, "cautilus") == "artifact_family"
    assert INVENTORY._discovery_source(repo, "selected-only") == "selected"
    assert INVENTORY._path_layout(repo, None) == "adapter_unmanaged"
    assert INVENTORY._path_layout(repo, "charness-artifacts/quality/missing.md") == "missing_current_pointer"
    directory_pointer = repo / "charness-artifacts" / "quality" / "directory-pointer"
    directory_pointer.mkdir()
    assert INVENTORY._path_layout(repo, "charness-artifacts/quality/directory-pointer") == "non_file_current_pointer"
    assert INVENTORY._portable_path(repo, tmp_path / "outside.md") == str(tmp_path / "outside.md")
    assert INVENTORY._md_cell("a|b") == "`a\\|b`"


def test_inventory_current_pointer_layouts_error_and_symlink_branches(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    artifact_dir = repo / "charness-artifacts" / "debug"
    artifact_dir.mkdir(parents=True)
    target = artifact_dir / "2026-06-16-debug.md"
    target.write_text("# Debug\n", encoding="utf-8")
    (artifact_dir / "latest.md").symlink_to(target.name)

    assert INVENTORY._fallback_pointer_state(repo, "charness-artifacts/debug/latest.md") == {
        "current_pointer_is_symlink": True,
        "current_pointer_target_path": "charness-artifacts/debug/2026-06-16-debug.md",
        "current_pointer_target_exists": True,
    }
    assert INVENTORY._fallback_pointer_state(repo, None) == {
        "current_pointer_is_symlink": None,
        "current_pointer_target_path": None,
        "current_pointer_target_exists": None,
    }
    assert INVENTORY._unresolved_status("boom") == ("unresolved", "resolver_error")

    monkeypatch.setattr(
        INVENTORY.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 0, "{", ""),
    )
    payload, error = INVENTORY._run_resolver(repo, "quality", date(2026, 6, 16))

    assert payload is None
    assert error is not None
    assert "invalid JSON" in error


def test_inventory_current_pointer_layouts_markdown_and_require_resolved(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"

    def fake_inventory(repo_root: Path, *, selected=None, day=None):
        del repo_root, selected, day
        return [
            INVENTORY.LayoutItem(
                skill_id="broken",
                status="unresolved",
                artifact_class=None,
                artifact_path=None,
                current_artifact_path=None,
                write_artifact_path=None,
                write_artifact_role=None,
                record_artifact_supported=None,
                current_pointer_is_symlink=None,
                current_pointer_target_path="missing-target.md",
                current_pointer_target_exists=False,
                on_disk_layout="resolver_error",
                discovery_source="selected",
                resolver_error="bad resolver",
            )
        ]

    monkeypatch.setattr(INVENTORY, "inventory", fake_inventory)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_current_pointer_layouts.py",
            "--repo-root",
            str(repo),
            "--skill-id",
            "broken",
            "--require-resolved",
        ],
    )

    assert INVENTORY.main() == 1
    output = capsys.readouterr().out
    assert "# Current Pointer Layout Inventory" in output
    assert "`missing-target.md (missing)`" in output
    assert "`unresolved: bad resolver`" in output


def test_inventory_current_pointer_layouts_main_json_smoke(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "latest.md").write_text("# Quality\n", encoding="utf-8")

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_current_pointer_layouts.py",
            "--repo-root",
            str(repo),
            "--skill-id",
            "quality",
            "--date",
            "2026-06-16",
            "--json",
        ],
    )

    assert INVENTORY.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "clean"
    assert payload["items"][0]["artifact_path"] == "charness-artifacts/quality/latest.md"


def test_inventory_current_pointer_layouts_dunder_main(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path / "repo"
    write_minimal_resolver(repo, "quality", "charness-artifacts/quality")
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    (artifact_dir / "latest.md").write_text("# Quality\n", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "inventory_current_pointer_layouts.py",
            "--repo-root",
            str(repo),
            "--skill-id",
            "quality",
            "--json",
        ],
    )

    try:
        runpy.run_path(str(ROOT / "scripts" / "inventory_current_pointer_layouts.py"), run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("inventory_current_pointer_layouts.py did not exit through SystemExit")
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "clean"


def test_quality_resolver_reports_artifact_path_alias() -> None:
    module = _load_quality_resolver()

    payload = module.payload_for(
        ROOT,
        slug="quality review",
        intent="current",
        artifact_date=date(2026, 6, 16),
    )

    assert payload["artifact_path"] == payload["current_artifact_path"]
    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"


def test_current_intent_resolves_symlinked_latest_to_write_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    artifact_dir = repo / "charness-artifacts" / "quality"
    artifact_dir.mkdir(parents=True)
    target = artifact_dir / "history" / "current-quality.md"
    target.parent.mkdir()
    target.write_text("# Quality Review\n", encoding="utf-8")
    (artifact_dir / "latest.md").symlink_to(Path("history") / "current-quality.md")

    payload = resolve_artifact_payload_for(
        repo,
        "quality",
        "quality review",
        adapter={
            "data": {"output_dir": "charness-artifacts/quality", "artifact_class": "history"},
            "artifact_class": "history",
        },
    )

    assert payload["artifact_path"] == "charness-artifacts/quality/latest.md"
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
