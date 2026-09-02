"""The #465 subprocess-coverage advisory: helper, gate wiring, and its bounds.

Split out of `test_changed_line_mutation_coverage.py` (D33: a cohesive concept,
not a mechanical spill) — every test here is about ONE question the changed-line
gate must answer honestly on a BLOCK: is this line uncovered, or was it exercised
by a spawn whose coverage was never attributed?

The advisory is not a gate, so the load-bearing tests are the CONTROLS: a passing
run must still pass, an env-inheriting spawn must NOT be advised on (this repo's
producer does measure those children), and a stale candidate entry must not be
asserted as a present fact.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from scripts.runtime_bootstrap import import_repo_module

from .seeding_support import seed_two_changed_pool_files
from .support import ROOT, run_script

_TEETH = str(ROOT / "scripts" / "mutation" / "check_changed_line_mutation_coverage.py")


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
    return import_repo_module(__file__, "scripts.mutation.subprocess_only_coverage_advisory")


def _write_raw(source: str) -> Path:
    """A throwaway repo holding `tests/test_foo.py` with exactly this source.

    Used by the mechanism-level tests, which are about what the AST reader concludes
    from one file and need no persisted inventory artifact, git history, or coverage fixture.
    """
    import tempfile

    root = Path(tempfile.mkdtemp())
    (root / "tests").mkdir()
    (root / "tests" / "test_foo.py").write_text(source, encoding="utf-8")
    return root


def test_blocked_file_with_recorded_subprocess_pairs_gets_an_advisory(tmp_path: Path) -> None:
    """#465: a BLOCK whose recorded test spawns the file with a scrubbed env says so.

    `scripts/bar.py` is the discriminating control in the same run: blocked by the
    identical coverage fixture, and recorded in the same live inventory, but its test
    spawns without replacing the environment, so the child keeps
    COVERAGE_PROCESS_START and its lines really are attributed. Advising on it
    would be false reassurance printed onto a blocking gate — the class the gate
    itself exists to catch.
    """
    repo, base, head = seed_two_changed_pool_files(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "scripts/foo.py": {"executed_lines": [1, 2], "missing_lines": [5, 6]},
                    "scripts/bar.py": {"executed_lines": [1, 2], "missing_lines": [5, 6]},
                }
            }
        ),
        encoding="utf-8",
    )
    _write_test_file(repo, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    _write_test_file(repo, "tests/test_bar.py", "scripts/bar.py", shape="inherits-env")

    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == ["scripts/bar.py", "scripts/foo.py"]
    advisory = payload["subprocess_coverage_advisory"]
    assert list(advisory) == ["scripts/foo.py"], (
        "the env-inheriting control is recorded in the same inventory and must not be named"
    )
    entry = advisory["scripts/foo.py"]
    assert entry["subprocess_tests"] == ["tests/test_foo.py"]
    assert entry["blocked_lines"] == [5, 6]
    # The claim is bounded to what the live inventory actually records.
    assert "FILE GRANULARITY ONLY" in entry["note"]
    assert "environment-REPLACING `env=`" in entry["note"]
    assert "does NOT establish that line(s) 5, 6 are reached" in entry["note"]
    assert "ADVISORY (not a blocker)" in result.stderr
    assert "scripts/bar.py" not in result.stderr.split("ADVISORY (not a blocker)")[1]


def test_advisory_does_not_add_or_remove_a_blocking_condition(tmp_path: Path) -> None:
    """Control for the above: the advisory is not a gate.

    Same repo and same live inventory, but coverage now reaches the changed lines. A run
    that would pass must still pass with exit 0 and an empty advisory — otherwise
    the feature could have degenerated into "a recorded pair blocks".
    """
    repo, base, head = seed_two_changed_pool_files(tmp_path)
    cov = repo / "coverage.json"
    cov.write_text(
        json.dumps(
            {
                "files": {
                    "scripts/foo.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []},
                    "scripts/bar.py": {"executed_lines": [1, 2, 5, 6], "missing_lines": []},
                }
            }
        ),
        encoding="utf-8",
    )
    result = run_script(
        _TEETH,
        "--repo-root",
        str(repo),
        "--base-sha",
        base,
        "--head-sha",
        head,
        "--reuse-coverage",
        "--coverage-json",
        str(cov),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["blocking"] == []
    assert payload["subprocess_coverage_advisory"] == {}
    assert "ADVISORY (not a blocker)" not in result.stderr


def test_an_unavailable_inventory_never_crashes_or_silences_the_advisory(
    tmp_path: Path, monkeypatch
) -> None:
    """The live inventory is advisory input and must fail open if unavailable.

    The gate's real verdict has already been computed by the time this runs, so
    an inventory failure must not turn an advisory into a lost blocking report.
    The reference map remains an independent candidate source.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")

    import scripts.gates.inventory_boundary_bypass_lib as inventory

    def fail(_repo_root):
        raise RuntimeError("inventory unavailable")

    monkeypatch.setattr(inventory, "find_boundary_bypass_candidates", fail)
    assert lib.load_subprocess_boundary_pairs(tmp_path) == {}, "loader degrades to no pairs"
    assert lib.advisory_scope(tmp_path, targets)["inventory"] == "unavailable"
    # ...and the advisory survives on the independent reference-map source.
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]

    # Control for the control: with NEITHER source naming the file, it is silent.
    # `scripts/other.py` is blocked and no test references it.
    assert (
        lib.subprocess_coverage_advisory(
            tmp_path, {"scripts/other.py": [{"line": 5, "source": "def b():"}]}
        )
        == {}
    )


def test_advisory_stderr_line_is_none_when_nothing_was_recorded() -> None:
    lib = _advisory_lib()

    assert lib.advisory_stderr_line({}) is None
    line = lib.advisory_stderr_line({"scripts/foo.py": {"subprocess_tests": ["tests/test_foo.py"]}})
    assert "scripts/foo.py" in line
    assert "does not establish that those tests reach the blocked lines" in line
    # The guarantee must stay conditional. Round 2 found the earlier unconditional
    # "is never named here" was false under the file-level bound, and it was the most
    # reassuring sentence in the text.
    assert "is never named here" not in line


def test_advisory_rechecks_live_inventory_instead_of_stale_candidate_data(tmp_path: Path) -> None:
    """The live inventory must reflect the test files that exist now.

    It never prunes a pair whose test has since been converted to an in-process
    one. A test whose source no longer names the script, or no longer spawns it
    with a scrubbed env, must not produce an advisory.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
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
    those children ARE measured — including when the live inventory records them.
    Advising there tells the operator to doubt a TRUE block.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="extends-env")
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    # control: the replacing shape, same file, still fires.
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]


def test_a_basename_that_merely_appears_inside_another_name_does_not_count(tmp_path: Path) -> None:
    """`in source` containment matched far too much: `doctor.py` hit any file
    mentioning `test_doctor.py`; only the exact script path is a candidate."""
    lib = _advisory_lib()
    targets = {"scripts/doctor.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
    _write_test_file(
        tmp_path, "tests/test_doctor.py", "helpers/test_doctor.py", shape="replaces-env"
    )

    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}

    _write_test_file(tmp_path, "tests/test_doctor.py", "scripts/doctor.py", shape="replaces-env")
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/doctor.py"]


def test_an_unreadable_or_binary_test_file_is_silence_not_a_lost_blocking_report(
    tmp_path: Path,
) -> None:
    """The gate's real verdict is already computed when this runs, so an exception
    here would replace the blocking report with a traceback. `read_text` raises
    UnicodeDecodeError (a ValueError, not an OSError) on non-UTF-8 bytes, and
    `ast.parse` raises ValueError on NUL bytes — neither is a SyntaxError.
    """
    lib = _advisory_lib()
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}
    (tmp_path / "scripts").mkdir()
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
        # A splat of anything this reader cannot follow answers "inherits". The
        # earlier cut answered True here, breaking the very invariant this test
        # states: `base` may hold an `os.environ.copy()` from two lines up, in which
        # case the child IS measured and firing is false reassurance on a true block.
        '{**base, "PATH": "/usr/bin"}': False,
        '{**os.environ, "PATH": "/usr/bin"}': False,
        "{**environ}": False,
        "{**os.environ.copy()}": False,
        "env": False,
        "None": False,
        'dict(os.environ, PATH="/usr/bin")': False,
        "os.environ.copy()": False,
        # A real repo shape the dict-literal-only reader used to miss entirely:
        # tests/quality_gates/test_python_and_security_gates.py passes this.
        'dict(PATH="/usr/bin", TEST_OUTPUT="x")': True,
        # A `**` inside a dict() call carries the parent through just like the literal
        # splat does; it is a keyword whose arg is None, not a positional argument.
        'dict(**os.environ, PATH="/usr/bin")': False,
        # A `**`-free literal REPLACES even when a value reads os.environ: forwarding
        # one variable still drops COVERAGE_PROCESS_START. An earlier cut walked the
        # whole node for `environ` and called this "inherits" — a false negative reached
        # by the wrong reasoning, and the arms that produced it were unreachable once
        # the splat check ran first, which is how the changed-line gate surfaced it.
        '{"PATH": os.environ["PATH"]}': True,
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
    trust = import_repo_module(__file__, "scripts.gates_support.changed_line_run_trust")

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
    trust = import_repo_module(__file__, "scripts.gates_support.changed_line_run_trust")

    trust.write_blocking_stderr(
        ["scripts/foo.py"],
        {"scripts/foo.py": [{"line": 5, "source": "def b():"}]},
        {"scripts/foo.py": {"subprocess_tests": ["tests/test_foo.py"], "blocked_lines": [5]}},
    )

    err = capsys.readouterr().err
    assert "ADVISORY (not a blocker)" in err
    assert err.index("uncovered changed lines") < err.index("ADVISORY (not a blocker)")


def test_an_out_of_tree_copy_of_the_script_is_advised_on_even_with_an_inherited_env() -> None:
    """The mechanism the first two cuts both missed, and the one behind #465's own
    first instance.

    MEASURED, not inferred. The rcfile sets `source = <repo_root>`
    (`mutation_sampling_lib._write_coverage_config`), so a test that copies a script
    into `tmp_path` and spawns the COPY loses the attribution even though the child
    inherits COVERAGE_PROCESS_START in full. Running only
    `test_maintainer_hooks.py::test_validate_maintainer_setup_requires_installed_hookspath`
    under the repo's own producer attributes **0** lines to
    `scripts/setup/validate_maintainer_setup.py`, while
    `test_release_narrative_audit.py` — an inherited-env spawn of the script at its
    REAL path — attributes 143 lines to it. Same env, opposite outcome: the
    discriminator is the out-of-tree copy, not the process boundary.

    So an env-based detector alone is silent on the reporter's own case, which is
    what made the shipped advisory inert. This pins the repair.
    """
    lib = _advisory_lib()
    source = (
        "import shutil\n"
        "import subprocess\n"
        "import sys\n"
        "from pathlib import Path\n"
        "ROOT = Path(__file__).resolve().parents[2]\n\n\n"
        "def test_it(tmp_path):\n"
        '    shutil.copy2(ROOT / "scripts" / "foo.py", tmp_path / "scripts" / "foo.py")\n'
        '    subprocess.run([sys.executable, "scripts/foo.py"], cwd=tmp_path)\n'
    )

    assert lib.unmeasured_spawn_mechanisms(
        _write_raw(source), "tests/test_foo.py", "scripts/foo.py"
    ) == ["copies-this-script"]

    # Discriminating control: a copy of a DIFFERENT file, plus an in-repo
    # inherited-env spawn of the blocked script. Round 2 caught the absence of this
    # control on a reader that matched the copy's PARENT DIRECTORY name, so any test
    # copying anything out of `scripts/` was reported as copying whichever script it
    # mentioned — `scripts/plugin_export/check_supply_chain.py` really was named that way.
    other = source.replace('"scripts" / "foo.py", tmp_path', '"scripts" / "other.sh", tmp_path')
    assert (
        lib.unmeasured_spawn_mechanisms(_write_raw(other), "tests/test_foo.py", "scripts/foo.py")
        == []
    )


def test_an_in_tree_inherited_env_spawn_is_the_control_and_stays_silent() -> None:
    """The other half of the measured pair: 143 lines WERE attributed to a script
    exercised only by an inherited-env spawn at its real path, so naming it would be
    false reassurance printed onto a true block. No copy, no env= -> no mechanism."""
    lib = _advisory_lib()
    source = (
        "import subprocess\n"
        "import sys\n"
        "from pathlib import Path\n"
        "ROOT = Path(__file__).resolve().parents[2]\n\n\n"
        "def test_it():\n"
        '    subprocess.run([sys.executable, "scripts/foo.py"], cwd=ROOT)\n'
    )

    assert (
        lib.unmeasured_spawn_mechanisms(_write_raw(source), "tests/test_foo.py", "scripts/foo.py")
        == []
    )


def test_an_unreadable_env_splat_is_treated_as_inheriting_not_as_a_scrub() -> None:
    """The safe-direction invariant the module docstring states, which the shipped
    cut violated in the unsafe direction.

    `{**base, "PATH": x}` may splat an `os.environ.copy()` two lines up, in which
    case the child IS measured and advising on it is exactly the false reassurance
    this module must never print. An unreadable shape answers "inherits".
    """
    lib = _advisory_lib()
    import ast as _ast

    def verdict(expr: str) -> bool:
        return lib._replaces_environment(_ast.parse(expr, mode="eval").body)

    assert verdict('{**base, "PATH": "/usr/bin"}') is False, "unreadable splat must stay silent"
    assert verdict('{**os.environ, "PATH": "/usr/bin"}') is False
    assert verdict("env") is False, "a bare name cannot be followed"
    # ...and the shapes that provably do replace still fire, so the above is not a
    # detector that has been narrowed into never answering True.
    assert verdict('{"PATH": "/usr/bin"}') is True
    assert verdict('dict(PATH="/usr/bin", TEST_OUTPUT="x")') is True, (
        "a real repo shape: tests/quality_gates/test_python_and_security_gates.py"
    )
    assert verdict('dict(os.environ, PATH="/usr/bin")') is False, (
        "positional environ carries through"
    )


def test_candidate_tests_come_from_live_inventory_and_reference_map(tmp_path: Path) -> None:
    """The live inventory and reference map both contribute candidate tests."""
    lib = _advisory_lib()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_foo.py").write_text(
        "import subprocess\nimport sys\n\n\ndef test_it():\n"
        '    subprocess.run([sys.executable, "scripts/foo.py"], env={"PATH": "/usr/bin"})\n',
        encoding="utf-8",
    )
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}

    assert lib.load_subprocess_boundary_pairs(tmp_path) == {}, "the target is not import-safe"
    advisory = lib.subprocess_coverage_advisory(tmp_path, targets)
    assert list(advisory) == ["scripts/foo.py"]
    assert advisory["scripts/foo.py"]["mechanisms"] == {"tests/test_foo.py": ["env-replaces"]}


def test_advisory_scope_says_what_was_examined_so_silence_is_not_an_absence(tmp_path: Path) -> None:
    """The class #465 named, applied to this surface: a proof surface that reports a
    gap without reporting the property that produced it makes the reader re-derive
    the diagnosis. Advisory SILENCE has the same problem — "nothing recorded",
    "recorded but no longer present", and "inventory unavailable" were one
    indistinguishable empty dict. `scope` separates them.
    """
    lib = _advisory_lib()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}

    scope = lib.advisory_scope(tmp_path, targets)
    assert scope["inventory"] == "read"
    assert scope["blocked_files_examined"] == 1
    assert scope["files_named"] == []
    assert "NOT proof" in scope["silence_means"]
    # and the report entrypoint carries both keys from one pass
    report = lib.subprocess_coverage_advisory_report(tmp_path, targets)
    assert set(report) == {"subprocess_coverage_advisory", "subprocess_coverage_advisory_scope"}


def test_an_unexpected_exception_degrades_to_silence_instead_of_losing_the_verdict() -> None:
    """Structural, not enumerated. The advisory is called inside the gate's verdict
    body BEFORE the report is emitted, and `main()` is `raise SystemExit(main())`
    with no wrapper — so on a CLEAN run an escaping exception turns exit 0 into
    exit 1, a false BLOCK produced entirely by the advisory. The inner handlers
    catch OSError/ValueError/SyntaxError by name; RecursionError and MemoryError are
    neither.
    """
    lib = _advisory_lib()

    class Exploding(dict):
        def __iter__(self):
            raise RecursionError("pathological input")

    assert lib.subprocess_coverage_advisory(Path("."), Exploding()) == {}
    assert "error" in lib.advisory_scope(Path("."), Exploding())
    report = lib.subprocess_coverage_advisory_report(Path("."), Exploding())
    assert report["subprocess_coverage_advisory"] == {}
    assert "error" in report["subprocess_coverage_advisory_scope"]


def test_an_env_replacing_spawn_of_a_DIFFERENT_script_does_not_implicate_this_one() -> None:
    """The round-2 blocker, pinned. The earlier reader asked only "does this FILE
    contain an env-replacing call anywhere", so a test that scrubs the env for an
    unrelated shell script cast doubt on every Python script it happened to mention.

    The live instance was real: `tests/quality_gates/test_python_and_security_gates.py`
    scrubs the env for a shell-script test at one line and names
    `scripts/plugin_export/check_supply_chain.py` at another — a script whose only exercise is an
    inherited-env spawn at its real in-repo path, i.e. MEASURED. The advisory named
    it anyway. The mechanism is now bound to the spawn call whose command names this
    script.
    """
    lib = _advisory_lib()
    source = (
        "import subprocess\n"
        "import sys\n\n\n"
        "def test_it(tmp_path):\n"
        # scrubbed env, but spawning something else entirely
        '    subprocess.run([sys.executable, "scripts/unrelated.py"], env={"PATH": "/usr/bin"})\n'
        # the blocked script: in-repo, inherited env -> measured
        '    subprocess.run([sys.executable, "scripts/foo.py"])\n'
    )

    assert (
        lib.unmeasured_spawn_mechanisms(_write_raw(source), "tests/test_foo.py", "scripts/foo.py")
        == []
    )

    # Control: move the scrubbed env onto the spawn that DOES name this script.
    bound = source.replace(
        '    subprocess.run([sys.executable, "scripts/foo.py"])\n',
        '    subprocess.run([sys.executable, "scripts/foo.py"], env={"PATH": "/usr/bin"})\n',
    )
    assert lib.unmeasured_spawn_mechanisms(
        _write_raw(bound), "tests/test_foo.py", "scripts/foo.py"
    ) == ["env-replaces"]


def test_a_blocked_file_with_no_proof_targets_is_still_examined(tmp_path: Path) -> None:
    """Round 2, finding 7. The advisory keyed on `blocking_targets`, but a file that
    blocks WITHOUT producing a `path:line` target is the single most likely candidate
    for this diagnosis — its own `blocking_detail` reads "file not tracked by the test
    suite (untested, or exercised only where coverage was never attributed)". It was
    examined zero times, and `scope`
    reported that as nothing to examine.
    """
    lib = _advisory_lib()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")

    # No entry in blocking_targets at all; the file is only in `blocking`.
    advisory = lib.subprocess_coverage_advisory_report(tmp_path, {}, blocking=["scripts/foo.py"])[
        "subprocess_coverage_advisory"
    ]
    assert list(advisory) == ["scripts/foo.py"]
    assert advisory["scripts/foo.py"]["blocked_lines"] == [], "no targets means no line claim"
    # ...and with neither source naming it, the old behaviour (silence) is unchanged.
    assert (
        lib.subprocess_coverage_advisory_report(tmp_path, {}, blocking=[])[
            "subprocess_coverage_advisory"
        ]
        == {}
    )


def test_advisory_silence_is_narrated_to_the_operator_not_only_to_the_json(capsys) -> None:
    """Round 2, finding 3: the #465 class recurring on the repair. With an empty
    advisory, the BLOCK narration was byte-identical to the pre-#465 gate, so the
    reader could not tell "examined 7 candidates, found nothing" from "never ran" —
    and re-derived the diagnosis by hand, which is the waste #465 was filed about.
    Scope belongs in the channel a human reads, not only in the payload.
    """
    trust = import_repo_module(__file__, "scripts.gates_support.changed_line_run_trust")
    scope = {
        "candidate_tests_examined": 7,
        "blocked_files_examined": 1,
        "inventory": "read",
        "files_named": [],
        "silence_means": "...",
    }

    trust.write_blocking_stderr(
        ["scripts/foo.py"],
        {"scripts/foo.py": [{"line": 5, "source": "def b():"}]},
        {},
        scope,
    )
    err = capsys.readouterr().err
    assert "ADVISORY SCOPE (not a blocker)" in err
    assert "examined 7 candidate test file(s) across 1 blocked file(s)" in err
    assert "NOT proof these blocks are honest" in err

    # When the advisory DID name something, its own sentence carries the scope and
    # the extra line would be noise.
    trust.write_blocking_stderr(
        ["scripts/foo.py"],
        {"scripts/foo.py": [{"line": 5, "source": "def b():"}]},
        {"scripts/foo.py": {"subprocess_tests": ["tests/test_foo.py"], "blocked_lines": [5]}},
        {**scope, "files_named": ["scripts/foo.py"]},
    )
    err = capsys.readouterr().err
    assert "ADVISORY (not a blocker)" in err
    assert "ADVISORY SCOPE" not in err

    # A scope that could not be computed says so rather than reading as "clean".
    trust.write_blocking_stderr(["scripts/foo.py"], {}, {}, {"error": "boom"})
    assert "advisory did not run (boom); silence is unexamined" in capsys.readouterr().err


def test_a_reference_map_returning_a_non_mapping_degrades_to_no_candidates(
    tmp_path: Path, monkeypatch
) -> None:
    """The second candidate source is another module's function, so its return shape
    is an assumption. The advisory rides a gate whose verdict already exists, so a
    mapper that returns something unexpected must contribute no candidates rather
    than raise on `.items()` and replace a blocking report with a traceback.
    """
    import sys
    import types

    lib = _advisory_lib()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "foo.py").write_text("def a():\n    return 1\n", encoding="utf-8")
    _write_test_file(tmp_path, "tests/test_foo.py", "scripts/foo.py", shape="replaces-env")
    targets = {"scripts/foo.py": [{"line": 5, "source": "def b():"}]}

    # Control first: with the real mapper, this file IS found via the reference map
    # (the live inventory has no matching row), so the assertions below are about the
    # degraded shape and not about a helper that never finds anything.
    assert list(lib.subprocess_coverage_advisory(tmp_path, targets)) == ["scripts/foo.py"]

    stub = types.ModuleType("scripts.mutation.suggest_mutation_coverage_command")
    stub.tests_referencing_paths = lambda repo_root, paths: ["not", "a", "mapping"]
    monkeypatch.setitem(sys.modules, "scripts.mutation.suggest_mutation_coverage_command", stub)

    assert lib._referencing_tests(tmp_path, ["scripts/foo.py"]) == {}
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}, (
        "no inventory, no map -> silent"
    )
    assert lib.advisory_scope(tmp_path, targets)["reference_map"] == "empty-or-unavailable"

    # ...and a mapper that RAISES is the same silence, not a lost verdict.
    def explode(repo_root, paths):
        raise RuntimeError("mapper blew up")

    stub.tests_referencing_paths = explode
    assert lib._referencing_tests(tmp_path, ["scripts/foo.py"]) == {}
    assert lib.subprocess_coverage_advisory(tmp_path, targets) == {}
