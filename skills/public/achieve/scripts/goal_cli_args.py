"""The goal-locating CLI surface every achieve helper shares, and the no-shell
prose channel they share with it.

`--repo-root / --goal-path / --slug / --date` and the resolution rule behind them
were written out per script. Two copies is where a rule starts drifting: one script
learning a new selector, or a changed refusal message, silently makes the two
disagree about which file "the goal" means. This is the one statement.

`load_fields_file` is here for the same reason and was extracted the moment a
SECOND helper needed it. Its refusals are the whole value of the channel -- the
caller wrote that JSON blind, so a message it cannot act on is a message it works
around -- and two drifting copies of "what this file may contain" would put one
helper's silent-loss guard in front of one helper only.

It lives beside the helpers rather than in `goal_artifact_lib` because `SystemExit`
and `argparse` are CLI concerns; the library stays importable by anything.
"""
from __future__ import annotations

import argparse
import json
from datetime import date as date_cls
from pathlib import Path


def add_goal_target_args(parser: argparse.ArgumentParser) -> None:
    """The four flags that name a goal artifact.

    Used by `append_slice_log.py` and `check_goal_artifact.py`, which had a copy each.
    NOT by every achieve helper -- `normalize_goal_closeout.py` and
    `record_metric_window.py` still declare their own `--goal-path`, and saying
    "identically in every helper" here would assert a reach this does not have.
    """
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root that owns charness-artifacts/goals/")
    parser.add_argument("--goal-path", type=Path, help="Explicit path to the goal artifact (overrides --slug/--date)")
    parser.add_argument("--slug", help="Goal slug, used with --date to locate the artifact")
    parser.add_argument("--date", default=date_cls.today().isoformat(), help="Goal date prefix YYYY-MM-DD used with --slug")


def resolve_goal_path(args, goal_lib) -> Path:
    """`--goal-path` wins; otherwise `--slug` + `--date`. Refuses rather than guessing.

    ``goal_lib`` is injected so this module stays free of the library's import cost
    and its callers keep loading it their own way.
    """
    if args.goal_path is not None:
        return args.goal_path.expanduser().resolve()
    repo_root = args.repo_root.expanduser().resolve()
    if not (args.slug and args.date):
        raise SystemExit("provide --goal-path, or both --slug and --date")
    try:
        return goal_lib.goal_path(repo_root, args.date, args.slug)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def load_fields_file(path: Path, *, known: set[str], flag: str = "--fields-file") -> dict[str, str]:
    """Read a helper's prose fields from ONE JSON file, so no prose crosses a shell.

    The lossy channel this closes is in front of ``argv`` and cannot be seen from
    inside the process. Goal and slice prose cites identifiers, so it is full of
    backticks; passed as a shell argument, the shell performs command substitution
    BEFORE the program starts, and what arrives is well-formed text with words
    missing. Exit 0, a success verdict, and a durable artifact with holes in it --
    which is the surface a compacted or resumed session reads to learn what the work
    IS. No validation here could ever have detected it: there is nothing left to
    compare against.

    A file has no such layer. The caller writes the JSON with its own file tool (or
    a heredoc it controls), and the bytes on disk are the bytes this reads.

    Returns the raw field -> text mapping. Per-field SHAPE rules (single-line, no
    heading) stay with the caller, because they differ: a slice-log value is one
    rendered list item, while a goal body is a whole markdown section.
    """
    def _no_duplicate_keys(pairs):
        # `json.loads` is LAST-WINS on a repeated key, which is this channel's own
        # defect inside its own repair: a long hand-written file with `changed` twice
        # would write a record missing one of them and report success. Undetectable
        # from inside, exactly like the shell was.
        seen = [key for key, _ in pairs]
        if repeated := sorted({key for key in seen if seen.count(key) > 1}):
            raise SystemExit(f"{flag} repeats field(s): {', '.join(repeated)}; each may appear once")
        return dict(pairs)

    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)
    except OSError as exc:
        raise SystemExit(f"{flag} unreadable: {exc}") from exc
    except UnicodeDecodeError as exc:
        # Caught by name, not by `ValueError`: `json.JSONDecodeError` is also a
        # ValueError, and a bare `except ValueError` would swallow the duplicate-key
        # SystemExit's sibling paths under one message. A non-UTF-8 file used to
        # escape as a traceback, which is the one refusal that did not name its cause.
        raise SystemExit(f"{flag} is not UTF-8: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"{flag} is not valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise SystemExit(f"{flag} must contain a JSON object of field -> text")
    # REFUSE an unknown key rather than ignoring it. A typo'd field name in a file the
    # caller cannot see the effect of is the same silent-loss shape this flag exists to
    # remove: the run would report success over an artifact missing that field.
    if unknown := sorted(set(raw) - known):
        raise SystemExit(f"{flag} has unknown field(s): {', '.join(unknown)}; known: {', '.join(sorted(known))}")
    if bad := sorted(key for key, value in raw.items() if not isinstance(value, str)):
        raise SystemExit(f"{flag} values must be strings; not strings: {', '.join(bad)}")
    return raw
