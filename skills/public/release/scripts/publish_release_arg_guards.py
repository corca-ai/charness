"""Operator-supplied values, refused before they reach the release record.

Split from `publish_release_preflight` at its length cap. One concept, and the
semantic half of `publish_release_args`: that module declares what the command
surface ACCEPTS, this one declares what a value must not BE once it is rendered into
a document other surfaces prove release state by reading. Every guard here runs at
argument time, before any mutation, because the record they protect is committed,
tagged and published before most of its readers ever run.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from typing import Callable

CRITIQUE_ARTIFACT_PREFIX = "charness-artifacts/critique/"

# One owner for the record-sentinel rule. This path is rendered into the release record
# as `## Review Proof` on every write, including the published one.
_claims_evidence = runpy.run_path(
    str(Path(__file__).resolve().with_name("claims_review_evidence.py"))
)


def validate_critique_artifact_arg(
    repo_root: Path,
    artifact: str | None,
    *,
    run_command: Callable,
) -> str | None:
    if artifact is None:
        return None
    relpath = Path(artifact)
    if relpath.is_absolute() or any(part in ("", ".", "..") for part in relpath.parts):
        raise SystemExit("--critique-artifact must be a normalized repo-relative path")
    normalized = relpath.as_posix()
    if not normalized.startswith(CRITIQUE_ARTIFACT_PREFIX) or relpath.suffix != ".md":
        raise SystemExit("--critique-artifact must point at a critique markdown artifact")
    _claims_evidence["assert_no_record_sentinel"](normalized, "--critique-artifact")
    resolved = (repo_root / relpath).resolve()
    try:
        resolved.relative_to(repo_root)
    except ValueError as exc:
        raise SystemExit("--critique-artifact must stay inside the repo root") from exc
    if not resolved.is_file():
        raise SystemExit(f"--critique-artifact does not exist: {normalized}")
    tracked = run_command(["git", "ls-files", "--error-unmatch", normalized], cwd=repo_root, check=False)
    if tracked.returncode != 0:
        raise SystemExit(f"--critique-artifact must be tracked before release: {normalized}")
    return normalized


def validate_bump_rationale_arg(bump_rationale: str | None) -> str | None:
    """The `--bump-rationale` value, refused when it would forge or HIDE release state.

    Rendered into the release record, which other surfaces prove release state by
    substring-matching -- the same exposure `--critique-artifact` has, and the reason
    the sentinel rule is shared rather than re-derived here.

    ONE rule now, and the deleted one is the more interesting half. A guard used to
    enumerate constructs that hide the rest of a RENDERED record -- raw-text elements,
    unclosed tags, HTML comments. It was widened, narrowed and rebuilt across three
    review rounds and was wrong in both directions every time, because it decided what a
    renderer shows while being unable to see a renderer: this repo declares no renderer
    dependency, no test re-ran the check, and no artifact recorded its output, so the
    word "measured" in its docstring was testimony a reader could not verify. The record
    also emits a raw `<!--` on line two of every prepared release itself, and proves
    release state by substring-matching it -- so this document's shipped model was always
    text, and the guard was reasoning about a reader nobody had evidence of.

    The class is closed by POSITION instead: `write_release_artifact` emits
    `## Bump Rationale` last, so an unterminated construct in operator prose has nothing
    below it to hide. That works for every renderer, measured or not, and rewrites none
    of the operator's bytes.

    What remains is renderer-independent. A record-state sentinel is matched as a
    SUBSTRING by other surfaces to prove release state, so it cannot be neutralised by
    position or by quoting without changing what the operator wrote. It stops the run at
    argument time, before any mutation.
    """
    if bump_rationale is not None:
        _claims_evidence["assert_no_record_sentinel"](bump_rationale, "--bump-rationale")
    return bump_rationale


