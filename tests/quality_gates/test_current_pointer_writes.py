from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT, init_git_repo, run_script

WRITER_SPEC = importlib.util.spec_from_file_location(
    "current_pointer_writer_lib", ROOT / "scripts" / "current_pointer_writer_lib.py"
)
assert WRITER_SPEC is not None and WRITER_SPEC.loader is not None
WRITER = importlib.util.module_from_spec(WRITER_SPEC)
WRITER_SPEC.loader.exec_module(WRITER)

RELEASE_SPEC = importlib.util.spec_from_file_location(
    "publish_release_artifact",
    ROOT / "skills" / "public" / "release" / "scripts" / "publish_release_artifact.py",
)
assert RELEASE_SPEC is not None and RELEASE_SPEC.loader is not None
RELEASE_ARTIFACT = importlib.util.module_from_spec(RELEASE_SPEC)
RELEASE_SPEC.loader.exec_module(RELEASE_ARTIFACT)

FIND_SKILLS_SPEC = importlib.util.spec_from_file_location(
    "find_skills_inventory_artifact",
    ROOT / "skills" / "public" / "find-skills" / "scripts" / "inventory_artifact.py",
)
assert FIND_SKILLS_SPEC is not None and FIND_SKILLS_SPEC.loader is not None
FIND_SKILLS_ARTIFACT = importlib.util.module_from_spec(FIND_SKILLS_SPEC)
FIND_SKILLS_SPEC.loader.exec_module(FIND_SKILLS_ARTIFACT)

SCANNER_SPEC = importlib.util.spec_from_file_location(
    "check_current_pointer_writes",
    ROOT / "scripts" / "check_current_pointer_writes.py",
)
assert SCANNER_SPEC is not None and SCANNER_SPEC.loader is not None
SCANNER = importlib.util.module_from_spec(SCANNER_SPEC)
sys.modules[SCANNER_SPEC.name] = SCANNER
SCANNER_SPEC.loader.exec_module(SCANNER)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_current_pointer_writer_replaces_symlink_without_mutating_target(tmp_path: Path) -> None:
    output = tmp_path / "artifacts"
    output.mkdir()
    prior = output / "2026-05-01-prior.md"
    prior.write_text("# prior\n", encoding="utf-8")
    pointer = output / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    payload = WRITER.write_current_pointer_text(pointer, "# latest\n")

    assert payload["status"] == "updated"
    assert payload["pointer_was_symlink"] is True
    assert not pointer.is_symlink()
    assert pointer.read_text(encoding="utf-8") == "# latest\n"
    assert _sha(prior) == prior_sha


def test_release_artifact_does_not_follow_symlinked_latest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    release_dir = repo / "charness-artifacts" / "release"
    release_dir.mkdir(parents=True)
    prior = release_dir / "2026-05-01-prior.md"
    prior.write_text("# prior release\n", encoding="utf-8")
    pointer = release_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    relpath = RELEASE_ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
        real_host_payload={"required": False},
    )

    assert relpath == "charness-artifacts/release/latest.md"
    assert not pointer.is_symlink()
    assert "target version: `0.2.0`" in pointer.read_text(encoding="utf-8")
    assert _sha(prior) == prior_sha


def test_release_artifact_records_adapter_preflight_non_claim(tmp_path: Path) -> None:
    repo = tmp_path / "repo"

    relpath = RELEASE_ARTIFACT.write_release_artifact(
        repo,
        output_dir="charness-artifacts/release",
        package_id="demo",
        previous_version="0.1.0",
        target_version="0.2.0",
        remote="origin",
        branch="main",
        quality_command="./scripts/run-quality.sh",
        release_url=None,
        update_instructions=[],
        real_host_payload={"required": False},
        release_adapter_preflight_payload={
            "status": "not_evaluable",
            "reason": "release adapter changed, but no previous release tag is available for field diff",
            "commands": [],
        },
    )

    text = (repo / relpath).read_text(encoding="utf-8")
    assert "## Release Adapter Preflight" in text
    assert "Release adapter focused preflight status: `not_evaluable`." in text
    assert "Focused preflight commands: none executed." in text


def test_find_skills_inventory_noops_when_canonical_inventory_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    output = repo / "charness-artifacts" / "find-skills"
    inventory = {
        "public_skills": [],
        "support_skills": [],
        "support_capabilities": [],
        "integrations": [],
        "trusted_skills": [],
        "tool_recommendations": [{"id": "query-only"}],
        "tool_recommendation_query": {"mode": "task_text"},
        "support_skill_recommendations": [],
        "support_recommendation_query": None,
        "support_recommendation_note": "query note",
        "workflow_recommendations": [],
    }

    first = FIND_SKILLS_ARTIFACT.persist_inventory(repo_root=repo, output_dir=output, inventory=inventory)
    first_text = (output / "latest.json").read_text(encoding="utf-8")
    second = FIND_SKILLS_ARTIFACT.persist_inventory(repo_root=repo, output_dir=output, inventory=inventory)

    assert first["updated"] is True
    assert second["updated"] is False
    assert (output / "latest.json").read_text(encoding="utf-8") == first_text


def test_hitl_sync_artifact_does_not_follow_symlinked_latest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    target = repo / "docs" / "decision.md"
    target.parent.mkdir(parents=True)
    target.write_text("# Decision\n", encoding="utf-8")

    bootstrap = run_script(
        "skills/public/hitl/scripts/bootstrap_review.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-symlink",
        "--target",
        str(target),
    )
    assert bootstrap.returncode == 0, bootstrap.stderr

    hitl_dir = repo / "charness-artifacts" / "hitl"
    hitl_dir.mkdir(parents=True, exist_ok=True)
    prior = hitl_dir / "2026-05-01-prior.md"
    prior.write_text("# prior hitl record\n", encoding="utf-8")
    pointer = hitl_dir / "latest.md"
    pointer.symlink_to(prior.name)
    prior_sha = _sha(prior)

    sync = run_script(
        "skills/public/hitl/scripts/sync_review_artifact.py",
        "--repo-root",
        str(repo),
        "--session-id",
        "hitl-symlink",
    )

    assert sync.returncode == 0, sync.stderr
    payload = json.loads(sync.stdout)
    assert payload["status"] == "synced"
    assert payload["artifact_path"] == "charness-artifacts/hitl/latest.md"
    assert not pointer.is_symlink()
    assert "<!-- hitl-runtime-sync" in pointer.read_text(encoding="utf-8")
    assert _sha(prior) == prior_sha


def test_current_pointer_write_scanner_flags_direct_latest_write(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "bad_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "target = Path('charness-artifacts/demo') / 'latest.md'\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/bad_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/bad_writer.py:3" in result.stdout


def test_current_pointer_write_scanner_flags_direct_expression_write(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "expression_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "(Path('charness-artifacts/demo') / CURRENT).write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/expression_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/expression_writer.py:3" in result.stdout


def test_current_pointer_write_scanner_json_output(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "json_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/json_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--json")

    assert result.returncode == 0
    assert json.loads(result.stdout)["findings"][0]["path"] == "scripts/json_writer.py"


def test_current_pointer_write_scanner_fallback_file_listing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    target = script_dir / "fallback_writer.py"
    target.write_text("from pathlib import Path\n", encoding="utf-8")

    monkeypatch.setattr(
        SCANNER.subprocess,
        "run",
        lambda *_args, **_kwargs: subprocess.CompletedProcess([], 1, b"", b""),
    )

    assert SCANNER._git_visible_python_files(repo) == [target]


def test_current_pointer_write_scanner_skips_generated_plugin_mirrors(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    plugin_script_dir = repo / "plugins" / "charness" / "scripts"
    plugin_script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    mirrored = plugin_script_dir / "mirrored_writer.py"
    mirrored.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "plugins/charness/scripts/mirrored_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 0


def test_current_pointer_write_scanner_ignores_helper_and_syntax_error(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    helper = script_dir / "current_pointer_writer_lib.py"
    helper.write_text("from pathlib import Path\nPath('x/latest.md').write_text('ok')\n", encoding="utf-8")
    broken = script_dir / "broken.py"
    broken.write_text("def broken(:\n", encoding="utf-8")

    assert SCANNER.scan_path(repo, helper) == []
    assert SCANNER.scan_path(repo, broken) == []


def test_current_pointer_write_scanner_does_not_exempt_mixed_helper_file(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "mixed_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "from scripts.current_pointer_writer_lib import write_current_pointer_text\n"
        "target = Path('charness-artifacts/demo') / 'latest.md'\n"
        "write_current_pointer_text(target, 'ok')\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/mixed_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/mixed_writer.py:5" in result.stdout


def test_current_pointer_write_scanner_flags_write_bytes_and_path_open(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "binary_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "target = Path('charness-artifacts/demo') / 'latest.json'\n"
        "target.write_bytes(b'bad')\n"
        "with target.open('w', encoding='utf-8') as handle:\n"
        "    handle.write('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/binary_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/binary_writer.py:3" in result.stdout
    assert "scripts/binary_writer.py:4" in result.stdout


def test_current_pointer_write_scanner_resolves_simple_filename_constants(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "constant_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "target = Path('charness-artifacts/demo') / CURRENT\n"
        "target.write_text('bad', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/constant_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/constant_writer.py:4" in result.stdout


def test_current_pointer_write_scanner_resolves_builtin_open_constant_path(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    bad = script_dir / "constant_open_writer.py"
    bad.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "with open(Path('charness-artifacts/demo') / CURRENT, 'w', encoding='utf-8') as handle:\n"
        "    handle.write('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/constant_open_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/constant_open_writer.py:3" in result.stdout


def test_current_pointer_write_scanner_does_not_treat_local_shadow_as_pointer(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    ok = script_dir / "shadow_writer.py"
    ok.write_text(
        "from pathlib import Path\n"
        "CURRENT = 'latest.md'\n"
        "def write_record() -> None:\n"
        "    CURRENT = '2026-05-24-record.md'\n"
        "    target = Path('charness-artifacts/demo') / CURRENT\n"
        "    target.write_text('ok', encoding='utf-8')\n",
        encoding="utf-8",
    )
    init_git_repo(repo, ".gitignore", "scripts/shadow_writer.py")

    result = run_script("scripts/check_current_pointer_writes.py", "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 0


def test_current_pointer_write_scanner_constant_helpers_ignore_non_name_targets() -> None:
    tree = SCANNER.ast.parse("obj.attr = 'latest.md'\nCURRENT = 'latest.md'\ntarget = CURRENT\n")
    SCANNER._attach_parent_links(tree)
    first_assign = tree.body[0]

    assert SCANNER._resolved_string_constants(tree) == {"CURRENT": "latest.md"}
    assert SCANNER._scope_assigned_names(first_assign) == set()
    assert SCANNER._pointer_names_in_resolved(tree.body[2].value, {"CURRENT": "latest.md"}, set()) == {"latest.md"}


def test_current_pointer_write_scanner_prefilters_non_candidate_files(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    (script_dir / "ordinary_writer.py").write_text(
        "from pathlib import Path\nPath('notes.md').write_text('ok')\n",
        encoding="utf-8",
    )
    candidate = script_dir / "candidate_writer.py"
    candidate.write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(
        repo,
        ".gitignore",
        "scripts/ordinary_writer.py",
        "scripts/candidate_writer.py",
    )

    scanned: list[str] = []

    def fake_scan(repo_root: Path, path: Path, text: str) -> list[object]:
        del text
        scanned.append(path.relative_to(repo_root).as_posix())
        return []

    monkeypatch.setattr(SCANNER, "_scan_text", fake_scan)

    assert SCANNER.scan_repo(repo) == []
    assert scanned == ["scripts/candidate_writer.py"]


def test_current_pointer_write_scanner_skips_helper_during_repo_scan(
    tmp_path: Path,
    monkeypatch,
) -> None:
    repo = tmp_path / "repo"
    script_dir = repo / "scripts"
    script_dir.mkdir(parents=True)
    (repo / ".gitignore").write_text("\n", encoding="utf-8")
    (script_dir / "current_pointer_writer_lib.py").write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('helper')\n",
        encoding="utf-8",
    )
    (script_dir / "candidate_writer.py").write_text(
        "from pathlib import Path\n"
        "(Path('charness-artifacts/demo') / 'latest.md').write_text('bad')\n",
        encoding="utf-8",
    )
    init_git_repo(
        repo,
        ".gitignore",
        "scripts/current_pointer_writer_lib.py",
        "scripts/candidate_writer.py",
    )

    scanned: list[str] = []

    def fake_scan(repo_root: Path, path: Path, text: str) -> list[object]:
        del text
        scanned.append(path.relative_to(repo_root).as_posix())
        return []

    monkeypatch.setattr(SCANNER, "_scan_text", fake_scan)

    assert SCANNER.scan_repo(repo) == []
    assert scanned == ["scripts/candidate_writer.py"]


def test_current_pointer_write_scanner_prefilter_allows_spaced_open_call() -> None:
    assert SCANNER._could_write_current_pointer("target = 'latest.md'\npath.open ('w')\n")
