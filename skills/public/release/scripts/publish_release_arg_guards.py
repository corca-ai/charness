"""Operator-supplied values, refused before they reach the release record.

Split from `publish_release_preflight` at its length cap. One concept, and the
semantic half of `publish_release_args`: that module declares what the command
surface ACCEPTS, this one declares what a value must not BE once it is rendered into
a document other surfaces prove release state by reading. Every guard here runs at
argument time, before any mutation, because the record they protect is committed,
tagged and published before most of its readers ever run.
"""

from __future__ import annotations

import re
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
        _assert_no_raw_html(bump_rationale)
    return bump_rationale


_RAW_HTML_RE = re.compile(r"<[!/]?[A-Za-z]|<!--")


def _assert_no_raw_html(bump_rationale: str) -> None:
    """Refuse raw HTML in prose that is rendered into the published record.

    The class, not one member of it. This started as an `"<!--" in value` check,
    because an HTML comment hides every line after it from the RENDERED document a
    human reads while leaving the bytes every substring audit reads intact -- so the
    state ledger, the "NOT recorded" sentences and a `Claims review verdict: unproven`
    all disappear from view with every gate green. Hiding the negatives is worse than
    forging a positive and no check in this repo can see it.

    But `<!--` is not the only construct with that property: an unterminated `<details>`
    collapses the remainder of the rendered document into a disclosure widget, and
    `<summary>` and other unclosed containers behave similarly. Naming one member is
    the blacklist shape the sibling renderer's docstring argues against, so the rule is
    "no raw HTML" -- a bump rationale is prose and needs none. Quoting cannot help here:
    a blockquote renders its HTML.
    """
    match = _RAW_HTML_RE.search(bump_rationale)
    if match:
        raise SystemExit(
            f"--bump-rationale must not contain raw HTML (found {match.group(0)!r}); it is "
            "rendered into the published release record, and an unterminated tag or comment "
            "hides every line after it from the document a reader sees while leaving the "
            "bytes every audit reads intact. Say it in prose instead."
        )
