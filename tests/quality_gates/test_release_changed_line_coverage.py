"""The release-final changed-line proof (D40).

The lane this replaces exited 0 by construction, which is how a gate that fired
eight times still let eight regressions land. Its replacement is only worth having
if it cannot be read as a pass when it did not judge — so most of what these tests
pin is the SHAPE OF NOT KNOWING: producer death, an unresolvable base, a consumer
refusal, and a mapping that reached nothing all have to be distinguishable from a
clean run, on the exit code and in the payload.
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .support import ROOT, run_script

SCRIPT = "scripts/release_changed_line_coverage.py"


@pytest.fixture()
def gate():
    from tests.script_loader import load_script_module

    return load_script_module("release_changed_line_coverage_under_test", ROOT / SCRIPT)


def _recommendation(**overrides) -> dict:
    payload = {
        "status": "partial",
        "base_sha": "b" * 40,
        "changed_pool_files": ["scripts/mapped.py", "scripts/unmapped.py"],
        "mapped_tests_by_file": {"scripts/mapped.py": ["tests/test_mapped.py"]},
        "unmapped_changed_pool_files": ["scripts/unmapped.py"],
    }
    payload.update(overrides)
    targets = sorted(
        {target for paths in payload["mapped_tests_by_file"].values() for target in paths}
    )
    if targets:
        payload.setdefault(
            "command",
            shlex.join(
                [
                    "python3",
                    "scripts/run_standing_pytest.py",
                    "--repo-root",
                    ".",
                    "--mode",
                    "read-only",
                    *(token for target in targets for token in ("--pytest-target", target)),
                ]
            ),
        )
    else:
        payload.pop("command", None)
    return payload


def test_no_base_sha_is_a_no_verdict_not_a_pass(gate, monkeypatch, capsys) -> None:
    """Exit 0 here is what the old lane did, and it is the whole bug: a range that
    could not be resolved was reported the same way as a range with nothing wrong."""
    monkeypatch.setattr(gate._producer, "default_mutation_base_sha", lambda _root: "")

    assert gate.main(["--repo-root", str(ROOT)]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == "no-verdict"
    assert "It is NOT a pass" in captured.err


def test_a_dead_producer_is_a_no_verdict_not_a_pass(gate, monkeypatch, capsys) -> None:
    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())

    def _boom(*_args, **_kwargs):
        error = RuntimeError("producer failed")
        error.returncode = 1  # type: ignore[attr-defined]
        raise error

    monkeypatch.setattr(gate._producer, "produce_command_coverage", _boom)

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert payload["status"] == "no-verdict"
    assert payload["reason"] == "focused producer failed"
    assert "This is NOT a pass" in captured.err


def test_nothing_mapped_warns_loudly_and_does_not_block(gate, monkeypatch, capsys) -> None:
    """Policy (a), chosen 2026-07-29 and PRESERVED: an unmapped file is a MAPPER gap,
    not a coverage gap, so the producer reports it as unproven rather than inventing
    a coverage failure over the tool's blind spot.

    What changed 2026-08-06 (operator decision on #488) is the BYTE, not the policy.
    The lane used to return 0 here — the same verdict as a run that analyzed its whole
    changed set — so `run-quality.sh` printed PASS beside the warning below, and a real
    release proof could have carried an unproven result. It now returns 4 (`PARTIAL`),
    which cannot be read as a clean release result."""
    monkeypatch.setattr(
        gate._suggest,
        "build_recommendation",
        lambda *_a, **_k: _recommendation(status="missing", mapped_tests_by_file={}),
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == 4, "an unanalyzed changed set must not wear a bare pass"
    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert payload["status"] == "unproven"
    assert payload["unmapped_changed_pool_files"] == ["scripts/unmapped.py"]
    assert captured.err.startswith("WARNING")
    assert "nothing could be proven" in captured.err


def test_noop_is_quiet(gate, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation(status="noop")
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == 0

    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == "noop"
    assert "WARNING" not in captured.err


def test_warning_lines_use_the_head_run_quality_actually_surfaces(gate, capsys) -> None:
    """`run-quality.sh::print_phase_output` only shows a PASSING gate's output when a
    line matches `^(WARNING|WARN|WEAK|ADVISORY)`. A warning that does not start that
    way is invisible on exactly the runs it exists for, which is the failure mode the
    previous lane already had."""
    gate._warn("something unproven")

    assert capsys.readouterr().err.startswith("WARNING (release changed-line coverage):")


def test_focused_command_is_instrumentable_and_keeps_broad_marker_policy(gate) -> None:
    """Target narrowing may not admit tests the broad coverage producer excludes."""
    from scripts.mutation_sampling_lib import read_test_command

    command = gate._focused_pytest_command(
        _recommendation(
            mapped_tests_by_file={
                "a.py": ["tests/test_b.py"],
                "c.py": ["tests/test_a.py", "tests/test_b.py"],
            }
        )
    )

    tokens = shlex.split(command)
    assert tokens[:6] == [
        "python3",
        "scripts/run_standing_pytest.py",
        "--repo-root",
        ".",
        "--mode",
        "read-only",
    ]
    broad_tokens = shlex.split(read_test_command(ROOT / "cosmic-ray.toml"))
    marker_index = broad_tokens.index("-m", broad_tokens.index("pytest") + 1)
    assert broad_tokens[marker_index + 1] == "not release_only"
    assert "--include-release-only" not in tokens
    assert tokens.count("--pytest-target") == 2
    assert tokens[tokens.index("--pytest-target") + 1] == "tests/test_a.py"
    assert (
        tokens[tokens.index("--pytest-target", tokens.index("--pytest-target") + 1) + 1]
        == "tests/test_b.py"
    )
    assert gate._producer.is_instrumentable_pytest_command(command)


@pytest.mark.boundary_contract(
    reason="prove the focused release command excludes release-only tests at its real pytest process boundary"
)
@pytest.mark.slow_corpus
def test_focused_command_excludes_a_release_only_execution_path(gate, tmp_path) -> None:
    """Execute the real child command, not only its token shape.

    The release-only case is the sole writer of the sentinel. If the focused lane
    widens the broad population again, this control observes the execution that can
    turn a broad-missing changed line into a focused-executed false clean.
    """
    sentinel = tmp_path / "release-only-ran"
    test_file = tmp_path / "test_marker_population.py"
    test_file.write_text(
        "import pathlib\n"
        "import pytest\n\n"
        "@pytest.mark.release_only\n"
        "def test_release_only_path():\n"
        f"    pathlib.Path({str(sentinel)!r}).write_text('ran', encoding='utf-8')\n\n"
        "def test_standing_control():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    command = gate._focused_pytest_command(
        _recommendation(mapped_tests_by_file={"scripts/a.py": [str(test_file)]})
    )
    env = os.environ.copy()
    env["PYTEST_ADDOPTS"] = "-p no:xdist"

    result = subprocess.run(
        shlex.split(command), cwd=ROOT, env=env, capture_output=True, text=True, check=False
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert not sentinel.exists()
    assert "1 passed" in result.stdout
    assert "1 deselected" in result.stdout


def test_focused_command_is_none_when_no_test_is_mapped(gate) -> None:
    assert gate._focused_pytest_command(_recommendation(mapped_tests_by_file={})) is None


def test_focused_producer_exports_only_mapped_changed_files(gate, monkeypatch) -> None:
    captured: dict = {}
    monkeypatch.setattr(
        gate._suggest,
        "build_recommendation",
        lambda *_a, **_k: _recommendation(
            status="recommended",
            changed_pool_files=["scripts/mapped.py"],
            unmapped_changed_pool_files=[],
        ),
    )

    def fake_produce(*_args, **kwargs):
        captured.update(kwargs)
        return {"returncode": 0, "produced_mutation_coverage": True}

    monkeypatch.setattr(gate._producer, "produce_command_coverage", fake_produce)
    monkeypatch.setattr(Path, "is_file", lambda _self: True)

    def fake_consumer_main():
        captured["consumer_argv"] = [sys.executable, *sys.argv]
        print(json.dumps({"ok": True, "blocking": []}))
        return 0

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=fake_consumer_main),
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == 0
    assert captured["include_paths"] == ["scripts/mapped.py"]
    assert "--require-fresh-coverage" in captured["consumer_argv"]


@pytest.mark.parametrize(
    "producer_result",
    [
        {"returncode": 1, "produced_mutation_coverage": False},
        {"returncode": 0, "produced_mutation_coverage": False},
    ],
)
def test_unconfirmed_producer_result_is_no_verdict(
    gate, monkeypatch, capsys, producer_result: dict
) -> None:
    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())
    monkeypatch.setattr(
        gate._producer, "produce_command_coverage", lambda *_a, **_k: producer_result
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.NO_VERDICT_EXIT
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["reason"] == "focused coverage was not produced"


def test_run_command_surfaces_stdout_on_failure(gate, tmp_path, capsys) -> None:
    """pytest reports failures on STDOUT. Surfacing only stderr left the operator with
    `the producer failed (exit 1)` and no failing test name — and a gate whose failure
    cannot be diagnosed is a gate that gets disabled."""
    with pytest.raises(RuntimeError):
        gate._run_command(tmp_path, "echo FAILED_TEST_MARKER_ON_STDOUT; exit 1", "verify")

    assert "FAILED_TEST_MARKER_ON_STDOUT" in capsys.readouterr().err


def test_cli_help_names_the_repo_root_and_base(monkeypatch) -> None:
    result = run_script(SCRIPT, "--help")

    assert result.returncode == 0
    assert "--base-sha" in result.stdout
    assert "--repo-root" in result.stdout


# --------------------------------------------------------------------------- #
# Round-1 review repairs. Each of these was exit 0 reported as `clean` while the
# consumer's own payload said it had established nothing — the exit-0-means-proven
# equivalence this lane exists to break, reintroduced at the surface reporting the
# lane's verdict.
# --------------------------------------------------------------------------- #
def _consumer(stdout: str, returncode: int = 0):
    return SimpleNamespace(returncode=returncode, stdout=stdout, stderr="")


def test_a_dirty_pool_is_unestablished_not_clean(gate) -> None:
    """The focused coverage is produced by running pytest against the LIVE worktree
    while the changed-line mapping is computed against HEAD. Line numbers can skew
    between the two trees, so an executed worktree line can be attributed to a
    different HEAD statement — a false PASS, and outside the subset-of-full-coverage
    safety argument, which covers test-subsetting only."""
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": True, "blocking": [], "dirty_pool_unverified": True}))
    )

    assert status == gate.UNESTABLISHED_STATUS
    assert "different tree" in reason


def test_a_limit_that_analyzed_nothing_is_unestablished_not_clean(gate) -> None:
    status, reason = gate._verdict_from_consumer(
        _consumer(
            json.dumps(
                {
                    "ok": True,
                    "blocking": [],
                    "reason": "every changed mutation-pool file (2) fell OUTSIDE --limit-to-file; "
                    "this run analyzed nothing and proves nothing about them",
                }
            )
        )
    )

    assert status == gate.UNESTABLISHED_STATUS
    assert "proves nothing" in reason


def test_an_unreadable_consumer_payload_is_a_no_verdict(gate) -> None:
    """Exit 0 with no readable payload means the exit code stands for nothing."""
    status, reason = gate._verdict_from_consumer(_consumer("not json"))

    assert status == "no-verdict"
    assert "stands for nothing" in reason


def test_a_real_clean_verdict_is_still_clean(gate) -> None:
    """The discriminating control: the repairs narrowed `clean`, they did not delete it.
    Without this, every test above would pass on a surface that never reports clean."""
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": True, "blocking": [], "changed_pool_files": ["scripts/a.py"]}))
    )

    assert status == "clean"
    assert "covered" in reason


def test_blocking_is_read_from_the_exit_code_not_the_payload(gate) -> None:
    status, reason = gate._verdict_from_consumer(
        _consumer(json.dumps({"ok": False, "blocking": ["scripts/a.py"]}), returncode=1)
    )

    assert status == "blocked"
    assert "uncovered changed lines" in reason


def test_the_focused_coverage_path_is_not_the_canonical_mutation_artifact(gate) -> None:
    """Writing subset coverage to `reports/mutation/test-coverage.json` would leave it
    at the path the broad mutation report owns, carrying a valid freshness marker, so
    every `--require-fresh-coverage` consumer would read freshness as breadth."""
    default = gate.parse_args(["--repo-root", "."]).coverage_json

    assert default.name == "release-changed-line-coverage.json"
    assert default.as_posix() != "reports/mutation/test-coverage.json"


# --------------------------------------------------------------------------- #
# Round-2 review repair. Round 1 made the lane NAME an unestablished result; round 2
# found that naming it changed nothing, because it still exited 0 -- so one
# uncommitted pool file disarmed the whole lane, and `run-quality.sh` states that a
# live dirty worktree is the normal condition. Exit 0 plus prose is exactly what the
# predecessor did and exactly why it was walked past eight times.
# --------------------------------------------------------------------------- #
def _blocking_consumer_stub(gate, monkeypatch, consumer_payload: dict, returncode: int = 0):
    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_a, **_k: {"returncode": 0, "produced_mutation_coverage": True},
    )
    monkeypatch.setattr(Path, "is_file", lambda _self: True)

    def fake_consumer_main():
        print(json.dumps(consumer_payload))
        return returncode

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=fake_consumer_main),
    )


def test_the_wrapper_does_not_rewrite_an_unestablished_status_into_partial(
    gate, monkeypatch, capsys
) -> None:
    """The braces half of the guard above, driven directly.

    If a consumer ever returns 4 for a payload the wrapper reads as dirty, the
    wrapper must keep the refusable status rather than adopting the non-refusable
    one. This is the seam the first cut broke; the consumer-side fix alone would
    leave it re-breakable by any future change to the consumer's ordering."""
    _blocking_consumer_stub(
        gate,
        monkeypatch,
        {"ok": True, "blocking": [], "dirty_pool_unverified": True},
        returncode=4,
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    assert code == 1
    assert yaml.safe_load(capsys.readouterr().out)["status"] == gate.UNESTABLISHED_STATUS


def test_a_partial_consumer_result_becomes_partial_and_never_refuses(
    gate, monkeypatch, capsys
) -> None:
    """The #488 seam, end to end. `returncode=4` is what the consumer ACTUALLY returns
    for this payload — SOME changed pool files analyzed, one left out — so the stub does
    not fabricate a combination the consumer cannot produce.

    The measured failure this closes: the consumer printed "this run analyzed only 6 of
    7 changed mutation-pool file(s). A clean verdict says NOTHING about the rest",
    returned 0, this lane returned 0, and `run-quality.sh` printed PASS beside an
    unproven result. The explicit nonzero partial byte prevents that."""
    _blocking_consumer_stub(
        gate,
        monkeypatch,
        {
            "ok": True,
            "blocking": [],
            "changed_line_proof": "partial",
            "unanalyzed_changed_pool_files": ["scripts/bar.py"],
        },
        returncode=4,
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == 4
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == gate.PARTIAL_STATUS
    assert "analyzed only PART of the changed mutation-pool set" in captured.err


def test_a_partial_consumer_result_stays_unproven_without_release_refusal(
    gate, monkeypatch, capsys
) -> None:
    """The discriminating control for the test above, and the one that keeps the repair
    from overturning policy (a) sideways. The state now has a non-zero byte, so the
    cheap next step would be to route it through `--refuse-unestablished` — which is
    intentionally reserved for the unestablished release result. This diagnostic
    still reports 4, not a clean pass."""
    _blocking_consumer_stub(
        gate,
        monkeypatch,
        {
            "ok": True,
            "blocking": [],
            "changed_line_proof": "partial",
            "unanalyzed_changed_pool_files": ["scripts/bar.py"],
        },
        returncode=4,
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    assert code == 4, "the partial state is unproven, not a clean pass"
    assert yaml.safe_load(capsys.readouterr().out)["status"] == gate.PARTIAL_STATUS


def test_an_unestablished_result_refuses_at_release_boundary(gate, monkeypatch, capsys) -> None:
    # `returncode=3` is what the consumer ACTUALLY returns for this payload. Stubbing
    # 0 alongside a `dirty_pool_unverified` payload fabricated a combination the
    # consumer cannot produce, so this pair stayed green while the wrapper/consumer
    # seam was broken end to end.
    _blocking_consumer_stub(
        gate, monkeypatch, {"ok": True, "blocking": [], "dirty_pool_unverified": True}, returncode=3
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    assert code == 1
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == gate.UNESTABLISHED_STATUS
    assert "an unestablished changed-line result is not a pass" in captured.err


def test_the_same_result_stays_non_blocking_mid_work(gate, monkeypatch, capsys) -> None:
    """The discriminating control. A dirty worktree IS the normal state during the
    verify phase, which runs before commit, so refusing unconditionally would hard-fail
    every ordinary run and get the lane disabled — the failure mode being repaired.

    Non-blocking is NOT exit 0: `run-quality.sh` prints PASS for 0, which is the green
    over an unestablished scope this lane exists to refuse. Exit 3 is rendered UNPROVEN
    and counted in neither column."""
    _blocking_consumer_stub(
        gate, monkeypatch, {"ok": True, "blocking": [], "dirty_pool_unverified": True}, returncode=3
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.UNESTABLISHED_EXIT
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == gate.UNESTABLISHED_STATUS
    assert "established no changed-line verdict" in captured.err


def test_policy_a_stays_non_blocking_for_direct_diagnostics(gate, monkeypatch, capsys) -> None:
    """`--refuse-unestablished` must NOT govern policy (a). An unmapped file is a mapper
    gap, and the repo owner's decision is that a direct diagnostic is never stopped over the tool's
    blind spot. Conflating the two would silently overturn that decision.

    This is the test that keeps the #488 repair honest. The repair gives the state its
    own non-zero byte; the temptation is then to route it through the existing refusal
    flag, which would reverse policy (a) under a defect-repair banner. Direct
    diagnostics still read 4, not 1."""
    monkeypatch.setattr(
        gate._suggest,
        "build_recommendation",
        lambda *_a, **_k: _recommendation(status="missing", mapped_tests_by_file={}),
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    # Discriminating because the INPUT varies: `--refuse-unestablished` is passed.
    # Asserting `!= 1` right after `== 4` on the same value would restate it.
    assert code == 4, "policy (a) reports PARTIAL for direct diagnostics, not a refusal"
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "unproven"


def test_missing_focused_coverage_refuses_instead_of_stalling(gate, monkeypatch, capsys) -> None:
    """The consumer runs with `--reuse-coverage`; a missing file makes it fall through
    to a broad probe, turning a ~24s lane into an 11-15 minute stall with no
    explanation. A gate that hangs is a gate that gets disabled."""
    monkeypatch.setattr(gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation())
    monkeypatch.setattr(
        gate._producer,
        "produce_command_coverage",
        lambda *_a, **_k: {"returncode": 0, "produced_mutation_coverage": True},
    )
    monkeypatch.setattr(Path, "is_file", lambda _self: False)

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.NO_VERDICT_EXIT
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["reason"] == "focused coverage missing after produce"
    assert "wrote no coverage" in captured.err


# --------------------------------------------------------------------------- #
# The lane's own uncovered changed lines, named by the lane itself on its first
# committed run. Each is a not-a-pass arm or the human channel that reports one:
# leaving them unexecuted would mean the paths that exist to refuse silence had
# never themselves been run.
# --------------------------------------------------------------------------- #
def test_a_blocked_suggester_is_a_no_verdict(gate, monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        gate._suggest, "build_recommendation", lambda *_a, **_k: _recommendation(status="blocked")
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["reason"] == "suggester blocked"
    assert "This is NOT a pass" in captured.err


def test_a_consumer_refusal_is_a_no_verdict(gate, monkeypatch, capsys) -> None:
    """The consumer exits 2 for a startup refusal or a mid-run drift — its own
    "no verdict". Passing that through as anything else would launder a refusal."""
    _blocking_consumer_stub(gate, monkeypatch, {"ok": True, "blocking": []}, returncode=2)

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    payload = yaml.safe_load(captured.out)
    assert payload["status"] == "no-verdict"
    assert "exit 2" in payload["reason"]
    assert "this is NOT a pass" in captured.err


def test_output_reports_status_and_reason(gate, monkeypatch, capsys) -> None:
    """This document IS the operator's whole view of the verdict; the run-quality
    summary prints only the label and PASS/FAIL.

    The `status -- reason` human line this used to read was deleted with `--json`
    on 2026-08-14. Both facts it carried are payload keys now, so the assertion
    moves to the keys rather than to the sentence that formatted them."""
    _blocking_consumer_stub(
        gate, monkeypatch, {"ok": True, "blocking": [], "changed_pool_files": ["scripts/a.py"]}
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == 0

    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "clean"
    assert "covered" in payload["reason"]


def test_the_consumer_payload_reaches_the_operator(gate, monkeypatch, capsys) -> None:
    """The consumer's own payload used to be written raw to stdout beside this
    lane's human line. One YAML document cannot carry interleaved child bytes, so
    it rides under `consumer_stdout` — the operator must still be able to read it."""
    _blocking_consumer_stub(
        gate, monkeypatch, {"ok": True, "blocking": [], "marker": "PAYLOAD_MARKER"}
    )

    gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert "PAYLOAD_MARKER" in yaml.safe_load(capsys.readouterr().out)["consumer_stdout"]


def test_run_command_returns_the_producer_result_on_success(gate, tmp_path) -> None:
    result = gate._run_command(tmp_path, "echo produced", "verify")

    assert result["returncode"] == 0
    assert result["phase"] == "verify"
    assert "produced" in result["stdout"]


def test_an_unreadable_consumer_payload_refuses_end_to_end(gate, monkeypatch, capsys) -> None:
    """The consumer exited 0 but emitted nothing parseable, so its exit code stands for
    nothing. Reached through `main` rather than the classifier alone: the classifier
    returning `no-verdict` is worthless if `main` still returns the consumer's 0."""
    _blocking_consumer_stub(gate, monkeypatch, {}, returncode=0)

    def unreadable_consumer_main():
        print("<html>not json</html>")
        return 0

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=unreadable_consumer_main),
    )

    assert gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40]) == gate.NO_VERDICT_EXIT

    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out)["status"] == "no-verdict"
    assert "established no changed-line verdict" in captured.err


def test_a_consumer_error_is_still_a_no_verdict_not_an_unestablished(
    gate, monkeypatch, capsys
) -> None:
    """Exit 3 is the ONLY consumer code routed to the unestablished path. A refusal
    (2) or any other non-zero must stay `no-verdict`, or the wrapper launders a real
    failure into a non-blocking word."""
    _blocking_consumer_stub(gate, monkeypatch, {"ok": False, "blocking": []}, returncode=2)

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.NO_VERDICT_EXIT
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "no-verdict"


def test_an_unreadable_consumer_payload_stays_a_no_verdict_even_on_exit_three(
    gate, monkeypatch, capsys
) -> None:
    """`no-verdict` means the consumer's stdout could not be READ, so its exit code
    stands for nothing — including a 3. Rewriting it to `unestablished` reported an
    unreadable result as a bounded, non-blocking "ran, established nothing": the same
    exit-code-stands-for-nothing equivalence this lane exists to break, one layer in."""
    _blocking_consumer_stub(gate, monkeypatch, {}, returncode=3)

    def unreadable_consumer_main():
        print("not json at all")
        return 3

    monkeypatch.setattr(
        gate,
        "import_repo_module",
        lambda *_args: SimpleNamespace(main=unreadable_consumer_main),
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40])

    assert code == gate.NO_VERDICT_EXIT
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "no-verdict"


def test_the_release_refusal_carries_the_payload_that_names_what_went_unproven(
    gate, monkeypatch, capsys
) -> None:
    """The consumer payload is where the unestablished FILES are listed. Emitting it
    on the non-blocking path and withholding it on the release-refusal path is
    a refusal the operator cannot diagnose."""
    _blocking_consumer_stub(
        gate,
        monkeypatch,
        {
            "ok": True,
            "blocking": [],
            "dirty_pool_unverified": True,
            "uncommitted_pool_files": ["scripts/x.py"],
        },
        returncode=3,
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    assert code == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    assert "scripts/x.py" in payload["consumer_stdout"]


def test_an_empty_changed_set_is_clean_not_refusable(gate, monkeypatch, capsys) -> None:
    """An empty scope is nothing to prove, not something left unproven. Mapping it to
    `unestablished` made it refusable, so a release could be stopped with the reason
    "no eligible mutation-pool files changed" — an incoherent blocker."""
    _blocking_consumer_stub(
        gate,
        monkeypatch,
        {
            "ok": True,
            "blocking": [],
            "reason": "no eligible mutation-pool files changed in this range",
        },
        returncode=0,
    )

    code = gate.main(["--repo-root", str(ROOT), "--base-sha", "b" * 40, "--refuse-unestablished"])

    assert code == 0
    assert yaml.safe_load(capsys.readouterr().out)["status"] == "clean"
