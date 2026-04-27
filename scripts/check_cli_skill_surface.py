#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)
REQUIRED_PRODUCT_SURFACES = {"installable_cli", "bundled_skill"}
DEFAULT_COMMAND_DOCS = (".agents/command-docs.yaml",)
DEFAULT_CHANGE_GLOBS = (
    "charness",
    "scripts/**",
    "skills/public/**",
    "skills/support/**",
    "plugins/**",
    ".claude-plugin/**",
    ".agents/plugins/**",
    "packaging/**",
    ".agents/command-docs.yaml",
)
_adapter_lib = import_repo_module(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib.load_yaml_file


def _string_list(data: dict[str, Any], field: str) -> list[str]:
    value = data.get(field)
    return list(value) if isinstance(value, list) and all(isinstance(item, str) for item in value) else []


def _load_adapter(repo_root: Path, adapter_path: Path) -> dict[str, Any]:
    path = adapter_path if adapter_path.is_absolute() else repo_root / adapter_path
    raw = load_yaml_file(path) if path.is_file() else {}
    return raw if isinstance(raw, dict) else {}


def _required(data: dict[str, Any]) -> bool:
    return REQUIRED_PRODUCT_SURFACES.issubset(set(_string_list(data, "product_surfaces")))


def _default_skill_paths(repo_root: Path) -> list[Path]:
    paths: list[Path] = []
    public_root = repo_root / "skills" / "public"
    generated_support_root = repo_root / "skills" / "support" / "generated"
    direct_skill_root = repo_root / "skills"
    if public_root.is_dir():
        paths.extend(sorted(public_root.glob("*/SKILL.md")))
    if generated_support_root.is_dir():
        paths.extend(sorted(generated_support_root.glob("*/SKILL.md")))
    if direct_skill_root.is_dir():
        paths.extend(sorted(direct_skill_root.glob("*/SKILL.md")))
    return paths


def _has_root_executable(repo_root: Path) -> bool:
    if not repo_root.is_dir():
        return False
    for path in repo_root.iterdir():
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix in {".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".lock"}:
            continue
        if path.stat().st_mode & 0o111:
            return True
    return False


def _has_cli_marker(repo_root: Path, data: dict[str, Any]) -> bool:
    return bool(_probe_commands(data)) or bool(_existing_docs(_command_doc_paths(repo_root, data))) or _has_root_executable(repo_root)


def _product_surface_source(repo_root: Path, data: dict[str, Any], skills: list[Path]) -> str | None:
    if _required(data):
        return "declared"
    if skills and _has_cli_marker(repo_root, data):
        return "inferred"
    return None


def _relevant_change(data: dict[str, Any], changed_paths: list[str]) -> bool:
    if not changed_paths:
        return True
    globs = _string_list(data, "cli_skill_surface_change_globs") or list(DEFAULT_CHANGE_GLOBS)
    return any(fnmatch.fnmatch(path, pattern) for path in changed_paths for pattern in globs)


def _skill_paths(repo_root: Path, data: dict[str, Any]) -> list[Path]:
    configured = _string_list(data, "cli_skill_surface_skill_paths")
    if configured:
        return [(repo_root / path).resolve() for path in configured]
    return _default_skill_paths(repo_root)


def _command_doc_paths(repo_root: Path, data: dict[str, Any]) -> list[Path]:
    configured = _string_list(data, "cli_skill_surface_command_docs") or list(DEFAULT_COMMAND_DOCS)
    return [(repo_root / path).resolve() for path in configured]


def _existing_docs(paths: list[Path]) -> list[Path]:
    return [path for path in paths if path.is_file()]


def _probe_commands(data: dict[str, Any]) -> list[str]:
    return _string_list(data, "cli_skill_surface_probe_commands")


def _run_probe(repo_root: Path, command: str) -> dict[str, object]:
    result = subprocess.run(
        shlex.split(command),
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=20,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout_preview": result.stdout[:400],
        "stderr_preview": result.stderr[:400],
    }


def _adapter_weaknesses(data: dict[str, Any], *, source: str, skills: list[Path]) -> list[str]:
    declared = set(_string_list(data, "product_surfaces"))
    weaknesses: list[str] = []
    if source == "inferred":
        for surface in sorted(REQUIRED_PRODUCT_SURFACES - declared):
            weaknesses.append(f"adapter does not declare `{surface}` in product_surfaces despite detected CLI plus skill shape")
    if not _string_list(data, "cli_skill_surface_probe_commands"):
        weaknesses.append("cli_skill_surface_probe_commands is empty for a CLI plus bundled-skill surface")
    if not _string_list(data, "cli_skill_surface_command_docs"):
        weaknesses.append("cli_skill_surface_command_docs is empty; using default command-doc discovery only")
    if skills and not _string_list(data, "cli_skill_surface_skill_paths"):
        weaknesses.append("cli_skill_surface_skill_paths is empty; using common skill layout discovery only")
    globs = _string_list(data, "cli_skill_surface_change_globs")
    if not globs:
        weaknesses.append("cli_skill_surface_change_globs is empty; using default broad change globs")
    elif not any(fnmatch.fnmatch("skills/public/demo/SKILL.md", pattern) for pattern in globs):
        weaknesses.append("cli_skill_surface_change_globs does not match common public skill paths")
    elif not any(fnmatch.fnmatch("plugins/demo/SKILL.md", pattern) for pattern in globs):
        weaknesses.append("cli_skill_surface_change_globs does not match common plugin export paths")
    return weaknesses


def build_payload(
    repo_root: Path,
    *,
    adapter_path: Path,
    changed_paths: list[str],
    run_probes: bool,
) -> dict[str, object]:
    data = _load_adapter(repo_root, adapter_path)
    skills = [path for path in _skill_paths(repo_root, data) if path.is_file()]
    source = _product_surface_source(repo_root, data, skills)
    if source is None:
        return {
            "status": "not_applicable",
            "reason": "no declared or inferred installable CLI plus bundled-skill surface",
            "adapter_weaknesses": [],
        }
    if not _relevant_change(data, changed_paths):
        return {"status": "skipped", "reason": "no CLI, skill, plugin, package, or install-surface change matched"}

    probes = _probe_commands(data)
    docs = _existing_docs(_command_doc_paths(repo_root, data))
    adapter_weaknesses = _adapter_weaknesses(data, source=source, skills=skills)
    blockers: list[str] = []
    if not skills:
        blockers.append("No bundled public/support skill path was available to inspect.")
    if not docs and not any("--help" in command for command in probes):
        blockers.append("No command-docs file or `--help` probe delegates broad command discovery to the binary.")
    if not any(("doctor" in command or "--version" in command) for command in probes):
        blockers.append("No doctor/readiness or version probe demonstrates installable CLI readiness.")
    if not (docs or any(token in " ".join(probes).lower() for token in ("example", "catalog", "registry", "--json"))):
        blockers.append("No command-owned example, registry, catalog, or JSON probe is declared for packet/example shapes.")

    probe_results = [_run_probe(repo_root, command) for command in probes] if run_probes else []
    for result in probe_results:
        if result["returncode"] != 0:
            blockers.append(f"CLI plus skill probe failed: `{result['command']}` exited {result['returncode']}")

    findings = [
        {
            "type": "skill_core_review_prompt",
            "message": "Inspect bundled skill cores for agent-facing delegation to binary help, registries, examples, and readiness probes before prose review.",
            "skill_count": len(skills),
        }
    ]
    return {
        "status": "blocked" if blockers else "ok",
        "adapter_path": str(adapter_path),
        "product_surface_source": source,
        "product_surfaces": _string_list(data, "product_surfaces"),
        "adapter_weaknesses": adapter_weaknesses,
        "changed_paths": changed_paths,
        "skill_paths": [str(path.relative_to(repo_root)) for path in skills],
        "command_docs": [str(path.relative_to(repo_root)) for path in docs],
        "probe_commands": probes,
        "probe_results": probe_results,
        "findings": findings,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--adapter-path", type=Path, default=Path(".agents/quality-adapter.yaml"))
    parser.add_argument("--changed-path", action="append", default=[])
    parser.add_argument("--run-probes", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = build_payload(
        args.repo_root.resolve(),
        adapter_path=args.adapter_path,
        changed_paths=args.changed_path,
        run_probes=args.run_probes,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"CLI plus bundled-skill surface check: {payload['status']}")
        for blocker in payload.get("blockers", []):
            print(f"- {blocker}", file=sys.stderr)
    return 1 if payload["status"] == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
