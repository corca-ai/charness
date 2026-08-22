"""What to run NEXT when the changed-line gate could not use the coverage it found.

Split from `check_changed_line_mutation_coverage.py` as its own concept: the gate
owns the VERDICT, and this owns the ROUTE back to a usable one. One owner because
the gate reaches this state down two different branches -- a stale fingerprint and
an absent corpus -- and they used to answer the same question with two different
costs.

The measured gap this closes (#696, and the goal slice that filed it): the stale
branch's structured `reason` named only "Re-run the closeout producer", which
rebuilds the WHOLE coverage corpus at a measured 11-15 minutes. The incremental
lane -- `prepush_focused_changed_line_coverage.py`, which instruments only the
standing tests that reference the changed pool files -- is measured on this repo at
~24s for a single-commit slice and ~4min for a nine-commit session, and it was
reachable only by reading the source. The multiple depends on the slice: 11-15min
against ~24s is 27-38x for a single-commit slice, and about 3x for the
nine-commit case at ~4min. Printing only the expensive route as THE answer is how
an operator ends up rebuilding the corpus several times in one session.

Direction of the recommendation matters and is why the cheap lane is safe to name
first: focused coverage is a SUBSET of full coverage, so it can report a covered
line as uncovered but never an uncovered line as covered. It can cost a false
stop; it cannot grant a false pass. The broad producer stays named as the
fallback, because a false stop still has to be resolvable.
"""

from __future__ import annotations

import shlex
from pathlib import Path

#: The incremental lane. Its own default `--coverage-json` is deliberately NOT the
#: canonical corpus (subset coverage carrying a valid freshness marker would let
#: every `--require-fresh-coverage` consumer read freshness as breadth), so this
#: route never passes one -- letting that script's own default stand is the point.
INCREMENTAL_SCRIPT = "scripts/prepush_focused_changed_line_coverage.py"
BROAD_SCRIPT = "scripts/run_slice_closeout.py"


def incremental_refresh_command(repo_root: Path, base_sha: str) -> str:
    """The copyable cheapest-first refresh command for this repo and range."""
    return (
        f"python3 {INCREMENTAL_SCRIPT} "
        f"--repo-root {shlex.quote(str(repo_root))} "
        f"--base-sha {shlex.quote(base_sha)}"
    )


def broad_rebuild_command(repo_root: Path) -> str:
    """The whole-corpus rebuild: correct, and the fallback rather than the first move.

    Carries `--repo-root` for the same reason the incremental arm does. As a bare
    constant it did not, and `run_slice_closeout.py` derives its root from its own
    `__file__` -- so a gate invoked with `--repo-root /other/tree` printed a
    two-step route whose second step would have produced coverage for a different
    tree than the one it had just judged.
    """
    return (
        f"python3 {BROAD_SCRIPT} --repo-root {shlex.quote(str(repo_root))} "
        "--produce-mutation-coverage --verification-lock"
    )


def resume_route(repo_root: Path, base_sha: str) -> str:
    """The two-step route, cheapest first, as one sentence for a `reason` field.

    Emitted into the STRUCTURED payload rather than only onto stderr: the payload
    is what a resumed or compacted session reads back, and a route that exists
    only in a stream nobody replays is not reachable from the tool's output.
    """
    return (
        "Cheapest route FIRST -- this renders the changed-line verdict ITSELF, from a "
        "focused subset corpus at its own path, rather than refreshing the coverage "
        f"source this run just rejected: {incremental_refresh_command(repo_root, base_sha)}. "
        "Only if it cannot map the change, rebuild the whole corpus at the canonical "
        f"path: {broad_rebuild_command(repo_root)}."
    )


def resume_fields(repo_root: Path, base_sha: str) -> dict:
    """The route back to a usable verdict, as STRUCTURED payload fields.

    Two fields, not one, and neither folded into `reason`. `reason` is re-embedded
    verbatim inside the gate's #335 stderr tripwire, so a multi-sentence route
    there buries the file list that tripwire exists to show. And a route that is
    only prose in a sentence has to be re-parsed by whatever reads it back; a
    resumed or compacted session wants the command, not the paragraph around it.

    Lives HERE rather than in the gate because the gate is inside its length warn
    band and because this is the same concept as the two builders above -- the
    payload shape and the route it carries drift apart the moment they live in
    different files.
    """
    return {
        "resume_command": incremental_refresh_command(repo_root, base_sha),
        "resume_route": resume_route(repo_root, base_sha),
    }
