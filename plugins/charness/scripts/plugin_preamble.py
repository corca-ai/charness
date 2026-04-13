#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import load_capabilities, read_lock

VALIDATE_PACKAGING_PATH = REPO_ROOT / "scripts" / "validate-packaging.py"
VALIDATE_PACKAGING_SPEC = importlib.util.spec_from_file_location(
    "validate_packaging_for_plugin_preamble",
    VALIDATE_PACKAGING_PATH,
)
assert VALIDATE_PACKAGING_SPEC is not None and VALIDATE_PACKAGING_SPEC.loader is not None
VALIDATE_PACKAGING = importlib.util.module_from_spec(VALIDATE_PACKAGING_SPEC)
VALIDATE_PACKAGING_SPEC.loader.exec_module(VALIDATE_PACKAGING)

VENDORED_COPY_CANDIDATES = (
    Path(".claude/skills/charness"),
    Path(".agents/skills/charness"),
    Path("plugins/charness"),
)


def load_packaging(repo_root: Path) -> dict[str, object]:
    return json.loads((repo_root / "packaging" / "charness.json").read_text(encoding="utf-8"))


def collect_readiness_summary(repo_root: Path) -> list[dict[str, str]]:
    summaries: list[dict[str, str]] = []
    for capability in load_capabilities(repo_root):
        lock_payload = read_lock(repo_root, capability["tool_id"])
        doctor = lock_payload.get("doctor") if lock_payload else None
        summaries.append(
            {
                "tool_id": capability["tool_id"],
                "status": doctor.get("doctor_status", "unknown") if doctor else "unknown",
            }
        )
    return summaries


def detect_copy_warnings(consumer_root: Path) -> list[str]:
    warnings: list[str] = []
    source_repo = (consumer_root / "packaging" / "charness.json").exists()
    for relative_path in VENDORED_COPY_CANDIDATES:
        if source_repo and relative_path == Path("plugins/charness"):
            continue
        candidate = consumer_root / relative_path
        if candidate.exists() and not candidate.is_symlink():
            warnings.append(
                f"vendored charness copy detected at `{relative_path}`; prefer a generated or pinned upstream artifact"
            )
    return warnings


def evaluate_root_install_surface(repo_root: Path) -> dict[str, object]:
    manifest_path = repo_root / "packaging" / "charness.json"
    try:
        VALIDATE_PACKAGING.validate_packaging_manifest(manifest_path, repo_root)
    except (VALIDATE_PACKAGING.ValidationError, FileNotFoundError, json.JSONDecodeError) as exc:
        return {"ok": False, "warning": str(exc)}
    return {"ok": True, "warning": None}


def build_payload(repo_root: Path, consumer_root: Path) -> dict[str, object]:
    packaging = load_packaging(repo_root)
    return {
        "package_id": packaging["package_id"],
        "version": packaging["version"],
        "runtime_self_update": False,
        "update_hints": {
            "claude": "Run `charness update`, then restart Claude Code.",
            "codex": "Run `charness update`; it will try Codex's official plugin/install refresh for enabled local installs. Then restart Codex and only use Plugin Directory if drift remains.",
        },
        "root_install_surface": evaluate_root_install_surface(repo_root),
        "readiness": collect_readiness_summary(repo_root),
        "warnings": detect_copy_warnings(consumer_root),
    }


def print_text(payload: dict[str, object]) -> None:
    print(f"CHARNESS_VERSION: {payload['version']}")
    print("RUNTIME_SELF_UPDATE: disabled")
    root_install_surface = payload["root_install_surface"]
    print(f"ROOT_INSTALL_SURFACE: {'ok' if root_install_surface['ok'] else 'warning'}")
    if root_install_surface["warning"]:
        print(f"INSTALL_WARNING: {root_install_surface['warning']}")
    print("UPDATE_HINTS:")
    print(f"- Claude: {payload['update_hints']['claude']}")
    print(f"- Codex: {payload['update_hints']['codex']}")
    print("READINESS:")
    for entry in payload["readiness"]:
        print(f"- {entry['tool_id']}: {entry['status']}")
    if payload["warnings"]:
        print("WARNINGS:")
        for warning in payload["warnings"]:
            print(f"- {warning}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--consumer-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.repo_root.resolve(), args.consumer_root.resolve())
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
