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

DETECTION is deliberately WIDER than the carrier's. ``close_targets`` adds the
``GH-123`` and full-issue-URL spellings GitHub also closes on and the canonical
``iter_close_keyword_refs`` does not match. Widening the shared scanner would
change every surface that consumes it; widening here errs toward refusal on the
one surface whose job is to model GitHub rather than to model this repo's
convention. The shared-scanner gap is real and is NOT fixed by this file.

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
    it is CAPPED at ``MAX_UNBOUNDED_CREATION_SCAN`` commits and the cap is
    reported. Commits past it are not judged. That is a stated gap, not coverage.

Exit codes:
  0  no close-keyword refs in the range, or every one clears the closeout floor
  1  a commit in the range close-keywords an issue with no valid closeout carrier
  2  the range could not be read, or the guard crashed, so it judged nothing.
     Deliberately distinct from 1: an unusable run must never be readable as
     either a pass or a verdict.
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
# Re-exported so the CLI's `--range` help and the hook read one name. `MAX_...` is
# imported for the docstring's cap claim to resolve to a real value here.
__all__ = ["MAX_UNBOUNDED_CREATION_SCAN", "evaluate", "main", "report_payload"]


def _load_sibling(module_name: str):
    """Load a sibling script BY PATH, because this runs as a git hook from an
    arbitrary working directory where ``scripts`` is not an importable package."""
    return load_path_module(module_name, Path(__file__).resolve().with_name(f"{module_name}.py"))


def evaluate(repo_root: Path, push_refs: list[dict[str, str]], repo: str, remote: str) -> dict[str, Any]:
    """Apply the carrier's floor to every close-keyword commit in the range."""
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
        "dropped_stdin_lines": max((int(ref.get("dropped_lines") or 0) for ref in push_refs), default=0),
        "coverage_notes": notes,
        "close_keyword_commits": findings,
    }


def _judge(
    repo_root: Path, repo: str, sha: str, checker: Any, issue_verify_closeout: Any
) -> dict[str, Any] | None:
    """One commit, through the carrier's own decision sequence.

    Follows ``check_issue_closeout_commit_msg.evaluate`` -- artifacts, pause carve-out,
    covered numbers, bare numbers, authorization, then one ``verify_closeout`` per
    carrier -- with the commit's TREE standing in for the index. Two deliberate
    differences, both stated rather than mirrored: ``close_targets`` is wider, and a
    close KEYWORD is required (see below), so the artifact-only trigger the carrier
    has does not exist here. A consequence of the second is that ``_pause_briefs`` is
    always empty: an artifact only reaches the partition when the message
    close-keywords one of its numbers, which is exactly the overlap that ends the
    pause exemption. It is returned and named rather than dropped silently.
    """
    body = commit_body(repo_root, sha)
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
            list_paths=lambda root, _sha=sha: commit_paths(root, _sha),
            read_file=lambda root, path, _sha=sha: commit_file(root, _sha, path),
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
    payload = dict(result)
    if not result["ok"]:
        payload["summary"] = _REFUSAL_SUMMARY
        payload["remediation"] = _REFUSAL_REMEDIATION
    return payload


def _push_refs_from_args(args: argparse.Namespace) -> list[dict[str, str]] | None:
    if not args.ranges:
        return parse_push_stdin(sys.stdin.read() if not sys.stdin.isatty() else "")
    push_refs = []
    for spec in args.ranges:
        remote_sha, _, local_sha = spec.partition("..")
        if not remote_sha or not local_sha:
            print(f"charness pre-push: unparseable --range {spec!r}", file=sys.stderr)
            return None
        push_refs.append(
            {"local_ref": "", "local_sha": local_sha, "remote_ref": "", "remote_sha": remote_sha}
        )
    return push_refs


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

    push_refs = _push_refs_from_args(args)
    if push_refs is None:
        return NO_VERDICT_EXIT
    if not push_refs:
        emit_yaml({"ok": True, "status": "no-refs", "commits_scanned": 0, "close_keyword_commits": []})
        return 0

    try:
        result = evaluate(repo_root, push_refs, args.repo, args.remote)
    except RangeUnreadable as exc:
        print(f"charness pre-push close-keyword guard: {exc}", file=sys.stderr)
        emit_yaml({"ok": False, "status": "no-verdict", "reason": str(exc)})
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


if __name__ == "__main__":
    raise SystemExit(cli())
