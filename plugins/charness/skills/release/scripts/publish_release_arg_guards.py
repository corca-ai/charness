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
_claims_review = runpy.run_path(
    str(Path(__file__).resolve().with_name("publish_release_claims_review.py"))
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
    _claims_review["assert_no_record_sentinel"](normalized, "--critique-artifact")
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

    Two rules, and the split is deliberate. Line-start constructs (headings, fences,
    claim-shaped bullets) are made inert at RENDER time by quoting the prose, because
    the value is a human explanation supplied after the critique gate and a refusal
    there costs a release cycle to reword. `<!--` cannot be handled that way: quoting
    does not stop an HTML comment from swallowing the rest of the RENDERED document,
    so a record whose every substring audit passes would show a human reader nothing
    below the rationale -- not the state ledger, not the "NOT recorded" sentences, not
    a `Claims review verdict: unproven`. Hiding the negatives is worse than forging a
    positive, and it is invisible to every check this repo has. Same for a record-state
    sentinel, which cannot be neutralised without changing what the operator wrote.
    Both stop the run at argument time, before any mutation.
    """
    if bump_rationale is not None:
        _claims_review["assert_no_record_sentinel"](bump_rationale, "--bump-rationale")
        _assert_no_hidden_record(bump_rationale)
    return bump_rationale


def _assert_no_hidden_record(bump_rationale: str) -> None:
    """Refuse the one construct that hides a rendered record from OUTSIDE a blockquote.

    This was widened to all raw HTML and narrowed back, and the measurement is why.
    Every rationale line is quoted, so a markdown BLOCK container -- `<details>`,
    `<summary>`, an unclosed `<div>` -- is closed at the end of the blockquote and its
    blast radius stops there. An unterminated `<!--` does not: it survives into the
    emitted HTML stream and is consumed by the HTML parser, which has no idea a
    blockquote ended, so everything below it disappears from the document a human reads
    while every substring audit passes over the raw bytes. That asymmetry is the whole
    reason this guard exists, and it names exactly one construct because exactly one
    construct has the property.

    The wide version refused ordinary prose. `<[!/]?[A-Za-z]` matches `<path>`, `<ref>`,
    `<repo>` and a bare autolink -- placeholders this repo writes constantly, including
    in its own root docs -- so a release was blocked at argument time for English, with
    an error quoting two characters as the offender. The sibling that renders this record
    already owns that lesson: `strip_display_code` exists because content shown AS CODE
    is not asserted to the reader, and its docstring records breaking "in opposite
    directions" when that was ignored. A guard whose false positives are ordinary
    sentences is not paying for the true positives it adds.
    """
    if "<!--" in bump_rationale:
        raise SystemExit(
            "--bump-rationale must not contain '<!--'; it is rendered into the published "
            "release record, and an unterminated HTML comment survives past the blockquote "
            "this value is rendered in, hiding every line below it from the document a "
            "reader sees while leaving the bytes every audit reads intact. Say it in prose "
            "instead. Angle-bracket placeholders like `<path>` are fine: they are inside "
            "the blockquote and cannot escape it."
        )
