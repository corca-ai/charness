#!/usr/bin/env python3

"""Symlink-safe writer for gather dated records and the current pointer.

Resolves the gather adapter, writes a fresh dated canonical record under
`<output_dir>/<YYYY-MM-DD>-<slug>.md`, then safely refreshes the current
pointer (`latest.md`) via the lstat-aware helper in `gather_writer_lib`
so a writer that hits a symlinked pointer never silently follows the
link and clobbers an unrelated dated record. The refresh is
unlink-then-write rather than strictly POSIX-atomic; gather's read-mostly
workload tolerates the small window. See corca-ai/charness#138.

Idempotent on the dated path: if a dated record with the same slug+date
already exists, the script refuses to overwrite. Use a different slug or
update the prior record manually with the same lstat-aware care.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "skill_runtime_bootstrap", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gather_writer_lib as wlib  # noqa: E402
import resolve_adapter as gather_adapter  # noqa: E402


def _resolve_output_dir(repo_root: Path) -> Path:
    payload = gather_adapter.load_adapter(repo_root)
    data = payload.get("data") or {}
    output_dir = data.get("output_dir")
    if not isinstance(output_dir, str):
        raise wlib.WriteError("gather adapter did not declare output_dir")
    return (repo_root / output_dir).resolve()


def _read_content(path: Path | None) -> str:
    if path is None:
        return sys.stdin.read()
    if not path.is_file():
        raise wlib.WriteError(f"--content-file {path} does not exist or is not a file")
    return path.read_text(encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--slug", required=True, help="lowercase slug for the dated record")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD (default: today UTC)")
    parser.add_argument(
        "--content-file",
        type=Path,
        default=None,
        help="path to the record content (defaults to stdin)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="write the dated record and refresh the pointer (otherwise dry-run)",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()
    root = args.repo_root.resolve()
    wlib.validate_slug(args.slug)
    date = args.date or wlib.today_iso()
    wlib.validate_date(date)
    output_dir = _resolve_output_dir(root)
    record_path = wlib.compute_record_path(output_dir, date, args.slug)
    payload: dict[str, Any] = {
        "repo_root": str(root),
        "slug": args.slug,
        "date": date,
        "output_dir": str(output_dir),
        "record_artifact_path": str(record_path),
        "current_pointer_path": str(output_dir / "latest.md"),
        "execute": args.execute,
        "would_write": True,
    }
    if record_path.exists():
        payload["status"] = "blocked"
        payload["reason"] = "dated record already exists; choose a different slug or date"
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 1
    content = _read_content(args.content_file)
    if not args.execute:
        payload["status"] = "planned"
        payload["content_bytes"] = len(content.encode("utf-8"))
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path.write_text(content, encoding="utf-8")
    payload["wrote_record"] = True
    pointer_path = output_dir / "latest.md"
    refresh = wlib.refresh_current_pointer(
        pointer_path, record_path, output_dir, execute=True
    )
    payload["pointer_refresh"] = refresh
    payload["status"] = "updated" if refresh.get("status") in {"updated", "noop"} else "partial"
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if payload["status"] != "partial" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except wlib.WriteError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
