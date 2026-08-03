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

    The lossy channel this closes is in front of ``argv`` and cannot be seen from
    inside the process. A slice report cites identifiers, so the prose is full of
    backticks; passed as a shell argument, the shell performs command substitution
    BEFORE this program starts, and what arrives is well-formed text with words
    missing. Exit 0, ``"action": "appended"``, and a durable record with holes in it
    -- which is the surface a compacted or resumed session reads to learn what
    happened. No validation here could ever have detected it: there is nothing left
    to compare against.

    A file has no such layer. The caller writes the JSON with its own file tool (or
    a heredoc it controls), and the bytes on disk are the bytes this reads.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"--fields-file unreadable: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--fields-file is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise SystemExit("--fields-file must contain a JSON object of field -> text")
    known = {flag for flag, _ in _FIELD_FLAGS} | {"name"}
    # REFUSE an unknown key rather than ignoring it. A typo'd field name in a file the
    # caller cannot see the effect of is the same silent-loss shape this flag exists to
    # remove: the run would report `appended` over a record missing that field.
    if unknown := sorted(set(raw) - known):
        raise SystemExit(f"--fields-file has unknown field(s): {', '.join(unknown)}; known: {', '.join(sorted(known))}")
    if bad := sorted(key for key, value in raw.items() if not isinstance(value, str)):
        raise SystemExit(f"--fields-file values must be strings; not strings: {', '.join(bad)}")
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
