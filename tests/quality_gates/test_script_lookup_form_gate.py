"""The script lookup form gate: one layout resolver, refused everywhere else (#777)."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from scripts.gates import check_script_lookup_form as gate
from tests.quality_gates.support import ROOT


def _seed(tmp_path: Path, body: str, *, where: str = "scripts/probe.py") -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts" / "core").mkdir(parents=True)
    (repo / "scripts" / "core" / "repo_layout.py").write_text(
        'def find_repo_script(root, name):\n    return next(iter((root / "scripts").rglob(name)), None)\n',
        encoding="utf-8",
    )
    target = repo / where
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return repo


@pytest.mark.parametrize(
    "body",
    [
        'from pathlib import Path\nROOT = Path(".")\nfound = sorted((ROOT / "scripts").rglob("yaml_output.py"))\n',
        'from pathlib import Path\nSCRIPTS = Path("scripts")\nname = "x"\nfound = SCRIPTS.rglob(f"{name}.py")\n',
        'from pathlib import Path\nscripts_root = Path("scripts")\nname = "x.py"\nfound = scripts_root.glob(name)\n',
    ],
)
def test_seeded_by_name_lookup_turns_the_gate_red(tmp_path: Path, body: str, capsys) -> None:
    repo = _seed(tmp_path, body)
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "scripts/probe.py:" in err
    assert "repo_script or find_repo_script" in err
    assert "repo_layout.py:" not in err


def test_a_lookup_in_a_test_file_is_refused_too(tmp_path: Path, capsys) -> None:
    repo = _seed(
        tmp_path,
        'from pathlib import Path\nROOT = Path(".")\nname = "x.py"\nfound = (ROOT / "scripts").rglob(name)\n',
        where="tests/test_probe.py",
    )
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "tests/test_probe.py:4" in capsys.readouterr().err


@pytest.mark.parametrize(
    "body",
    [
        'from pathlib import Path\nfor p in Path("scripts").rglob("*.py"):\n    pass\n',
        'from pathlib import Path\nscripts_root = Path("scripts")\nfor p in scripts_root.glob("*"):\n    pass\n',
        'from pathlib import Path\nrepo_root = Path(".")\npattern = "x"\nfor p in repo_root.glob(pattern):\n    pass\n',
    ],
)
def test_enumerations_and_non_script_trees_stay_green(tmp_path: Path, body: str) -> None:
    repo = _seed(tmp_path, body)
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_the_resolver_itself_is_exempt(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, "VALUE = 1\n")
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "2 file(s)" in capsys.readouterr().out


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "top_level.py").write_text("VALUE = 1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path)])


def test_live_repo_asks_only_the_resolver() -> None:
    # The acceptance line of #777: zero by-name script searches outside the resolver.
    failures = [
        failure
        for path in gate._iter_scan_paths(ROOT, require_git=True)
        for failure in gate.check_file(ROOT, path)
    ]
    assert failures == []


def test_an_unparseable_file_is_reported_not_skipped(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, "def broken(:\n")
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "scripts/probe.py: cannot parse" in capsys.readouterr().err


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch) -> None:
    repo = _seed(tmp_path, "VALUE = 1\n")
    monkeypatch.setattr(sys, "argv", ["check_script_lookup_form.py", "--repo-root", str(repo)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(ROOT / "scripts/gates/check_script_lookup_form.py"), run_name="__main__")
    assert excinfo.value.code == 0


def test_bootstrap_shim_inserts_the_repo_root_when_it_is_absent(monkeypatch) -> None:
    # The shim's insert branch runs only in a process where the root is not yet
    # on sys.path, which pytest never is; strip it so the branch is exercised.
    stripped = [entry for entry in sys.path if entry and Path(entry).resolve() != ROOT.resolve()]
    monkeypatch.setattr(sys, "path", stripped)
    gate._load_repo_runtime_bootstrap()
    assert str(ROOT.resolve()) in sys.path or str(ROOT) in sys.path
