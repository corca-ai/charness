#!/usr/bin/env python3
"""Incremental, blocking changed-line coverage for the release-final lane (D40).

The quality runner invokes this producer once, after every other release check.
Direct invocation remains available for focused diagnostics.

The recurring class (#219 -> #251 -> #260 -> #320 -> #321 -> #335 -> #453 -> #464)
is not a missing gate and not a quiet warning. Both existed and both fired. The
old push/PR mirror and ordinary wiring added a multi-minute feedback cost without
being a reliable release proof. They are removed from routine lanes; the release
runner invokes this producer with its blocking refusal option.

The reason routine local enforcement was defused is real and stays respected: producing
coverage from the BROAD suite costs 11-15 minutes, and a gate that expensive gets
skipped, which is how it came to prove nothing. So this producer is INCREMENTAL.
It asks `suggest_mutation_coverage_command` which standing tests reference the
changed mutation-pool files, instruments only those, and blocks on their uncovered
changed lines. Measured on this repo with the gate's own coverage mechanism:

    realistic single-commit slice (9 pool files, 55 tests)     ~24s
    whole 9-commit session       (31 pool files, 1009 tests)   ~4min
    broad producer                                             11-15min

Direction of error is the point. Coverage collected from a SUBSET of the suite is
a subset of full coverage, so this can report a covered line as uncovered but can
never report an uncovered line as covered. It can cost a false stop; it cannot
grant a false pass. That is the opposite of the failure this class is made of.

Policy for files the suggester cannot map to a standing test (option (a), chosen
by the repo owner 2026-07-29): they are NOT blocked on and NOT silently dropped.
Blocking them would false-stop on a mapper gap rather than a coverage gap — the
mapper matches textual references, and it already misses at least one real case
(`seed_dup_review.py` is loaded by `test_dup_review_seed.py` through a dynamic
string, not an import). They are named loudly instead, and the consumer records
them as `unanalyzed_changed_pool_files` so no green here can be read as covering
them. Narrowing that gap belongs to the mapper, not to this policy.

Exit codes:
  0  nothing to analyze, or every mapped file's changed lines are covered
  1  a mapped changed pool file has uncovered changed lines (the blocker), or an
     UNESTABLISHED result under `--refuse-unestablished`
  2  the run produced NO verdict (base discovery failed, or the focused producer
     itself failed). Deliberately distinct from 1, and deliberately NOT 0: an
     unusable run is not a pass.
  3  UNESTABLISHED: the lane judged nothing about the files it was asked to judge
     (a dirty pool whose edits `base..HEAD` cannot see, or a limit that
     intersected to nothing). Non-blocking without `--refuse-unestablished`;
     refusable at the release boundary with that flag, which is what makes it
     distinct from 4.
  4  PARTIAL: some of the changed pool set was analyzed and some was not, and
     what WAS analyzed came back clean. `run-quality.sh` renders it FAIL for THIS
     label: rendering 3/4 as UNPROVEN is opt-in per label via
     `UNESTABLISHED_CAPABLE_LABELS`, and `release-changed-line-coverage` is
     deliberately not in that list, so an incomplete release-final analysis stops
     the lane rather than annotating it. It
     is NOT refusable by `--refuse-unestablished` -- policy (a) above is the
     owner's deliberate non-blocking choice, and the repair for the false green
     it produced was to stop calling it a PASS, not to stop a release on the
     mapper's blind spot. 3 was previously undocumented here; documenting it
     alongside 4 is the point, since the difference between them IS the refusal.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import sys
from pathlib import Path
from types import SimpleNamespace

import yaml


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts import changed_line_verdict_codes as _verdict_codes  # noqa: E402
from scripts import mutation_coverage_producer as _producer  # noqa: E402
from scripts import suggest_mutation_coverage_command as _suggest  # noqa: E402
from scripts.runtime_bootstrap import import_repo_module  # noqa: E402
from scripts.subprocess_guard import run_monitored_phase  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

NO_VERDICT_EXIT = _verdict_codes.REFUSED_EXIT
# The consumer's exit-0 reason for a range that contained no eligible pool file.
EMPTY_SCOPE_REASON_PREFIX = "no eligible mutation-pool files changed"
# What `check_changed_line_mutation_coverage.py` returns when it judged no scope.
# Non-blocking by design: mid-work it becomes this wrapper's own exit 3. Whether
# run-quality renders that UNPROVEN or FAIL is its per-label opt-in
# (`UNESTABLISHED_CAPABLE_LABELS`), which this label is not in; the release lane's
# `--refuse-unestablished` turns it into a 1 regardless.
CONSUMER_UNESTABLISHED_EXIT = _verdict_codes.UNESTABLISHED_EXIT
UNESTABLISHED_EXIT = _verdict_codes.UNESTABLISHED_EXIT
# What the consumer returns when it judged its analyzed set clean but could not
# analyze part of the changed set. Distinct from 3 because it is NOT refusable:
# policy (a) below keeps an unmapped changed pool file non-blocking, and the
# repair for that false green is to stop calling it a PASS, not to start
# stopping a release on the mapper's blind spot.
CONSUMER_PARTIAL_EXIT = _verdict_codes.PARTIAL_EXIT
# This lane's own byte for the same state. `run-quality.sh` renders it FAIL for
# this label, which is not in its `UNESTABLISHED_CAPABLE_LABELS` opt-in list.
PARTIAL_EXIT = _verdict_codes.PARTIAL_EXIT
CONSUMER = "scripts/check_changed_line_mutation_coverage.py"

#: The run judged nothing about the files it was asked to judge — a dirty pool whose
#: edits `base..HEAD` cannot see, or a limit that intersected to nothing. Kept DISTINCT
#: from `unproven` (policy (a): the mapper resolved no standing test) because only this
#: one is refusable: policy (a) is the owner's deliberate non-blocking choice, while
#: this one is the lane failing to do its job and must not read as a release pass.
UNESTABLISHED_STATUS = "unestablished"

#: The lane analyzed part of its changed set and says so IN THE VERDICT. Policy (a)
#: (below) is preserved -- this never refuses on a mapper blind spot -- but it stops
#: wearing exit 0.
#: The measured failure it removes: a local run printed "this run analyzed only 6 of
#: 7 changed mutation-pool file(s). A clean verdict says NOTHING about the rest",
#: returned the same byte as a run with no blind spot, and a release could have
#: carried an unproven result.
PARTIAL_STATUS = "partial"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--base-sha",
        default=None,
        help="Base SHA; defaults to the merge-base of origin/main and HEAD.",
    )
    parser.add_argument(
        "--coverage-json",
        type=Path,
        default=Path("reports/mutation/release-changed-line-coverage.json"),
        help=(
            "Where the focused producer writes coverage plus its "
            "`.changed-line.fingerprint` marker. "
            "The release-final report stays separate from the canonical broad mutation "
            "report because this lane's coverage comes from a test SUBSET."
        ),
    )
    parser.add_argument(
        "--refuse-unestablished",
        action="store_true",
        help=(
            "Exit non-zero when the run establishes NOTHING about the files it was asked "
            "to judge (a dirty mutation pool, or a limit that intersected to nothing). "
            "The release runner supplies this flag because an unestablished result is not "
            "a release proof. Without it, the same outcome stays non-blocking and merely "
            "loud. This flag does NOT govern policy (a): a file "
            "the mapper resolves to no standing test is non-blocking in every mode, by "
            "the repo owner's decision, because that is a mapper gap and not a coverage "
            "gap."
        ),
    )
    return parser.parse_args(argv)


def _warn(message: str) -> None:
    # The `WARNING` head is load-bearing: run-quality.sh's print_phase_output only
    # surfaces a PASSING gate's output when a line matches ^(WARNING|WARN|WEAK|ADVISORY).
    sys.stderr.write(f"WARNING (release changed-line coverage): {message}\n")


def _focused_pytest_command(recommendation: dict) -> str | None:
    """The suggester-owned command when coverage can instrument it.

    The suggester emits a `run_standing_pytest.py` invocation for operator use, and
    the producer can instrument that runner as a child process. Keeping the runner
    here makes the focused lane inherit its host-safe xdist, worker-cap, scheduler-
    compatibility, and external-temp policy instead of maintaining a second copy.
    Consuming the emitted command directly keeps the suggester as the one owner of
    both target selection and command assembly.

    The canonical runner's default `-m not release_only` is load-bearing here. The
    broad coverage producer uses the same marker policy, so the focused file list
    may narrow its test population but must not widen it with release-only cases.
    """
    command = recommendation.get("command")
    if not isinstance(command, str) or not command.strip():
        return None
    return command


def _dispose_consumer_verdict(payload: dict, result, args) -> int | None:
    """The exit code for a consumer result that is not an ordinary pass/block, or
    ``None`` when the caller should fall through to the normal path.

    One place decides what a consumer code MEANS, because the two readings that
    exist here are easy to conflate and were:

    - exit 3 is "ran, established nothing". Sending it to `no-verdict` reported it
      as refused-or-errored and returned 2, which made the diagnostic path fail
      before `--refuse-unestablished` could express its intended boundary behavior.
    - an unestablished result is non-blocking without the release flag but NOT exit 0.
      Returning 0 made `run-quality.sh` print PASS beside the warning below.
    """
    if result.returncode == CONSUMER_PARTIAL_EXIT:
        # Same readability guard as the unestablished branch below: `no-verdict`
        # means the payload could not be read, so the consumer's exit code stands
        # for nothing and must not be rewritten into a bounded status.
        #
        # `UNESTABLISHED_STATUS` is guarded for a sharper reason: it is the only
        # REFUSABLE status here, and `partial` is deliberately not. Overwriting it
        # would let a partial scope launder a dirty-pool result past
        # `--refuse-unestablished` -- a push this lane used to stop, waved through
        # by a repair that was never about the dirty-pool cause. Belt to the
        # consumer's braces: the consumer now returns 3 (not 4) when both hold, so
        # this branch should not see that combination at all; a defence at both
        # ends is cheap, and the seam between them is where the first cut broke.
        if payload["status"] not in ("no-verdict", UNESTABLISHED_STATUS):
            payload["status"] = PARTIAL_STATUS
            payload.setdefault(
                "reason",
                "the consumer analyzed only part of the changed mutation-pool set",
            )
    elif result.returncode == CONSUMER_UNESTABLISHED_EXIT:
        # Only when the payload was READABLE. `no-verdict` means the consumer's stdout
        # could not be read, so its exit code stands for nothing -- including this one.
        # Rewriting that to `unestablished` reported an unreadable result as a bounded,
        # non-blocking "ran, established nothing": the same exit-code-stands-for-nothing
        # equivalence this lane exists to break, one layer in.
        if payload["status"] != "no-verdict":
            payload["status"] = UNESTABLISHED_STATUS
    elif result.returncode not in (0, 1):
        payload["status"] = "no-verdict"
        payload["reason"] = f"the consumer refused or errored (exit {result.returncode})"
        _warn(f"the changed-line consumer exited {result.returncode}; this is NOT a pass.")
        emit_yaml(payload)
        return NO_VERDICT_EXIT
    if payload["status"] == PARTIAL_STATUS:
        # Loud for the same reason the unestablished warning is: in a summary that
        # prints only a label and a status, a quiet partial is a pass.
        _warn(
            "this run analyzed only PART of the changed mutation-pool set; a clean "
            f"verdict says nothing about the rest: {payload['reason']}"
        )
        _emit_consumer_stdout(payload, result)
        emit_yaml(payload)
        # NOT gated on `--refuse-unestablished`: policy (a) is preserved on purpose.
        return PARTIAL_EXIT
    if payload["status"] in (UNESTABLISHED_STATUS, "no-verdict"):
        # Has to be LOUD or it is indistinguishable from a pass in a summary that
        # prints only the label and its status.
        _warn(f"this run established no changed-line verdict: {payload['reason']}")
    if payload["status"] == "no-verdict":
        emit_yaml(payload)
        return NO_VERDICT_EXIT
    if payload["status"] == UNESTABLISHED_STATUS:
        if args.refuse_unestablished:
            # The predecessor lane was walked past because its worst outcome was exit
            # 0 plus prose. Repeating that here would rebuild the defect this lane
            # exists to fix.
            _warn("refusing release: an unestablished changed-line result is not a pass.")
            # The consumer payload names WHICH files went unestablished. Withholding
            # it on the one path that stops a push -- while emitting it on the path
            # that does not -- is a gate whose refusal cannot be diagnosed.
            _emit_consumer_stdout(payload, result)
            emit_yaml(payload)
            return 1
        _emit_consumer_stdout(payload, result)
        emit_yaml(payload)
        return UNESTABLISHED_EXIT
    return None


def _emit_consumer_stdout(payload: dict, result) -> None:
    """Carry the consumer's own payload INSIDE this lane's document.

    It used to be written raw to stdout whenever the caller had not asked for
    JSON. Output here is now one YAML document, and interleaving the child's bytes
    with it would produce a stream no reader can parse -- while dropping them would
    delete the only text naming WHICH files went unestablished, on the paths that
    refuse a push.
    """
    payload["consumer_stdout"] = result.stdout


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    base_sha = args.base_sha or _producer.default_mutation_base_sha(repo_root)
    if not base_sha:
        _warn(
            "no base SHA (no origin/main merge-base): there is no range to analyze, so "
            "this run rendered no changed-line verdict. It is NOT a pass."
        )
        emit_yaml({"status": "no-verdict", "reason": "base discovery failed", "base_sha": None})
        return NO_VERDICT_EXIT

    recommendation = _suggest.build_recommendation(repo_root, base_sha=base_sha)
    status = recommendation.get("status")
    mapped = sorted((recommendation.get("mapped_tests_by_file") or {}).keys())
    unmapped = sorted(recommendation.get("unmapped_changed_pool_files") or [])

    if status == "noop":
        emit_yaml(
            {
                "status": "noop",
                "reason": "no eligible mutation-pool files changed",
                "base_sha": base_sha,
            }
        )
        return 0

    if status == "blocked":
        _warn(
            "the suggester could not resolve a base; no changed-line verdict was "
            "rendered. This is NOT a pass."
        )
        emit_yaml({"status": "no-verdict", "reason": "suggester blocked", "base_sha": base_sha})
        return NO_VERDICT_EXIT

    if status == "missing" or not mapped:
        # Every changed pool file is unmapped. Option (a): warn, do not block. A stop
        # here would be a stop on the mapper's blind spot, not on a coverage gap.
        _warn(
            f"{len(unmapped)} changed mutation-pool file(s) map to NO standing test, so "
            "nothing could be proven for this release. Add or identify a standing test "
            "reference the mapper can discover, then rerun the release lane; otherwise run the broad "
            f"producer. Unproven: {', '.join(unmapped)}"
        )
        emit_yaml(
            {
                "status": "unproven",
                "reason": "no changed pool file maps to a standing test",
                "base_sha": base_sha,
                "unmapped_changed_pool_files": unmapped,
            }
        )
        # Option (a) keeps this NON-BLOCKING -- and non-blocking is not the same
        # byte as proven-clean. Returning 0 here made `run-quality.sh` print PASS
        # beside the warning three lines up, which is the whole finding: a lane that
        # analyzed nothing wore the verdict of a lane that analyzed everything.
        return PARTIAL_EXIT

    command = _focused_pytest_command(recommendation)
    coverage_json = (
        args.coverage_json if args.coverage_json.is_absolute() else repo_root / args.coverage_json
    )
    try:
        producer_result = _producer.produce_command_coverage(
            repo_root,
            command,
            base_sha=base_sha,
            coverage_json=coverage_json,
            run_command=_run_command,
            phase="verify",
            # The focused test run stays unchanged. The consumer only needs
            # coverage for mapped changed files, so exporting the whole source
            # tree is avoidable serialization work on this lane.
            include_paths=mapped,
        )
    except RuntimeError as exc:
        # A producer that DIED proved nothing. Reporting 0 here would reinstate the
        # exact silence this gate replaces.
        exit_code = getattr(exc, "returncode", 1)
        _warn(
            f"the focused coverage producer failed (exit {exit_code}); no "
            "changed-line verdict was rendered. This is NOT a pass."
        )
        emit_yaml(
            {"status": "no-verdict", "reason": "focused producer failed", "base_sha": base_sha}
        )
        return NO_VERDICT_EXIT

    if producer_result.get("returncode") != 0 or not producer_result.get(
        "produced_mutation_coverage"
    ):
        _warn(
            "the focused coverage producer did not confirm a completed coverage export; "
            "no changed-line verdict was rendered. This is NOT a pass."
        )
        emit_yaml(
            {
                "status": "no-verdict",
                "reason": "focused coverage was not produced",
                "base_sha": base_sha,
            }
        )
        return NO_VERDICT_EXIT

    if not coverage_json.is_file():
        # The consumer runs with `--reuse-coverage`; if the file is missing it silently
        # falls through to the BROAD probe, turning a "~24s" lane into an 11-15 minute
        # stall with no explanation. Refuse instead of stalling.
        _warn(
            f"the focused producer reported success but wrote no coverage at {coverage_json}; "
            "no changed-line verdict was rendered. This is NOT a pass."
        )
        emit_yaml(
            {
                "status": "no-verdict",
                "reason": "focused coverage missing after produce",
                "base_sha": base_sha,
            }
        )
        return NO_VERDICT_EXIT

    if unmapped:
        _warn(
            f"{len(unmapped)} changed mutation-pool file(s) map to no standing test and "
            "were NOT analyzed by this run; a clean result below says nothing about "
            f"them: {', '.join(unmapped)}"
        )

    consumer_argv = [
        sys.executable,
        str(repo_root / CONSUMER),
        "--repo-root",
        str(repo_root),
        "--base-sha",
        base_sha,
        "--head-sha",
        "HEAD",
        "--coverage-json",
        str(coverage_json),
        "--reuse-coverage",
        "--require-fresh-coverage",
        "--allow-dirty",
    ]
    for path in mapped:
        consumer_argv += ["--limit-to-file", path]
    consumer = import_repo_module(__file__, "scripts.check_changed_line_mutation_coverage")
    consumer_stdout = io.StringIO()
    consumer_stderr = io.StringIO()
    previous_argv = sys.argv
    try:
        sys.argv = consumer_argv[1:]
        with (
            contextlib.redirect_stdout(consumer_stdout),
            contextlib.redirect_stderr(consumer_stderr),
        ):
            try:
                consumer_returncode = int(consumer.main())
            except SystemExit as exc:
                consumer_returncode = int(exc.code or 0)
    finally:
        sys.argv = previous_argv
    result = SimpleNamespace(
        args=consumer_argv,
        returncode=consumer_returncode,
        stdout=consumer_stdout.getvalue(),
        stderr=consumer_stderr.getvalue(),
    )
    sys.stderr.write(result.stderr)
    status, reason = _verdict_from_consumer(result)
    payload = {
        "status": status,
        "reason": reason,
        "base_sha": base_sha,
        "analyzed_changed_pool_files": mapped,
        "unmapped_changed_pool_files": unmapped,
        "consumer_returncode": result.returncode,
    }
    verdict_code = _dispose_consumer_verdict(payload, result, args)
    if verdict_code is not None:
        return verdict_code
    _emit_consumer_stdout(payload, result)
    emit_yaml(payload)
    return result.returncode


def _verdict_from_consumer(result) -> tuple[str, str]:  # noqa: ANN001
    """Read the consumer's PAYLOAD, not just its exit code.

    The consumer reaches exit 0 on three materially different outcomes, and only one
    of them is a pass:

    * every analyzed changed line is covered — a real verdict;
    * the `--limit-to-file` intersection emptied the analyzed set, so the run "analyzed
      nothing and proves nothing" — its own words;
    * `--allow-dirty` let it judge a tree whose uncommitted pool changes `base..HEAD`
      cannot see, recorded as `dirty_pool_unverified`.

    Deriving status from the return code alone renders all three as `clean`. That is
    the same equivalence — exit 0 means proven — that this whole lane exists to break,
    reintroduced at the surface that reports the lane's own verdict. The dirty case is
    worse than a bare mislabel: the focused coverage is produced by running pytest
    against the LIVE worktree while the changed-line mapping is computed against HEAD,
    so line numbers can skew between the two trees and an executed worktree line can be
    attributed to a different HEAD statement. That is a false PASS, and it is outside
    the "focused coverage is a subset of full coverage" safety argument, which covers
    test-subsetting only. So a dirty pool is reported `unproven`, never `clean`.
    """
    if result.returncode == 1:
        return "blocked", "a mapped changed pool file has uncovered changed lines"
    try:
        report = yaml.safe_load(result.stdout)
    except (TypeError, ValueError, yaml.YAMLError):
        report = None
    if not isinstance(report, dict):
        # `safe_load` returns None for empty input and a bare str for arbitrary
        # prose instead of raising, so the TYPE check -- not the exception alone --
        # is what keeps an unreadable consumer out of a verdict. Without it, this
        # lane would call `.get` on a string and crash on exactly the input the
        # `no-verdict` branch exists to describe.
        return (
            "no-verdict",
            "the consumer emitted no readable payload, so its exit code stands for nothing",
        )
    if report.get("dirty_pool_unverified"):
        return (
            UNESTABLISHED_STATUS,
            "mutation-pool files have uncommitted changes that base..HEAD cannot see; "
            "the focused coverage was collected from a different tree than the one "
            "analyzed, so this run proves nothing about them",
        )
    reason = str(report.get("reason") or "")
    if reason.startswith(EMPTY_SCOPE_REASON_PREFIX):
        # An empty changed set is nothing to prove, not something left unproven.
        # Mapping it to `unestablished` made it refusable, so a push could be
        # stopped with the reason "no eligible mutation-pool files changed" -- an
        # incoherent blocker on the gate whose credibility is the point.
        return "clean", reason
    if reason:
        return UNESTABLISHED_STATUS, reason
    return "clean", "every mapped changed pool file's changed lines are covered"


def _run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
    outcome = run_monitored_phase(
        command,
        cwd=repo_root,
        phase=phase,
        timeout_seconds=None,
        shell=True,
        capture=True,
    )
    if outcome.returncode != 0:
        # pytest reports failures on STDOUT. Surfacing only stderr here left the
        # operator with "the producer failed (exit 1)" and no way to see which test
        # failed — a gate whose failure cannot be diagnosed is a gate that gets
        # disabled, which is the whole history this lane is repairing.
        sys.stderr.write(outcome.stdout[-6000:])
    sys.stderr.write(outcome.stderr[-4000:])
    if outcome.returncode != 0:
        error = RuntimeError(f"coverage producer command failed with exit {outcome.returncode}")
        error.returncode = outcome.returncode  # type: ignore[attr-defined]
        error.output = outcome.stdout  # type: ignore[attr-defined]
        error.stderr = outcome.stderr  # type: ignore[attr-defined]
        raise error
    return {
        "command": command,
        "returncode": outcome.returncode,
        "stdout": outcome.stdout,
        "stderr": outcome.stderr,
        "phase": phase,
    }


if __name__ == "__main__":
    raise SystemExit(main())
