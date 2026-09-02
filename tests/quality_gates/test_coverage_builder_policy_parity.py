"""SC18: the repo has ONE policy on what may be instrumented under coverage.

Two builders wrap "run pytest under coverage": `mutation_sampling_lib.
coverage_run_command` (argv, used by the changed-line mutation gate) and
`mutation_coverage_producer.instrument_broad_command` (shell string, used by
the release producer). Until 2026-08-15 they held OPPOSITE policies on the standing pytest
runner -- the producer accepted it, the sampling lib refused it with *"use a
helper script for other runners"* -- and the changed-line gate used the refusing
one. That is why the repo's longest proof spawned serial bare pytest while the
xdist runner was already measured, budgeted, and blocking.

The FIRST repair shared only a boolean and left each builder's own inline shape
test in place; a round-1 bounded reviewer measured three shapes on which the two
still disagreed. So the shared thing is `classify_instrumentable_command`, and
these tests pin agreement per shape rather than per name.

They do NOT assert the builders emit the same STRING -- they deliberately do not
(argv here; a string with an unquoted glob there).
"""

from __future__ import annotations

import shlex
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import mutation_coverage_producer as producer
from scripts import mutation_sampling_lib as sampling

from .seeding_support import load_module
from .support import ROOT


def _load_teeth():
    return load_module(
        "check_changed_line_mutation_coverage",
        ROOT / "scripts/check_changed_line_mutation_coverage.py",
    )


#: (command, accepted). Every row was chosen because SOME reading of the two
#: builders answered it differently at some point in this slice's history.
COMMAND_SHAPES = [
    # The `cosmic-ray.toml` literal, and the shapes around it that the first
    # repair's prefix-with-trailing-space predicate refused while the argv
    # builder's token test accepted.
    ("python3 -m pytest -q -m 'not release_only' tests", True),
    ("python3 -m pytest", True),
    ("pytest -q tests", True),
    ("pytest", True),
    ("python -m pytest -q tests", True),
    ("/usr/bin/python3 -m pytest -q tests", True),
    # The standing runner: the shape SC18 names, in every interpreter spelling
    # the two builders stripped differently.
    ("python3 scripts/gates_support/run_standing_pytest.py", True),
    ("python3 scripts/gates_support/run_standing_pytest.py --mode full", True),
    ("python scripts/gates_support/run_standing_pytest.py --mode full", True),
    ("/usr/bin/python3 scripts/gates_support/run_standing_pytest.py", True),
    ("python3 /abs/path/to/scripts/gates_support/run_standing_pytest.py --mode read-only", True),
    ("scripts/gates_support/run_standing_pytest.py --mode full", True),
    # Helper flags print and exit. Instrumenting one yields an EMPTY coverage set
    # that reads exactly like a suite which covered nothing.
    ("python3 scripts/gates_support/run_standing_pytest.py --print-command", False),
    ("python3 scripts/gates_support/run_standing_pytest.py --print-last-run", False),
    ("python3 scripts/gates_support/run_standing_pytest.py --print-targets", False),
    ("python3 scripts/gates_support/run_standing_pytest.py --print-expanded-targets", False),
    ("python3 scripts/gates_support/run_standing_pytest.py --print-temp-root", False),
    # argparse accepts unambiguous abbreviations, so an ENUMERATED helper-flag
    # set is bypassed by spelling the same early exit shorter.
    ("python3 scripts/gates_support/run_standing_pytest.py --print-last", False),
    ("python3 scripts/gates_support/run_standing_pytest.py --print-temp", False),
    # Bad quoting must not become a way PAST the helper-flag rule: acceptance
    # falls back to a naive split precisely so a `--print*` token is still seen.
    ("python3 scripts/gates_support/run_standing_pytest.py --print-last 'unterminated", False),
    # The other side of the prefix rule: `--p*` flags that are NOT print flags
    # must stay accepted. `--pytest-target` is the repo's own documented focused
    # coverage command (docs/implementation-discipline.md), so
    # widening the prefix to `--p` would refuse it.
    ("python3 scripts/gates_support/run_standing_pytest.py --pytest-target tests/x.py::test_one", True),
    ("python3 scripts/gates_support/run_standing_pytest.py --extra-pytest-target tests/x.py", True),
    # A wrapper prefix renders into `coverage run env ...`, which execs the
    # wrapper as a Python script. Both builders refuse rather than emit it.
    ("env CHARNESS_STANDING_PYTEST_PYTHON=python3 python3 scripts/gates_support/run_standing_pytest.py", False),
    ("timeout 300 python3 -m pytest -q tests", False),
    ("ruff check .", False),
    ("bash scripts/run-quality.sh", False),
    ("", False),
]

#: Interpreter spellings whose RENDERING (not just acceptance) diverged between
#: the two builders: sampling stripped `python`/`python3` by exact match, the
#: producer stripped by basename, so each emitted an unrunnable command for the
#: spelling the other handled.
INTERPRETER_SPELLINGS = [
    "python3 scripts/gates_support/run_standing_pytest.py --mode full",
    "python scripts/gates_support/run_standing_pytest.py --mode full",
    "/usr/bin/python3 scripts/gates_support/run_standing_pytest.py --mode full",
    "scripts/gates_support/run_standing_pytest.py --mode full",
]


def test_the_policy_is_one_object_not_two_copies() -> None:
    """The producer RE-EXPORTS the classifier rather than defining its own.

    Necessary but NOT sufficient, and a round-1 reviewer was right to say so: the
    fork this slice repaired was not a second definition of the predicate, it was
    a second decision procedure inside `coverage_run_command`. That is what
    `test_both_builders_agree_with_the_shared_policy` covers; this test only stops
    the cheaper regression of rebinding a local copy."""
    assert producer.classify_instrumentable_command is sampling.classify_instrumentable_command
    assert producer.is_standing_pytest_runner_command is sampling.is_standing_pytest_runner_command
    assert producer.is_instrumentable_pytest_command is sampling.is_instrumentable_pytest_command


@pytest.mark.parametrize("command,accepted", COMMAND_SHAPES)
def test_both_builders_agree_with_the_shared_policy(
    command: str, accepted: bool, tmp_path: Path
) -> None:
    data_file = tmp_path / ".coverage"
    assert sampling.is_instrumentable_pytest_command(command) is accepted

    if accepted:
        argv = sampling.coverage_run_command(command, data_file)
        assert argv[1:5] == ["-m", "coverage", "run", "--data-file"]
        instrumented = producer.instrument_broad_command(command, data_file)
        assert "-m coverage run --data-file" in instrumented
        # Same driver from both builders, for every accepted shape -- not only the
        # four in INTERPRETER_SPELLINGS.
        assert shlex.split(instrumented)[0] == argv[0]
        return

    with pytest.raises(SystemExit):
        sampling.coverage_run_command(command, data_file)
    with pytest.raises(ValueError):
        producer.instrument_broad_command(command, data_file)


@pytest.mark.parametrize("command", INTERPRETER_SPELLINGS)
def test_both_builders_render_the_runner_the_same_way(command: str, tmp_path: Path) -> None:
    """Agreement on ACCEPTANCE is not enough: an accepted command rendered into
    `coverage run python scripts/...` or `coverage run /usr/bin/python3 ...` makes
    coverage exec the interpreter as a script. Both builders must drop the
    interpreter, whatever it is spelled."""
    data_file = tmp_path / ".coverage"

    argv = sampling.coverage_run_command(command, data_file)
    string_tokens = shlex.split(producer.instrument_broad_command(command, data_file))

    # tokens[0] is compared BETWEEN the two renderings on purpose: it is the only
    # position where they diverged, and a round-2 reviewer found the earlier
    # version of this test asserting every index except that one.
    assert argv[0] == string_tokens[0]
    for tokens in (argv, string_tokens):
        assert tokens[1:6] == ["-m", "coverage", "run", "--data-file", str(data_file)]
        # `coverage run <script>`, not `-m`: the runner is a script. Its pytest
        # child is measured through COVERAGE_PROCESS_START/sitecustomize.
        assert "-m" not in tokens[6:]
        assert Path(tokens[6]).name == "run_standing_pytest.py"
        assert tokens[7:] == ["--mode", "full"]


def test_bare_pytest_still_runs_through_the_module_form(tmp_path: Path) -> None:
    """The reconcile ADDS shapes; it must not change the one already in use by
    `cosmic-ray.toml`'s literal."""
    argv = sampling.coverage_run_command(
        "python3 -m pytest -q -m 'not release_only' tests", tmp_path / ".coverage"
    )
    assert argv[0] == "python3"
    assert argv[6:] == ["-m", "pytest", "-q", "-m", "not release_only", "tests"]


def test_the_producer_keeps_a_glob_unquoted_for_the_shell(tmp_path: Path) -> None:
    """The reason the two builders render differently at all. The producer's
    output is run through a shell, so the glob must survive verbatim."""
    command = "pytest -q tests/quality_gates tests/test_*.py"

    instrumented = producer.instrument_broad_command(command, tmp_path / ".coverage")

    assert instrumented.endswith(" -m pytest -q tests/quality_gates tests/test_*.py")


def test_an_unterminated_quote_is_refused_with_a_message_not_a_valueerror(tmp_path: Path) -> None:
    """Acceptance tolerates bad quoting (it only needs to see a `--print*` token),
    but the argv builder must SPLIT, and a raw ValueError escaping into the gate's
    probe is the late failure `parse_args` exists to prevent."""
    command = "python3 scripts/gates_support/run_standing_pytest.py 'unterminated"
    assert sampling.is_instrumentable_pytest_command(command) is True

    with pytest.raises(SystemExit) as excinfo:
        sampling.coverage_run_command(command, tmp_path / ".coverage")

    assert "cannot split" in str(excinfo.value)


# --- the changed-line gate's --test-command override ---------------------------
# Reconciling the builders is only half of SC18's point: the gate that spawns the
# dominated command reads `cosmic-ray.toml`'s `test-command` literal, so without
# an override the fast path stays unreachable from the surface that needed it.


def _probe_args(*, test_command: str | None) -> SimpleNamespace:
    return SimpleNamespace(
        reuse_coverage=False,
        config=Path("cosmic-ray.toml"),
        write_fresh_marker=False,
        test_command=test_command,
    )


def _parse(monkeypatch, *argv: str):
    teeth = _load_teeth()
    monkeypatch.setattr(sys, "argv", ["teeth", *argv])
    return teeth, teeth.parse_args()


def test_a_valid_test_command_parses_and_reaches_the_namespace(monkeypatch) -> None:
    """Pins that the FLAG EXISTS. Without this, the refusal test below is green
    against a tree where `--test-command` was never added -- argparse exits 2 for
    an unrecognized option too."""
    runner = "python3 scripts/gates_support/run_standing_pytest.py"
    _teeth, args = _parse(monkeypatch, "--test-command", runner)

    assert args.test_command == runner


def test_absent_override_leaves_the_namespace_empty(monkeypatch) -> None:
    _teeth, args = _parse(monkeypatch)

    assert args.test_command is None


def test_a_non_instrumentable_override_is_refused_by_the_shared_policy(monkeypatch, capsys) -> None:
    """Refused with the SHARED refusal text, at argument time. Asserting the
    message is what distinguishes 'the policy refused it' from argparse's generic
    exit 2 -- and from a local hand-rolled refusal that would drift."""
    with pytest.raises(SystemExit) as excinfo:
        _parse(monkeypatch, "--test-command", "bash scripts/run-quality.sh")

    assert excinfo.value.code == 2
    stderr = capsys.readouterr().err
    assert "is not an instrumentable pytest command" in stderr
    assert sampling.INSTRUMENTABLE_COMMAND_REFUSAL.split(".")[0] in stderr


def test_test_command_override_replaces_the_config_literal(tmp_path: Path, monkeypatch) -> None:
    teeth = _load_teeth()
    seen: dict[str, str] = {}
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q tests")
    monkeypatch.setattr(
        teeth,
        "run_test_coverage",
        lambda repo_root, command, coverage_json, **kw: seen.update(command=command),
    )

    runner = "python3 scripts/gates_support/run_standing_pytest.py"
    teeth._ensure_coverage(
        _probe_args(test_command=runner), tmp_path, tmp_path / "cov.json", "abc123"
    )

    assert seen["command"] == runner


def test_absent_override_still_reads_the_config_literal(tmp_path: Path, monkeypatch) -> None:
    """The override is opt-in: `cosmic-ray.toml` still decides by default, because
    it is also what cosmic-ray runs per mutant and this flag does not touch that."""
    teeth = _load_teeth()
    seen: dict[str, str] = {}
    monkeypatch.setattr(teeth, "read_test_command", lambda config: "python3 -m pytest -q tests")
    monkeypatch.setattr(
        teeth,
        "run_test_coverage",
        lambda repo_root, command, coverage_json, **kw: seen.update(command=command),
    )

    teeth._ensure_coverage(
        _probe_args(test_command=None), tmp_path, tmp_path / "cov.json", "abc123"
    )

    assert seen["command"] == "python3 -m pytest -q tests"
