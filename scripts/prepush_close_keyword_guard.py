#!/usr/bin/env python3
"""Blocking pre-push floor over the close keywords a push RANGE would fire.

The commit-msg carrier (``check_issue_closeout_commit_msg.py``) already refuses a
commit whose message close-keywords an issue with no closeout floor. It did not
stop the accidental close of #626, and the reason is why this second surface
exists rather than being one more branch in the first one.

What happened: a commit body contained the sentence

    ... before S7 rather than after because S7 closes
    #626/#627/#631 on the strength of that gate.

Prose describing a FUTURE release. The line carrying the refs begins with ``#``,
and the commit-msg carrier strips ``^\\s*#`` lines as git comments before scanning
-- correct for an editor-authored message under ``--cleanup=default``, wrong for
the ``-m``/``-F`` message that was actually committed, where git strips nothing.
So the carrier scanned a body the repository never stored, found no close keyword,
and reported ``not_applicable`` while GitHub read the STORED message and closed
#626. (Only #626 was CLOSED: the ``/`` separator is not GitHub's comma grammar, so
the scanner and GitHub both stop after the first ref. GitHub still cross-REFERENCES
every ``#N`` it sees; the claim here is about closing, not about linking.) That
divergence is repaired in the carrier too, but a floor that models what git will
store is a floor that can be wrong again.

This guard has no such model. It reads the stored message with
``git show -s --format=%B`` -- byte for byte what GitHub's parser will read -- for
every commit the push would land. That also covers the escapes the commit-msg hook
structurally cannot see, none of which are exotic: ``--no-verify``, a commit
authored before the hook was installed, a rebase or amend that rewrote a body
after its hook ran, a cherry-pick, and a merge of a branch whose commits never
passed through this repo's hooks.

It applies the carrier's floor by CALLING the carrier's own parts -- the same
staged-artifact parse (over the commit's tree instead of the index), the same
classification derivation, the same protected-target authorization, and the same
``verify_closeout``. Re-deriving any of them here produced a measured defect in
review: classification from the message alone defaults to ``bug``, so an
artifact-carried ``question`` close was refused with a demand for root-cause and
prevention claims that the disposition exists to refuse.

DETECTION was once WIDER than the carrier's, and is now the same grammar reached
twice. ``close_targets`` adds the ``GH-123`` and full-issue-URL spellings GitHub
also closes on; the canonical ``iter_close_keyword_refs`` did not match them, which
left every OTHER consumer of that function blind to a close it would fire. The
canonical scanner has since been widened to the same three spellings, so the gap
this paragraph used to disclaim is closed at the source. The local copy is kept
deliberately as REDUNDANCY rather than as the sole detector: ``close_targets``
unions both, so a future narrowing of the shared scanner cannot silently narrow the
one surface whose job is to model GitHub rather than this repo's convention.

Calibration, and what it does and does not establish. Command:
``python3 scripts/prepush_close_keyword_guard.py --repo-root . --range <sha>~1..<sha>``
run once per commit over ``git log -400 origin/main``, re-measured 2026-08-16 after
both review rounds: 20 commits carry a close-keyword ref, 19 pass and the single
refusal is 7817ace88, the commit that closed #626. That population is SELECTED for
having passed the commit-msg floor already, and every one was judged against that
day's worktree. It supports "zero false refusals on 400 historical main commits,
measured twice". It does not establish a false-refusal rate, and specifically does
not cover the channels review found: an artifact-only classification and an
artifact-only commit (both repaired and pinned by test), or a commit whose cited
critique/debug evidence has since moved (not repaired, disclaimed below).

Not claimed:
  - It floors ONE carrier. A close fired from a PR body, the API, or a manual
    click is outside it.
  - It judges every pushed ref, while GitHub auto-closes only on the DEFAULT
    branch. A topic-branch push carrying an unfloored keyword is refused even
    though nothing would have closed. That direction is deliberate -- the branch
    is usually merged later -- but it is over-fire, not precision.
  - It applies TODAY's floor to whatever commits are in the range, including old
    ones. A merge that brings in a commit whose cited evidence file has since
    been renamed is refused over a path, not over a close.
  - It is not offline-safe for one classification: ``consolidated`` drives a
    ``gh`` readback inside ``verify_closeout``. That reach is the shared floor's,
    not this file's, and is unchanged by moving it to push time.
  - A ref CREATION to a remote with no local tracking refs cannot be bounded, so
    it is CAPPED at ``MAX_UNBOUNDED_CREATION_SCAN`` commits and the cap is reported
    in ``coverage_notes`` (only because ``evaluate`` passes the list ``range_commits``
    needs -- see that function's own non-claim). Commits past it are not judged.
    That is a stated gap, not coverage.

Exit codes:
  0  every commit the guard READ is clean: no close-keyword refs, or every one
     clears the closeout floor. NOT a claim that the whole push was read. Three
     exit-0 shapes judge less than the push, and only the first is visible in the
     payload: the unbounded-creation CAP names its truncation in ``coverage_notes``;
     a STALE remote-tracking ref silently excludes commits the target remote has
     never seen (the scan module's own non-claim, reported nowhere); and
     ``status: no-refs`` means no ref lines arrived at all, which this cannot tell
     apart from a wrapper that drained the hook's stdin before calling it. An empty
     ``coverage_notes`` is therefore not a statement that the whole push was judged.
  1  a commit in the range close-keywords an issue with no valid closeout carrier
  2  the range could not be read, the pre-push stdin carried a line git could not
     have written, the run was handed no push at all on a terminal, or the guard
     crashed -- so it judged nothing. Deliberately distinct from 1: an unusable run
     must never be readable as either a pass or a verdict.

Why a truncated or stale range is exit 0 while a malformed stdin line is exit 2, when
all three leave part of a push unjudged: refusing the first two would refuse every URL
push of a long branch and every push from an unpruned clone, which is how a push-time
gate gets uninstalled -- and both are properties of the range this guard inherits from
every other consumer of ``origin/main`` here. A dropped stdin line is different in kind:
it names a ref nothing can recover, so there is not even a statement to make about what
went unjudged. That asymmetry is a DECISION, not a property, and the three exit-0 holes
above are disclosed rather than closed.
"""
from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.prepush_close_keyword_scan import (
        MAX_UNBOUNDED_CREATION_SCAN,
        RangeUnreadable,
        close_targets,
        commit_body,
        commit_file,
        commit_paths,
        local_numbers,
        parse_push_stdin,
        range_commits,
    )
    from scripts.runtime_bootstrap import load_path_module
    from scripts.yaml_output import emit_yaml
except ModuleNotFoundError:  # git-hook execution: `scripts/` is sys.path[0], not a package
    from prepush_close_keyword_scan import (
        MAX_UNBOUNDED_CREATION_SCAN,
        RangeUnreadable,
        close_targets,
        commit_body,
        commit_file,
        commit_paths,
        local_numbers,
        parse_push_stdin,
        range_commits,
    )

    from runtime_bootstrap import load_path_module
    from yaml_output import emit_yaml

NO_VERDICT_EXIT = 2
#: Why a dropped pre-push stdin line is a no-verdict rather than a scan of what parsed.
#: One string, used by the exported ``evaluate`` and printed by the CLI, so the library
#: caller and the hook operator are told the same thing.
STDIN_DROP_REASON = (
    "{dropped} pre-push stdin line(s) were not the "
    "`<local-ref> <local-sha> <remote-ref> <remote-sha>` grammar git emits, so the refs "
    "they named could not be read and the commits they would land were not judged. "
    "Re-check the intended range explicitly: `python3 scripts/prepush_close_keyword_guard.py "
    "--repo-root . --range <base>..<head>`."
)
# Re-exported so the CLI's `--range` help and the hook read one name. `MAX_...` is
# imported for the docstring's cap claim to resolve to a real value here.
__all__ = ["MAX_UNBOUNDED_CREATION_SCAN", "evaluate", "main", "report_payload"]


def no_verdict_payload(reason: str, *, dropped: int = 0) -> dict[str, Any]:
    """ONE shape for every no-verdict, so a consumer reading one reads them all.

    Three conditions produce a no-verdict -- a dropped stdin line, an unreadable range,
    and a run handed no push on a terminal -- and they used to emit three different key
    sets. A log parser reading ``commits_scanned`` off the documented shape then raised
    ``KeyError`` on the other two, which is a crash where the payload's whole purpose is
    to be legible when the guard could not judge.
    """
    return {
        "ok": False,
        "status": "no-verdict",
        "reason": reason,
        "commits_scanned": 0,
        "dropped_stdin_lines": dropped,
        "coverage_notes": [],
        "close_keyword_commits": [],
    }


def _load_sibling(module_name: str):
    """Load a sibling script BY PATH, because this runs as a git hook from an
    arbitrary working directory where ``scripts`` is not an importable package."""
    return load_path_module(module_name, Path(__file__).resolve().with_name(f"{module_name}.py"))


def evaluate(repo_root: Path, push_refs: list[dict[str, str]], repo: str, remote: str) -> dict[str, Any]:
    """Apply the carrier's floor to every close-keyword commit in the range.

    Fail-closed on a dropped stdin line HERE, not only in ``main``. This function is
    exported (``__all__``) and ships to consuming repos, so a consumer hook shim that
    calls it directly and branches on ``ok`` is a real caller -- and leaving the
    decision in ``main`` would hand that shim the exact false green this floor exists
    to stop: ``ok: true`` over a push whose refs were never read.
    """
    dropped = max((int(ref.get("dropped_lines") or 0) for ref in push_refs), default=0)
    if dropped:
        return no_verdict_payload(STDIN_DROP_REASON.format(dropped=dropped), dropped=dropped)

    checker = _load_sibling("check_issue_closeout_commit_msg")
    issue_verify_closeout = checker._load_issue_verify_closeout()

    seen: set[str] = set()
    findings: list[dict[str, Any]] = []
    notes: list[str] = []
    for push_ref in push_refs:
        if not push_ref["local_sha"]:
            continue
        for sha in range_commits(
            repo_root, push_ref["local_sha"], push_ref["remote_sha"], remote, notes
        ):
            if sha in seen:
                continue
            seen.add(sha)
            finding = _judge(repo_root, repo, sha, checker, issue_verify_closeout)
            if finding is not None:
                findings.append(finding)

    refused = [finding for finding in findings if not finding["ok"]]
    return {
        "ok": not refused,
        "status": "refused" if refused else ("verified" if findings else "not_applicable"),
        "commits_scanned": len(seen),
        # Always 0 here: a nonzero count returned the no-verdict payload above. Kept so
        # both payloads carry the field and a consumer reading one shape reads both.
        "dropped_stdin_lines": dropped,
        "coverage_notes": notes,
        "close_keyword_commits": findings,
    }


def _judge(
    repo_root: Path,
    repo: str,
    sha: str,
    checker: Any,
    issue_verify_closeout: Any,
    *,
    body: str | None = None,
    list_paths: Any = None,
    read_file: Any = None,
) -> dict[str, Any] | None:
    """One commit, through the carrier's own decision sequence.

    Follows ``check_issue_closeout_commit_msg.evaluate`` -- artifacts, pause carve-out,
    covered numbers, bare numbers, authorization, then one ``verify_closeout`` per
    carrier -- with the commit's TREE standing in for the index. ONE deliberate
    difference now, stated rather than mirrored: a close KEYWORD is required (see
    below), so the artifact-only trigger the carrier has does not exist here.
    ``close_targets`` used to be the second difference and is not any more -- the
    canonical scanner was widened to the same three spellings, so the union it takes
    is a no-op for every input and is kept only so a future narrowing there cannot
    silently narrow this surface. A consequence of the second is that ``_pause_briefs`` is
    always empty: an artifact only reaches the partition when the message
    close-keywords one of its numbers, which is exactly the overlap that ends the
    pause exemption. It is returned and named rather than dropped silently.
    """
    body = commit_body(repo_root, sha) if body is None else body
    qualified = close_targets(body, issue_verify_closeout.iter_close_keyword_refs)
    # A CLOSE KEYWORD is the trigger, not a touched artifact. The commit-msg carrier
    # keys on the staged artifact too, because staging one is an intent to close; a
    # commit that merely EDITS an old `charness-artifacts/issue/*.md` closes nothing,
    # and refusing it would have emitted "this commit close-keywords a GitHub issue"
    # over a message with no keyword in it, remediated by rewording a verb that is
    # not there.
    if not qualified:
        return None
    message_refs = {number for _repo, number in qualified}
    closable = local_numbers(qualified, repo)
    artifacts = [
        artifact
        for artifact in checker._issue_closeout_artifacts(
            repo_root,
            issue_verify_closeout.iter_close_keyword_refs,
            issue_verify_closeout.strip_code_fences,
            list_paths=list_paths
            or (lambda root, _sha=sha: commit_paths(root, _sha)),
            read_file=read_file
            or (lambda root, path, _sha=sha: commit_file(root, _sha, path)),
        )
        if set(artifact["numbers"]) & closable
    ]
    # The carrier's own partition, called rather than copied: the pause carve-out and
    # the covered-number subtraction decide WHICH floor each target gets, and two
    # copies of that answer would drift with nothing red. `message_refs` is the
    # UNFILTERED mention set the pause overlap is tested against, matching the
    # carrier; `closable` is the repo-filtered set the bare floor applies to.
    artifacts, _pause_briefs, bare_numbers = checker.partition_closeout_carriers(
        artifacts, message_refs, closable
    )

    subject = body.splitlines()[0] if body.strip() else ""
    # Protected-target authorization, the carrier's hard refusal at
    # `check_issue_closeout_commit_msg.py`. Omitting it here was found in review: a
    # commit close-keywording a crosswalk-protected issue WITH a complete ledger, made
    # under `--no-verify`, passed the guard and would have closed on push.
    authorization = checker._AUTHZ.authorize_commit_carrier(
        repo_root, set(qualified), artifacts, bare_numbers
    )
    for artifact in artifacts:
        artifact.pop("qualified_numbers", None)
        artifact.pop("body", None)
    if not authorization["authorized"]:
        return {
            "commit": sha,
            "subject": subject,
            "numbers": sorted(message_refs),
            "ok": False,
            "refused_by": "closeout_authorization",
            "closeout_authorization": authorization,
            "reports": [],
        }

    reports = _reports(
        repo_root, repo, body, artifacts, bare_numbers, checker, issue_verify_closeout
    )
    return {
        "commit": sha,
        "subject": subject,
        "numbers": sorted(message_refs),
        "ok": all(report["ok"] for report in reports),
        "refused_by": None if all(report["ok"] for report in reports) else "closeout_floor",
        "closeout_authorization": authorization,
        "reports": reports,
    }


def _reports(
    repo_root: Path,
    repo: str,
    body: str,
    artifacts: list[dict[str, Any]],
    bare_numbers: list[int],
    checker: Any,
    issue_verify_closeout: Any,
) -> list[dict[str, Any]]:
    """One ``verify_closeout`` per carrier, artifact-derived ones first.

    The commit MESSAGE is the ledger body in both cases -- an artifact contributes its
    numbers and its declared classification, exactly as on the commit-msg path.
    """
    carriers = [
        (artifact["numbers"], artifact["classification"], artifact["path"]) for artifact in artifacts
    ]
    if bare_numbers:
        carriers.append(
            (bare_numbers, checker._bare_classification(body, issue_verify_closeout.strip_code_fences), None)
        )

    reports: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        body_file = Path(tmp) / "carrier-body.md"
        body_file.write_text(body, encoding="utf-8")
        for numbers, classification, source in carriers:
            report = issue_verify_closeout.verify_closeout(
                repo_root=repo_root,
                repo=repo,
                numbers=numbers,
                classification=classification,
                carrier="pr-body",
                backend={"id": "gh"},
                body_file=body_file,
            )
            reports.append(
                {
                    "numbers": numbers,
                    "classification": classification,
                    "source_artifact": source,
                    "ok": bool(report.get("ok")),
                    "missing_fields": report.get("missing_fields") or [],
                    "missing_close_keywords": report.get("missing_close_keywords") or [],
                }
            )
    return reports


_REFUSAL_SUMMARY = (
    "a commit in this push range close-keywords a GitHub issue without a valid closeout "
    "carrier. Pushing it to the default branch CLOSES that issue, and a close is not "
    "undoable by pushing again."
)
_REFUSAL_REMEDIATION = (
    "Read the offending message first: `git show -s --format=%B <commit>`.\n"
    "If the close is NOT intended -- the keyword is prose describing past or future "
    "work, or it sits inside a quoted log -- reword so no `close/fix/resolve` verb "
    "sits immediately before a `#N`, a `GH-N`, or an issue URL. `git rebase -i "
    "<commit>~1` with `reword` is enough, and rephrasing to `S7's closing set covers "
    "#626` breaks the grammar without losing the sentence. This is the ONLY exit when "
    "`missing_close_keywords` names a number the message mentions only inside a CODE "
    "FENCE: GitHub reads fenced text and closes on it, the ledger parse strips fences "
    "and cannot see it, so no ledger you add will clear that refusal.\n"
    "If the close IS intended: give the commit message the closeout ledger the report's "
    "`missing_fields` names, or stage the closeout artifact that declares the "
    "classification, then amend or rebase so the LANDED message carries it. Re-check "
    "without paying for the full lane: `python3 scripts/prepush_close_keyword_guard.py "
    "--repo-root . --range <base>..<head>`.\n"
    "Do NOT reach for `--no-verify`: that revokes the push grant outright."
)


def report_payload(result: dict[str, Any]) -> dict[str, Any]:
    """Attach the refusal text to a REFUSAL, keyed on the status rather than on ``ok``.

    ``ok: False`` has meant two things since ``evaluate`` learned to fail closed on a
    dropped stdin line, and this function is exported beside it. Keyed on ``not ok``,
    a consumer shim printing ``report_payload(evaluate(...))`` told an operator that a
    commit close-keywords an issue without a carrier, and to rebase and reword it --
    a remedy for a commit that does not exist, over a run that judged nothing.
    """
    payload = dict(result)
    if result["status"] == "refused":
        payload["summary"] = _REFUSAL_SUMMARY
        payload["remediation"] = _REFUSAL_REMEDIATION
    return payload


def _push_refs_from_args(
    args: argparse.Namespace,
) -> tuple[list[dict[str, str]] | None, str]:
    """``(refs, "")`` or ``(None, reason)``. The reason is carried, not printed here,
    so every no-verdict leaves the same payload shape through one exit in ``main``."""
    if not args.ranges:
        if sys.stdin.isatty():
            # No `--range` and no piped stdin: this invocation was handed NO push to
            # judge. Substituting an empty read here used to produce `status: no-refs`
            # and exit 0, which is a manufactured pass -- a maintainer running the guard
            # bare in a terminal reads "ok: true" as "the range is clean". git's hook
            # always pipes, so nothing legitimate reaches this branch.
            return None, (
                "no push range. Pipe git's pre-push stdin, or pass "
                "`--range <base>..<head>`; a bare interactive run judges nothing and "
                "will not report a pass."
            )
        return parse_push_stdin(sys.stdin.read()), ""
    push_refs = []
    for spec in args.ranges:
        remote_sha, _, local_sha = spec.partition("..")
        if not remote_sha or not local_sha:
            return None, f"unparseable --range {spec!r}"
        push_refs.append(
            {"local_ref": "", "local_sha": local_sha, "remote_ref": "", "remote_sha": remote_sha}
        )
    return push_refs, ""


def _emit_no_verdict(reason: str) -> int:
    print(f"charness pre-push close-keyword guard: {reason}", file=sys.stderr)
    emit_yaml(no_verdict_payload(reason))
    return NO_VERDICT_EXIT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--repo", default="corca-ai/charness")
    parser.add_argument(
        "--remote",
        default="origin",
        help=(
            "The remote being pushed to, which git passes to a pre-push hook as its "
            "first argument. Only used to bound a ref CREATION to the commits that "
            "remote has not seen; `origin` is a default, not an assumption."
        ),
    )
    parser.add_argument(
        "--range",
        dest="ranges",
        action="append",
        default=[],
        metavar="REMOTE_SHA..LOCAL_SHA",
        help=(
            "Check an explicit range instead of reading git's pre-push stdin. Repeatable. "
            "This is how the guard is re-run after a reword without paying for the full "
            "push lane, and how the #626 close was reconstructed."
        ),
    )
    args = parser.parse_args(argv)
    repo_root = args.repo_root.resolve()

    push_refs, refusal = _push_refs_from_args(args)
    if push_refs is None:
        return _emit_no_verdict(refusal)
    if not push_refs:
        # Exit 0, and said out loud. NO ref lines arrived, which this cannot tell apart
        # from a wrapper that read the hook's stdin before calling the guard and handed
        # over a drained pipe -- the hazard `.githooks/pre-push` works around by reading
        # once and replaying. Refusing here would refuse every genuinely empty push, so
        # the ambiguity is disclosed on stderr rather than resolved by guessing.
        print(
            "charness pre-push close-keyword guard: no ref lines on stdin. Nothing was "
            "judged. If a wrapper read this hook's stdin first, the guard saw a drained "
            "pipe rather than an empty push -- read stdin ONCE and replay it.",
            file=sys.stderr,
        )
        emit_yaml({"ok": True, "status": "no-refs", "commits_scanned": 0, "close_keyword_commits": []})
        return 0

    try:
        result = evaluate(repo_root, push_refs, args.repo, args.remote)
    except RangeUnreadable as exc:
        return _emit_no_verdict(str(exc))

    # `evaluate` owns the fail-closed decision so a consumer calling it directly gets
    # it too; this maps its one no-verdict status onto the documented exit code rather
    # than re-deriving the condition, which would let the two answers drift.
    if result["status"] == "no-verdict":
        print(f"charness pre-push close-keyword guard: {result['reason']}", file=sys.stderr)
        emit_yaml(result)
        return NO_VERDICT_EXIT

    emit_yaml(report_payload(result))
    return 0 if result["ok"] else 1


def cli(argv: list[str] | None = None) -> int:
    """``main`` with the crash-to-exit-2 mapping the hook needs.

    A function rather than the body of the ``__main__`` guard so it can be executed
    in-process by a test. Left inline, the mapping's own lines were unreachable from
    every in-process run and only a subprocess could touch them -- which is how a
    blocking hook's last-resort branch ends up unproven.
    """
    try:
        return main(argv)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 -- a blocking hook must not report a crash as a verdict
        # Exit 2, not the bare 1 an uncaught traceback would give: 1 is this guard's
        # documented REFUSAL code, so a crash exiting 1 would be read as "a commit
        # close-keywords an issue with no carrier" and answered by rewording an
        # innocent message.
        print(f"charness pre-push close-keyword guard crashed: {exc!r}", file=sys.stderr)
        return NO_VERDICT_EXIT


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint, `cli()` is tested
    raise SystemExit(cli())
