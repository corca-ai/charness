#!/usr/bin/env python3

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from statistics import median
from typing import Any, Callable


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import load_path_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

# `unestablished` is the runner's third status: a gate that ran and judged no
# scope. It was rejected here, so the sample was dropped and every affected run
# printed "failed to record phase runtimes" -- a permanent telemetry hole in
# exactly the gates the status was added for.
VALID_STATUSES = ("pass", "fail", "unestablished")

REPO_ROOT = repo_root_from_script(__file__)


def _quality_script_path(repo_root: Path, filename: str) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / filename,
        repo_root / "skills" / "quality" / "scripts" / filename,
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"quality {filename} not found")


_quality_resolve_adapter = load_path_module(
    "quality_resolve_adapter", _quality_script_path(REPO_ROOT, "resolve_adapter.py")
)
load_adapter = _quality_resolve_adapter.load_adapter

# The profile id is a CONTRACT between this recorder and `check_runtime_budget`:
# whatever id gets written here is the id the budget gate later looks budgets up
# under. Two copies of that derivation is one copy too many -- the affinity fix
# had to be made twice, in lockstep, or the writer and the reader would disagree
# about which machine a sample came from. The skill lib owns it; this consumes it.
_runtime_profile_lib = load_path_module(
    "quality_runtime_profile_lib", _quality_script_path(REPO_ROOT, "runtime_profile_lib.py")
)
usable_cpu_count = _runtime_profile_lib.usable_cpu_count
machine_runtime_profile = _runtime_profile_lib.machine_runtime_profile
regime_scoped_profile = _runtime_profile_lib.regime_scoped_profile

SUMMARY_FILENAME = "runtime-signals.json"
SMOOTHING_FILENAME = "runtime-smoothing.json"
ARCHIVE_PREFIX = "runtime-signals-"
MAX_RECENT_SAMPLES = 20
MAX_ARCHIVE_FILES = 12
STATE_DIR = Path(".charness") / "quality"
SMOOTHING_ALPHA_BASE = 0.35
SMOOTHING_WARMUP_N = 5
DEFAULT_RUNTIME_PROFILE = "default"
RUNTIME_PROFILE_ID_RE = re.compile(r"[^A-Za-z0-9_.-]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument(
        "--state-root",
        type=Path,
        help="External runtime-state directory; defaults to <repo>/.charness/quality.",
    )
    parser.add_argument("--label")
    parser.add_argument("--elapsed-ms", type=int)
    parser.add_argument("--status", choices=VALID_STATUSES)
    parser.add_argument("--timestamp")
    parser.add_argument(
        "--batch",
        type=Path,
        help=(
            "JSONL file of {label, elapsed_ms, status, timestamp} records applied in order "
            "in one process. Same resulting state as one --label call per record, without "
            "paying an interpreter start and a full summary rewrite per gate."
        ),
    )
    parser.add_argument(
        "--runtime-profile",
        default=os.environ.get("CHARNESS_RUNTIME_PROFILE"),
        help="Named machine/runner profile for runtime samples. Defaults to a fast local machine profile.",
    )
    parser.add_argument(
        "--runtime-regime",
        default=os.environ.get("CHARNESS_RUNTIME_REGIME"),
        help=(
            "Gate-set regime these samples were taken under (e.g. `docs-only`, `filtered`). "
            "Scopes them into `<profile>.<regime>` so a subset run's cheaper timings never "
            "enter the window the full-queue budgets are enforced against."
        ),
    )
    args = parser.parse_args()
    if args.batch is None:
        missing = [
            name
            for name, value in (("--label", args.label), ("--elapsed-ms", args.elapsed_ms), ("--status", args.status))
            if value is None
        ]
        if missing:
            parser.error(f"the following arguments are required: {', '.join(missing)}")
    elif args.label is not None or args.elapsed_ms is not None or args.status is not None or args.timestamp is not None:
        parser.error("--batch cannot be combined with --label/--elapsed-ms/--status/--timestamp")
    return args


def _read_batch_line(line: str) -> dict[str, Any]:
    """Validate one batch line, raising ValueError with the reason if it is bad."""
    parsed = json.loads(line)
    if not isinstance(parsed, dict):
        raise ValueError("not a JSON object")
    missing = [key for key in ("label", "elapsed_ms", "status") if key not in parsed]
    if missing:
        raise ValueError(f"missing {', '.join(missing)}")
    if parsed["status"] not in VALID_STATUSES:
        raise ValueError(f"status {parsed['status']!r}; expected one of {', '.join(VALID_STATUSES)}")
    return {
        "label": str(parsed["label"]),
        "elapsed_ms": int(parsed["elapsed_ms"]),
        "status": parsed["status"],
        "timestamp": parsed.get("timestamp"),
    }


def load_batch_records(batch_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """Parse the runner-written batch file, reporting every malformed line.

    The producer is `run-quality.sh`, not a human, so a bad line means the runner
    broke and must be reported loudly. It must NOT cost the whole phase's samples
    though: one killed gate subshell emitting a truncated line would otherwise
    discard every other gate's sample for that phase and leave `check-runtime-budget`
    silently grading a stale store. Good records are applied; the caller still exits
    nonzero with the errors.
    """
    try:
        raw_lines = batch_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise SystemExit(f"runtime batch {batch_path} is unreadable: {exc}") from exc

    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for line_number, line in enumerate(raw_lines, start=1):
        if not line.strip():
            continue
        try:
            records.append(_read_batch_line(line))
        except (ValueError, TypeError) as exc:
            errors.append(f"runtime batch {batch_path} line {line_number} is malformed: {exc}")
    return records, errors


def normalize_runtime_profile(value: str | None) -> str:
    profile = (value or DEFAULT_RUNTIME_PROFILE).strip()
    if not profile:
        raise ValueError("runtime profile must be a non-empty string")
    return profile


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
        # missing_ok: a concurrent recorder may have already rotated this
        # archive away between our glob and this unlink; that must not fail
        # the recorder run.
        oldest.unlink(missing_ok=True)


def _update_commands(commands: dict[str, Any], record: dict[str, Any]) -> None:
    label = record["label"]
    current = commands.get(label, {})
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

    commands[label] = {
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


def update_store(
    store_path: Path,
    records: list[dict[str, Any]],
    empty_store: dict[str, Any],
    apply_record: Callable[[dict[str, Any], dict[str, Any]], None],
) -> None:
    """Apply records in order against one load/store of a runtime state file.

    Read-apply-write per record is what made this recorder cost ~70ms a gate; the
    per-record apply is unchanged, so a batch leaves the same state as the same
    records applied one process at a time. The summary and the smoothing store
    differ only in their empty document and their per-command apply.
    """
    if not records:
        return

    store = load_json(store_path)
    if not store:
        # deepcopy, not dict(): the loop below mutates the nested `commands`/
        # `profiles` dicts, and a shallow copy would write through into the
        # caller's literal — harmless only while both callers rebuild it per call.
        store = copy.deepcopy(empty_store)

    for record in records:
        profile_id = record["runtime_profile"]
        profiles = store.setdefault("profiles", {})
        profile_entry = profiles.setdefault(profile_id, {"commands": {}})
        apply_record(profile_entry.setdefault("commands", {}), record)
        profile_entry["updated_at"] = record["timestamp"]
        if profile_id == DEFAULT_RUNTIME_PROFILE:
            apply_record(store.setdefault("commands", {}), record)
        store["updated_at"] = record["timestamp"]
    store_path.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_summary(summary_path: Path, records: list[dict[str, Any]]) -> None:
    update_store(
        summary_path,
        records,
        {"schema_version": 2, "updated_at": None, "commands": {}, "profiles": {}},
        _update_commands,
    )


def adaptive_alpha(sample_count: int) -> float:
    warmup_ratio = min(1.0, sample_count / SMOOTHING_WARMUP_N)
    return SMOOTHING_ALPHA_BASE * warmup_ratio


def _update_smoothing_commands(commands: dict[str, Any], record: dict[str, Any]) -> None:
    label = record["label"]
    current = commands.get(label, {})
    samples = int(current.get("samples", 0)) + 1
    alpha = adaptive_alpha(samples)
    elapsed = int(record["elapsed_ms"])
    previous_ewma = current.get("ewma_elapsed_ms")
    if isinstance(previous_ewma, (int, float)):
        ewma = float(previous_ewma) + alpha * (elapsed - float(previous_ewma))
    else:
        ewma = float(elapsed)

    commands[label] = {
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


def update_smoothing(smoothing_path: Path, records: list[dict[str, Any]]) -> None:
    update_store(
        smoothing_path,
        records,
        {
            "schema_version": 2,
            "updated_at": None,
            "policy": {
                "kind": "ewma",
                "advisory": True,
                "alpha_base": SMOOTHING_ALPHA_BASE,
                "warmup_n": SMOOTHING_WARMUP_N,
            },
            "commands": {},
            "profiles": {},
        },
        _update_smoothing_commands,
    )


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
    state_dir = args.state_root.resolve() if args.state_root else repo_root / STATE_DIR
    if args.state_root and (state_dir == repo_root or repo_root in state_dir.parents):
        raise SystemExit("--state-root must be outside --repo-root")
    state_dir.mkdir(parents=True, exist_ok=True)

    try:
        runtime_profile = regime_scoped_profile(
            normalize_runtime_profile(args.runtime_profile or machine_runtime_profile()),
            args.runtime_regime,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    batch_errors: list[str] = []
    if args.batch is not None:
        pending, batch_errors = load_batch_records(args.batch)
    else:
        pending = [
            {
                "label": args.label,
                "elapsed_ms": args.elapsed_ms,
                "status": args.status,
                "timestamp": args.timestamp,
            }
        ]

    records = [
        {
            "timestamp": parse_timestamp(item["timestamp"]).isoformat().replace("+00:00", "Z"),
            "label": item["label"],
            "elapsed_ms": item["elapsed_ms"],
            "status": item["status"],
            "runtime_profile": runtime_profile,
        }
        for item in pending
    ]

    summary_path = state_dir / SUMMARY_FILENAME
    smoothing_path = state_dir / SMOOTHING_FILENAME
    archive_paths = [append_archive(state_dir / "history", record) for record in records]
    update_summary(summary_path, records)
    update_smoothing(smoothing_path, records)
    def rendered_path(path: Path) -> str:
        try:
            return str(path.relative_to(repo_root))
        except ValueError:
            return str(path)

    payload: dict[str, Any] = {
        "summary_path": rendered_path(summary_path),
        "smoothing_path": rendered_path(smoothing_path),
    }
    if args.batch is not None:
        payload["archive_paths"] = sorted({rendered_path(path) for path in archive_paths})
        payload["recorded_count"] = len(records)
        payload["malformed_lines"] = batch_errors
    else:
        payload["archive_path"] = rendered_path(archive_paths[0])
        payload["recorded"] = records[0]
    # Receipt only. The runtime signals themselves live under the selected state
    # directory, which task-owned runs place outside the checkout.
    emit_yaml(payload)
    if batch_errors:
        # The good records above are already applied; this exit only reports the
        # runner bug that produced the bad ones.
        for error in batch_errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
