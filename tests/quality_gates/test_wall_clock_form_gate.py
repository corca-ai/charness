"""The wall-clock form gate: recorded sites only shrink, a new one is refused (#779)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.gates import check_wall_clock_form as gate
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
        "import time\n\n\ndef test_x():\n    time.sleep(0.1)\n",
        "import time\n\n\ndef test_x():\n    deadline = time.monotonic() + 1\n    assert deadline\n",
        "from time import sleep\n\n\ndef test_x():\n    sleep(0.1)\n",
        "import time\n\n\ndef test_x():\n    assert time.perf_counter() > 0\n",
    ],
)
def test_a_seeded_new_wall_clock_call_turns_the_gate_red(tmp_path: Path, body: str, capsys) -> None:
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "tests/test_probe.py: 1 wall-clock call(s), baseline 0" in err
    assert "force the observation or delete the test" in err


def test_a_sleep_inside_a_seeded_child_string_is_not_a_site(tmp_path: Path) -> None:
    body = 'CHILD = "import time\\ntime.sleep(30)\\n"\n\n\ndef test_x():\n    assert "sleep" in CHILD\n'
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_time_time_as_data_is_not_a_site(tmp_path: Path) -> None:
    body = "import time\n\n\ndef test_x():\n    stamp = time.time() - 86400\n    assert stamp\n"
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_a_recorded_site_passes_and_one_more_than_recorded_fails(tmp_path: Path, capsys) -> None:
    one = "import time\n\n\ndef test_x():\n    time.sleep(0.1)\n"
    repo = _seed(tmp_path, one, baseline={"tests/test_probe.py": 1})
    assert gate.main(["--repo-root", str(repo)]) == 0
    (repo / "tests" / "test_probe.py").write_text(
        one + "\n\ndef test_y():\n    time.sleep(0.2)\n", encoding="utf-8"
    )
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "2 wall-clock call(s), baseline 1" in capsys.readouterr().err


def test_a_shrunk_file_prompts_to_lower_the_record_and_the_writer_refuses_to_raise(
    tmp_path: Path, capsys
) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={"tests/test_probe.py": 2})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "0 < baseline 2; drop it from the record" in capsys.readouterr().err
    (repo / "tests" / "test_probe.py").write_text(
        "import time\n\n\ndef test_x():\n    time.sleep(0.1)\n    time.sleep(0.1)\n    time.sleep(0.1)\n",
        encoding="utf-8",
    )
    with pytest.raises(SystemExit, match="refusing to raise the wall-clock baseline"):
        gate.main(["--repo-root", str(repo), "--write-baseline"])


def test_fixture_children_are_not_scanned(tmp_path: Path) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    child = repo / "tests" / "fixtures" / "slow_child.py"
    child.parent.mkdir()
    child.write_text("import time\ntime.sleep(30)\n", encoding="utf-8")
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "top_level.py").write_text("VALUE = 1\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path)])


def test_live_repo_has_no_wall_clock_site_above_its_record() -> None:
    found, scanned = gate.measure(ROOT, require_git=True)
    assert scanned
    failures, _prompts = gate.judge(found, gate.load_baseline(ROOT / gate.DEFAULT_BASELINE_REL))
    assert failures == []
