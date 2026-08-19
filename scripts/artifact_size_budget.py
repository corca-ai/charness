"""How an artifact's SIZE is measured, and the refusal that enforces a ceiling.

Split out of `artifact_validator` on 2026-08-19, when the unit changed and the
reasoning that had to travel with it did not fit under that module's code-length
cap. This is a cohesive owner, not a mechanical spill (D33): the measurement and
the refusal that reads it are one decision, and every prose-artifact family --
debug, quality, cautilus proof, and the doc-authoring preflight's fallback --
resolves both from here.

WHY WORDS AND NOT LINES. A line count charged for the author's WRAP WIDTH, not
for the reading load it named, and nothing in this repo enforces a width at all
(`.markdownlint-cli2.jsonc` sets `MD013: false`). Measured on the repo's own
corpora, one line ceiling admitted a 5.4x spread of words (debug: 276-1487
across 146 artifacts at the 180-line cap) and a 7.5x spread (quality: 229-1727
across 161 at 140). So the cheapest way under a line ceiling was to rewrap
wider, which shortens nothing and makes the artifact harder to read while the
gate goes green.

The word ceilings that replaced those caps are NEW decisions, not conversions,
and each says so where it is declared -- with a 5.4x and 7.5x spread there is no
number that reproduces the old bar's behavior.

BLIND CLASS -- what this measure CANNOT see:

- A word is a whitespace-separated token, so a bare URL costs 1 and a fenced
  code block costs whatever its tokens happen to be, while either can dominate a
  screen. This is a READING-LOAD proxy, never a screen-space one.
- Markdown punctuation counts. `# Title` is three tokens, not two; a table row
  is priced by its cell contents plus its pipes.
- It cannot see repetition, hedging, or a paragraph that says nothing. No
  automatic measure can, which is why each family keeps an authoring TARGET well
  under its ceiling and treats the ceiling as a failure guard.
- It is the WRONG unit for a budget that means "at most N ENTRIES" (a vocabulary
  block, a reference list). Charge entries there. `charge the unit you mean` is
  the rule; `always charge words` is not.
"""
from __future__ import annotations

from typing import Sequence

from runtime_bootstrap import import_repo_module

# Sibling resolution, not a bare import: `from artifact_run_scope import ...` binds
# only where `scripts/` happens to be on sys.path -- true in the repo, false in the
# exported plugin layout, where it would silently degrade a consumer's gate.
_run_scope = import_repo_module(__file__, "scripts.artifact_run_scope")
ValidationError = _run_scope.ValidationError
_violation_report = import_repo_module(__file__, "scripts.artifact_violation_report")
_scaffold_rel = _violation_report._scaffold_rel


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
