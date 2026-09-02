"""The subprocess form gate: one spawn primitive, refused everywhere else (#768)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.gates import check_subprocess_form as gate
from tests.quality_gates.support import ROOT


def _seed(tmp_path: Path, body: str) -> Path:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "scripts" / "core").mkdir(parents=True, exist_ok=True)
    (repo / "scripts" / "core" / "subprocess_guard.py").write_text(
        "import subprocess\n\ndef run_process(command, *, cwd):\n    return subprocess.run(command, cwd=cwd)\n",
        encoding="utf-8",
    )
    (repo / "scripts" / "probe.py").write_text(body, encoding="utf-8")
    return repo


@pytest.mark.parametrize(
    "body, form",
    [
        ('import subprocess\nsubprocess.run(["git", "status"])\n', "subprocess.run"),
        ('import subprocess\nsubprocess.Popen(["git"])\n', "subprocess.Popen"),
        ('from subprocess import check_output\ncheck_output(["git"])\n', "subprocess.check_output"),
        ('import os\nos.system("git status")\n', "os.system"),
    ],
)
def test_seeded_direct_spawn_turns_the_gate_red(
    tmp_path: Path, body: str, form: str, capsys
) -> None:
    repo = _seed(tmp_path, body)
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "scripts/probe.py:2" in err
    assert form in err
    assert "subprocess_guard" not in err.split("probe.py")[0]


def test_guard_module_itself_is_exempt_and_clean_tree_is_green(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, "from runtime_bootstrap import x\n")
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "2 production file(s)" in capsys.readouterr().out


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "top_level.py").write_text("VALUE = 1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path)])


def test_live_repo_spawns_only_through_the_guard() -> None:
    # The acceptance line of #768: zero `subprocess.` call sites outside the guard.
    failures = [
        failure
        for path in gate._iter_scan_paths(ROOT, require_git=True)
        for failure in gate.check_file(ROOT, path)
    ]
    assert failures == []
