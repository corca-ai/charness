#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
CAUTILUS_DIR = Path("charness-artifacts/cautilus")
MAX_FINDING_LINES = 180
MACHINE_EVIDENCE_NAMES = (
    "observed.v1.json",
    "summary.v1.json",
    "report.json",
)
NON_DIAGNOSTIC_DIR_PREFIXES = (
    "chatbot-benchmark/",
    "chatbot-proposals/",
    "skill-experiment-",
)
VALID_STATUSES = {"passed", "failed", "degraded", "blocked"}
VALID_RECOMMENDATIONS = {"accept-now", "accept", "reject", "discard", "revise", "blocked"}
# floor-addition-restraint: keep as a narrow blocking floor because evaluator
# diagnostic bundles are shared closeout evidence; the check only fires on
# changed Cautilus finding bundles and does not weaken `latest.md` proof.
SOURCE_MARKERS = (
    "## What ran",
    "## Fixture",
    "## Reproduce",
    "## Behavior Source",
)
VERDICT_MARKERS = (
    "## Verdict",
    "## Deterministic Observed Packet",
    "## Outcome",
)
INTERPRETATION_MARKERS = (
    "## Diagnosis",
    "## What it means",
    "## Non-Claims",
    "not closable",
    "follow-up",
    "followup",
)

_scripts_artifact_validator_module = import_repo_module(__file__, "scripts.artifact_validator")
ValidationError = _scripts_artifact_validator_module.ValidationError
_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
normalize_repo_path = _scripts_surfaces_lib_module.normalize_repo_path


def _is_diagnostic_bundle_path(path: str) -> bool:
    normalized = normalize_repo_path(path)
    if not normalized.startswith(f"{CAUTILUS_DIR.as_posix()}/"):
        return False
    tail = normalized.removeprefix(f"{CAUTILUS_DIR.as_posix()}/")
    if "/" not in tail:
        return False
    # First-class diagnostic bundles are run directories, not the rolling proof
    # pointer, maintained benchmark summaries, or skill-experiment demo packet.
    return not tail.startswith(NON_DIAGNOSTIC_DIR_PREFIXES)


def _bundle_dir_for_path(repo_root: Path, path: str) -> Path | None:
    if not _is_diagnostic_bundle_path(path):
        return None
    rel = Path(normalize_repo_path(path))
    bundle_dir = Path(rel.parts[0], rel.parts[1], rel.parts[2])
    finding = repo_root / bundle_dir / "finding.md"
    if finding.exists() or rel.name == "finding.md" or rel.name in MACHINE_EVIDENCE_NAMES:
        return bundle_dir
    return None


def _changed_bundle_dirs(repo_root: Path, changed_paths: list[str]) -> list[Path]:
    dirs: list[Path] = []
    seen: set[str] = set()
    for path in changed_paths:
        bundle_dir = _bundle_dir_for_path(repo_root, path)
        if bundle_dir is None:
            continue
        key = bundle_dir.as_posix()
        if key in seen:
            continue
        seen.add(key)
        dirs.append(bundle_dir)
    return dirs


def _all_bundle_dirs(repo_root: Path) -> list[Path]:
    root = repo_root / CAUTILUS_DIR
    if not root.is_dir():
        return []
    bundle_dirs: list[Path] = []
    for path in sorted(root.iterdir()):
        if not path.is_dir():
            continue
        rel = path.relative_to(repo_root).as_posix()
        tail = rel.removeprefix(f"{CAUTILUS_DIR.as_posix()}/")
        if tail.startswith(NON_DIAGNOSTIC_DIR_PREFIXES):
            continue
        if (path / "finding.md").is_file() or any((path / name).is_file() for name in MACHINE_EVIDENCE_NAMES):
            bundle_dirs.append(path.relative_to(repo_root))
    return bundle_dirs


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"`{path}` is not valid JSON: {exc}") from exc


def _validate_observed(path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValidationError(f"`{path}` must contain a JSON object")
    evaluations = payload.get("evaluations")
    if not isinstance(evaluations, list) or not evaluations:
        raise ValidationError(f"`{path}` must contain a non-empty `evaluations` list")
    for index, evaluation in enumerate(evaluations):
        if not isinstance(evaluation, dict):
            raise ValidationError(f"`{path}` evaluation {index} must be an object")
        status = evaluation.get("outcome") or evaluation.get("status")
        if status not in VALID_STATUSES:
            valid = "|".join(sorted(VALID_STATUSES))
            raise ValidationError(f"`{path}` evaluation {index} must carry `outcome/status: {valid}`")


def _validate_summary(path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValidationError(f"`{path}` must contain a JSON object")
    recommendation = payload.get("recommendation")
    if recommendation is not None and recommendation not in VALID_RECOMMENDATIONS:
        valid = "|".join(sorted(VALID_RECOMMENDATIONS))
        raise ValidationError(f"`{path}` `recommendation` must be one of {valid}")
    evaluations = payload.get("evaluations") or payload.get("evaluationRuns")
    if not isinstance(evaluations, list) or not evaluations:
        raise ValidationError(f"`{path}` must contain `evaluations` or `evaluationRuns`")


def _validate_report(path: Path, payload: Any) -> None:
    if not isinstance(payload, dict):
        raise ValidationError(f"`{path}` must contain a JSON object")
    if "schemaVersion" not in payload and "schema_version" not in payload:
        raise ValidationError(f"`{path}` must carry a schema version")


def _validate_machine_evidence(bundle_abs: Path) -> list[str]:
    present = [name for name in MACHINE_EVIDENCE_NAMES if (bundle_abs / name).is_file()]
    if not present:
        expected = ", ".join(MACHINE_EVIDENCE_NAMES)
        raise ValidationError(f"`{bundle_abs}` must include one machine evidence file: {expected}")
    for name in present:
        path = bundle_abs / name
        payload = _load_json(path)
        if name == "observed.v1.json":
            _validate_observed(path, payload)
        elif name == "summary.v1.json":
            _validate_summary(path, payload)
        elif name == "report.json":
            _validate_report(path, payload)
    return present


def _contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def _validate_finding(bundle_abs: Path) -> None:
    path = bundle_abs / "finding.md"
    if not path.is_file():
        raise ValidationError(f"diagnostic bundle `{bundle_abs}` must include `finding.md`")
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValidationError(f"`{path}` must start with an H1 title")
    if len(lines) > MAX_FINDING_LINES:
        raise ValidationError(f"`{path}` should stay concise; move raw logs to sibling files")
    text = "\n".join(lines)
    if not _contains_any(text, SOURCE_MARKERS):
        raise ValidationError(f"`{path}` must name the behavior source or fixture (`## What ran` or `## Fixture`)")
    if not _contains_any(text, VERDICT_MARKERS):
        raise ValidationError(f"`{path}` must carry a verdict or deterministic observed-packet section")
    if not _contains_any(text, INTERPRETATION_MARKERS):
        raise ValidationError(
            f"`{path}` must include diagnosis, non-claims, follow-up, or why the finding is not closable"
        )


def _validate_trace_digest(bundle_abs: Path) -> None:
    # Per-tool-call efficiency trace emitted by build-skill-execution-observation.mjs.
    # Validated WHEN PRESENT, not required: build now always writes it next to
    # --output, but `--all` currently has a pre-existing finding.md gap in older
    # bundles (the retro capture bundles use PROOF.md), so requiring a digest here
    # would pile onto an already-red --all.
    # floor-addition-restraint: promote to required once --all is green and every
    # capture bundle ships a digest (recorded gap: the 2026-06-29 hitl capture lost
    # its transcript because only count-level summaries were retained).
    path = bundle_abs / "trace-digest.jsonl"
    if not path.is_file():
        return
    lines = [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        raise ValidationError(f"`{path}` must contain at least one tool-call record")
    for index, line in enumerate(lines):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"`{path}` line {index + 1} is not valid JSON: {exc}") from exc
        if not isinstance(record, dict) or not isinstance(record.get("name"), str):
            raise ValidationError(f"`{path}` line {index + 1} must be an object with a string `name`")


def validate_bundle(repo_root: Path, bundle_dir: Path) -> None:
    bundle_abs = repo_root / bundle_dir
    _validate_finding(bundle_abs)
    _validate_machine_evidence(bundle_abs)
    _validate_trace_digest(bundle_abs)


def validate_cautilus_diagnostics(repo_root: Path, changed_paths: list[str], *, all_bundles: bool = False) -> str:
    bundle_dirs = _all_bundle_dirs(repo_root) if all_bundles else _changed_bundle_dirs(repo_root, changed_paths)
    if not bundle_dirs:
        return "no changed cautilus diagnostic bundles"
    for bundle_dir in bundle_dirs:
        validate_bundle(repo_root, bundle_dir)
    return f"validated {len(bundle_dirs)} cautilus diagnostic bundle(s)"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument("--all", action="store_true", help="Validate every diagnostic bundle with a finding.md")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if args.all:
        changed_paths = []
    else:
        changed_paths = [normalize_repo_path(path) for path in args.paths] if args.paths else collect_changed_paths(repo_root)
    print(validate_cautilus_diagnostics(repo_root, changed_paths, all_bundles=args.all))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
