#!/usr/bin/env python3
"""Create or update the canonical planning-only Goal Draft."""
from __future__ import annotations

import argparse
import runpy
from datetime import date as date_cls
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
goal_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_artifact_lib")
goal_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "goal_cli_args")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")

_PROSE_FIELDS = ("title", "goal-body")


def _load_fields_file(path: Path) -> dict[str, str]:
    return goal_cli.load_fields_file(path, known=set(_PROSE_FIELDS))


def _normalize_newlines(value: str) -> str:
    return goal_lib.normalize_goal_text(value)


def _reject_unwritable_prose(title: str, goal_body: str) -> None:
    try:
        goal_lib.validate_goal_values(title, goal_body)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def _resolve_slug(slug: str) -> str:
    try:
        return goal_lib.resolve_supplied_slug(slug)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or update a planning-only achieve Goal Draft."
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root that owns charness-artifacts/goals/",
    )
    parser.add_argument("--slug", required=True, help="Short kebab-case goal slug")
    parser.add_argument(
        "--title",
        default=None,
        help="Human-readable title (or `title` in --fields-file)",
    )
    parser.add_argument(
        "--date",
        default=date_cls.today().isoformat(),
        help="Goal date prefix YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--fields-file",
        type=Path,
        help="JSON object containing the prose fields: title and goal-body",
    )
    parser.add_argument(
        "--goal-body",
        default=None,
        help="Goal statement (or `goal-body` in --fields-file)",
    )
    return parser.parse_args()


def _merge_field(flag_value: str | None, from_file: dict[str, str], key: str) -> str:
    if flag_value is None:
        return from_file.get(key, "")
    if not flag_value.strip() and from_file.get(key, "").strip():
        raise SystemExit(
            f"--{key} was passed empty while --fields-file supplies a non-empty `{key}`"
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
        if not path.exists() and not title.strip():
            raise ValueError("goal title is empty; a new planning record needs --title")
        _reject_unwritable_prose(title, goal_body)
        result = goal_lib.upsert_goal(
            repo_root,
            date=args.date,
            slug=slug,
            title=title,
            goal_body=goal_body,
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    yaml_output.emit_yaml(result)
    return 1 if result.get("action") == "refused" else 0


if __name__ == "__main__":
    raise SystemExit(main())
