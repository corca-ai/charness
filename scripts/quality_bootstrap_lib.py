from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file, render_yaml_mapping

LINEAGE_ORDER = ("python-quality", "typescript-quality", "specdown-quality", "monorepo-quality")
ADAPTER_CANDIDATES = (
    Path(".agents/quality-adapter.yaml"),
    Path(".codex/quality-adapter.yaml"),
    Path(".claude/quality-adapter.yaml"),
    Path("docs/quality-adapter.yaml"),
    Path("quality-adapter.yaml"),
)


def _repo_has_any(repo_root: Path, *relative_paths: str) -> bool:
    return any((repo_root / rel_path).exists() for rel_path in relative_paths)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _package_json_has_workspaces(path: Path) -> bool:
    data = _load_json(path)
    if data is None:
        return False
    workspaces = data.get("workspaces")
    if isinstance(workspaces, list):
        return bool(workspaces)
    return isinstance(workspaces, dict) and isinstance(workspaces.get("packages"), list) and bool(workspaces["packages"])


def _package_json_signals_typescript(path: Path) -> bool:
    data = _load_json(path)
    if data is None:
        return False
    dependencies: dict[str, Any] = {}
    for field in ("dependencies", "devDependencies", "peerDependencies"):
        value = data.get(field)
        if isinstance(value, dict):
            dependencies.update(value)
    if "typescript" in dependencies:
        return True
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return False
    return any(isinstance(command, str) and "tsc" in command for command in scripts.values())


def detect_preset_lineage(repo_root: Path) -> list[str]:
    detected: list[str] = []
    if _repo_has_any(repo_root, "pyproject.toml", "requirements.txt", "requirements-dev.txt", "uv.lock", "poetry.lock"):
        detected.append("python-quality")
    if _repo_has_any(repo_root, "tsconfig.json", "tsconfig.base.json") or _package_json_signals_typescript(
        repo_root / "package.json"
    ):
        detected.append("typescript-quality")
    if (
        (repo_root / "pnpm-workspace.yaml").is_file()
        or _package_json_has_workspaces(repo_root / "package.json")
        or any((repo_root / "packages").glob("*/package.json"))
    ):
        detected.append("monorepo-quality")
    if (repo_root / ".specdown").exists() or (repo_root / "specdown.json").is_file() or any(
        repo_root.rglob("*.spec.md")
    ):
        detected.append("specdown-quality")
    return [preset_id for preset_id in LINEAGE_ORDER if preset_id in detected]


def detect_concept_paths(repo_root: Path) -> list[str]:
    candidates = (
        "README.md",
        "docs/control-plane.md",
        "docs/public-skill-validation.md",
        "docs/operator-acceptance.md",
        "docs/handoff.md",
        "docs/roadmap.md",
        "skill-outputs/quality/quality.md",
    )
    return [path for path in candidates if (repo_root / path).is_file()]


def detect_preflight_commands(repo_root: Path) -> list[str]:
    commands: list[str] = []
    if (repo_root / "scripts" / "validate-maintainer-setup.py").is_file():
        commands.append("python3 scripts/validate-maintainer-setup.py --repo-root .")
    if (repo_root / "scripts" / "doctor.py").is_file():
        commands.append("python3 scripts/doctor.py --json")
    return commands


def detect_gate_commands(repo_root: Path) -> list[str]:
    commands: list[str] = []
    if (repo_root / "scripts" / "run-quality.sh").is_file():
        commands.append("./scripts/run-quality.sh")
    if (repo_root / "scripts" / "check-github-actions.py").is_file():
        commands.append("python3 scripts/check-github-actions.py --repo-root .")
    return commands


def detect_security_commands(repo_root: Path) -> list[str]:
    commands: list[str] = []
    if (repo_root / "scripts" / "check-secrets.sh").is_file():
        commands.append("./scripts/check-secrets.sh")
    if (repo_root / "scripts" / "check-supply-chain.py").is_file():
        commands.append("python3 scripts/check-supply-chain.py --repo-root .")
    return commands


def _merge_unique(existing: list[str], inferred: list[str]) -> list[str]:
    merged = list(existing)
    for item in inferred:
        if item not in merged:
            merged.append(item)
    return merged


def _classify_command_deferral(field: str, preset_lineage: list[str]) -> dict[str, Any]:
    if field == "gate_commands":
        families = ["repo-native test runner", "repo-native lint or typecheck gate"]
        if "python-quality" in preset_lineage:
            families = ["pytest or repo-native test runner", "ruff, mypy, or pyright"]
        elif "typescript-quality" in preset_lineage:
            families = ["vitest or jest", "eslint or tsc --noEmit"]
        elif "specdown-quality" in preset_lineage:
            families = ["specdown smoke", "overlap or adapter-depth guard"]
        reason = "No repo-owned quality gate command was detected."
    elif field == "preflight_commands":
        families = ["maintainer setup validation", "repo doctor or setup sanity"]
        reason = "No repo-owned maintainer setup or doctor command was detected."
    else:
        families = ["secret scan", "dependency or supply-chain audit"]
        reason = "No repo-owned security helper was detected."
    return {"field": field, "status": "deferred", "reason": reason, "suggested_families": families}


def _infer_defaults(repo_root: Path) -> dict[str, Any]:
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "skill-outputs/quality",
        "preset_id": "portable-defaults",
        "customized_from": "portable-defaults",
        "preset_lineage": [],
        "concept_paths": [],
        "preflight_commands": [],
        "gate_commands": [],
        "security_commands": [],
    }


def _load_existing_adapter_data(repo_root: Path) -> dict[str, Any]:
    defaults = _infer_defaults(repo_root)
    adapter_path = next((repo_root / candidate for candidate in ADAPTER_CANDIDATES if (repo_root / candidate).is_file()), None)
    if adapter_path is None:
        return defaults
    raw = load_yaml_file(adapter_path)
    if not isinstance(raw, dict):
        return defaults
    data = dict(defaults)
    for field in ("version", "repo", "language", "output_dir", "preset_id", "preset_version", "customized_from"):
        value = raw.get(field)
        if value is not None:
            data[field] = value
    for field in ("preset_lineage", "concept_paths", "preflight_commands", "gate_commands", "security_commands"):
        value = raw.get(field)
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            data[field] = list(value)
    return data


def build_bootstrap_state(repo_root: Path) -> tuple[dict[str, Any], dict[str, str], list[dict[str, Any]]]:
    existing = _load_existing_adapter_data(repo_root)
    detected_lineage = detect_preset_lineage(repo_root)
    field_statuses: dict[str, str] = {}
    deferred_setup: list[dict[str, Any]] = []
    final = {
        "version": 1,
        "repo": existing["repo"],
        "language": existing["language"],
        "output_dir": existing["output_dir"],
        "preset_id": existing.get("preset_id") or (detected_lineage[0] if detected_lineage else "portable-defaults"),
        "customized_from": existing.get("customized_from") or (detected_lineage[0] if detected_lineage else "portable-defaults"),
        "preset_version": existing.get("preset_version"),
    }

    existing_lineage = existing.get("preset_lineage", [])
    if existing_lineage:
        merged_lineage = _merge_unique(existing_lineage, detected_lineage)
        field_statuses["preset_lineage"] = "augmented" if merged_lineage != existing_lineage else "preserved"
    elif detected_lineage:
        merged_lineage = detected_lineage
        field_statuses["preset_lineage"] = "inferred"
    else:
        merged_lineage = []
        field_statuses["preset_lineage"] = "deferred"
    final["preset_lineage"] = merged_lineage

    concept_paths = detect_concept_paths(repo_root)
    existing_concepts = [path for path in existing.get("concept_paths", []) if (repo_root / path).is_file()]
    if existing_concepts:
        merged_concepts = _merge_unique(existing_concepts, concept_paths)
        field_statuses["concept_paths"] = "augmented" if merged_concepts != existing_concepts else "preserved"
    elif concept_paths:
        merged_concepts = concept_paths
        field_statuses["concept_paths"] = "inferred"
    else:
        merged_concepts = []
        field_statuses["concept_paths"] = "deferred"
    final["concept_paths"] = merged_concepts

    for field, detected in (
        ("preflight_commands", detect_preflight_commands(repo_root)),
        ("gate_commands", detect_gate_commands(repo_root)),
        ("security_commands", detect_security_commands(repo_root)),
    ):
        existing_values = existing.get(field, [])
        if existing_values:
            final[field] = list(existing_values)
            field_statuses[field] = "preserved"
            continue
        if detected:
            final[field] = detected
            field_statuses[field] = "installed"
            continue
        final[field] = []
        field_statuses[field] = "deferred"
        deferred_setup.append(_classify_command_deferral(field, merged_lineage))

    return final, field_statuses, deferred_setup


def render_bootstrap_adapter(data: dict[str, Any]) -> str:
    items: list[tuple[str, Any]] = [
        ("version", data["version"]),
        ("repo", data["repo"]),
        ("language", data["language"]),
        ("output_dir", data["output_dir"]),
        ("preset_id", data["preset_id"]),
        ("customized_from", data["customized_from"]),
    ]
    if data.get("preset_version"):
        items.append(("preset_version", data["preset_version"]))
    items.extend(
        [
            ("preset_lineage", data["preset_lineage"]),
            ("concept_paths", data["concept_paths"]),
            ("preflight_commands", data["preflight_commands"]),
            ("gate_commands", data["gate_commands"]),
            ("security_commands", data["security_commands"]),
        ]
    )
    return render_yaml_mapping(items)


def bootstrap_quality_adapter(
    *, repo_root: Path, output_path: Path, report_path: Path, dry_run: bool
) -> dict[str, Any]:
    adapter_path = output_path if output_path.is_absolute() else repo_root / output_path
    resolved_report_path = report_path if report_path.is_absolute() else repo_root / report_path
    final_data, field_statuses, deferred_setup = build_bootstrap_state(repo_root)
    adapter_text = render_bootstrap_adapter(final_data)
    existing_text = adapter_path.read_text(encoding="utf-8") if adapter_path.is_file() else None

    if dry_run:
        adapter_status = "dry-run"
    elif existing_text is None:
        adapter_path.parent.mkdir(parents=True, exist_ok=True)
        adapter_path.write_text(adapter_text, encoding="utf-8")
        adapter_status = "written"
    elif existing_text == adapter_text:
        adapter_status = "unchanged"
    else:
        adapter_path.write_text(adapter_text, encoding="utf-8")
        adapter_status = "updated"

    report = {
        "adapter_path": str(adapter_path),
        "adapter_status": adapter_status,
        "artifact_path": str(Path(final_data["output_dir"]) / "quality.md"),
        "report_path": str(resolved_report_path),
        "preset_lineage": final_data["preset_lineage"],
        "field_statuses": field_statuses,
        "deferred_setup": deferred_setup,
    }
    if not dry_run:
        resolved_report_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report
