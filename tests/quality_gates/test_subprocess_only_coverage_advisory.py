"""The #465 subprocess-coverage advisory: helper, gate wiring, and its bounds.

Split out of `test_changed_line_mutation_coverage.py` (D33: a cohesive concept,
not a mechanical spill) — every test here is about ONE question the changed-line
gate must answer honestly on a BLOCK: is this line uncovered, or was it exercised
by a spawn whose coverage was never attributed?

The advisory is not a gate, so the load-bearing tests are the CONTROLS: a passing
run must still pass, an env-inheriting spawn must NOT be advised on (this repo's
producer does measure those children), and a stale ratchet entry must not be
asserted as a present fact.
"""
from __future__ import annotations

import json
from pathlib import Path

from scripts.runtime_bootstrap import import_repo_module

from .support import ROOT, run_script

_TEETH = str(ROOT / "scripts" / "check_changed_line_mutation_coverage.py")


def _git(repo: Path, *args: str) -> str:
    import subprocess

    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo, check=True, capture_output=True, text=True,
    ).stdout.strip()


def _seed_two_changed_pool_files(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    _git(repo, "init", "-q")
    for name in ("foo.py", "bar.py"):
        (repo / "scripts" / name).write_text("def a():\n    return 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    base = _git(repo, "rev-parse", "HEAD")
    for name in ("foo.py", "bar.py"):
        (repo / "scripts" / name).write_text(
            "def a():\n    return 1\n\n\ndef b():\n    return 2\n", encoding="utf-8"
        )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "head")
    return repo, base, _git(repo, "rev-parse", "HEAD")


def _write_boundary_baseline(repo: Path, keys: list[str]) -> None:
    (repo / "scripts" / "boundary-bypass-baseline.json").write_text(
        json.dumps({"policy": "no_increase", "candidate_keys": keys}), encoding="utf-8"
    )


#: How a test file spawns the script under test. The keyword alone is NOT the
#: trigger -- `{**os.environ, ...}` is this repo's house style and carries
#: COVERAGE_PROCESS_START straight through, so those children ARE measured and
#: advising on them would be false reassurance printed onto a blocking gate.
SPAWN_SHAPES = {
    "replaces-env": 'subprocess.run([sys.executable, "{target}"], env={{"PATH": "/usr/bin"}})',
    "extends-env": 'subprocess.run([sys.executable, "{target}"], env={{**os.environ, "PATH": "/usr/bin"}})',
    "inherits-env": 'subprocess.run([sys.executable, "{target}"])',
}


def _write_test_file(repo: Path, rel: str, target: str, *, shape: str = "replaces-env") -> None:
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    spawn = SPAWN_SHAPES[shape].format(target=target)
    path.write_text(
        f"import os\nimport subprocess\nimport sys\n\n\ndef test_it():\n    {spawn}\n",
        encoding="utf-8",
    )


def _advisory_lib():
    return import_repo_module(__file__, "scripts.subprocess_only_coverage_advisory")


def test_blocked_file_with_recorded_subprocess_pairs_gets_an_advisory(tmp_path: Path) -> None:
    """#465: a BLOCK whose recorded test spawns the file with a scrubbed env says so.

    `scripts/bar.py` is the discriminating control in the same run: blocked by the
    identical coverage fixture, and recorded in the same baseline, but its test
    spawns without replacing the environment, so the child keeps
    COVERAGE_PROCESS_START and its lines really are attributed. Advising on it
    would be false reassurance printed onto a blocking gate — the class the gate
    itself exists to catch.
    """
    repo, base, head = _seed_two_changed_pool_files(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps({"files": {
            "scripts/foo.py": {"executed_lines": [1, 2], "missing_lines": [5, 6]},
            "scripts/bar.py": {"executed_lines": [1, 2], "missing_lines": [5, 6]},
        }}),
        encoding="utf-8",
    )
    _write_boundary_baseline(
        repo, ["tests/test_foo.py::scripts/foo.py", "tests/test_bar.py::scripts/bar.py"]
    )
    _write_test_file(repo, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    _write_test_file(repo, "tests/test_bar.py", "scripts/bar.py", shape="inherits-env")

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["blocking"] == ["scripts/bar.py", "scripts/foo.py"]
    advisory = payload["subprocess_coverage_advisory"]
    assert list(advisory) == ["scripts/foo.py"], (
        "the env-inheriting control is recorded in the same baseline and must not be named"
    )
    entry = advisory["scripts/foo.py"]
    assert entry["subprocess_tests"] == ["tests/test_foo.py"]
    assert entry["blocked_lines"] == [5, 6]
    # The claim is bounded to what the baseline actually records.
    assert "FILE GRANULARITY ONLY" in entry["note"]
    assert "environment-REPLACING `env=`" in entry["note"]
    assert "does NOT establish that line(s) 5, 6 are reached" in entry["note"]
    assert "ADVISORY (not a blocker)" in result.stderr
    assert "scripts/bar.py" not in result.stderr.split("ADVISORY (not a blocker)")[1]


def test_advisory_does_not_add_or_remove_a_blocking_condition(tmp_path: Path) -> None:
    """Control for the above: the advisory is not a gate.

    Same repo and same baseline, but coverage now reaches the changed lines. A run
    that would pass must still pass with exit 0 and an empty advisory — otherwise
    the feature could have degenerated into "a recorded pair blocks".
    """
    repo, base, head = _seed_two_changed_pool_files(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps({"files": {
            "scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []},
            "scripts/bar.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []},
        }}),
        encoding="utf-8",
    )
    _write_boundary_baseline(repo, ["tests/test_foo.py::scripts/foo.py"])

    result = run_script(
        _TEETH, "--repo-root", str(repo), "--base-sha", base, "--head-sha", head,
        "--reuse-coverage", "--coverage-json", str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload["blocking"] == []
    assert payload["subprocess_coverage_advisory"] == {}
    assert "ADVISORY (not a blocker)" not in result.stderr


def test_advisory_is_silent_when_the_baseline_is_absent_or_malformed(tmp_path: Path) -> None:
    """In-process arm: an unusable baseline degrades to silence, never to a crash.

    The gate's real verdict has already been computed by the time this runs, so any
    exception here would turn an advisory into a lost blocking report.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")

    assert lib.load_subprocess_boundary_pairs(tmp_path) == {}
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "boundary-bypass-baseline.json").write_text("{not json", encoding="utf-8")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}
    (tmp_path / "scripts" / "boundary-bypass-baseline.json").write_text(
        json.dumps({"candidate_keys": "not-a-list"}), encoding="utf-8"
    )
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}
    # Control: the same call on a well-formed baseline does produce the advisory,
    # so the assertions above test tolerance rather than a helper that never fires.
    (tmp_path / "scripts" / "boundary-bypass-baseline.json").write_text(
        json.dumps({"candidate_keys": ["tests/test_foo.py::scripts/foo.py", "malformed-no-separator", ""]}),
        encoding="utf-8",
    )
    assert lib.load_subprocess_boundary_pairs(tmp_path) == {"scripts/foo.py": ["tests/test_foo.py"]}
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]


def test_advisory_stderr_line_is_none_when_nothing_was_recorded() -> None:
    lib = _advisory_lib()

    assert lib.advisory_stderr_line({}) is None
    line = lib.advisory_stderr_line({"scripts/foo.py": {"subprocess_tests": ["tests/test_foo.py"]}})
    assert "scripts/foo.py" in line
    assert "does not establish that the env-replacing call runs this script" in line


def test_advisory_re_checks_the_ratchet_baseline_instead_of_trusting_it(tmp_path: Path) -> None:
    """The baseline is a no-increase RATCHET, not a current inventory.

    It never prunes a pair whose test has since been converted to an in-process
    one, and the live detector already derives more keys than the file records. So
    a recorded pair whose test no longer names the script, or no longer spawns it
    with a scrubbed env, must not produce an advisory — asserting a stale record as
    a present fact is the class this gate exists to catch.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_boundary_baseline(tmp_path, ["tests/test_foo.py::scripts/foo.py"])

    # converted: still spawns something with env=, but no longer names this script
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/other.py", shape="replaces-env")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # converted the other way: still names the script, but inherits the environment
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="inherits-env")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # deleted outright
    (tmp_path / "tests" / "test_foo.py").unlink()
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # control: the live shape still fires, so the three assertions above are not
    # passing because the helper can never produce anything.
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]


def test_an_environ_extending_spawn_is_measured_and_must_not_be_advised_on(tmp_path: Path) -> None:
    """The premise repair, pinned.

    The first cut fired on any `env=` keyword and asserted the child was
    unattributed. `env={**os.environ, ...}` is this repo's house style (60+ uses
    under tests/) and carries COVERAGE_PROCESS_START and PYTHONPATH through, so
    those children ARE measured — several of them under recorded baseline pairs.
    Advising there tells the operator to doubt a TRUE block.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_boundary_baseline(tmp_path, ["tests/test_foo.py::scripts/foo.py"])

    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="extends-env")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # control: the replacing shape, same file, same baseline, still fires.
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]


def test_a_basename_that_merely_appears_inside_another_name_does_not_count(tmp_path: Path) -> None:
    """`in source` containment matched far too much: `doctor.py` hit any file
    mentioning `test_doctor.py`, and both are real recorded baseline entries."""
    lib = _advisory_lib()
    targets = {"scripts/doctor.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_boundary_baseline(tmp_path, ["tests/test_doctor.py::scripts/doctor.py"])
    _write_test_file(tmp_path, "tests/test_doctor.py", "helpers/test_doctor.py", shape="replaces-env")

    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    _write_test_file(tmp_path, "tests/test_doctor.py", "scripts/doctor.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/doctor.py"]


def test_an_unreadable_or_binary_test_file_is_silence_not_a_lost_blocking_report(tmp_path: Path) -> None:
    """The gate's real verdict is already computed when this runs, so an exception
    here would replace the blocking report with a traceback. `read_text` raises
    UnicodeDecodeError (a ValueError, not an OSError) on non-UTF-8 bytes, and
    `ast.parse` raises ValueError on NUL bytes — neither is a SyntaxError.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_boundary_baseline(tmp_path, ["tests/test_foo.py::scripts/foo.py"])
    (tmp_path / "tests").mkdir()

    (tmp_path / "tests" / "test_foo.py").write_bytes(b"\xff\xfe scripts/foo.py env={}")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    (tmp_path / "tests" / "test_foo.py").write_bytes(
        b'import subprocess\n\x00\nsubprocess.run(["scripts/foo.py"], env={"PATH": "/"})\n'
    )
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # control: a well-formed file in the same position does produce the advisory.
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]


def test_a_malformed_baseline_key_is_skipped_without_losing_the_others(tmp_path: Path) -> None:
    """A ratchet file is hand-edited; one bad key must not drop the rest."""
    lib = _advisory_lib()
    (tmp_path / "scripts").mkdir()
    _write_boundary_baseline(
        tmp_path,
        ["no-separator-here", "::scripts/only.py", "tests/t.py::", "  ::  ", 42, "tests/t.py::scripts/real.py"],
    )

    assert lib.load_subprocess_boundary_pairs(tmp_path) == {"scripts/real.py": ["tests/t.py"]}


def test_only_a_literal_dict_can_replace_the_environment(tmp_path: Path) -> None:
    """`_replaces_environment` reads one AST node, and everything it cannot READ has
    to answer "inherits" — silence is the safe direction for an advisory that rides a
    blocking gate. A bare `env=env` name, `env=None`, and a call expression are all
    unfollowable from here, so none of them may be reported as a scrub.
    """
    import ast

    lib = _advisory_lib()
    replaces = {
        '{"PATH": "/usr/bin"}': True,
        '{**base, "PATH": "/usr/bin"}': True,
        '{**os.environ, "PATH": "/usr/bin"}': False,
        '{**environ}': False,
        '{**os.environ.copy()}': False,
        'env': False,
        'None': False,
        'dict(os.environ, PATH="/usr/bin")': False,
        'os.environ.copy()': False,
    }
    for source, expected in replaces.items():
        node = ast.parse(source, mode="eval").body
        assert lib._replaces_environment(node) is expected, source


def test_a_blocked_file_without_proof_targets_is_named_rather_than_dropped(capsys) -> None:
    """The narration's own unestablished arm: a file that BLOCKS but produced no
    exact `path:line` target must be named, because the operator's next step
    (`cite one blocking_targets entry, mutate that line`) is impossible for it and
    silence would read as "every blocker has a target".
    """
    trust = import_repo_module(__file__, "scripts.changed_line_run_trust")

    trust.write_blocking_stderr(
        ["scripts/mapped.py", "scripts/unmapped.py"],
        {"scripts/mapped.py": [{"line": 5, "source": "def b():"}]},
    )

    err = capsys.readouterr().err
    assert "could not produce exact proof targets for: scripts/unmapped.py" in err
    assert "scripts/mapped.py" not in err.split("could not produce")[1].split("\n")[0]
    assert "2 changed file(s) have uncovered changed lines" in err
    assert "ADVISORY (not a blocker)" not in err  # no advisory passed


def test_the_advisory_sentence_rides_the_blocking_narration_when_one_exists(capsys) -> None:
    trust = import_repo_module(__file__, "scripts.changed_line_run_trust")

    trust.write_blocking_stderr(
        ["scripts/foo.py"],
        {"scripts/foo.py": [{"line": 5, "source": "def b():"}]},
        {"scripts/foo.py": {"subprocess_tests": ["tests/test_foo.py"], "blocked_lines": [5]}},
    )

    err = capsys.readouterr().err
    assert "ADVISORY (not a blocker)" in err
    assert err.index("uncovered changed lines") < err.index("ADVISORY (not a blocker)")
