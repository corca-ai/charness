#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from datetime import date as date_cls
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
goal_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_cli_args")

_PROSE_FIELDS = ("title", "goal-body")


def _load_fields_file(path: Path) -> dict[str, str]:
    """Read this helper's PROSE fields from ONE JSON file, so no prose crosses a shell.

    The field set is deliberately NOT `append_slice_log.py`'s. Only `title` and
    `goal-body` are free prose. `--status` is a closed enum and `--date` an ISO date,
    both of which refuse loudly when a shell damages them; `--slug` is resolved
    through `goal_artifact_lib.slugify` and refuses only total loss to the fallback
    (see `_resolve_slug`). Mirroring the other helper's whole surface for symmetry
    would add flags with nothing to fix.
    """
    return goal_cli.load_fields_file(path, known=set(_PROSE_FIELDS))


def _normalize_newlines(value: str) -> str:
    """Collapse CRLF and lone CR to LF before anything checks or writes the value.

    Every reader of a goal artifact uses `Path.read_text`, which opens in universal-
    newline mode, so a lone `\\r` written to disk is handed back as a `\\n`. A guard
    that only knows `\\n` therefore passes text that BECOMES a line break -- and
    `\\r## Slice Log` reads back as a heading nobody wrote, under a `created` verdict.
    Normalizing first makes the bytes on disk agree with the bytes every reader sees,
    which closes the gap rather than merely refusing at it.
    """
    return goal_lib.normalize_goal_text(value)


def _reject_unwritable_prose(title: str, goal_body: str) -> None:
    """Shape rules for the VALUES being written, whatever channel delivered them.

    These deliberately do not live in `_load_fields_file`: a caller building `argv`
    as a list is documented as an equally safe channel against the shell, and it is
    -- but it is not safe against these two, and a guard that fires only for
    `--fields-file` would leave the documented alternative unpoliced. The property
    belongs to the value, not to its transport.
    """
    try:
        goal_lib.validate_goal_values(title, goal_body)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def _resolve_slug(slug: str) -> str:
    """Refuse a slug that lost EVERYTHING to coercion, not one that was merely coerced.

    `goal_artifact_lib.slugify` never raises: it coerces, and an empty result becomes
    the literal `goal`. So a shell-damaged `--slug` does not fail -- it creates
    `<date>-goal.md` and reports `created`, which is the same silent-damage-under-a-
    success-verdict class this helper is being repaired for.

    THAT total loss is the signature, and it is the only thing refused here. The first
    cut refused any slug `slugify` would rewrite at all, and that was the wrong boundary
    -- again. Coercion is not damage: it is GLOBAL and consistent, because `goal_path`
    slugifies too and every sibling helper resolves through it. So `--slug PROJ_184`
    round-tripped across `upsert_goal`, `append_slice_log` and `check_goal_artifact`
    alike, and refusing it here broke a correct caller while its siblings kept working
    -- including on a status flip against an artifact created weeks earlier. The caller
    never asked for a filename; it asked for a stable key, and the key resolved.

    An emptied slug is different in kind: nothing of what was passed survives, and the
    `goal` that replaces it was never anyone's key.
    """
    try:
        return goal_lib.resolve_supplied_slug(slug)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a new achieve goal artifact, or update only the status of an existing one."
    )
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--slug", required=True, help="Short kebab-case goal slug (e.g. acme-184-push-confidence)")
    parser.add_argument("--title", default=None, help="Human-readable goal title shown in the artifact heading (or `title` in --fields-file)")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD (default: today)")
    parser.add_argument(
        "--status",
        default="draft",
        choices=goal_lib.VALID_STATUSES,
        help="Lifecycle status; new artifacts default to draft and only activate when the user runs /goal @file",
    )
    parser.add_argument(
        "--fields-file",
        type=Path,
        help="JSON object of field -> text (keys: " + ", ".join(_PROSE_FIELDS) + "). PREFER THIS "
        "for a real goal body: an argument carrying backticks is expanded by the shell before "
        "this program starts, so the `## Goal` section -- the first thing a fresh session reads "
        "to learn what the goal IS -- is written with words silently missing and the run still "
        "reports `created`. Per-field flags override the file.",
    )
    parser.add_argument("--goal-body", default=None, help="Initial goal statement inserted under the Goal section on creation (or `goal-body` in --fields-file)")
    return parser.parse_args()


def _merge_field(flag_value: str | None, from_file: dict[str, str], key: str) -> str:
    """One prose field from the flag, else the file. An EMPTY flag never wins.

    `None` (flag absent) means "not given" rather than "empty", so an unpassed flag
    cannot blank a file value. The remaining hole was the flag PRESENT and empty:
    `--goal-body "$(cat body.txt)"` where the substitution yields nothing hands argv
    `--goal-body ""`, which is not None, so it overrode the file and the artifact was
    created with the scaffold placeholder under `"action": "created"`. That is this
    helper's own total-loss shape -- the one `_resolve_slug` exists to close -- landing
    on the very field the channel was built to protect. An empty override of a
    non-empty file value is not intent; it is the damage signature.
    """
    if flag_value is None:
        return from_file.get(key, "")
    if not flag_value.strip() and from_file.get(key, "").strip():
        raise SystemExit(
            f"--{key} was passed empty while --fields-file supplies a non-empty `{key}`. "
            f"An empty argument is what a failed shell substitution looks like, so this "
            f"refuses rather than discarding the file's value. Drop the flag to use the file."
        )
    return flag_value


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.expanduser().resolve()
    slug = _resolve_slug(args.slug)
    from_file = _load_fields_file(args.fields_file) if args.fields_file else {}
    title = _normalize_newlines(_merge_field(args.title, from_file, "title"))
    goal_body = _normalize_newlines(_merge_field(args.goal_body, from_file, "goal-body"))
    try:
        path = goal_lib.goal_path(repo_root, args.date, slug)
    except ValueError as exc:
        print(str(exc))
        return 2
    if path.exists():
        # `upsert_goal` never overwrites an existing title or body -- correct, and the
        # reason a goal's prose is safe from a re-run. But it dropped supplied values in
        # SILENCE under `"action": "updated"`, and this slice makes that far likelier by
        # telling callers to author both fields in a file and re-run the same command.
        #
        # Only a value that would CHANGE the artifact refuses. A re-run carrying the same
        # prose is the documented idempotent bootstrap ("scaffold or locate"), and turning
        # that into an error would make the helper's own first-listed command fail on
        # every invocation after the first.
        existing = path.read_text(encoding="utf-8")
        if changed := [
            key for key, value in (("title", title), ("goal-body", goal_body))
            if value.strip() and value.strip() not in existing
        ]:
            raise SystemExit(
                f"refusing to discard {' and '.join(f'`{key}`' for key in changed)}: "
                f"{goal_lib.goal_rel(repo_root, path)} already exists, and an existing artifact's "
                "heading and `## Goal` section are never rewritten. Edit the file directly, or drop "
                "the field to change only --status."
            )
        # The shape guards below police what gets WRITTEN. Nothing here is written, so
        # applying them would refuse a status flip over a value the artifact already
        # carries -- and would report a shape error where the real answer is "ignored".
    else:
        # A title is needed to CREATE an artifact and is ignored when updating one, so
        # requiring it on a status flip only forced every caller (and every doc example)
        # to re-type prose into a shell for a value nothing reads.
        if not title.strip():
            raise SystemExit("goal title is empty; a new artifact needs --title or a non-empty `title` in --fields-file")
        _reject_unwritable_prose(title, goal_body)
    try:
        result = goal_lib.upsert_goal(
            repo_root,
            date=args.date,
            slug=slug,
            title=title,
            status=args.status,
            goal_body=goal_body,
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result.get("action") == "refused" else 0


if __name__ == "__main__":
    raise SystemExit(main())
