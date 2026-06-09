#!/usr/bin/env python3
"""Author-time required-shape source for the goal-closeout complete gate.

``check_goal_artifact.py`` (at the complete flip) enforces closeout-evidence
forms an author otherwise discovers by failing the flip several times (the
recurring authoring-preflight class). This module is the *shape source* the
artifact-surface preflight dispatcher reads for ``--type goal-closeout``,
alongside the goal template's ``## Final Verification``
block: the template seeds the lines to author into, and this module surfaces the
enforced FORMS the template prose leaves implicit.

It never re-declares the contract: the allowed skip-reason enum and the
disposition opt-out floor are rendered from the LIVE enforced constants, so the
surfaced shape cannot drift from the gate.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(
        module_name, Path(__file__).resolve().parent / f"{module_name}.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside describe_goal_closeout_shape.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_repo_script(module_name: str) -> Any:
    """Load a repo-root ``scripts/<module_name>.py`` via the nearest ``scripts/``
    ancestor — the clone-safe walk the skill packages use, resolving in the
    working tree and the installed plugin export alike."""
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / "scripts" / f"{module_name}.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(module_name, candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError(f"scripts/{module_name}.py not found")


# Single sources: the skip-reason enum, the disposition-line form summaries, and
# the opt-out min length are read live from the validators that enforce them.
_PRESCRIBED = _load_repo_script("check_prescribed_skill_executed_lib")
_DISPOSITION_FORM = _load_repo_script("disposition_form")
_DISPOSITION = _load_sibling("goal_artifact_disposition_grammar")


def required_shape() -> str:
    skip_enum = ", ".join(sorted(_PRESCRIBED.ALLOWED_SKIP_REASONS))
    min_skip = _PRESCRIBED.MIN_SKIP_LENGTH
    min_optout = _DISPOSITION.MIN_OPTOUT_REASON
    valid_form = _DISPOSITION_FORM.VALID_FORM_SUMMARY
    dest_form = _DISPOSITION_FORM.DESTINATION_FORM_SUMMARY
    lines = [
        "goal-closeout required shape (enforced by `check_goal_artifact.py` at the",
        "complete flip — `Status: complete`). The template above seeds the lines;",
        "these are the FORMS the gate enforces on them:",
        "",
        "`## Final Verification` — `Retro:`, `Host log probe:`, and (for in-scope goals)",
        "`Disposition review:` each must be EITHER:",
        "  - a bound `<path>`: the evidence file EXISTS, is non-empty, and BINDS to this",
        "    goal — its basename or content contains the goal slug (the Activation line's",
        "    `/goal @<...-slug>` minus the date prefix). Citing an unrelated pre-existing",
        "    artifact fails the binding check. A bare path, not `<path>`/`TODO`/`TBD`.",
        f"  - OR `skipped: <reason>: <detail>` where <reason> is one of: {skip_enum}",
        f"    (free text is rejected) and the whole reason is >= {min_skip} chars.",
        "",
        "`## Coordination Cues` — `Routing:` must NAME both `find-skills` and the routed",
        "skill for recorded work (e.g. `Routing: find-skills recommended achieve for the",
        "goal lifecycle`), or `Routing: n/a — <reason>` (>= 30 chars). Gather/Release/Issue",
        "closeout floors fire the same way — see `--type goal-coordination` for the full shape.",
        "",
        "`## Auto-Retro` — the disposition floor: replace the seeded `Retro dispositions: TODO`.",
        f"  - per-improvement / opt-out (`Retro dispositions:`), one of: {valid_form}",
        f"    (the `none — <reason>` opt-out is >= {min_optout} chars; bare prose/memory is rejected).",
        f"  - `Structural follow-up:` (when the retro names transferable waste), one of: {dest_form}",
        "A blank/placeholder `## Auto-Retro` with a cited retro listing improvements is refused.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def stub() -> str:
    """A starter closeout block (bound evidence paths + a disposition opt-out)."""
    return (
        "<!-- goal-closeout starter; bind each path to THIS goal's slug, or use a "
        "skipped: <allowed-reason>: <detail> line. Run --type goal-closeout for the forms. -->\n"
        "## Final Verification\n\n"
        "Retro: charness-artifacts/retro/<date>-<goal-slug>.md\n"
        "Host log probe: charness-artifacts/retro/<date>-<goal-slug>-host-log.md\n"
        "Disposition review: charness-artifacts/critique/<date>-<goal-slug>-disposition-review.md\n\n"
        "## Auto-Retro\n\n"
        "Retro dispositions: none — <>=30-char reason no surfaced improvement needs active disposition>\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--stub", action="store_true", help="Emit a starter closeout block")
    args = parser.parse_args(argv)
    sys.stdout.write(stub() if args.stub else required_shape())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
