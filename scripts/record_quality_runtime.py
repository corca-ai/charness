#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
_RESOLVER_DIR = REPO_ROOT / "skills" / "public" / "quality" / "scripts"
if not _RESOLVER_DIR.is_dir():
    _RESOLVER_DIR = REPO_ROOT / "skills" / "quality" / "scripts"
sys.path[:0] = [str(_RESOLVER_DIR), str(REPO_ROOT)]

from resolve_adapter import load_adapter

SUMMARY_FILENAME = "runtime-signals.json"
ARCHIVE_PREFIX = "runtime-signals-"
MAX_RECENT_SAMPLES = 20
MAX_ARCHIVE_FILES = 12
STATE_DIR = Path(".charness") / "quality"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--label", required=True)
    parser.add_argument("--elapsed-ms", type=int, required=True)
    parser.add_argument("--status", choices=("pass", "fail"), required=True)
    parser.add_argument("--timestamp")
    return parser.parse_args()


def parse_timestamp(value: str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_recent(recent: list[dict[str, Any]]) -> dict[str, Any]:
    elapsed_values = [int(item["elapsed_ms"]) for item in recent]
    return {
        "recent_samples": len(recent),
        "median_recent_elapsed_ms": int(median(elapsed_values)),
        "min_recent_elapsed_ms": min(elapsed_values),
        "max_recent_elapsed_ms": max(elapsed_values),
    }


def rotate_archives(history_dir: Path) -> None:
    archives = sorted(history_dir.glob(f"{ARCHIVE_PREFIX}*.jsonl"))
    while len(archives) > MAX_ARCHIVE_FILES:
        oldest = archives.pop(0)
        oldest.unlink()


def update_summary(summary_path: Path, record: dict[str, Any]) -> None:
    summary = load_json(summary_path)
    if not summary:
        summary = {
            "schema_version": 1,
            "updated_at": record["timestamp"],
            "commands": {},
        }

    commands = summary.setdefault("commands", {})
    current = commands.get(record["label"], {})
    recent = list(current.get("recent", []))
    recent.append(
        {
            "timestamp": record["timestamp"],
            "elapsed_ms": record["elapsed_ms"],
            "status": record["status"],
        }
    )
    recent = recent[-MAX_RECENT_SAMPLES:]

    passes = int(current.get("passes", 0)) + (1 if record["status"] == "pass" else 0)
    failures = int(current.get("failures", 0)) + (1 if record["status"] == "fail" else 0)
    samples = int(current.get("samples", 0)) + 1

    commands[record["label"]] = {
        "samples": samples,
        "passes": passes,
        "failures": failures,
        "latest": {
            "timestamp": record["timestamp"],
            "elapsed_ms": record["elapsed_ms"],
            "status": record["status"],
        },
        "recent": recent,
        **summarize_recent(recent),
    }
    summary["updated_at"] = record["timestamp"]
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_archive(history_dir: Path, record: dict[str, Any]) -> Path:
    history_dir.mkdir(parents=True, exist_ok=True)
    month_id = record["timestamp"][:7]
    archive_path = history_dir / f"{ARCHIVE_PREFIX}{month_id}.jsonl"
    with archive_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    rotate_archives(history_dir)
    return archive_path


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    load_adapter(repo_root)
    state_dir = repo_root / STATE_DIR
    state_dir.mkdir(parents=True, exist_ok=True)

    timestamp = parse_timestamp(args.timestamp).isoformat().replace("+00:00", "Z")
    record = {
        "timestamp": timestamp,
        "label": args.label,
        "elapsed_ms": args.elapsed_ms,
        "status": args.status,
    }

    summary_path = state_dir / SUMMARY_FILENAME
    archive_path = append_archive(state_dir / "history", record)
    update_summary(summary_path, record)
    print(
        json.dumps(
            {
                "summary_path": str(summary_path.relative_to(repo_root)),
                "archive_path": str(archive_path.relative_to(repo_root)),
                "recorded": record,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
