#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)




_scripts_simple_skill_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.simple_skill_adapter_lib")
load_simple_adapter = _scripts_simple_skill_adapter_lib_module.load_simple_adapter

# CONTENT words, not file lines and no longer content LINES: the budget excludes blank
# lines, the canonical `##` headings the validator itself requires, and the whole
# `## References` block, then charges per whitespace-separated token of what remains.
# Named apart from debug/quality's `max_artifact_lines` for the reason that name was
# always separate -- one shared name across the two families would have meant two
# different measurements, so a repo copying a number between adapters would silently get
# a different ceiling than it read. That hazard is now sharper, not softer: the two
# families no longer share a UNIT either.
WORD_BUDGET_FIELD = "max_content_words"
# 1, not 0: a ceiling of 0 refuses every possible handoff, including the scaffold's stub.
INT_FIELDS = ((WORD_BUDGET_FIELD, 1),)
# `max_content_lines` was this field until 2026-08-19. It is REFUSED rather than ignored,
# and rather than silently reinterpreted: 78 read as a word ceiling would refuse every
# real handoff, and dropping it would leave a consuming repo's declared bar inert while
# the adapter reported `valid: true`. Neither the loader's uninterpreted-line channel nor
# `declarations_dropped` can see this: both report what the PARSER dropped, and a
# well-formed key the SCHEMA stopped reading parses perfectly. A retired field is exactly
# the class those doors cannot cover, which is why it needs its own refusal.
RETIRED_FIELDS = ((
    "max_content_lines",
    WORD_BUDGET_FIELD,
    "the handoff budget now charges CONTENT WORDS, not lines, because a line count "
    "measured the author's wrap width (a 3.3x swing on identical prose). A line "
    "ceiling cannot be converted automatically -- the old bar admitted 222-1240 words "
    "-- so restate the bar you want in words; the shipped default is 900",
),)


def load_adapter(repo_root: Path) -> dict[str, object]:
    return load_simple_adapter(
        repo_root,
        skill_id="handoff",
        artifact_filename="handoff.md",
        default_output_dir="docs",
        artifact_class="rolling",
        missing_warnings=(
            "No handoff adapter found. Using default docs/handoff.md location.",
            "Create .agents/handoff-adapter.yaml to move the artifact path or record preset provenance.",
        ),
        int_fields=INT_FIELDS,
        retired_fields=RETIRED_FIELDS,
    )


def main() -> None:
    SKILL_RUNTIME.run_adapter_cli(load_adapter, label="handoff resolve_adapter", repo_root_help="Repo root for resolving the handoff adapter")


if __name__ == "__main__":
    main()
