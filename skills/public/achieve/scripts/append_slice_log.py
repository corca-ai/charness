#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
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

_FIELD_FLAGS = (
    ("objective", "Objective"),
    ("why", "Why this approach"),
    ("commits", "Commits"),
    ("changed", "What changed"),
    ("alternatives", "Alternatives rejected"),
    ("verification", "Targeted verification"),
    ("test-pressure", "Test duplication pressure"),
    ("critique", "Critique"),
    ("off-goal", "Off-goal findings"),
    ("lessons", "Lessons carried forward"),
    ("metrics", "Metrics"),
)


def _load_fields_file(path: Path) -> dict[str, str]:
    """Read every slice field from ONE JSON file, so no prose crosses a shell.

    The parse, the duplicate-key refusal, the unknown-key refusal and the type check
    are `goal_cli_args.load_fields_file`, shared with `upsert_goal.py`. What stays
    here is the one rule that is genuinely slice-log-specific: a slice field renders
    as a single `- <label>: <value>` list item, so it must be one line.
    """
    raw = goal_cli.load_fields_file(path, known={flag for flag, _ in _FIELD_FLAGS} | {"name"})
    # A JSON report makes multi-line prose easy where a shell argument made it awkward,
    # and the renderer writes `- <label>: <value>` verbatim. A value carrying a line
    # that starts `### Slice` or `## ` becomes a heading the caller never wrote, which
    # `next_slice_number` and the section checks then read as real -- record corruption
    # under an `appended` verdict, the class this whole helper is being repaired for.
    if multiline := sorted(key for key, value in raw.items() if "\n" in value):
        raise SystemExit(
            f"--fields-file values must be single-line; these contain newlines: "
            f"{', '.join(multiline)}. A line beginning `## ` or `### Slice` would be "
            f"read back as a real heading. Write the value as one line."
        )
    return raw


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append one slice report to a goal artifact's Slice Log.")
    goal_cli.add_goal_target_args(parser)
    parser.add_argument("--name", help="Short slice name for the slice heading (or `name` in --fields-file)")
    parser.add_argument(
        "--fields-file",
        type=Path,
        help="JSON object of field -> text (keys: name, "
        + ", ".join(flag for flag, _ in _FIELD_FLAGS)
        + "). PREFER THIS for real slice prose: an argument carrying backticks is "
        "expanded by the shell before this program starts, so the text arrives with "
        "words silently missing and the run still reports `appended`. Per-field flags "
        "override the file.",
    )
    for flag, label in _FIELD_FLAGS:
        parser.add_argument(f"--{flag}", default=None, help=f"Slice report value for '{label}'")
    args = parser.parse_args()
    if args.name is None and args.fields_file is None:
        parser.error("provide --name, or --fields-file carrying a `name` key")
    return args


def main() -> int:
    args = parse_args()
    path = goal_cli.resolve_goal_path(args, goal_lib)
    if not path.exists():
        raise SystemExit(f"goal artifact not found: {path}")
    text = path.read_text(encoding="utf-8")
    number = goal_lib.next_slice_number(text)
    from_file = _load_fields_file(args.fields_file) if args.fields_file else {}
    # A per-field flag overrides the file, and `None` (flag absent) means "not given"
    # rather than "empty" -- otherwise every unpassed flag would blank a file value.
    fields = {
        label: (value if (value := getattr(args, flag.replace("-", "_"))) is not None else from_file.get(flag, ""))
        for flag, label in _FIELD_FLAGS
    }
    name = args.name if args.name is not None else from_file.get("name", "")
    if not name.strip():
        raise SystemExit("slice name is empty; pass --name or a non-empty `name` in --fields-file")
    block = goal_lib.render_slice_block(number, name, fields)
    updated = goal_lib.append_slice(text, block)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
    print(json.dumps({"action": "appended", "slice": number, "path": str(path)}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
