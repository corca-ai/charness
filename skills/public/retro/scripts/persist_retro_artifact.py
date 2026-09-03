#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))

SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)







_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapters.adapter_version_verdict"
)

_scripts_retro_persistence_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.retro_debug.retro_persistence_lib")
persist_retro_artifact = _scripts_retro_persistence_lib_module.persist_retro_artifact

emit_yaml = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output").emit_yaml

_ledger_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.lessons.lesson_ledger_lib"
)
_seeder = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.lessons.seed_lesson_transitions"
)

# The SAME pattern persistence stamps `Persisted:` with, read from the module that
# owns it rather than re-spelled here. Two regexes for one line is how the
# `Seeding:` note would end up anchored to a line shape persistence no longer
# writes, and this note is only readable because it sits under that one.
_PERSISTED_LINE_PATTERN = _scripts_retro_persistence_lib_module._PERSISTED_LINE_PATTERN
SEEDING_LINE_PREFIX = "Seeding: "


def stamp_seeding_note(markdown_text: str, note: str) -> str:
    """Carry the seeding outcome on the line directly under the stamped `Persisted:`.

    Same shape and same no-op rule as `stamp_persisted_path`: a body with no
    `Persisted:` line is returned untouched, because a retro that never claimed a
    durable home has no line for this one to qualify. The receipt still reports the
    seeding, so nothing is lost silently -- only the in-artifact copy is skipped.

    An existing `Seeding:` line immediately below is REPLACED rather than appended
    to. Re-persisting an explicitly named artifact runs the seeder again, and a
    second note would leave the reader two answers with no way to tell which run
    produced which.
    """
    match = _PERSISTED_LINE_PATTERN.search(markdown_text)
    if match is None:
        return markdown_text
    head, tail = markdown_text[: match.end()], markdown_text[match.end() :]
    stale = tail.split("\n", 2)
    if len(stale) > 1 and stale[1].startswith(SEEDING_LINE_PREFIX):
        tail = tail[len(stale[1]) + 1 :]
    return f"{head}\n{SEEDING_LINE_PREFIX}{note}{tail}"


def seed_tagged_lesson_classes(
    repo_root: Path, output_dir: Path, summary_path: Path | None
) -> str | None:
    """Seed every class the retros now tag, and say what happened in one line.

    A retro bullet tagged `(recurrence-class: <id>)` only makes a lesson SEEDABLE;
    the transition that makes it selectable is a second command nobody ran, so
    tagged classes accumulated unseeded and the lesson stayed invisible to the
    selection index it was written for. Persisting the retro is the moment the tag
    becomes durable, so it is the moment to seed.

    Repo-gated exactly like the digest refresh in `persist_retro_artifact`: the
    ledger is optional, consuming repos routinely keep none, and this is a portable
    skill script. No ledger means no seeder run and no `Seeding:` line at all.

    Returns None when there is nothing to report; never raises. A refusal (the
    fixed active-lesson budget is the expected one) is a legitimate ledger state
    awaiting a human archive decision, not a reason to fail a retro that is already
    written to disk -- so it comes back as text the artifact carries.

    Like every seeder call, the result lands in the worktree UNCOMMITTED. See that
    command's module docstring: a committed transition breaks unrepairably if its
    cited retro is later renamed, so a human inspects before the commit freezes it.
    """
    if not _ledger_lib.lesson_ledger_path(output_dir).is_file():
        return None
    try:
        receipt = _seeder.seed_transitions(
            repo_root=repo_root,
            output_dir=output_dir,
            summary_path=summary_path,
            lesson_ids=None,
            dry_run=False,
        )
    except (FileNotFoundError, OSError, ValueError, json.JSONDecodeError, KeyError) as exc:
        # Collapsed to one line: this note lives in a metadata block whose reader
        # scans line-per-fact, and a multi-line refusal would break that shape.
        return "refused: " + " ".join(str(exc).split())
    seeded = receipt["seeded_count"]
    return f"{seeded} class(es) seeded" if seeded else "none pending"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root that owns the retro adapter and output directory")
    parser.add_argument(
        "--artifact-name",
        required=True,
        help="Subject key, or an explicitly named dated retro artifact filename",
    )
    parser.add_argument("--markdown-file", type=Path, required=True, help="Path to the rendered retro markdown body to persist")
    parser.add_argument(
        "--goal-path",
        type=Path,
        help=(
            "Opt into goal-aware persistence; the retro must contain exactly one "
            "matching `Goal:` field before any output is written"
        ),
    )
    parser.add_argument(
        "--goal-lineage-file",
        type=Path,
        help="Bind the retro to one repo-local Goal Run lineage JSON; cannot be combined with --goal-path.",
    )
    parser.add_argument(
        "--force-empty-summary",
        action="store_true",
        help=(
            "Allow the summary refresh to write an empty-stub digest even when "
            "lesson extraction returns 0 candidates and a non-stub summary "
            "already exists. Default behavior preserves the existing summary."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    SKILL_RUNTIME.require_repo_local_helper(__file__, repo_root)
    adapter = load_adapter(repo_root)
    # Both paths below are adapter-declared, and a version this reader cannot speak
    # leaves both at the charness defaults: the retro would be persisted outside the
    # directory the repo keeps retros in, and a SECOND lessons digest would appear at
    # the default `summary_path` while the repo's own stopped being refreshed -- on the
    # surface every session reads before work.
    #
    # Widened in round 2 of the slice-5 review: this asked `version_refused`, one of the
    # two doors into "nothing declared is honored". A parser refusal is the other, and
    # would have written a shadow retro AND a shadow lessons digest at the charness
    # defaults -- on the surface every session reads before work.
    errors = adapter.get("errors")
    if _version_verdict.declarations_unhonored(errors):
        print(
            f"retro adapter {_version_verdict.unhonored_cause(errors)} "
            f"({'; '.join(errors or [])}); nothing it declares is honored, "
            "so this retro would be written to the charness default directory rather "
            "than this repo's. "
            + _version_verdict.unhonored_remedy(errors, "retro-adapter.yaml"),
            file=sys.stderr,
        )
        return 1
    output_dir = repo_root / adapter["data"]["output_dir"]
    summary_rel = adapter["data"].get("summary_path")
    summary_path = (repo_root / summary_rel) if isinstance(summary_rel, str) else None
    markdown_text = args.markdown_file.read_text(encoding="utf-8")
    try:
        result = persist_retro_artifact(
            repo_root=repo_root,
            output_dir=output_dir,
            artifact_name=args.artifact_name,
            markdown_text=markdown_text,
            summary_path=summary_path,
            force_empty_summary=args.force_empty_summary,
            goal_path=args.goal_path,
            goal_lineage_path=args.goal_lineage_file,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    # AFTER the artifact, digest, and selection index are on disk: the seeder derives
    # its candidates from `output_dir/*.md`, so the class this very retro tags is only
    # visible to it once this retro is durable.
    note = seed_tagged_lesson_classes(repo_root, output_dir, summary_path)
    if note is not None:
        result["seeding"] = note
        artifact_path = repo_root / result["artifact_path"]
        artifact_path.write_text(
            stamp_seeding_note(artifact_path.read_text(encoding="utf-8"), note), encoding="utf-8"
        )
    emit_yaml(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
