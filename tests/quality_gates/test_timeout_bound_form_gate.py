"""The timeout-bound form gate: a deadline-riding verdict is refused, recorded ones only shrink (#786)."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts.gates import check_timeout_bound_form as gate
from tests.quality_gates.support import ROOT

KNOB_BODY = (
    "import os, subprocess\n\n\n"
    "def test_x(tmp_path):\n"
    "    env = os.environ.copy()\n"
    '    env["CHARNESS_PROBE_TIMEOUT_SECONDS"] = "0.5"\n'
    "    result = subprocess.run(['x'], env=env, capture_output=True, text=True)\n"
    "    assert 'partial verdict' in result.stdout\n"
)
DERIVED_BODY = (
    "import subprocess, yaml\n\n\n"
    "def test_x(monkeypatch):\n"
    '    monkeypatch.setenv("CHARNESS_PROBE_TIMEOUT_SECONDS", "0.1")\n'
    "    result = subprocess.run(['x'], capture_output=True, text=True)\n"
    "    payload = yaml.safe_load(result.stdout)\n"
    "    probe = payload['probe_results'][0]\n"
    "    assert 'partial verdict' in probe['stdout_preview']\n"
)
SETATTR_BODY = (
    "import mod\n\n\n"
    "def test_x(monkeypatch):\n"
    '    monkeypatch.setattr(mod, "AWIKI_TIMEOUT_SECONDS", 0.25)\n'
    "    result = mod.run()\n"
    "    assert result.returncode == 124\n"
)
ASSIGN_BODY = (
    "import mod\n\n\n"
    "def test_x():\n"
    "    mod._RESOLVE_TIMEOUT_SECONDS = 0.001\n"
    "    out, err = mod.process().communicate()\n"
    "    assert out == ''\n"
)
DEADLINE_BODY = (
    "import subprocess\n\n\n"
    "def test_x():\n"
    "    process = subprocess.Popen(['x'], stdout=subprocess.PIPE)\n"
    "    try:\n"
    "        stdout, _ = process.communicate(timeout=0.5)\n"
    "    except subprocess.TimeoutExpired:\n"
    "        assert False, 'the child never answered'\n"
)
DEADLINE_RAISE_BODY = (
    "import subprocess\n\n\n"
    "def test_x():\n"
    "    try:\n"
    "        subprocess.run(['x'], timeout=0.25)\n"
    "    except (OSError, subprocess.TimeoutExpired):\n"
    "        raise AssertionError('hung')\n"
)


def _seed(
    tmp_path: Path,
    body: str,
    *,
    baseline: dict[str, int] | None = None,
    reasons: dict[str, str] | None = None,
) -> Path:
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_probe.py").write_text(body, encoding="utf-8")
    if baseline is not None:
        record = repo / gate.DEFAULT_BASELINE_REL
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(
            json.dumps(
                {
                    "schema": gate.BASELINE_SCHEMA,
                    "files": baseline,
                    "reasons": reasons if reasons is not None else {k: "kept: certain to fire" for k in baseline},
                    "total": sum(baseline.values()),
                }
            ),
            encoding="utf-8",
        )
    return repo


@pytest.mark.parametrize(
    "body, fragment",
    [
        (KNOB_BODY, "CHARNESS_PROBE_TIMEOUT_SECONDS=0.5s at line 6 with an assert on the child's output at line 8"),
        (DERIVED_BODY, "CHARNESS_PROBE_TIMEOUT_SECONDS=0.1s at line 5 with an assert on the child's output at line 9"),
        (SETATTR_BODY, "AWIKI_TIMEOUT_SECONDS=0.25s at line 5 with an assert on the child's output at line 7"),
        (ASSIGN_BODY, "_RESOLVE_TIMEOUT_SECONDS=0.001s at line 5 with an assert on the child's output at line 7"),
        (DEADLINE_BODY, "communicate(timeout=0.5) with an asserting TimeoutExpired handler at line 7"),
        (DEADLINE_RAISE_BODY, "run(timeout=0.25) with an asserting TimeoutExpired handler at line 6"),
    ],
)
def test_a_seeded_timeout_bound_verdict_turns_the_gate_red(
    tmp_path: Path, body: str, fragment: str, capsys
) -> None:
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert "tests/test_probe.py: 1 timeout-bound verdict(s), baseline 0" in err
    assert fragment in err, err
    assert "spend the budget by an observation on a controlled clock" in err


def test_a_controlled_clock_exempts_the_function(tmp_path: Path) -> None:
    body = (
        "import subprocess, yaml\n\n\n"
        "def test_x(monkeypatch):\n"
        '    monkeypatch.setenv("CHARNESS_PROBE_TIMEOUT_SECONDS", "0.1")\n'
        '    monkeypatch.setattr("scripts.core.subprocess_guard.time.monotonic", lambda: 100.0)\n'
        "    result = subprocess.run(['x'], capture_output=True, text=True)\n"
        "    assert result.returncode == 1\n"
    )
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0
    body_attr = body.replace(
        '    monkeypatch.setattr("scripts.core.subprocess_guard.time.monotonic", lambda: 100.0)\n',
        '    monkeypatch.setattr(guard.time, "monotonic", lambda: 100.0)\n',
    )
    repo = _seed(tmp_path / "attr", body_attr, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


@pytest.mark.parametrize(
    "body",
    [
        # A knob at or above the limit is a hang guard, not a deadline race.
        KNOB_BODY.replace('"0.5"', '"5"'),
        # A deadline at or above one second is the suite's own bound.
        DEADLINE_BODY.replace("timeout=0.5", "timeout=30"),
        # A knob read as a value is data.
        "import mod\n\n\ndef test_x():\n    assert mod.DEFAULT_TIMEOUT_SECONDS == 10\n",
        # A fake that raises TimeoutExpired involves no clock.
        (
            "import subprocess, mod\n\n\ndef test_x(monkeypatch):\n"
            "    def boom(*_a, **_k):\n        raise subprocess.TimeoutExpired('x', mod.NOSE_TIMEOUT_SECONDS)\n"
            "    monkeypatch.setattr(mod.subprocess, 'run', boom)\n    assert mod.run()['status'] == 'error'\n"
        ),
        # A knob without an assertion on the child's output is not a verdict.
        KNOB_BODY.replace("    assert 'partial verdict' in result.stdout\n", "    assert result\n"),
        # A non-test function is not scanned.
        KNOB_BODY.replace("def test_x", "def helper"),
        # A knob restored from a saved value is not a literal.
        "import mod\n\n\ndef test_x():\n    original = mod.X_TIMEOUT_SECONDS\n    mod.X_TIMEOUT_SECONDS = original\n    assert mod.run().returncode == 0\n",
        # The handler that does not assert is a cleanup path, not a claim.
        DEADLINE_BODY.replace("        assert False, 'the child never answered'\n", "        process.kill()\n"),
    ],
)
def test_shapes_outside_the_rule_are_not_sites(tmp_path: Path, body: str) -> None:
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_deadline_sites_skip_other_calls_keywords_and_bare_handlers(tmp_path: Path, capsys) -> None:
    body = (
        "import subprocess\n\n\n"
        "def test_x():\n"
        "    try:\n"
        "        process = subprocess.Popen(['x'], stdout=subprocess.PIPE)\n"
        "        stdout, _ = process.communicate(input='go', timeout=0.5)\n"
        "    except OSError:\n"
        "        pass\n"
        "    except subprocess.TimeoutExpired:\n"
        "        raise AssertionError('the child never answered')\n"
        "    except:\n"
        "        raise\n"
    )
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "communicate(timeout=0.5) with an asserting TimeoutExpired handler at line 7" in (
        capsys.readouterr().err
    )


def test_a_handler_that_re_raises_a_stored_error_is_not_an_assertion(tmp_path: Path) -> None:
    body = (
        "import subprocess\n\n\n"
        "def test_x():\n"
        "    errors = [RuntimeError('x')]\n"
        "    try:\n"
        "        subprocess.run(['x'], timeout=0.2)\n"
        "    except subprocess.TimeoutExpired:\n"
        "        raise errors[0]\n"
    )
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_the_controlled_clock_exemption_needs_a_dotted_time_module(tmp_path: Path) -> None:
    body = (
        "import subprocess\n\n\n"
        "def test_x(monkeypatch):\n"
        '    monkeypatch.setenv("CHARNESS_PROBE_TIMEOUT_SECONDS", "0.1")\n'
        '    monkeypatch.setattr(clock_module(), "monotonic", lambda: 100.0)\n'
        "    result = subprocess.run(['x'], capture_output=True, text=True)\n"
        "    assert result.returncode == 1\n"
    )
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1


def test_the_stated_blind_shapes_are_indeed_blind(tmp_path: Path) -> None:
    """Pinned so that the docstring's blind list stays true, not so the blindness is desired."""
    through_a_call = KNOB_BODY.replace(
        "    result = subprocess.run(['x'], env=env, capture_output=True, text=True)\n"
        "    assert 'partial verdict' in result.stdout\n",
        "    result = run_bounded(env=env)\n    assert 'partial verdict' in result\n",
    )
    unpacked = SETATTR_BODY.replace(
        "    result = mod.run()\n    assert result.returncode == 124\n",
        "    returncode, output = mod.run()\n    assert returncode == 124\n",
    )
    for name, body in (("call", through_a_call), ("unpack", unpacked)):
        repo = _seed(tmp_path / name, body, baseline={})
        assert gate.main(["--repo-root", str(repo)]) == 0


def test_a_recorded_site_passes_and_one_more_than_recorded_fails(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, KNOB_BODY, baseline={"tests/test_probe.py": 1})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "none new" in capsys.readouterr().out
    two = KNOB_BODY + "\n" + KNOB_BODY.replace("def test_x", "def test_y").split("\n\n\n", 1)[1]
    repo = _seed(tmp_path / "two", two, baseline={"tests/test_probe.py": 1})
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert "2 timeout-bound verdict(s), baseline 1" in capsys.readouterr().err


def test_a_shrunk_file_prompts_to_lower_the_record_and_the_writer_refuses_to_raise(
    tmp_path: Path, capsys
) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={"tests/test_probe.py": 1})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "0 < baseline 1; drop it from the record" in capsys.readouterr().err
    raised = _seed(tmp_path / "raised", KNOB_BODY, baseline={"tests/other.py": 1})
    with pytest.raises(SystemExit, match="refusing to raise the timeout-bound baseline"):
        gate.main(["--repo-root", str(raised), "--write-baseline"])


def test_a_partly_shrunk_file_prompts_with_its_new_count(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, KNOB_BODY, baseline={"tests/test_probe.py": 3})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "tests/test_probe.py: 1 < baseline 3; lower the record" in capsys.readouterr().err


def test_writing_the_record_keeps_the_reason_and_refuses_a_site_without_one(
    tmp_path: Path, capsys
) -> None:
    repo = _seed(
        tmp_path,
        KNOB_BODY,
        baseline={"tests/test_probe.py": 3},
        reasons={"tests/test_probe.py": "kept: the child sleeps 600 s against 0.5 s"},
    )
    assert gate.main(["--repo-root", str(repo), "--write-baseline"]) == 0
    assert "Wrote timeout-bound baseline: 1 site(s) in 1 file(s)." in capsys.readouterr().out
    counts, reasons = gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL)
    assert counts == {"tests/test_probe.py": 1}
    assert reasons == {"tests/test_probe.py": "kept: the child sleeps 600 s against 0.5 s"}
    assert gate.main(["--repo-root", str(repo)]) == 0

    unreasoned = _seed(tmp_path / "unreasoned", KNOB_BODY)
    with pytest.raises(SystemExit, match="without a written reason"):
        gate.main(["--repo-root", str(unreasoned), "--write-baseline"])


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"schema": "other", "files": {}}, "not a charness.timeout-bound-baseline/v1 record"),
        ({"schema": gate.BASELINE_SCHEMA, "files": {"tests/x.py": 0}}, "positive site counts"),
        ({"schema": gate.BASELINE_SCHEMA, "files": {"tests/x.py": 1}}, "written reason"),
        (
            {"schema": gate.BASELINE_SCHEMA, "files": {"tests/x.py": 1}, "reasons": {"tests/x.py": " "}},
            "written reason",
        ),
    ],
)
def test_a_malformed_record_is_refused(tmp_path: Path, payload: dict, message: str) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n")
    record = repo / gate.DEFAULT_BASELINE_REL
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        gate.main(["--repo-root", str(repo)])


def test_fixture_children_are_not_scanned(tmp_path: Path) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    (repo / "tests" / "fixtures").mkdir()
    (repo / "tests" / "fixtures" / "child.py").write_text(KNOB_BODY, encoding="utf-8")
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path / "empty")])


def test_live_repo_has_no_timeout_bound_site_above_its_record() -> None:
    found, scanned = gate.measure(ROOT, require_git=True)
    assert scanned
    counts, reasons = gate.load_baseline(ROOT / gate.DEFAULT_BASELINE_REL)
    assert set(counts) == set(reasons)
    failures, _prompts = gate.judge(found, counts)
    assert failures == []


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch) -> None:
    repo = _seed(tmp_path, "def test_x():\n    assert True\n", baseline={})
    monkeypatch.setattr(sys, "argv", ["check_timeout_bound_form.py", "--repo-root", str(repo)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(ROOT / "scripts/gates/check_timeout_bound_form.py"), run_name="__main__")
    assert excinfo.value.code == 0


def test_bootstrap_shim_inserts_the_repo_root_when_it_is_absent(monkeypatch) -> None:
    stripped = [entry for entry in sys.path if entry and Path(entry).resolve() != ROOT.resolve()]
    monkeypatch.setattr(sys, "path", stripped)
    gate._load_repo_runtime_bootstrap()
    assert str(ROOT.resolve()) in sys.path or str(ROOT) in sys.path
