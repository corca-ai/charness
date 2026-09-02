from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

from scripts.core.git_checkout import discoverable as _git_metadata_is_discoverable

try:
    from scripts.core.subprocess_guard import run_process
except ImportError:  # flat layout: the repo root is not on sys.path
    _repo_root = next(
        ancestor
        for ancestor in Path(__file__).resolve().parents
        if (ancestor / "scripts" / "core" / "subprocess_guard.py").is_file()
    )
    if str(_repo_root) not in sys.path:
        sys.path.insert(0, str(_repo_root))
    from scripts.core.subprocess_guard import run_process


def _present_paths(repo_root: Path, candidates: tuple[str, ...]) -> list[str]:
    return [candidate for candidate in candidates if (repo_root / candidate).is_file()]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""


def _file_digest(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return None
    return digest.hexdigest()


def _detect_language_evidence(repo_root: Path) -> dict[str, list[str]]:
    """Expose cheap, high-signal language markers for a setup proposal.

    This is deliberately not a SLOC counter and never chooses a linter from one
    extension. The quality skill owns the exact preset and gate contract; setup
    only exposes evidence that should be shown before approval.
    """

    markers = {
        "python": ("pyproject.toml", "uv.lock", "requirements.txt", "setup.py", "tox.ini"),
        "javascript-typescript": ("package.json", "tsconfig.json", "vite.config.ts", "biome.json"),
        "go": ("go.mod", "go.sum"),
        "rust": ("Cargo.toml", "Cargo.lock"),
        "java": ("pom.xml", "build.gradle", "build.gradle.kts"),
        "ruby": ("Gemfile", "Gemfile.lock"),
        "php": ("composer.json",),
        "swift": ("Package.swift",),
    }
    evidence: dict[str, list[str]] = {}
    for language, names in markers.items():
        paths = _present_paths(repo_root, names)
        if paths:
            evidence[language] = paths
    return evidence


def _detect_hook_policy(repo_root: Path, package_json: dict[str, object]) -> dict[str, object]:
    hook_files = _present_paths(
        repo_root,
        (
            "lefthook.yml",
            "lefthook.yaml",
            ".husky/pre-commit",
            ".husky/pre-push",
            ".githooks/pre-commit",
            ".githooks/pre-push",
            ".pre-commit-config.yaml",
            "overcommit.yml",
            ".git/hooks/pre-commit",
            ".git/hooks/pre-push",
        ),
    )
    hook_candidates: list[tuple[str, str]] = []
    if any(path in hook_files for path in ("lefthook.yml", "lefthook.yaml")):
        hook_candidates.append(
            ("lefthook", "existing Lefthook config must be preserved and integrated")
        )
    if any(path.startswith(".husky/") for path in hook_files) or (repo_root / ".husky").is_dir():
        hook_candidates.append(("husky", "existing Husky hooks must be preserved and integrated"))
    if any(path.startswith(".githooks/") or path.startswith(".git/hooks/") for path in hook_files):
        hook_candidates.append(
            ("git-native", "existing git hook path must be preserved and integrated")
        )
    if ".pre-commit-config.yaml" in hook_files:
        hook_candidates.append(
            ("pre-commit", "existing pre-commit configuration must be preserved and integrated")
        )
    if "overcommit.yml" in hook_files:
        hook_candidates.append(
            ("overcommit", "existing Overcommit configuration must be preserved and integrated")
        )
    if isinstance(package_json.get("simple-git-hooks"), dict):
        hook_candidates.append(
            (
                "simple-git-hooks",
                "existing package hook configuration must be preserved and integrated",
            )
        )
    if isinstance(package_json.get("husky"), dict) and not any(
        name == "husky" for name, _ in hook_candidates
    ):
        hook_candidates.append(
            ("husky", "existing package Husky configuration must be preserved and integrated")
        )
    if isinstance(package_json.get("pre-commit"), (dict, list, str)) and not any(
        name == "pre-commit" for name, _ in hook_candidates
    ):
        hook_candidates.append(
            (
                "pre-commit",
                "existing package pre-commit configuration must be preserved and integrated",
            )
        )
    configured = ""
    if _git_metadata_is_discoverable(repo_root):
        try:
            configured = run_process(
                ["git", "config", "--get", "core.hooksPath"],
                cwd=repo_root,
                timeout_seconds=2,
            ).stdout.strip()
        except OSError:
            configured = ""
    if configured and not any(name == "git-native" for name, _ in hook_candidates):
        hook_candidates.append(("git-native", f"git core.hooksPath={configured}"))
    hook_manager = hook_candidates[0][0] if hook_candidates else None
    hook_reason = hook_candidates[0][1] if hook_candidates else None
    if len(hook_candidates) > 1:
        hook_manager = "multiple"
        hook_reason = "multiple existing hook managers detected; preserve and integrate each before proposing changes"
    return {
        "hook_evidence": hook_files,
        "hook_manager": hook_manager,
        "hook_managers": [name for name, _ in hook_candidates],
        "hook_conflict": len(hook_candidates) > 1,
        "hook_policy": {
            "recommendation": "prefer-lefthook-when-no-hook-manager",
            "rationale": "Lefthook is recommended for declarative stages, parallel commands, worktree installation, and visible failure text/log routing; this is a preference, not permission to replace an existing hook system.",
            "existing_manager_action": "preserve-and-integrate"
            if hook_manager
            else "propose-lefthook",
            "existing_manager_reason": hook_reason,
        },
    }


def _detect_quality_tooling(repo_root: Path) -> dict[str, object]:
    files = {
        "formatters": _present_paths(
            repo_root,
            ("biome.json", "biome.jsonc", ".prettierrc", ".prettierrc.json", "rustfmt.toml"),
        ),
        "linters": _present_paths(
            repo_root,
            (
                "ruff.toml",
                ".flake8",
                ".eslintrc",
                ".eslintrc.json",
                "eslint.config.js",
                "eslint.config.mjs",
                ".golangci.yml",
            ),
        ),
        "ratchets": _present_paths(
            repo_root,
            (
                ".jscpd.json",
                "stryker.config.mjs",
                "stryker.config.js",
                "mutmut-config.py",
                ".coveragerc",
            ),
        ),
    }
    pyproject = repo_root / "pyproject.toml"
    if pyproject.is_file():
        pyproject_text = _read_text(pyproject)
        if "[tool.ruff" in pyproject_text:
            files["linters"].append("pyproject.toml:[tool.ruff]")
        if "[tool.pyright" in pyproject_text or "[tool.mypy" in pyproject_text:
            files.setdefault("type_checkers", []).append("pyproject.toml")
    package_json: dict[str, object] = {}
    package_path = repo_root / "package.json"
    if package_path.is_file():
        try:
            parsed = json.loads(package_path.read_text(encoding="utf-8"))
            package_json = parsed if isinstance(parsed, dict) else {}
        except (OSError, UnicodeError, json.JSONDecodeError):
            package_json = {}
    package_text = json.dumps(package_json)
    for tool, section in (
        ("biome", "formatters"),
        ("prettier", "formatters"),
        ("eslint", "linters"),
        ("lint-staged", "scoped_hooks"),
    ):
        if tool in package_text and tool not in files.setdefault(section, []):
            files[section].append(f"package.json:{tool}")
    package_managers = {
        "npm": "package.json",
        "pnpm": "pnpm-lock.yaml",
        "yarn": "yarn.lock",
        "bun": "bun.lockb",
        "uv": "uv.lock",
        "cargo": "Cargo.toml",
        "go": "go.mod",
    }
    detected_managers = [
        name for name, marker in package_managers.items() if (repo_root / marker).is_file()
    ]
    hook_policy = _detect_hook_policy(repo_root, package_json)
    quality_adapter = repo_root / ".agents" / "quality-adapter.yaml"
    return {
        "language_evidence": _detect_language_evidence(repo_root),
        "package_managers": detected_managers,
        "existing": files,
        **hook_policy,
        "scope_policy": {
            "required": "staged-and-related-files",
            "reason": "fast hooks must avoid whole-repository rescans while preserving the linter's true ownership scope",
            "lint_staged": "advisory: use only when the native tool cannot express the required staged/related-file scope",
        },
        "quality_adapter_path": ".agents/quality-adapter.yaml",
        "quality_adapter_exists": quality_adapter.is_file(),
    }


def probe_awiki(repo_root: Path) -> dict[str, object]:
    command = "awiki lint -root docs -recursive"
    binary = shutil.which("awiki")
    if binary is None:
        return {
            "status": "unproven",
            "binary_found": False,
            "command": command,
            "reason": "awiki binary not found; docs graph health is unproven",
        }
    try:
        probe = run_process([binary, "--help"], cwd=repo_root, timeout_seconds=3)
    except OSError as exc:
        return {
            "status": "unproven",
            "binary_found": True,
            "binary": binary,
            "command": command,
            "reason": f"awiki healthcheck failed: {exc}",
        }
    if probe.returncode == 124:
        return {
            "status": "unproven",
            "binary_found": True,
            "binary": binary,
            "command": command,
            "reason": "awiki healthcheck failed: timed out after 3s",
        }
    return {
        "status": "unproven",
        "binary_status": "available" if probe.returncode == 0 else "unproven",
        "binary_found": True,
        "binary": binary,
        "command": command,
        "healthcheck": {"command": f"{binary} --help", "returncode": probe.returncode},
        "reason": None if probe.returncode == 0 else "awiki healthcheck returned non-zero",
    }


def docs_inventory(repo_root: Path) -> dict[str, object]:
    docs_root = repo_root / "docs"
    if not docs_root.is_dir():
        return {
            "status": "missing",
            "root": "docs",
            "paths": [],
            "nested_paths": [],
            "migration_policy": "preserve-existing-nested-until-explicit-approval",
        }
    paths: list[dict[str, object]] = []
    for path in sorted(docs_root.rglob("*")):
        if path.is_file() and path.suffix.lower() == ".md":
            paths.append(
                {"path": path.relative_to(repo_root).as_posix(), "sha256": _file_digest(path)}
            )
    nested_paths = [
        item["path"]
        for item in paths
        if isinstance(item.get("path"), str) and "/" in item["path"][len("docs/") :]
    ]
    return {
        "status": "observed",
        "root": "docs",
        "paths": paths,
        "nested_paths": nested_paths,
        "migration_policy": "preserve-existing-nested-until-explicit-approval",
    }


def approval_plan(
    repo_root: Path, payload: dict[str, object], default_surfaces: dict[str, Path]
) -> dict[str, object]:
    tooling = payload["quality_setup"]["tooling"]
    candidate_paths = {str(path) for path in default_surfaces.values()}
    candidate_paths.update({".agents/setup-adapter.yaml", ".agents/quality-adapter.yaml"})
    surfaces = payload.get("surfaces")
    if isinstance(surfaces, dict):
        for state in surfaces.values():
            if isinstance(state, dict):
                for key in ("path", "configured_path"):
                    value = state.get(key)
                    if isinstance(value, str):
                        candidate_paths.add(value)
    if isinstance(tooling, dict):
        for key in ("language_evidence", "existing"):
            entries = tooling.get(key)
            if isinstance(entries, dict):
                for values in entries.values():
                    if isinstance(values, list):
                        candidate_paths.update(str(value).split(":", 1)[0] for value in values)
        hook_files = tooling.get("hook_evidence")
        if isinstance(hook_files, list):
            candidate_paths.update(str(value) for value in hook_files)
    inventory = payload.get("docs_inventory")
    if isinstance(inventory, dict):
        for item in inventory.get("paths", []):
            if isinstance(item, dict) and isinstance(item.get("path"), str):
                candidate_paths.add(item["path"])
    inputs = {path: _file_digest(repo_root / path) for path in sorted(candidate_paths)}
    basis = {
        "inspection": {key: value for key, value in payload.items() if key != "approval_plan"},
        "inputs": inputs,
    }
    encoded = json.dumps(basis, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode(
        "utf-8"
    )
    return {
        "identity": f"sha256:{hashlib.sha256(encoded).hexdigest()}",
        "algorithm": "sha256",
        "state": "plan-only",
        "approval_required": True,
        "input_paths": sorted(inputs),
    }


def quality_setup_snapshot(repo_root: Path) -> dict[str, object]:
    """Expose quality's bootstrap state without creating a second contract."""

    tooling = _detect_quality_tooling(repo_root)
    from scripts.setup_operating_surface_lib import detect_operating_surface_ownership

    ownership = detect_operating_surface_ownership(repo_root)
    plan_commands = {
        "dry_run": "python3 $SKILL_DIR/../quality/scripts/bootstrap_adapter.py --repo-root . --dry-run",
        "apply_after_user_approval": "python3 $SKILL_DIR/../quality/scripts/bootstrap_adapter.py --repo-root . --migrate",
        "verify": "python3 $SKILL_DIR/../quality/scripts/plan_quality_run.py --repo-root . --detail",
    }
    try:
        from scripts.adapters.quality_adapter_lib import load_quality_adapter
        from scripts.adapters.quality_bootstrap_lib import build_bootstrap_state

        resolved = load_quality_adapter(repo_root)
        state, field_statuses, deferred_setup = build_bootstrap_state(repo_root)
        adapter_status = (
            "configured" if resolved.get("found") and resolved.get("valid") else "plan-only"
        )
        if resolved.get("found") and not resolved.get("valid"):
            adapter_status = "blocked"
        return {
            "owner_skill": "quality",
            "status": adapter_status,
            "adapter": {
                "path": resolved.get("path"),
                "found": bool(resolved.get("found")),
                "valid": bool(resolved.get("valid")),
                "errors": list(resolved.get("errors") or []),
                "warnings": list(resolved.get("warnings") or []),
            },
            "preset_lineage": list(state.get("preset_lineage") or []),
            "field_statuses": field_statuses,
            "deferred_setup": deferred_setup,
            "plan_commands": plan_commands,
            "tooling": tooling,
            "operating_surface_ownership": ownership,
            "non_claims": [
                "setup does not claim that a quality gate is green; quality owns execution and verdicts",
                "tool installation and hook registration remain unperformed until the user approves the plan",
            ],
        }
    except Exception as exc:
        return {
            "owner_skill": "quality",
            "status": "unavailable",
            "adapter": {"path": ".agents/quality-adapter.yaml", "found": False, "valid": False},
            "tooling": tooling,
            "operating_surface_ownership": ownership,
            "plan_commands": plan_commands,
            "non_claims": [f"quality bootstrap state could not be read: {exc}"],
        }
