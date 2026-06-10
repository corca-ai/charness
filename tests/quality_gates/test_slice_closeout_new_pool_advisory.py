"""New-mutation-pool-module closeout advisory.

A slice that ADDS a new pool module must get a pre-bundle nudge naming the
early changed-line self-check, so the producer confirms instead of
discovering at the bundle boundary.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from scripts import sample_mutation_files
from scripts.slice_closeout_advisories import _added_vs_base, advise_new_pool_module

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_added_vs_base_detects_new_and_existing_paths() -> None:
    paths = ["scripts/run_slice_closeout.py", "scripts/not_a_real_module_344.py"]
    added = _added_vs_base(REPO_ROOT, paths)
    assert "scripts/not_a_real_module_344.py" in added
    assert "scripts/run_slice_closeout.py" not in added


def test_added_vs_base_degrades_without_base_ref(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "--quiet", str(tmp_path)], check=True)
    assert _added_vs_base(tmp_path, ["anything.py"]) == []


def test_advisory_fires_for_new_eligible_module(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(sample_mutation_files, "list_eligible", lambda repo_root: ["scripts/fake_new_module.py"])
    monkeypatch.setattr(
        "scripts.slice_closeout_advisories._added_vs_base",
        lambda repo_root, paths, base="origin/main": ["scripts/fake_new_module.py"],
    )
    advise_new_pool_module(REPO_ROOT, ["scripts/fake_new_module.py", "docs/x.md"])
    err = capsys.readouterr().err
    assert "new mutation-pool module(s) added" in err
    assert "scripts/fake_new_module.py" in err
    assert "CONFIRMS instead of discovering" in err
    assert "implementation-discipline.md" in err


def test_advisory_silent_without_python_changes(capsys) -> None:
    advise_new_pool_module(REPO_ROOT, ["docs/handoff.md"])
    assert capsys.readouterr().err == ""


def test_advisory_silent_for_existing_pool_module(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(
        "scripts.slice_closeout_advisories._added_vs_base",
        lambda repo_root, paths, base="origin/main": [],
    )
    advise_new_pool_module(REPO_ROOT, ["scripts/run_slice_closeout.py"])
    assert capsys.readouterr().err == ""


def test_advisory_silent_for_new_non_pool_python(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    monkeypatch.setattr(sample_mutation_files, "list_eligible", lambda repo_root: [])
    monkeypatch.setattr(
        "scripts.slice_closeout_advisories._added_vs_base",
        lambda repo_root, paths, base="origin/main": ["conftest_only_helper.py"],
    )
    advise_new_pool_module(REPO_ROOT, ["conftest_only_helper.py"])
    assert capsys.readouterr().err == ""


def test_run_slice_closeout_wires_the_advisory_call_site() -> None:
    # A deleted call site would pass the function-level tests; pin both the
    # rebinding and the invocation beside the sibling advisories.
    from scripts import run_slice_closeout as rsc
    from scripts import slice_closeout_advisories as advisories

    assert rsc.advise_new_pool_module is advisories.advise_new_pool_module
    source = (REPO_ROOT / "scripts" / "run_slice_closeout.py").read_text(encoding="utf-8")
    assert 'advise_new_pool_module(repo_root, payload["changed_paths"])' in source
