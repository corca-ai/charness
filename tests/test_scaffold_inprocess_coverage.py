"""In-process coverage for the recurring subprocess-only scaffold CLI class.

Background (issue history #219 -> #251 -> #260 -> the #306 self-healing loop):
the scheduled mutation gate's *changed-line* signal blocks when a changed line
sits on a statement coverage.py never recorded as executed. The recurring
offenders are the public-skill ``scaffold_*_artifact.py`` CLI scripts, which
were exercised ONLY through ``subprocess.run(["python3", SCAFFOLD, ...])`` in
``tests/test_*_scaffold.py``. Even when the subprocess child's coverage is
captured, those tests only walk the ``--json`` happy path with an ancestor
``scripts/`` validator present, so two branches per scaffold stay uncovered:

  * the non-``--json`` ``main()`` print path, and
  * the ``repo_local`` validator fallback + its ``FileNotFoundError`` raise
    (only reachable when no ancestor ``scripts/<validator>.py`` exists).

A changed line landing on either branch reads as uncovered and re-files the
auto-issue. These tests import each scaffold IN-PROCESS (so the normal
pytest+coverage run records the lines) and drive BOTH the happy and fallback
branches, making the changed-line coverage probe honest for this class without
demoting the gate. The companion gate test
``tests/quality_gates/test_scaffold_changed_line_coverage.py`` asserts the
recurring lines now read as covered through the gate's own coverage probe.
"""

from __future__ import annotations

import importlib.util
import inspect
import io
import json
import os
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]

# retro/critique/ideation pass write_artifact_path to validator_command;
# debug/handoff/quality take only repo_root.
SCAFFOLDS = [
    "critique",
    "debug",
    "handoff",
    "ideation",
    "quality",
    "retro",
]

# Scaffolds whose artifact is a `latest.md` current-pointer symlink. Their
# payload_for routes through _current_pointer_write_path / _portable_path, whose
# symlink branches the subprocess happy-path tests never reach.
CURRENT_POINTER_SCAFFOLDS = ["debug", "quality"]


def _scaffold_path(slug: str) -> Path:
    return REPO_ROOT / "skills" / "public" / slug / "scripts" / f"scaffold_{slug}_artifact.py"


def _load_scaffold(slug: str):
    """Import the real scaffold module by path so coverage attributes its lines."""
    path = _scaffold_path(slug)
    spec = importlib.util.spec_from_file_location(f"scaffold_{slug}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _expected_validator_names(module) -> tuple[str, ...]:
    """Parse the validator filenames the scaffold's repo_local fallback looks for."""
    source = inspect.getsource(module.validator_command)
    match = re.search(r"for script_name in \(([^)]*)\)", source)
    assert match, "validator_command must iterate a script_name tuple"
    return tuple(re.findall(r"[\"']([^\"']+\.py)[\"']", match.group(1)))


def _call_validator(module, repo_root: Path) -> str:
    """validator_command arity differs across scaffolds; call it either way."""
    params = inspect.signature(module.validator_command).parameters
    if len(params) >= 2:
        return module.validator_command(repo_root, "charness-artifacts/x/2026-06-06-x.md")
    return module.validator_command(repo_root)


@pytest.mark.parametrize("slug", SCAFFOLDS)
def test_scaffold_main_runs_both_output_branches_in_process(slug: str, tmp_path: Path, monkeypatch) -> None:
    module = _load_scaffold(slug)
    repo = tmp_path / "consumer"
    repo.mkdir()

    # Non-json branch: writes the rendered template to stdout.
    monkeypatch.setattr(sys, "argv", ["scaffold", "--repo-root", str(repo)])
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    assert module.main() == 0
    template_text = out.getvalue()
    assert template_text.startswith("# "), template_text[:40]
    assert template_text.rstrip().endswith(template_text.rstrip().splitlines()[-1])

    # JSON branch: emits a payload with the canonical scaffold keys.
    monkeypatch.setattr(sys, "argv", ["scaffold", "--repo-root", str(repo), "--json"])
    out_json = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out_json)
    assert module.main() == 0
    payload = json.loads(out_json.getvalue())
    assert payload["template"].startswith("# ")
    assert "validator_command" in payload
    # The non-json template and the json payload template must agree.
    assert payload["template"] == template_text


@pytest.mark.parametrize("slug", SCAFFOLDS)
def test_scaffold_validator_command_repo_local_fallback(slug: str, tmp_path: Path) -> None:
    """Cover the repo_local fallback: no ancestor scripts/<validator>.py exists.

    The subprocess tests always find an ancestor validator (the real repo), so
    this branch never executes there. Pointing the module's __file__ at an
    isolated directory forces the ancestor walk to miss, exercising the
    fallback and its FileNotFoundError raise in the ORIGINAL file.
    """
    module = _load_scaffold(slug)
    isolated = tmp_path / "deep" / "nest" / "scaffold.py"
    isolated.parent.mkdir(parents=True)
    module.__file__ = str(isolated)

    validator_names = _expected_validator_names(module)
    assert validator_names

    # repo_local present -> fallback returns a `scripts/<validator>` command.
    repo = tmp_path / "consumer"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / validator_names[0]).write_text("# stub\n", encoding="utf-8")
    command = _call_validator(module, repo)
    assert f"python3 scripts/{validator_names[0]}" in command

    # No local validator anywhere -> the documented FileNotFoundError raise.
    empty_repo = tmp_path / "empty"
    empty_repo.mkdir()
    with pytest.raises(FileNotFoundError):
        _call_validator(module, empty_repo)


@pytest.mark.parametrize("slug", CURRENT_POINTER_SCAFFOLDS)
def test_scaffold_current_pointer_symlink_branches(slug: str, tmp_path: Path) -> None:
    """Cover _current_pointer_write_path / _portable_path symlink branches.

    The subprocess happy path scaffolds into a fresh repo where ``latest.md``
    does not yet exist, so only the non-symlink return is reached. Pre-seeding a
    relative then an absolute ``latest.md`` symlink drives the resolution
    branches the changed-line probe otherwise reports as uncovered.
    """
    module = _load_scaffold(slug)
    repo = tmp_path / "consumer"
    repo.mkdir()

    # Non-symlink: artifact_path returned verbatim with the current_pointer role.
    plain = module.payload_for(repo, title=None)
    assert plain["write_artifact_role"] == "current_pointer"
    assert plain["current_pointer_symlink_target"] is None

    output_dir = repo / Path(plain["artifact_path"]).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    real = output_dir / "2026-06-06-record.md"
    real.write_text("# record\n", encoding="utf-8")
    link = output_dir / "latest.md"

    # Relative symlink: resolves to the target's portable repo-relative path.
    os.symlink("2026-06-06-record.md", link)
    relative = module.payload_for(repo, title=None)
    assert relative["write_artifact_role"] == "current_pointer_target"
    assert relative["current_pointer_symlink_target"] == "2026-06-06-record.md"
    assert relative["write_artifact_path"] == real.relative_to(repo).as_posix()

    # Absolute symlink: same resolved write path via the absolute target branch.
    link.unlink()
    os.symlink(str(real), link)
    absolute = module.payload_for(repo, title=None)
    assert absolute["write_artifact_role"] == "current_pointer_target"
    assert absolute["write_artifact_path"] == real.relative_to(repo).as_posix()
