"""In-process coverage for the recurring subprocess-only scaffold CLI class.

Background (issue history #219 -> #251 -> #260 -> the #306 self-healing loop):
the scheduled mutation gate's *changed-line* signal blocks when a changed line
sits on a statement coverage.py never recorded as executed. The recurring
offenders are the public-skill ``scaffold_*_artifact.py`` CLI scripts, which
were exercised ONLY through ``subprocess.run(["python3", SCAFFOLD, ...])`` in
``tests/test_*_scaffold.py``. Even when the subprocess child's coverage is
captured, those tests walk the happy path with an ancestor ``scripts/``
validator present, so the ``repo_local`` validator fallback + its
``FileNotFoundError`` raise (only reachable when no ancestor
``scripts/<validator>.py`` exists) stays uncovered.

A changed line landing on that branch reads as uncovered and re-files the
auto-issue. These tests import each scaffold IN-PROCESS (so the normal
pytest+coverage run records the lines) and drive the ``main()`` output path and
the fallback branch, making the changed-line coverage probe honest for this
class without demoting the gate. The companion gate test
``tests/quality_gates/test_scaffold_changed_line_coverage.py`` asserts the
recurring lines now read as covered through the gate's own coverage probe.
"""

from __future__ import annotations

import datetime as dt
import inspect
import io
import os
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module

REPO_ROOT = Path(__file__).resolve().parents[1]

# retro/critique/ideation pass write_artifact_path to validator_command;
# debug/quality take only repo_root.
SCAFFOLDS = [
    "critique",
    "debug",
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
    return load_script_module(f"scaffold_{slug}_inproc", path)


def _expected_validator_names(module) -> tuple[str, ...]:
    """Return the validator filenames the scaffold's repo_local fallback looks for."""
    names = getattr(module, "VALIDATOR_SCRIPT_NAMES", ())
    assert names, "scaffold must expose VALIDATOR_SCRIPT_NAMES"
    return tuple(names)


def _call_validator(module, repo_root: Path) -> str:
    """validator_command arity differs across scaffolds; call it either way."""
    params = inspect.signature(module.validator_command).parameters
    if len(params) >= 2:
        return module.validator_command(repo_root, "charness-artifacts/x/2026-06-06-x.md")
    return module.validator_command(repo_root)


@pytest.mark.parametrize("slug", SCAFFOLDS)
def test_scaffold_main_emits_yaml_payload_in_process(slug: str, tmp_path: Path, monkeypatch) -> None:
    module = _load_scaffold(slug)
    repo = tmp_path / "consumer"
    repo.mkdir()

    # main() has a single output path: it always emits the full structured
    # payload as YAML (the run reads `template` plus the sibling contract fields).
    # There is no flag and no bare rendered-template branch to cover.
    monkeypatch.setattr(sys, "argv", ["scaffold", "--repo-root", str(repo)])
    out = io.StringIO()
    monkeypatch.setattr(sys, "stdout", out)
    assert module.main() == 0
    payload = yaml.safe_load(out.getvalue())
    assert payload["template"].startswith("# "), payload["template"][:40]
    assert "validator_command" in payload


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


# `ideation` is deliberately self-contained (no adapter, no scripts package),
# so it carries no `_load_skill_runtime_bootstrap()` shim to force -- unlike the
# other five scaffolds, which all resolve an adapter through SKILL_RUNTIME.
SCAFFOLDS_WITH_BOOTSTRAP_SHIM = [slug for slug in SCAFFOLDS if slug != "ideation"]


@pytest.mark.parametrize("slug", SCAFFOLDS_WITH_BOOTSTRAP_SHIM)
def test_scaffold_shim_not_found_raises_import_error(slug: str, tmp_path: Path, monkeypatch) -> None:
    """Cover the canonical bootstrap shim's `raise ImportError` guard (mirrors
    ``tests/test_adapter_shim_inprocess_coverage.py``'s forcing technique). Every
    shim-carrying scaffold has its own copy of ``_load_skill_runtime_bootstrap()``,
    and the happy path always finds ``skill_runtime_bootstrap.py`` walking up from
    THIS repo, so the not-found branch never executes unless ``__file__`` is
    pointed at an isolated tree with no ancestor bootstrap.
    """
    module = _load_scaffold(slug)
    isolated = tmp_path / "deep" / "nest" / "scaffold.py"
    isolated.parent.mkdir(parents=True)
    monkeypatch.setattr(module, "__file__", str(isolated))
    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        module._load_skill_runtime_bootstrap()


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

    # Relative symlink: resolves to the target's portable repo-relative path, which is what
    # this test covers. The payload no longer WRITES there — the seeded record belongs to
    # subject `record` and the invocation declares none, so both families route to their own
    # record and report the pointer's target as declined. The resolution branch under test is
    # still exercised, and `refused_write_artifact_path` is where its result now surfaces.
    os.symlink("2026-06-06-record.md", link)
    relative = module.payload_for(repo, title=None)
    assert relative["current_pointer_symlink_target"] == "2026-06-06-record.md"
    assert relative["refused_write_artifact_path"] == real.relative_to(repo).as_posix()
    assert relative["write_artifact_path"] != real.relative_to(repo).as_posix()

    # Absolute symlink: same resolved target via the absolute-target branch.
    link.unlink()
    os.symlink(str(real), link)
    absolute = module.payload_for(repo, title=None)
    assert absolute["refused_write_artifact_path"] == real.relative_to(repo).as_posix()

    # Declaring the seeded record's subject reaches the in-place branch, so the
    # `current_pointer_target` role stays covered rather than becoming unreachable. Dated
    # TODAY, because the two families key differently on purpose: `quality` adds the record
    # date to its subject key (its recorded defect is a review written over the previous day's
    # record), so a same-slug record from another day is correctly still not this review.
    mine = output_dir / f"{dt.date.today().isoformat()}-record.md"
    mine.write_text("# record\n", encoding="utf-8")
    link.unlink()
    os.symlink(mine.name, link)
    owned = module.payload_for(repo, title=None, subject="record")
    assert owned["write_artifact_role"] == "current_pointer_target"
    assert owned["write_artifact_path"] == mine.relative_to(repo).as_posix()
    assert owned["write_artifact_subject_match"] == "match"
