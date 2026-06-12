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

    # manifest mode: judge from the run's downloaded sample manifest:
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --sample-manifest reports/mutation/sample.json  # or sample.md

    # run mode: resolve the trigger event live via `gh run view`:
    python3 scripts/check_mutation_run_proof.py --claim changed-line \\
        --run-id <id> [--repo <org/repo>]

Exit 0 when the run can support the claim; exit 1 with the class key and the
supported proof paths when it cannot.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

CLASS_KEY = "mutation-dispatch-no-base-sha-false-proof"
SUPPORTED_CHANGED_LINE_PROOF_PATHS = [
    "the next scheduled mutation run (schedule events compute base_sha from the previous completed run)",
    "a local run of scripts/check_changed_line_mutation_coverage.py with explicit MUTATION_BASE_SHA/MUTATION_HEAD_SHA over the fix range",
]
_MANIFEST_MD_BASE_RE = re.compile(r"^- Base SHA: `([^`]*)`", re.MULTILINE)


def classify_run_proof(
    claim: str,
    *,
    event: str | None = None,
    base_sha: str | None = None,
    conclusion: str | None = None,
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
            return refuse("pull_request runs in dry-run mode and produces no mutation verdict at all")
        if not base:
            return refuse(
                "no base_sha evidence: the changed-line classifier only runs over a real "
                "base..head range; supply --base-sha or the run's sample manifest",
                class_hit=True,
            )
        verdict["provable"] = True
        verdict["reason"] = "changed-line classifier was live over a real base..head range"
        return verdict
    if event == "pull_request":
        return refuse("pull_request runs in dry-run mode and produces no mutation verdict at all")
    verdict["provable"] = True
    verdict["reason"] = "score/survivor path runs in full mode for schedule and workflow_dispatch events"
    return verdict


def facts_from_manifest(manifest_path: Path) -> dict[str, str | None]:
    """Extract base_sha facts from a downloaded sample manifest (.json or .md)."""
    text = manifest_path.read_text(encoding="utf-8")
    if manifest_path.suffix == ".json":
        base = json.loads(text).get("base_sha")
        return {"base_sha": str(base) if base else ""}
    match = _MANIFEST_MD_BASE_RE.search(text)
    if match is None:
        raise ValueError(f"no `- Base SHA:` line found in {manifest_path}")
    base = match.group(1)
    return {"base_sha": "" if base == "(none)" else base}


def facts_from_run(run_id: str, repo: str | None) -> dict[str, str | None]:
    """Resolve trigger event and conclusion live via ``gh run view``."""
    command = ["gh", "run", "view", run_id, "--json", "event,conclusion"]
    if repo:
        command[3:3] = ["--repo", repo]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh run view failed: {result.stderr.strip()}")
    payload = json.loads(result.stdout)
    return {"event": payload.get("event"), "conclusion": payload.get("conclusion")}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Refuse citing a mutation run as proof of a claim its trigger cannot evaluate."
    )
    parser.add_argument("--claim", required=True, choices=["changed-line", "score"])
    parser.add_argument("--event", default=None, choices=["schedule", "workflow_dispatch", "pull_request"])
    parser.add_argument("--base-sha", default=None, help="Base SHA the run analyzed; empty means none.")
    parser.add_argument("--conclusion", default=None, help="Run conclusion when known (e.g. success).")
    parser.add_argument("--sample-manifest", type=Path, default=None, help="Downloaded sample.json or sample.md.")
    parser.add_argument("--run-id", default=None, help="Resolve event/conclusion via `gh run view`.")
    parser.add_argument("--repo", default=None, help="org/repo for --run-id (defaults to the cwd repo).")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    event, base_sha, conclusion = args.event, args.base_sha, args.conclusion
    try:
        if args.run_id:
            run_facts = facts_from_run(args.run_id, args.repo)
            event = event or run_facts["event"]
            conclusion = conclusion or run_facts["conclusion"]
        if args.sample_manifest:
            manifest_facts = facts_from_manifest(args.sample_manifest)
            base_sha = manifest_facts["base_sha"] if base_sha is None else base_sha
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"could not resolve run facts: {error}", file=sys.stderr)
        return 1
    verdict = classify_run_proof(args.claim, event=event, base_sha=base_sha, conclusion=conclusion)
    print(json.dumps(verdict, indent=2, sort_keys=True))
    if verdict["provable"]:
        return 0
    refusal = [f"REFUSED: this run cannot prove the {args.claim} claim ({verdict['reason']})."]
    if "class_key" in verdict:
        refusal.append(f"This is the {CLASS_KEY} false-proof class.")
    if args.claim == "changed-line":
        refusal.append("Supported changed-line proof paths: " + "; ".join(SUPPORTED_CHANGED_LINE_PROOF_PATHS) + ".")
    print("\n".join(refusal), file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
