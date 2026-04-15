from __future__ import annotations

import json
from pathlib import Path
from typing import Any

LINEAGE_ORDER = ("python-quality", "typescript-quality", "specdown-quality", "monorepo-quality")


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
    return isinstance(scripts, dict) and any(isinstance(command, str) and "tsc" in command for command in scripts.values())


def detect_preset_lineage(repo_root: Path) -> list[str]:
    detected: list[str] = []
    if _repo_has_any(repo_root, "pyproject.toml", "requirements.txt", "requirements-dev.txt", "uv.lock", "poetry.lock"):
        detected.append("python-quality")
    if _repo_has_any(repo_root, "tsconfig.json", "tsconfig.base.json") or _package_json_signals_typescript(repo_root / "package.json"):
        detected.append("typescript-quality")
    if (repo_root / "pnpm-workspace.yaml").is_file() or _package_json_has_workspaces(repo_root / "package.json") or any((repo_root / "packages").glob("*/package.json")):
        detected.append("monorepo-quality")
    if (repo_root / ".specdown").exists() or (repo_root / "specdown.json").is_file() or any(repo_root.rglob("*.spec.md")):
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
        "charness-artifacts/quality/latest.md",
    )
    return [path for path in candidates if (repo_root / path).is_file()]


def detect_preflight_commands(repo_root: Path) -> list[str]:
    return [cmd for exists, cmd in (
        ((repo_root / "scripts" / "validate-maintainer-setup.py").is_file(), "python3 scripts/validate-maintainer-setup.py --repo-root ."),
        ((repo_root / "scripts" / "doctor.py").is_file(), "python3 scripts/doctor.py --json"),
    ) if exists]


def detect_gate_commands(repo_root: Path) -> list[str]:
    return [cmd for exists, cmd in (
        ((repo_root / "scripts" / "run-quality.sh").is_file(), "./scripts/run-quality.sh"),
        ((repo_root / "scripts" / "check-github-actions.py").is_file(), "python3 scripts/check-github-actions.py --repo-root ."),
    ) if exists]


def detect_security_commands(repo_root: Path) -> list[str]:
    return [cmd for exists, cmd in (
        ((repo_root / "scripts" / "check-secrets.sh").is_file(), "./scripts/check-secrets.sh"),
        ((repo_root / "scripts" / "check-supply-chain.py").is_file(), "python3 scripts/check-supply-chain.py --repo-root ."),
    ) if exists]
