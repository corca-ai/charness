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
RUNTIME_BUDGET_LIB = Path("skills/public/quality/scripts/runtime_budget_lib.py")
RUNTIME_SIGNALS = Path(".charness/quality/runtime-signals.json")
FIND_SKILLS_INVENTORY = Path("charness-artifacts/find-skills/latest.json")
INTEGRATIONS_DIR = Path("integrations/tools")
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
TARGET_VERSION_RE = re.compile(r"- target version:\s*`([^`]+)`")


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
    runtime_budget_sources = checker
    runtime_budget_lib = repo_root / RUNTIME_BUDGET_LIB
    if runtime_budget_lib.is_file():
        runtime_budget_sources += "\n" + runtime_budget_lib.read_text(encoding="utf-8")
    missing: list[str] = []
    required_fragments = (
        (GITIGNORE, gitignore, ".charness/quality/runtime-smoothing.json"),
        (RUNTIME_RECORDER, recorder, 'SMOOTHING_FILENAME = "runtime-smoothing.json"'),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_ALPHA_BASE = 0.35"),
        (RUNTIME_RECORDER, recorder, "SMOOTHING_WARMUP_N = 5"),
        (RUNTIME_RECORDER, recorder, '"advisory": True'),
        (RUNTIME_BUDGET_CHECKER, runtime_budget_sources, 'SMOOTHING_PATH = Path(".charness") / "quality" / "runtime-smoothing.json"'),
        (RUNTIME_BUDGET_CHECKER, runtime_budget_sources, "ewma_advisory_elapsed_ms"),
        (RUNTIME_BUDGET_CHECKER, runtime_budget_sources, "ewma {entry['ewma_advisory_elapsed_ms']:.1f}ms advisory"),
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


def _manifest_default(field: str) -> object:
    return None if field == "recommendation_role" else []


def validate_find_skills_integration_claims(repo_root: Path) -> None:
    inventory_path = repo_root / FIND_SKILLS_INVENTORY
    integrations_dir = repo_root / INTEGRATIONS_DIR
    if not inventory_path.is_file() or not integrations_dir.is_dir():
        return
    payload = _load_json(inventory_path)
    inventory = payload.get("inventory")
    if not isinstance(inventory, dict):
        return
    artifact_integrations = {
        item.get("path"): item
        for item in inventory.get("integrations", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    stale: list[str] = []
    for manifest_path in sorted(integrations_dir.glob("*.json")):
        if manifest_path.name == "manifest.schema.json":
            continue
        manifest = _load_json(manifest_path)
        relative_path = str(manifest_path.relative_to(repo_root))
        artifact_entry = artifact_integrations.get(relative_path)
        if not artifact_entry:
            stale.append(f"`{relative_path}` missing from `{FIND_SKILLS_INVENTORY}`")
            continue
        for field in ("intent_triggers", "supports_public_skills", "recommendation_role"):
            if artifact_entry.get(field) != manifest.get(field, _manifest_default(field)):
                stale.append(f"`{relative_path}` `{field}` differs from `{FIND_SKILLS_INVENTORY}`")
    if stale:
        raise ValidationError(
            "find-skills inventory pointer is stale:\n"
            + "\n".join(f"- {item}" for item in stale)
        )


def validate_current_pointer_freshness(repo_root: Path) -> None:
    validate_gate_is_queued(repo_root)
    validate_no_stale_claims(repo_root)
    validate_quality_command_claims(repo_root)
    validate_runtime_smoothing_claim(repo_root)
    validate_quality_runtime_signal_claims(repo_root)
    validate_release_version_claim(repo_root)
    validate_find_skills_integration_claims(repo_root)


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
