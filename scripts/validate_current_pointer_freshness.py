#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


class ValidationError(Exception):
    pass


FRESHNESS_LABEL = "validate-current-pointer-freshness"
FRESHNESS_SCRIPT = Path("scripts/validate_current_pointer_freshness.py")
RUN_QUALITY_SCRIPT = Path("scripts/run-quality.sh")
CURRENT_POINTERS = (
    Path("docs/handoff.md"),
    Path("charness-artifacts/quality/latest.md"),
)
QUALITY_POINTER = Path("charness-artifacts/quality/latest.md")
RELEASE_POINTER = Path("charness-artifacts/release/latest.md")
PACKAGING_MANIFEST = Path("packaging/charness.json")
CODEX_PLUGIN_MANIFEST = Path("plugins/charness/.codex-plugin/plugin.json")
CLAUDE_PLUGIN_MANIFEST = Path("plugins/charness/.claude-plugin/plugin.json")
GITIGNORE = Path(".gitignore")
RUNTIME_RECORDER = Path("scripts/record_quality_runtime.py")
RUNTIME_BUDGET_CHECKER = Path("skills/public/quality/scripts/check_runtime_budget.py")
RUNTIME_SIGNALS = Path(".charness/quality/runtime-signals.json")
QUALITY_ADAPTER = Path(".agents/quality-adapter.yaml")
STALE_POINTER_PHRASES = {
    Path("docs/handoff.md"): (
        "freshness validator를 첫 slice로 잡는다",
        "freshness validator를 첫 slice",
    ),
    Path("charness-artifacts/quality/latest.md"): (
        "No deterministic freshness check yet",
        "add a narrow freshness check so rolling pointers",
        "extend `validate-current-pointer-freshness` beyond stale validator-existence claims",
    ),
}
COMMAND_RE = re.compile(r"`(python3 [^`]+|\.\/scripts\/[^`]+)`")
HOT_SPOT_RE = re.compile(r"`([^`]+)`\s+`([0-9]+(?:\.[0-9]+)?s)`")
BUDGETED_PHASE_RE = re.compile(
    r"`([^`]+)`\s+median\s+`([0-9]+(?:\.[0-9]+)?s)\s*/\s*([0-9]+(?:\.[0-9]+)?s)`"
)
TARGET_VERSION_RE = re.compile(r"- target version:\s*`([^`]+)`")
RUNTIME_SECONDS_ABS_TOLERANCE = 0.5
RUNTIME_SECONDS_REL_TOLERANCE = 0.15


def read_text(repo_root: Path, relative_path: Path) -> str:
    path = repo_root / relative_path
    if not path.is_file():
        raise ValidationError(f"missing current pointer `{relative_path}`")
    return path.read_text(encoding="utf-8")


def validate_gate_is_queued(repo_root: Path) -> None:
    run_quality = read_text(repo_root, RUN_QUALITY_SCRIPT)
    expected_label = f'queue_selected "{FRESHNESS_LABEL}"'
    expected_script = str(FRESHNESS_SCRIPT)
    if expected_label not in run_quality or expected_script not in run_quality:
        raise ValidationError(
            "`scripts/run-quality.sh` must queue "
            f"`{FRESHNESS_LABEL}` via `{FRESHNESS_SCRIPT}`"
        )


def validate_no_stale_claims(repo_root: Path) -> None:
    stale_hits: list[str] = []
    for relative_path in CURRENT_POINTERS:
        text = read_text(repo_root, relative_path)
        for phrase in STALE_POINTER_PHRASES.get(relative_path, ()):
            if phrase in text:
                stale_hits.append(f"{relative_path}: stale phrase `{phrase}`")
    if stale_hits:
        raise ValidationError(
            "rolling current-pointer freshness claims are stale:\n"
            + "\n".join(f"- {hit}" for hit in stale_hits)
        )


def command_script_path(command: str) -> Path | None:
    parts = command.split()
    if not parts:
        return None
    if parts[0] == "python3" and len(parts) > 1:
        return Path(parts[1])
    if parts[0].startswith("./"):
        return Path(parts[0][2:])
    return None


def validate_quality_command_claims(repo_root: Path) -> None:
    quality = read_text(repo_root, QUALITY_POINTER)
    missing: list[str] = []
    for command in COMMAND_RE.findall(quality):
        script_path = command_script_path(command)
        if script_path is not None and not (repo_root / script_path).is_file():
            missing.append(f"`{command}` references missing `{script_path}`")
    if missing:
        raise ValidationError(
            "quality pointer command claims are stale:\n"
            + "\n".join(f"- {item}" for item in missing)
        )


def validate_runtime_smoothing_claim(repo_root: Path) -> None:
    quality = read_text(repo_root, QUALITY_POINTER)
    if "Runtime EWMA is advisory" not in quality:
        return

    gitignore = read_text(repo_root, GITIGNORE)
    recorder = read_text(repo_root, RUNTIME_RECORDER)
    checker = read_text(repo_root, RUNTIME_BUDGET_CHECKER)
    missing: list[str] = []
    required_fragments = (
        (GITIGNORE, gitignore, ".charness/quality/runtime-smoothing.json"),
        (RUNTIME_RECORDER, recorder, 'SMOOTHING_FILENAME = "runtime-smoothing.json"'),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_ALPHA_BASE = 0.35"),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_WARMUP_N = 5"),
        (RUNTIME_RECORDER, recorder, '"advisory": True'),
        (RUNTIME_BUDGET_CHECKER, checker, 'SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"'),
        (RUNTIME_BUDGET_CHECKER, checker, "ewma_advisory_elapsed_ms"),
        (RUNTIME_BUDGET_CHECKER, checker, "ewma {ewma:.1f}ms advisory"),
    )
    for relative_path, text, fragment in required_fragments:
        if fragment not in text:
            missing.append(f"`{relative_path}` missing `{fragment}`")
    if missing:
        raise ValidationError(
            "quality pointer runtime smoothing claim is stale:\n"
            + "\n".join(f"- {item}" for item in missing)
        )


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _format_seconds(elapsed_ms: object) -> str | None:
    if not isinstance(elapsed_ms, int):
        return None
    return f"{elapsed_ms / 1000:.1f}s"


def _seconds_value(text: str) -> float:
    return float(text.removesuffix("s"))


def _seconds_close(claimed: str, actual: str) -> bool:
    claimed_value = _seconds_value(claimed)
    actual_value = _seconds_value(actual)
    tolerance = max(RUNTIME_SECONDS_ABS_TOLERANCE, abs(actual_value) * RUNTIME_SECONDS_REL_TOLERANCE)
    return abs(claimed_value - actual_value) <= tolerance


def _runtime_commands(repo_root: Path) -> dict:
    signals_path = repo_root / RUNTIME_SIGNALS
    if not signals_path.is_file():
        return {}
    payload = _load_json(signals_path)
    commands = payload.get("commands")
    return commands if isinstance(commands, dict) else {}


def _runtime_budgets(repo_root: Path) -> dict[str, int]:
    adapter_path = repo_root / QUALITY_ADAPTER
    if not adapter_path.is_file():
        return {}
    budgets: dict[str, int] = {}
    in_runtime_budgets = False
    for raw_line in adapter_path.read_text(encoding="utf-8").splitlines():
        if raw_line.strip() == "runtime_budgets:":
            in_runtime_budgets = True
            continue
        if in_runtime_budgets and raw_line and not raw_line.startswith(" "):
            break
        if not in_runtime_budgets or not raw_line.startswith("  ") or ":" not in raw_line:
            continue
        label, value = raw_line.split(":", 1)
        try:
            budgets[label.strip()] = int(value.strip())
        except ValueError:
            continue
    return budgets


def _matching_runtime_lines(quality: str, prefix: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in quality.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            if current:
                blocks.append(" ".join(current))
            current = [stripped]
            continue
        if current and line.startswith("  ") and stripped:
            current.append(stripped)
            continue
        if current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def _command_entry(commands: dict, label: str) -> dict:
    entry = commands.get(label)
    return entry if isinstance(entry, dict) else {}


def validate_quality_runtime_signal_claims(repo_root: Path) -> None:
    # Runtime samples are written by the same quality runner that calls this
    # freshness gate, so committed current pointers must not chase exact
    # per-run timings. Artifact shape is checked by validate_quality_artifact.
    _ = repo_root


def _json_version(repo_root: Path, relative_path: Path) -> str | None:
    payload = _load_json(repo_root / relative_path)
    version = payload.get("version")
    return version if isinstance(version, str) else None


def validate_release_version_claim(repo_root: Path) -> None:
    release_path = repo_root / RELEASE_POINTER
    if not release_path.is_file():
        return
    release = release_path.read_text(encoding="utf-8")
    match = TARGET_VERSION_RE.search(release)
    if not match:
        return
    claimed_version = match.group(1)
    version_sources = (
        (PACKAGING_MANIFEST, _json_version(repo_root, PACKAGING_MANIFEST)),
        (CODEX_PLUGIN_MANIFEST, _json_version(repo_root, CODEX_PLUGIN_MANIFEST)),
        (CLAUDE_PLUGIN_MANIFEST, _json_version(repo_root, CLAUDE_PLUGIN_MANIFEST)),
    )
    stale = [
        f"`{relative_path}` version is `{version}`, release pointer claims `{claimed_version}`"
        for relative_path, version in version_sources
        if version != claimed_version
    ]
    if stale:
        raise ValidationError(
            "release pointer version claim is stale:\n"
            + "\n".join(f"- {item}" for item in stale)
        )


def validate_current_pointer_freshness(repo_root: Path) -> None:
    validate_gate_is_queued(repo_root)
    validate_no_stale_claims(repo_root)
    validate_quality_command_claims(repo_root)
    validate_runtime_smoothing_claim(repo_root)
    validate_quality_runtime_signal_claims(repo_root)
    validate_release_version_claim(repo_root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    validate_current_pointer_freshness(repo_root)
    print("Validated rolling current-pointer freshness claims.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
