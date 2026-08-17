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
        _assert_no_hidden_record(bump_rationale)
    return bump_rationale


#: Element names whose CONTENT the HTML tokenizer stops parsing as markup: raw-text and
#: escapable-raw-text elements, plus the opaque legacy ones. An unterminated opener puts
#: the rest of the document inside them.
_OPAQUE_ELEMENTS = ("script", "style", "textarea", "pre", "plaintext", "xmp", "iframe", "noembed")
_OPAQUE_OPENER_RE = re.compile(r"<\s*/?\s*(" + "|".join(_OPAQUE_ELEMENTS) + r")\b", re.IGNORECASE)
#: A `<` starting a tag that is never closed by a `>`: an unterminated attribute value
#: swallows the rest of the document into the attribute.
_UNCLOSED_TAG_RE = re.compile(r"<[A-Za-z][^>]*$", re.DOTALL)


def _assert_no_hidden_record(bump_rationale: str) -> None:
    """Refuse the constructs MEASURED to remove the record from what a reader sees.

    Measured, not reasoned. Each candidate was rendered into a record body of the shape
    `write_release_artifact` emits and the output fed to an HTML parser, asking not "are
    the ledger bytes present" -- they always are, which is why every substring audit
    passes -- but "does the ledger arrive as document flow". Under python-markdown 3.3.6:

    * `<script>`, `<style>`, `<textarea>`: bytes present, ledger NOT visible. The
      tokenizer enters raw-text state and `</blockquote>` is character data there, so
      quoting does not bound them and everything below the rationale disappears.
    * an unterminated attribute (`<span title="x`): the ledger does not even reach the
      HTML.
    * `<details>`, `<summary>`, `<div>`: visible. The blockquote's end tag pops the stack
      and the stray element with it, so these are genuinely harmless and refusing them
      was the over-wide version's false positive.
    * `<!--`: visible under this renderer. Kept in the refusal anyway, because a
      pass-through renderer (`cmark --unsafe`, pandoc) emits it into the stream where it
      does hide the rest -- but recorded here as UNPROVEN for the renderer measured,
      rather than asserted as the guard's headline true positive the way it once was.

    Which renderer produces "the document a human reader sees" is not settled and the
    guard cannot settle it: GitHub sanitizes `<script>`/`<style>` away entirely, and
    `cmark` in safe mode replaces all raw HTML with a closed comment. The list is
    therefore the union of what any plausible target renders opaquely, which is still a
    CLOSED list of element names -- so `<path>`, `<ref>`, `<repo>` and autolinks, the
    notation this repo writes constantly, are untouched.
    """
    match = _OPAQUE_OPENER_RE.search(bump_rationale) or _UNCLOSED_TAG_RE.search(bump_rationale)
    if match or "<!--" in bump_rationale:
        found = match.group(0) if match else "<!--"
        raise SystemExit(
            f"--bump-rationale must not contain {found!r}; it is rendered into the published "
            "release record, and this construct puts every line below it inside an element "
            "the HTML parser does not read as markup -- the state ledger, the "
            "\"NOT recorded\" sentences and the claims verdict vanish from the document a "
            "reader sees while the bytes every audit reads stay intact. Say it in prose "
            "instead; angle-bracket placeholders like `<path>` are fine."
        )
