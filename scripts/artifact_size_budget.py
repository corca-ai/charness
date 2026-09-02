"""How an artifact's SIZE is measured, and the refusal that enforces a ceiling.

Split out of `artifact_validator` on 2026-08-19, when the unit changed and the
reasoning that had to travel with it did not fit under that module's code-length
cap. This is a cohesive owner, not a mechanical spill (D33): the measurement and
the refusal that reads it are one decision, and every prose-artifact family --
debug, quality, and the doc-authoring preflight's fallback --
resolves both from here.

WHY WORDS AND NOT LINES. A line count charged for the author's WRAP WIDTH, not
for the reading load it named, and nothing in this repo enforces a width at all
(`.markdownlint-cli2.jsonc` sets `MD013: false`). Measured on the repo's own
corpora, one line ceiling admitted a 5.4x spread of words (debug: 276-1487 across
all 145 checked-in artifacts, every one of which fit the 180-line cap) and a 7.5x
spread (quality: 229-1727 across the 153 of 160 that fit the 140-line cap; the
other seven were already over it). So the cheapest way under a line ceiling was to rewrap
wider, which shortens nothing and makes the artifact harder to read while the
gate goes green.

The word ceilings that replaced those caps are NEW decisions, not conversions,
and each says so where it is declared -- with a 5.4x and 7.5x spread there is no
number that reproduces the old bar's behavior.

BLIND CLASS -- what this measure CANNOT see:

- A word is a whitespace-separated token, so a bare URL costs 1 and a fenced
  code block costs whatever its tokens happen to be, while either can dominate a
  screen. This is a READING-LOAD proxy, never a screen-space one.
- Markdown punctuation counts as its own token when a space follows it. `# Title`
  is TWO tokens (`#`, `Title`), and `# Debug Review` is three. An earlier draft of
  this line said `# Title` was three; a bounded reviewer caught it, and one of this
  slice's own test fixtures had the same off-by-one. A link is the opposite case:
  `[label](path)` holds no space and costs one.
- It cannot see repetition, hedging, or a paragraph that says nothing. No
  automatic measure can, which is why each family keeps an authoring TARGET well
  under its ceiling and treats the ceiling as a failure guard.
- It is the WRONG unit for a budget that means "at most N ENTRIES" (a vocabulary
  block, a reference list). `charge the unit you mean` is the rule; `always charge
  words` is not.

  Entry-shaped pressure budgets are owned by their skill-specific density checks;
  this module intentionally measures prose artifacts in words.
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Sequence

from runtime_bootstrap import import_repo_module

# Sibling resolution, not a bare import: `from artifact_run_scope import ...` binds
# only where `scripts/` happens to be on sys.path -- true in the repo, false in the
# exported plugin layout, where it would silently degrade a consumer's gate.
_run_scope = import_repo_module(__file__, "scripts.artifact_run_scope")
ValidationError = _run_scope.ValidationError
_violation_report = import_repo_module(__file__, "scripts.artifact_violation_report")
_scaffold_rel = _violation_report._scaffold_rel
_enforcement_scope = import_repo_module(__file__, "scripts.review.critique_enforcement_scope")


def artifact_words(lines: Sequence[str]) -> int:
    """Whitespace-separated tokens across an artifact's lines."""
    return sum(len(line.split()) for line in lines)


def validate_max_words(
    lines: Sequence[str], *, max_words: int, artifact_label: str, artifact_type: str | None = None
) -> None:
    counted = artifact_words(lines)
    if counted <= max_words:
        return
    message = (
        f"{artifact_label} is {counted} words; should stay concise — archive or move "
        f"durable detail to get back under {max_words} (cut ~{counted - max_words} words). "
        "Rewrapping cannot help: the budget charges words, not lines."
    )
    # A ceiling discovered only after writing long is a wasted draft; when the
    # owning scaffold publishes it as `size_budget.max_words`, say so here so
    # the next author writes-to-fit up front.
    scaffold = _scaffold_rel(artifact_type) if artifact_type else None
    if scaffold:
        message += f"; `python3 {scaffold} --repo-root .` reports this ceiling up front as `size_budget.max_words`"
    raise ValidationError(message)


# The date every prose-artifact budget in this repo changed unit.
WORD_CEILING_RULE_DATE = _dt.date(2026, 8, 19)


def word_ceiling_enforced(
    path: Path, lines: Sequence[str], *, rule_date: _dt.date = WORD_CEILING_RULE_DATE
) -> bool:
    """Whether a DATED artifact is in scope for the word ceiling.

    One owner, because the two callers that needed it (debug, quality) had already
    been written as byte-identical copies and the duplicate gate caught it in the
    same slice -- a repair carrying the class it repairs, which is what this repo
    spends its review rounds on.

    Grandfathering exists here because these are dated, append-only records that
    nobody may now rewrite. Current summaries use their owning workflow's shape.
    Measured at the cutover: seven checked-in debug artifacts sat between 1210 and
    1487 words under the new 1200 ceiling, and ten of the 160 quality artifacts sat
    above 1100.

    `observed_date` takes the LATER of filename and body date, so an artifact
    cannot date itself out of the ceiling with one author-written line. `None`
    (neither channel parses) is ENFORCED, never exempt -- otherwise stripping the
    date off a current file would buy the exemption.

    BLIND CLASS: an artifact whose date lives only in a containing DIRECTORY name
    is undatable by this rule, so a family stored that way cannot be grandfathered
    at all. A directory-dated diagnostic corpus is exactly that shape and therefore
    sets a ceiling above its corpus maximum instead of calling this.
    """
    # RESOLVE a pointer before reading the filename channel. `latest.md` carries no
    # date, so an unresolved read leaves the body `Date:` line -- the single
    # author-written channel -- deciding alone, which is precisely what `observed_date`'s
    # `max()` rule exists to prevent. `validate_quality_artifact.validate_date_channel_coherence`
    # already resolves for the same reason; this used to and did not, so on a byte-COPY
    # pointer layout (a first-class layout in this repo) one back-dated line disarmed the
    # ceiling with nothing refusing it. Same idiom as that check, deliberately.
    target = Path(path)
    if target.is_symlink():
        target = target.resolve()
    observed = _enforcement_scope.observed_date(target, "\n".join(lines))
    return observed is None or observed >= rule_date


def validate_max_words_when_dated_in_scope(
    path: Path,
    lines: Sequence[str],
    *,
    max_words: int,
    artifact_label: str,
    artifact_type: str | None = None,
    rule_date: _dt.date = WORD_CEILING_RULE_DATE,
) -> None:
    """`validate_max_words`, skipped for a dated artifact that predates the ceiling.

    One entry point rather than a `if word_ceiling_enforced(...) else None` ternary
    at each call site: the debug and quality gates expressed exactly that ternary as
    byte-identical copies, and the duplicate gate caught them in the slice that
    introduced them. A policy re-expressed at every call site is a policy that will
    diverge at one of them.
    """
    if not word_ceiling_enforced(path, lines, rule_date=rule_date):
        return
    validate_max_words(
        lines, max_words=max_words, artifact_label=artifact_label, artifact_type=artifact_type
    )
