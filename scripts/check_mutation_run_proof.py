#!/usr/bin/env python3
"""Deterministic claim gate for citing a mutation workflow run as proof (#358).

The recurring false-proof class ``mutation-dispatch-no-base-sha-false-proof``:
a ``workflow_dispatch``-triggered mutation run computes no ``base_sha``
(``.github/workflows/mutation-tests.yml`` computes one only for ``schedule``
events), so its changed-line classifier is inert and a green run proves only
the score/survivor path. Citing such a run as changed-line proof is a false
proof. The prior durable artifact for this class was prose (a retro lesson and
a reference bullet) and the class recurred anyway (#251 -> #301); this gate is
the deterministic upgrade — it refuses the unsupported claim instead of relying
on the reader remembering the rule.

Run it before citing a CI mutation run as proof in a closeout, issue
resolution, or release note::

    # facts mode (no network):
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --event workflow_dispatch                       # exit 1: refused
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --event schedule --base-sha <sha>               # exit 0: provable

    # manifest mode: judge from the run's downloaded sample manifest. This is the
    # only mode that ESTABLISHES the range: the manifest carries the changed-pool
    # count, so a run whose range held no pool file is refused rather than cited.
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --sample-manifest reports/mutation/sample.json  # or sample.md

    # run mode: resolve the trigger event live via `gh run view`:
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --run-id <id> [--repo <org/repo>]

Exit 0 when the run can support the claim; exit 1 when it cannot. Refusals carry
the supported proof paths; only the dispatch/no-base-sha family also carries the
``class_key`` -- a pull_request run, a non-success conclusion, and an empty
changed pool are different refusals, not that class.

Exit 0 does NOT mean the range contents were established: with ``--base-sha``
and no manifest, ``range_established`` is false and the reason says the trigger
COULD evaluate the claim. That hedge is printed to stderr so it is not a silent
green. Whether it should instead be a nonzero exit is the contract question
recorded alongside ``conclusion_established`` in
``charness-artifacts/critique/2026-07-27-empty-scope-family.md`` (F9).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module
from yaml_output import emit_yaml

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

CLASS_KEY = "mutation-dispatch-no-base-sha-false-proof"
SUPPORTED_CHANGED_LINE_PROOF_PATHS = [
    "the next scheduled mutation run (schedule events compute base_sha from the previous completed run)",
    "a local run of scripts/check_changed_line_mutation_coverage.py with explicit MUTATION_BASE_SHA/MUTATION_HEAD_SHA over the fix range",
]
_MANIFEST_MD_BASE_RE = re.compile(r"^- Base SHA: `([^`]*)`", re.MULTILINE)
_MANIFEST_MD_CHANGED_RE = re.compile(r"^- Changed pool files: (\d+)", re.MULTILINE)


def classify_run_proof(
    claim: str,
    *,
    event: str | None = None,
    base_sha: str | None = None,
    conclusion: str | None = None,
    changed_pool_files: int | None = None,
) -> dict[str, object]:
    """Judge whether a mutation run with these facts can support the claim.

    Pure by design: callers resolve the facts (CLI flags, sample manifest, or
    ``gh run view``) and this function owns the verdict, so the refusal logic
    is testable without network or git state.
    """
    verdict: dict[str, object] = {"claim": claim, "event": event, "base_sha": base_sha or None}
    base = (base_sha or "").strip()

    def refuse(reason: str, *, class_hit: bool = False) -> dict[str, object]:
        verdict["provable"] = False
        verdict["reason"] = reason
        if class_hit:
            verdict["class_key"] = CLASS_KEY
        if claim == "changed-line":
            verdict["supported_proof_paths"] = SUPPORTED_CHANGED_LINE_PROOF_PATHS
        return verdict

    # Set before any refusal: a consumer must be able to tell "the run was known
    # red" from "nobody established what the run concluded", and both reach a
    # refusal by different routes.
    # A conclusion is NOT required: this classifier's job is what a given trigger's
    # pipeline can evaluate, and callers legitimately judge that from a downloaded
    # sample manifest, which carries no conclusion. But `provable` then means "this
    # trigger could evaluate the claim", never "and the run was green" — a manifest
    # from a red run reaches here too. Say which of the two was established instead
    # of letting one word carry both.
    verdict["conclusion_established"] = conclusion is not None
    if conclusion is not None and conclusion != "success":
        return refuse(f"run concluded {conclusion!r}, not success; a non-green run proves no claim")
    if claim == "changed-line":
        if event == "workflow_dispatch":
            return refuse(
                "workflow_dispatch computes no base_sha, so the changed-line classifier is "
                "inert by construction; a green dispatch run proves only the score path",
                class_hit=True,
            )
        if event == "pull_request":
            return refuse(
                "pull_request runs in dry-run mode and produces no mutation verdict at all"
            )
        if not base:
            return refuse(
                "no base_sha evidence: the changed-line classifier only runs over a real "
                "base..head range; supply --base-sha or the run's sample manifest",
                class_hit=True,
            )
        # A live classifier over an EMPTY range evaluated no file, so it proves
        # nothing about the fix being cited. `base_sha` alone cannot see that --
        # it establishes that the trigger COULD evaluate the claim, never that it
        # DID over a non-empty scope. Same split this function already makes for
        # `conclusion_established`, applied to the other half of the claim.
        verdict["range_established"] = changed_pool_files is not None
        if changed_pool_files == 0:
            return refuse(
                "the changed-line classifier ran over an EMPTY changed pool: no file was in "
                "range, so the run evaluated nothing and proves nothing about the change "
                "being cited"
            )
        verdict["provable"] = True
        if changed_pool_files is None:
            verdict["reason"] = (
                "the changed-line classifier COULD run: a real base..head range was supplied. "
                "What was in that range is NOT established here -- pass the run's sample "
                "manifest to establish it"
            )
        else:
            verdict["reason"] = (
                f"changed-line classifier was live over {changed_pool_files} changed pool file(s)"
            )
        return verdict
    if event == "pull_request":
        return refuse("pull_request runs in dry-run mode and produces no mutation verdict at all")
    if event is None:
        # The score claim has no other discriminator — unlike changed-line, which is
        # judged on base_sha and so tolerates an unknown event. Without a trigger,
        # this branch used to answer `provable` having identified no run at all.
        return refuse(
            "no run identified: the score claim is judged from the run's trigger, so pass "
            "--run-id or --event; with neither, there is nothing to judge"
        )
    verdict["provable"] = True
    verdict["reason"] = (
        "score/survivor path runs in full mode for schedule and workflow_dispatch events"
    )
    return verdict


def _same_commit(left: str, right: str) -> bool:
    """Whether two base-SHA strings can name the same commit.

    Abbreviation-tolerant, not resolution: this tool has no git access by design,
    so it cannot turn `origin/main` into a sha. A raw `!=` called an abbreviated
    sha a contradiction with its own full form, which is the shape an operator
    following this repo's own `--base-sha origin/main` advice would hit.
    """
    left, right = left.strip().lower(), right.strip().lower()
    if left == right:
        return True
    short, long = sorted((left, right), key=len)
    if len(short) < 7 or not all(c in "0123456789abcdef" for c in short + long):
        return False
    return long.startswith(short)


def facts_from_manifest(manifest_path: Path) -> dict[str, object]:
    """Extract base_sha AND range-size facts from a downloaded sample manifest.

    The range size was already in every manifest the sampler writes -- the JSON
    carries ``changed_files_before_coverage`` and the markdown a
    ``- Changed pool files:`` line -- and this reader simply did not look. That
    is why a run over an empty changed pool could be cited as changed-line proof:
    the fact needed to refuse it was on disk the whole time.

    ``changed_pool_files`` is None when the manifest does not carry it (an older
    manifest shape), which the classifier reports as range-not-established rather
    than as an empty range.
    """
    text = manifest_path.read_text(encoding="utf-8")
    if manifest_path.suffix == ".json":
        payload = json.loads(text)
        # The changed-line ARM's own report also carries `base_sha`, including
        # when it refused to judge. Fed in here it read as a manifest and its
        # refusal became `provable: true` -- a report that says "I proved
        # nothing" accepted as proof. Reject the shape rather than the value.
        for marker in ("changed_line_proof", "refused", "blocking", "untrusted"):
            if marker in payload:
                raise ValueError(
                    f"{manifest_path} looks like a changed-line GATE REPORT "
                    f"(carries `{marker}`), not a sampler sample manifest; a gate "
                    "report is a verdict, not the run facts this tool judges"
                )
        base = payload.get("base_sha")
        # Deliberately no fallback to `changed_files`: that is the post-coverage
        # SAMPLING subset, so a range whose files were all coverage-excluded has
        # `changed_files == []` while the changed-line scope was non-empty and
        # usually blocking. Substituting it would refuse with a reason the input
        # cannot support. An absent key stays not-established.
        changed = payload.get("changed_files_before_coverage")
        return {
            "base_sha": str(base) if base else "",
            "changed_pool_files": len(changed) if isinstance(changed, list) else None,
        }
    match = _MANIFEST_MD_BASE_RE.search(text)
    if match is None:
        raise ValueError(f"no `- Base SHA:` line found in {manifest_path}")
    base = match.group(1)
    changed_match = _MANIFEST_MD_CHANGED_RE.search(text)
    return {
        "base_sha": "" if base == "(none)" else base,
        "changed_pool_files": int(changed_match.group(1)) if changed_match else None,
    }


def facts_from_run(run_id: str, repo: str | None) -> dict[str, str | None]:
    """Resolve trigger event and conclusion live via ``gh run view``."""
    command = ["gh", "run", "view", run_id, "--json", "event,conclusion"]
    if repo:
        command[3:3] = ["--repo", repo]
    result = run_process(command, cwd=Path.cwd(), timeout_seconds=None)
    if result.returncode != 0:
        raise RuntimeError(f"gh run view failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    return {"event": payload.get("event"), "conclusion": payload.get("conclusion")}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refuse citing a mutation run as proof of a claim its trigger cannot evaluate."
    )
    parser.add_argument("--claim", required=True, choices=["changed-line", "score"])
    parser.add_argument(
        "--event", default=None, choices=["schedule", "workflow_dispatch", "pull_request"]
    )
    parser.add_argument(
        "--base-sha", default=None, help="Base SHA the run analyzed; empty means none."
    )
    parser.add_argument(
        "--conclusion", default=None, help="Run conclusion when known (e.g. success)."
    )
    parser.add_argument(
        "--sample-manifest", type=Path, default=None, help="Downloaded sample.json or sample.md."
    )
    parser.add_argument(
        "--run-id", default=None, help="Resolve event/conclusion via `gh run view`."
    )
    parser.add_argument(
        "--repo", default=None, help="org/repo for --run-id (defaults to the cwd repo)."
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    event, base_sha, conclusion = args.event, args.base_sha, args.conclusion
    changed_pool_files: int | None = None
    try:
        if args.run_id:
            run_facts = facts_from_run(args.run_id, args.repo)
            event = event or run_facts["event"]
            conclusion = conclusion or run_facts["conclusion"]
        if args.sample_manifest:
            manifest_facts = facts_from_manifest(args.sample_manifest)
            manifest_base = manifest_facts["base_sha"]
            supplied = (base_sha or "").strip()
            if supplied and manifest_base and not _same_commit(supplied, manifest_base):
                # The range COUNT comes from the manifest while the base SHA came
                # from the flag, so a mismatch would attribute the manifest's
                # scope to a range it never analyzed. Refuse rather than pick one.
                print(
                    f"--base-sha {supplied} contradicts the manifest's own base "
                    f"{manifest_base}; they are not prefix-compatible, so they name "
                    "different ranges and no verdict can be attributed to either. If "
                    "you passed a ref name, pass the resolved sha or drop --base-sha "
                    "and let the manifest own the range.",
                    file=sys.stderr,
                )
                return 1
            if supplied and not manifest_base:
                # A manifest with no base of its own cannot lend its count to a base
                # it never analyzed -- that is this tool's own named class arriving
                # through the back door. Keep the flag's base, drop the count.
                print(
                    "the manifest records no base SHA of its own, so its changed-pool "
                    f"count is not attributable to --base-sha {supplied}; the range "
                    "stays unestablished",
                    file=sys.stderr,
                )
            else:
                changed_pool_files = manifest_facts["changed_pool_files"]
            base_sha = manifest_base if base_sha is None else base_sha
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"could not resolve run facts: {error}", file=sys.stderr)
        return 1
    verdict = classify_run_proof(
        args.claim,
        event=event,
        base_sha=base_sha,
        conclusion=conclusion,
        changed_pool_files=changed_pool_files,
    )
    if verdict.get("provable") and verdict.get("conclusion_established") is False:
        # The manifest carries no conclusion by construction, so a manifest from a
        # RED run reaches here identically to one from a green run. Round 1 made the
        # range hedge audible and left this twin silent while its own comment called
        # them the same deferred question.
        print(
            "WARNING: the run's CONCLUSION is not established by this invocation. "
            "A manifest is uploaded by failed runs too; pass --conclusion or --run-id "
            "before citing this run as proof of anything.",
            file=sys.stderr,
        )
    if verdict.get("provable") and verdict.get("range_established") is False:
        # Loud, because exit 0 is the whole signal a consumer reads. `base_sha`
        # alone says the trigger COULD evaluate the claim; nothing here says what
        # was in the range. Whether that should become a nonzero exit is the same
        # contract question the repo already deferred for `conclusion_established`
        # (2026-07-27 empty-scope critique F9) and is recorded there, not decided
        # silently here.
        remedy = (
            "The manifest you passed carries no changed-pool count (an older shape, or "
            "a markdown manifest without the `- Changed pool files:` line), so the range "
            "stays unestablished."
            if args.sample_manifest
            else "Pass the run's sample manifest to establish the range."
        )
        print(
            "WARNING: the RANGE CONTENTS are not established by this invocation. "
            "`--base-sha` alone shows the classifier could run, not that it evaluated "
            f"any file. {remedy}",
            file=sys.stderr,
        )
    emit_yaml(dict(sorted(verdict.items())))
    if verdict["provable"]:
        return 0
    refusal = [f"REFUSED: this run cannot prove the {args.claim} claim ({verdict['reason']})."]
    if "class_key" in verdict:
        refusal.append(f"This is the {CLASS_KEY} false-proof class.")
    if args.claim == "changed-line":
        refusal.append(
            "Supported changed-line proof paths: "
            + "; ".join(SUPPORTED_CHANGED_LINE_PROOF_PATHS)
            + "."
        )
    print("\n".join(refusal), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
