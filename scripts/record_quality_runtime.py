#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any

from runtime_bootstrap import load_path_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)


def _resolver_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "resolve_adapter.py",
        repo_root / "skills" / "quality" / "scripts" / "resolve_adapter.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("quality resolve_adapter.py not found")


_quality_resolve_adapter = load_path_module("quality_resolve_adapter", _resolver_path(REPO_ROOT))
load_adapter = _quality_resolve_adapter.load_adapter

SUMMARY_FILENAME = "runtime-signals.json"
SMOOTHING_FILENAME = "runtime-smoothing.json"
ARCHIVE_PREFIX = "runtime-signals-"
MAX_RECENT_SAMPLES = 20
MAX_ARCHIVE_FILES = 12
STATE_DIR = Path(".charness") / "quality"
SMOOTHING_ALPHA_BASE = 0.35
SMOOTHING_WARMUP_N = 5


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


def adaptive_alpha(sample_count: int) -> float:
    warmup_ratio = min(1.0, sample_count / SMOOTHING_WARMUP_N)
    return SMOOTHING_ALPHA_BASE * warmup_ratio


def update_smoothing(smoothing_path: Path, record: dict[str, Any]) -> None:
    smoothing = load_json(smoothing_path)
    if not smoothing:
        smoothing = {
            "schema_version": 1,
            "updated_at": record["timestamp"],
            "policy": {
                "kind": "ewma",
                "advisory": True,
                "alpha_base": SMOOTHING_ALPHA_BASE,
                "warmup_n": SMOOTHING_WARMUP_N,
            },
            "commands": {},
        }

    commands = smoothing.setdefault("commands", {})
    current = commands.get(record["label"], {})
    samples = int(current.get("samples", 0)) + 1
    alpha = adaptive_alpha(samples)
    elapsed = int(record["elapsed_ms"])
    previous_ewma = current.get("ewma_elapsed_ms")
    if isinstance(previous_ewma, (int, float)):
        ewma = float(previous_ewma) + alpha * (elapsed - float(previous_ewma))
    else:
        ewma = float(elapsed)

    commands[record["label"]] = {
        "samples": samples,
        "latest": {
            "timestamp": record["timestamp"],
            "elapsed_ms": elapsed,
            "status": record["status"],
        },
        "ewma_elapsed_ms": round(ewma, 2),
        "alpha_last": round(alpha, 4),
        "alpha_base": SMOOTHING_ALPHA_BASE,
        "warmup_n": SMOOTHING_WARMUP_N,
        "advisory": True,
    }
    smoothing["updated_at"] = record["timestamp"]
    smoothing_path.write_text(json.dumps(smoothing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


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
    smoothing_path = state_dir / SMOOTHING_FILENAME
    archive_path = append_archive(state_dir / "history", record)
    update_summary(summary_path, record)
    update_smoothing(smoothing_path, record)
    print(
        json.dumps(
            {
                "summary_path": str(summary_path.relative_to(repo_root)),
                "smoothing_path": str(smoothing_path.relative_to(repo_root)),
                "archive_path": str(archive_path.relative_to(repo_root)),
                "recorded": record,
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
