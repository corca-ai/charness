#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path


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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_control_plane_lib_module = import_repo_module(__file__, "scripts.adapters.control_plane_lib")
load_capabilities = _scripts_control_plane_lib_module.load_capabilities
read_lock = _scripts_control_plane_lib_module.read_lock

VALIDATE_PACKAGING_PATH = REPO_ROOT / "scripts" / "plugin_export" / "validate_packaging.py"
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
        # The ATTENTION STATE, spelled as the operator-facing token it always was.
        # `runtime_self_update: false` is a boolean nobody reads as "this capability
        # is off"; the word `disabled` was printed only by the human renderer, so
        # deleting that renderer without carrying the state would take the state out
        # of this command's output while leaving it green -- which is precisely what
        # `skills/public/quality/references/attention-state-visibility.json` declares
        # this file must not do.
        "runtime_self_update_attention": "RUNTIME_SELF_UPDATE: disabled",
        "update_hints": {
            "claude": "Run `charness update`, then restart Claude Code.",
            "codex": "Run `charness init` or `charness update`; both try Codex's official plugin/install path when the Codex CLI is available. Restart Codex only if the host state still needs to reload the installed plugin.",
            "grok": "Run `charness update`, then restart Grok Build. Grok loads `~/.grok/plugins/charness` when `[plugins].enabled` lists `charness`. No marketplace step.",
        },
        "root_install_surface": evaluate_root_install_surface(repo_root),
        "readiness": collect_readiness_summary(repo_root),
        "warnings": detect_copy_warnings(consumer_root),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--consumer-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    emit_yaml(build_payload(args.repo_root.resolve(), args.consumer_root.resolve()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
