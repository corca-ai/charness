"""Does the handoff chunker resolve its scripts from an INSTALLED plugin layout?

Split from `test_handoff_chunker_parse.py` when the 2026-08-14 YAML migration pushed
that file one line past its code-line cap. The split is by SUBJECT, not to dodge the
cap (D33): these five build a fake `~/.agents`-style installed tree and assert that a
stage resolves the installed copy — including preferring it over a stale source copy.
That is a question about layout resolution and script provenance; the original file
asks whether handoff entries PARSE. They shared a file only because they share a
pipeline.

The migration is what made the seam visible: every migrated handoff script now
resolves its renderer through `scripts/yaml_output.py`, so a fake layout that omits it
fails at import rather than at the behavior under test — which is exactly the class of
fixture staleness these tests exist to catch.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml

from tests.repo_copy import REPO_COPY_IGNORE

REPO_ROOT = Path(__file__).resolve().parent.parent


def _copy_installed_runtime(tmp_path: Path) -> None:
    for rel in (
        "skill_runtime_bootstrap.py",
        "scripts/skill_runtime_bootstrap.py",
        "scripts/runtime_bootstrap.py",
        "scripts/script_timeout.py",
        "scripts/adapter_lib.py",
        "scripts/artifact_naming_lib.py",
        "scripts/simple_skill_adapter_lib.py",
        # Shipped by the installed layout too (plugins/charness/scripts/yaml_output.py):
        # every migrated handoff script resolves the renderer through it, so a fake
        # layout without it fails at import, not at the behavior under test.
        "scripts/yaml_output.py",
    ):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)


def _copy_installed_handoff_scripts(tmp_path: Path) -> Path:
    target = tmp_path / "skills" / "handoff" / "scripts"
    shutil.copytree(
        REPO_ROOT / "skills/public/handoff/scripts",
        target,
        ignore=REPO_COPY_IGNORE,
    )
    return target


def test_cli_with_issues_resolves_installed_issue_skill_layout(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    issue_scripts = tmp_path / "skills" / "issue" / "scripts"
    issue_scripts.mkdir(parents=True)
    (issue_scripts / "resolve_adapter.py").write_text(
        "def load_adapter(repo_root):\n"
        "    return {'data': {'default_org': 'corca-ai', 'default_repo': 'charness', "
        "'remote_name': 'origin', 'issue_backend': {'id': 'stub', 'binary': 'stub', "
        "'commands': {'list_open': ['list', '{repo}', '{limit}']}}}}\n",
        encoding="utf-8",
    )
    (issue_scripts / "issue_runtime.py").write_text(
        "def resolve_target(repo_root, target, adapter_data):\n"
        "    return {'full_name': 'corca-ai/charness'}\n"
        "def _backend_json(argv):\n"
        "    assert argv == ['stub', 'list', 'corca-ai/charness', '50']\n"
        "    return [{'number': 275, 'title': 'installed issue source', "
        "'labels': [], 'body': ''}]\n",
        encoding="utf-8",
    )
    # #555: handoff resolves backend commands through the `issue` skill's OWNER
    # (`issue_backend.try_resolve_op`) instead of reimplementing the rule, so the installed
    # layout must carry it. Copied REAL rather than stubbed: a stub here would agree with
    # whatever this test's author had in mind, and this test exists to prove the installed
    # cross-skill route actually works.
    for name in ("issue_backend.py", "issue_local_import.py"):
        shutil.copy2(REPO_ROOT / "skills/public/issue/scripts" / name, issue_scripts / name)
    docs = tmp_path / "docs"
    docs.mkdir()
    handoff = docs / "handoff.md"
    handoff.write_text("## Next Session\n\n1. Pick #184.\n\n## End\n", encoding="utf-8")

    result = subprocess.run(
        [
            "python3",
            str(handoff_scripts / "parse_handoff_entries.py"),
            "--repo-root",
            str(tmp_path),
            "--handoff-path",
            str(handoff),
            "--with-issues",
        ],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["issue_entry_count"] == 1
    assert payload["issue_source_diagnostic"] is None
    assert any(entry["referenced_issues"] == [275] for entry in payload["entries"])


def test_draft_goal_help_resolves_installed_achieve_skill_layout(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    achieve_scripts = tmp_path / "skills" / "achieve" / "scripts"
    achieve_scripts.mkdir(parents=True)
    (achieve_scripts / "goal_artifact_lib.py").write_text(
        "# Stub is enough for --help import-time portability proof.\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(handoff_scripts / "draft_goal_from_chunk.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--date" in result.stdout


def test_draft_goal_help_prefers_installed_achieve_over_stale_source(tmp_path):
    _copy_installed_runtime(tmp_path)
    handoff_scripts = _copy_installed_handoff_scripts(tmp_path)
    installed = tmp_path / "skills" / "achieve" / "scripts"
    source = tmp_path / "skills" / "public" / "achieve" / "scripts"
    installed.mkdir(parents=True)
    source.mkdir(parents=True)
    (installed / "goal_artifact_lib.py").write_text(
        "# Stub is enough for --help import-time portability proof.\n",
        encoding="utf-8",
    )
    (source / "goal_artifact_lib.py").write_text(
        "raise RuntimeError('stale source achieve loaded')\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["python3", str(handoff_scripts / "draft_goal_from_chunk.py"), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--date" in result.stdout
