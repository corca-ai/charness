"""The module-eviction form gate: a raw `sys.modules` eviction in tests/ is refused (#781)."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts.gates import check_module_eviction_form as gate
from tests.quality_gates.support import ROOT


def _seed(tmp_path: Path, body: str, *, baseline: dict[str, int] | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_probe.py").write_text(body, encoding="utf-8")
    if baseline is not None:
        record = repo / gate.DEFAULT_BASELINE_REL
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(
            json.dumps(
                {"schema": gate.BASELINE_SCHEMA, "files": baseline, "total": sum(baseline.values())}
            ),
            encoding="utf-8",
        )
    return repo


@pytest.mark.parametrize(
    "body",
    [
        'import sys\n\n\ndef test_x(monkeypatch):\n    monkeypatch.delitem(sys.modules, "scripts.core.x")\n',
        'import sys\n\n\ndef test_x():\n    sys.modules.pop("scripts.core.x", None)\n',
        'import sys\n\n\ndef test_x():\n    del sys.modules["scripts.core.x"]\n',
        'from sys import modules\n\n\ndef test_x():\n    del modules["scripts.core.x"]\n',
        'from sys import modules as m\n\n\ndef test_x():\n    m.pop("scripts.core.x", None)\n',
    ],
)
def test_a_seeded_raw_eviction_turns_the_gate_red(tmp_path: Path, body: str, capsys) -> None:
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "tests/test_probe.py: 1 raw sys.modules eviction(s), baseline 0" in err
    assert "evict through tests/module_eviction.py" in err


@pytest.mark.parametrize(
    "body",
    [
        # the owner's own form, which is what the gate is pushing every site onto
        "from tests.module_eviction import evict_module\n\n\ndef test_x(monkeypatch):\n"
        '    evict_module(monkeypatch, "scripts.core.x")\n',
        # adding a throwaway probe name is not an eviction; pytest deletes it again
        'import sys\n\n\ndef test_x(monkeypatch):\n    monkeypatch.setitem(sys.modules, "probe", 1)\n',
        # reading the table is not an eviction
        'import sys\n\n\ndef test_x():\n    assert "sys" in sys.modules\n',
        # a `pop` on something that is not `sys.modules`
        'def test_x():\n    registry = {"a": 1}\n    registry.pop("a", None)\n',
        # a seeded child body is a string literal, not a call
        "CHILD = \"import sys\\ndel sys.modules['x']\\n\"\n\n\ndef test_x():\n    assert CHILD\n",
    ],
)
def test_the_safe_forms_are_not_sites(tmp_path: Path, body: str) -> None:
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_the_owner_module_is_not_scanned(tmp_path: Path) -> None:
    """`tests/module_eviction.py` is where the raw calls are SUPPOSED to live."""
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    owner = repo / gate.OWNER_REL
    owner.write_text(
        "import sys\n\n\ndef evict(name):\n    sys.modules.pop(name, None)\n", encoding="utf-8"
    )
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_fixture_children_are_not_scanned(tmp_path: Path) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    child = repo / "tests" / "fixtures" / "evicting_child.py"
    child.parent.mkdir()
    child.write_text('import sys\n\ndel sys.modules["x"]\n', encoding="utf-8")
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "top_level.py").write_text("VALUE = 1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path)])


def test_live_repo_has_no_raw_eviction_site() -> None:
    """#781 folded every raw site onto the owner, so the live count is zero, not `<= record`."""
    found, scanned = gate.measure(ROOT, require_git=True)
    assert scanned
    assert found == {}
    assert gate.load_baseline(ROOT / gate.DEFAULT_BASELINE_REL) == {}


def test_every_spelling_is_reported_with_its_line_and_name() -> None:
    body = (
        "import sys\n"
        "\n"
        "\n"
        "def test_x(monkeypatch):\n"
        '    monkeypatch.delitem(sys.modules, "a")\n'
        '    sys.modules.pop("b", None)\n'
        '    del sys.modules["c"]\n'
    )
    assert gate.eviction_sites(body, "probe.py") == [
        (5, "delitem(sys.modules, ...)"),
        (6, "sys.modules.pop(...)"),
        (7, "del sys.modules[...]"),
    ]


def test_a_recorded_site_passes_and_one_more_than_recorded_fails(tmp_path: Path, capsys) -> None:
    one = 'import sys\n\n\ndef test_x():\n    del sys.modules["a"]\n'
    repo = _seed(tmp_path, one, baseline={"tests/test_probe.py": 1})
    assert gate.main(["--repo-root", str(repo)]) == 0
    (repo / "tests" / "test_probe.py").write_text(
        one + '\n\ndef test_y():\n    del sys.modules["b"]\n', encoding="utf-8"
    )
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "2 raw sys.modules eviction(s), baseline 1" in capsys.readouterr().err


def test_a_shrunk_file_prompts_to_lower_the_record_and_the_writer_refuses_to_raise(
    tmp_path: Path, capsys
) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={"tests/test_probe.py": 2})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "0 < baseline 2; drop it from the record" in capsys.readouterr().err
    (repo / "tests" / "test_probe.py").write_text(
        'import sys\n\n\ndef test_x():\n    del sys.modules["a"]\n'
        '    del sys.modules["b"]\n    del sys.modules["c"]\n',
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="refusing to raise the module-eviction baseline"):
        gate.main(["--repo-root", str(repo), "--write-baseline"])


def test_a_partly_shrunk_file_prompts_with_its_new_count(tmp_path: Path, capsys) -> None:
    repo = _seed(
        tmp_path,
        'import sys\n\n\ndef test_x():\n    del sys.modules["a"]\n',
        baseline={"tests/test_probe.py": 3},
    )
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "tests/test_probe.py: 1 < baseline 3; lower the record" in capsys.readouterr().err


def test_writing_the_record_lowers_it_and_the_written_record_reads_back(
    tmp_path: Path, capsys
) -> None:
    repo = _seed(
        tmp_path,
        'import sys\n\n\ndef test_x():\n    del sys.modules["a"]\n',
        baseline={"tests/test_probe.py": 3},
    )
    assert gate.main(["--repo-root", str(repo), "--write-baseline"]) == 0
    assert "Wrote module-eviction baseline: 1 site(s) in 1 file(s)." in capsys.readouterr().out
    assert gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL) == {"tests/test_probe.py": 1}
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_without_a_record_every_site_is_new(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, 'import sys\n\n\ndef test_x():\n    del sys.modules["a"]\n')
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "baseline 0" in capsys.readouterr().err


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"schema": "other", "files": {}}, "not a charness.module-eviction-baseline/v1 record"),
        ({"schema": gate.BASELINE_SCHEMA, "files": {"tests/x.py": 0}}, "positive site counts"),
        ({"schema": gate.BASELINE_SCHEMA, "files": ["tests/x.py"]}, "positive site counts"),
    ],
)
def test_a_malformed_record_is_refused(tmp_path: Path, payload: dict, message: str) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n")
    record = repo / gate.DEFAULT_BASELINE_REL
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        gate.main(["--repo-root", str(repo)])


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    monkeypatch.setattr(sys, "argv", ["check_module_eviction_form.py", "--repo-root", str(repo)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(
            str(ROOT / "scripts/gates/check_module_eviction_form.py"), run_name="__main__"
        )
    assert excinfo.value.code == 0


def test_bootstrap_shim_inserts_the_repo_root_when_it_is_absent(monkeypatch) -> None:
    # The shim's insert branch runs only in a process where the root is not yet
    # on sys.path, which pytest never is; strip it so the branch is exercised.
    stripped = [entry for entry in sys.path if entry and Path(entry).resolve() != ROOT.resolve()]
    monkeypatch.setattr(sys, "path", stripped)
    gate._load_repo_runtime_bootstrap()
    assert str(ROOT.resolve()) in sys.path or str(ROOT) in sys.path
