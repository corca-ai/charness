from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.capability_catalog_artifact import persist_catalog
from tests.script_loader import load_script_module
from tests.script_main import run_loaded_script_main

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

SCANNER_SPEC = importlib.util.spec_from_file_location(
    "check_current_pointer_writes",
    ROOT / "scripts" / "check_current_pointer_writes.py",
)
assert SCANNER_SPEC is not None and SCANNER_SPEC.loader is not None
SCANNER = importlib.util.module_from_spec(SCANNER_SPEC)
sys.modules[SCANNER_SPEC.name] = SCANNER
SCANNER_SPEC.loader.exec_module(SCANNER)

HITL_SYNC_REVIEW_ARTIFACT = load_script_module(
    "tests.quality_gates.current_pointer_hitl_sync_review_artifact",
    ROOT / "skills/public/hitl/scripts/sync_review_artifact.py",
)


def run_current_pointer_scanner(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_current_pointer_writes.py", *args])
    code = SCANNER.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


def run_hitl_sync_review_artifact(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["sync_review_artifact.py", *args])
    code = HITL_SYNC_REVIEW_ARTIFACT.main() or 0
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=code, stdout=captured.out, stderr=captured.err)


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


def test_capability_catalog_noops_when_canonical_inventory_unchanged(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
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

    first = persist_catalog(repo, inventory)
    output = repo / "charness-artifacts" / "capability-catalog"
    first_text = (output / "latest.json").read_text(encoding="utf-8")
    second = persist_catalog(repo, inventory)

    assert first["updated"] is True
    assert second["updated"] is False
    assert (output / "latest.json").read_text(encoding="utf-8") == first_text


def test_hitl_sync_artifact_does_not_follow_symlinked_latest(tmp_path: Path, monkeypatch, capsys) -> None:
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

    sync = run_hitl_sync_review_artifact(
        monkeypatch,
        capsys,
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


def test_current_pointer_write_scanner_flags_direct_expression_write(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

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


def test_current_pointer_write_scanner_skips_generated_plugin_mirrors(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

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


def test_current_pointer_write_scanner_does_not_exempt_mixed_helper_file(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/mixed_writer.py:5" in result.stdout


def test_current_pointer_write_scanner_flags_write_bytes_and_path_open(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/binary_writer.py:3" in result.stdout
    assert "scripts/binary_writer.py:4" in result.stdout


def test_current_pointer_write_scanner_resolves_simple_filename_constants(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/constant_writer.py:4" in result.stdout


def test_current_pointer_write_scanner_resolves_builtin_open_constant_path(tmp_path: Path, monkeypatch, capsys) -> None:
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

    assert result.returncode == 1
    assert "scripts/constant_open_writer.py:3" in result.stdout


def test_current_pointer_write_scanner_does_not_treat_local_shadow_as_pointer(
    tmp_path: Path,
    monkeypatch,
    capsys,
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

    result = run_current_pointer_scanner(monkeypatch, capsys, "--repo-root", str(repo), "--require-empty")

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


def _pointer_write_fixture(repo: Path, relative: str, body: str) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


_LITERAL_WRITE = (
    "from pathlib import Path\n"
    "def write(root):\n"
    '    (root / "charness-artifacts" / "quality" / "latest.md").write_text("x")\n'
)
_COMPUTED_WRITE = (
    "from pathlib import Path\n"
    "def write(root, ext='md'):\n"
    '    (root / "charness-artifacts" / f"latest.{ext}").write_text("x")\n'
)


def test_pointer_write_scan_covers_skills_shared(tmp_path: Path) -> None:
    """D9 regression: `skills/shared` was absent from `SCAN_ROOTS`, so the gate
    reported clean over a scope that excluded it.

    Confirmed with the discriminating control: an IDENTICAL violation was caught
    under `scripts/` and `skills/public/` and invisible under `skills/shared/`."""
    repo = tmp_path / "repo"
    for relative in (
        "scripts/writer.py",
        "skills/public/x/scripts/writer.py",
        "skills/shared/scripts/writer.py",
    ):
        _pointer_write_fixture(repo, relative, _LITERAL_WRITE)

    findings = SCANNER.scan_repo(repo)
    flagged = {finding.path for finding in findings}

    assert "skills/shared/scripts/writer.py" in flagged
    assert "scripts/writer.py" in flagged
    assert "skills/public/x/scripts/writer.py" in flagged


def test_pointer_write_scan_refuses_silence_on_a_computed_name(tmp_path: Path) -> None:
    """The other half of D9: the gate matched string constants only, so
    `f"latest.{ext}"` produced a path it could not see — and the prefilter
    required the literal `latest.md` in the text, so such a file never even
    reached the AST scan. A computed pointer name is a scope this gate cannot
    establish, and it now says so instead of reporting clean."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(repo, "scripts/computed.py", _COMPUTED_WRITE)

    findings = SCANNER.scan_repo(repo)

    assert len(findings) == 1
    assert findings[0].path == "scripts/computed.py"
    assert "BUILT at runtime" in findings[0].reason


def test_pointer_write_scan_still_passes_a_clean_tree(tmp_path: Path) -> None:
    """Falsifiable counterpart: neither widening flags an ordinary write."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(
        repo,
        "skills/shared/scripts/ordinary.py",
        "from pathlib import Path\ndef write(root):\n    (root / 'notes.md').write_text('x')\n",
    )

    assert SCANNER.scan_repo(repo) == []


def test_computed_pointer_name_is_caught_through_an_assigned_variable(tmp_path: Path) -> None:
    """The computed detector originally saw only the single-expression form, but
    the two-statement form is the idiom this repo actually writes — and its
    LITERAL twin was already handled, so covering one and not the other left the
    dominant shape invisible.

    Also pins the concatenation case: Python parses `a + b + c`
    left-associatively, so in `str(out) + "/latest." + ext` the pointer-ish
    literal is only ever a RIGHT operand and inspecting `left` alone missed it."""
    repo = tmp_path / "repo"
    shapes = {
        "assigned.py": (
            "from pathlib import Path\ndef write(root, ext='md'):\n"
            '    target = root / "charness-artifacts" / f"latest.{ext}"\n'
            '    target.write_text("x")\n'
        ),
        "concat.py": (
            "from pathlib import Path\ndef write(out, ext='md'):\n"
            '    Path(str(out) + "/latest." + ext).write_text("x")\n'
        ),
        "keyword_mode.py": (
            "from pathlib import Path\ndef write(root, ext='md'):\n"
            '    target = root / f"latest.{ext}"\n'
            '    target.open(mode="w").write("x")\n'
        ),
    }
    for name, body in shapes.items():
        _pointer_write_fixture(repo, f"scripts/{name}", body)

    flagged = {finding.path for finding in SCANNER.scan_repo(repo)}

    assert flagged == {f"scripts/{name}" for name in shapes}


def test_computed_detector_leaves_an_ordinary_assigned_write_alone(tmp_path: Path) -> None:
    """Falsifiable counterpart for the widened detector: an assigned path that is
    not a pointer name is untouched, and so is an f-string that merely mentions
    `latest` in prose."""
    repo = tmp_path / "repo"
    _pointer_write_fixture(
        repo,
        "scripts/ordinary.py",
        "from pathlib import Path\ndef write(root, n=1):\n"
        '    target = root / "notes.md"\n'
        '    target.write_text(f"latest sample {n}")\n',
    )

    assert SCANNER.scan_repo(repo) == []


def test_computed_detector_catches_a_bare_stem_head_and_ignores_a_read_open() -> None:
    """Two narrow edges of the D9 detector, pinned directly on the helpers.

    The extension can live entirely in the interpolated half — `"latest" + ext`
    or `f"latest{suffix}"` leaves the literal head as the bare stem with no dot,
    which the `head == "latest."` / `startswith("latest.")` tests both miss. And
    `Path.open()` in a READ mode is not a write at all: dispatching it to the
    same target as `write_text` would make every pointer read a finding."""
    bare_stem = SCANNER.ast.parse('name = "latest" + ext\n').body[0].value
    assert SCANNER._computed_pointer_name_in(bare_stem) == "latest.<computed>"

    dotted = SCANNER.ast.parse('name = f"latest.{ext}"\n').body[0].value
    assert SCANNER._computed_pointer_name_in(dotted) == "latest.<computed>"

    unrelated = SCANNER.ast.parse('name = "notes" + ext\n').body[0].value
    assert SCANNER._computed_pointer_name_in(unrelated) is None

    read_open = SCANNER.ast.parse('path.open("r")\n').body[0].value
    assert SCANNER._write_target_node(read_open) is None

    write_open = SCANNER.ast.parse('path.open("w")\n').body[0].value
    assert SCANNER._write_target_node(write_open) is not None


REFRESH_CURRENT_POINTER = load_script_module(
    "refresh_current_pointer_under_test", ROOT / "scripts" / "refresh_current_pointer.py"
)


def _refresh_pointer(repo: Path, record: Path):
    """In-process, not a subprocess: the boundary-bypass ratchet classifies this
    crossing as convertible, and the verdict under test is the returned payload rather
    than any process-level behavior."""
    return run_loaded_script_main(
        "refresh_current_pointer.py",
        REFRESH_CURRENT_POINTER,
        "--repo-root", str(repo),
        "--skill-id", "gather",
        "--record-artifact-path", f"charness-artifacts/gather/{record.name}",
        "--execute",
    )


def test_refresh_current_pointer_refuses_an_empty_record(tmp_path: Path) -> None:
    """Sweep row S19's destructive half, at the surface that actually owns it.

    The gather writer was fixed to refuse empty content, but `is_file()` was the only
    content check in `scripts/refresh_current_pointer.py` — the GENERIC pointer writer
    every skill routes through — and a 0-byte file passes it. Repointing `latest.md` at
    nothing destroys the asset other sessions read as current and reports
    `{"status": "updated"}`, which is the same wrong output one command over."""
    repo = tmp_path / "repo"
    gather = repo / "charness-artifacts" / "gather"
    gather.mkdir(parents=True)
    real = gather / "2026-05-09-real.md"
    real.write_text("# Real asset\n\nGathered text.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.symlink_to(real.name)

    for label, body in (("empty", ""), ("whitespace-only", "  \n\n\t\n")):
        record = gather / f"2026-05-10-{label}.md"
        record.write_text(body, encoding="utf-8")
        result = _refresh_pointer(repo, record)
        assert result.returncode == 1, label
        payload = json.loads(result.stdout)
        assert payload["status"] == "blocked", label
        assert "record artifact is empty" in payload["reason"], label
        assert payload["would_update"] is False, label
        assert os.readlink(pointer) == real.name, f"pointer repointed by the {label} record"

    # Falsifiable counterpart: a record with real bytes still repoints the pointer, so
    # the refusal is about emptiness and not about the writer having been broken.
    fresh = gather / "2026-05-11-fresh.md"
    fresh.write_text("# Fresh asset\n\nMore gathered text.\n", encoding="utf-8")
    ok = _refresh_pointer(repo, fresh)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert os.readlink(pointer) == fresh.name


def test_refresh_current_pointer_refuses_an_unreadable_record(tmp_path: Path) -> None:
    """`is_file()` is not `can_read()`.

    The emptiness guard above reads the record to judge it. A record that exists but
    cannot be READ (mode 000, a stale mount, an ACL) raises inside that read, and an
    unhandled raise on the generic pointer writer either crashes the caller or — worse,
    if the read were moved after the write — leaves `latest.md` already repointed. The
    refusal has to be a payload, on the same channel as every other blocked reason, so
    the caller distinguishes "the pointer was not moved" from "the tool fell over".
    """
    repo = tmp_path / "repo"
    gather = repo / "charness-artifacts" / "gather"
    gather.mkdir(parents=True)
    real = gather / "2026-05-09-real.md"
    real.write_text("# Real asset\n\nGathered text.\n", encoding="utf-8")
    pointer = gather / "latest.md"
    pointer.symlink_to(real.name)

    unreadable = gather / "2026-05-12-unreadable.md"
    unreadable.write_text("# Has content\n\nBut cannot be read.\n", encoding="utf-8")
    unreadable.chmod(0o000)
    if os.access(unreadable, os.R_OK):  # running as root: the mode is not a barrier
        pytest.skip("cannot make a file unreadable for this user")

    try:
        result = _refresh_pointer(repo, unreadable)
    finally:
        unreadable.chmod(0o644)

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert "could not be read" in payload["reason"]
    assert payload["would_update"] is False
    assert os.readlink(pointer) == real.name, "pointer repointed by an unreadable record"
