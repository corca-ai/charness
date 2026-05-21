from __future__ import annotations

import hashlib
import importlib.util
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
