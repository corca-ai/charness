#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.core.subprocess_guard"
).run_process


_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
command_script_target = _resolve_adapter_module.command_script_target
_yaml_output_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
)
emit_yaml = _yaml_output_module.emit_yaml

VERSION_RE = re.compile(r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-[0-9A-Za-z.-]+)?$")
SYNC_TIMEOUT_SECONDS = 300


def parse_version(version: str) -> tuple[int, int, int]:
    match = VERSION_RE.fullmatch(version)
    if match is None:
        raise SystemExit(f"Unsupported version format: {version}")
    return tuple(int(match.group(name)) for name in ("major", "minor", "patch"))


def bump_part(version: str, part: str) -> str:
    major, minor, patch = parse_version(version)
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "major":
        return f"{major + 1}.0.0"
    raise SystemExit(f"Unsupported bump part: {part}")


def write_packaging_version(manifest_path: Path, new_version: str) -> str:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    old_version = data["version"]
    data["version"] = new_version
    data["claude"]["manifest"]["version"] = new_version
    data["codex"]["manifest"]["version"] = new_version
    manifest_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return old_version


def run_sync(repo_root: Path, command: str) -> None:
    result = run_process(
        command,
        cwd=repo_root,
        shell=True,
        timeout_seconds=SYNC_TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise SystemExit(
            f"sync_command failed with {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root used to resolve the release adapter",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--part", choices=("patch", "minor", "major"), help="Semver component to bump"
    )
    group.add_argument("--set-version", help="Explicit version string to set (overrides --part)")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        raise SystemExit(f"release adapter is invalid: {adapter['errors']}")
    data = adapter["data"]
    manifest_path = repo_root / data["packaging_manifest_path"]
    if not manifest_path.is_file():
        raise SystemExit(f"Packaging manifest not found: {manifest_path}")

    # BEFORE the manifest is written. `sync_command` is an EXECUTED field whose
    # inferred default names this authoring repo's own `scripts/`, so a consuming repo
    # that never wrote a release adapter inherits a command that cannot run. Checked
    # after the write, the bump would land and the sync would not: a version bumped in
    # `packaging/` with an unsynced plugin mirror, repaired only by hand. The recognizer
    # answers `None` for any command shape it cannot read, and `None` is not a refusal.
    sync_target = command_script_target(data["sync_command"])
    if sync_target is not None and not (repo_root / sync_target).exists():
        raise SystemExit(
            f"sync_command names {sync_target!r}, which does not exist under {repo_root}.\n"
            f"Nothing was bumped. `sync_command` is RUN after the version is written, so a "
            f"missing script would leave a bumped manifest with an unsynced plugin mirror.\n"
            f"Set `sync_command` in this repo's release adapter to the command that "
            f"regenerates its materialized plugin export."
        )

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    current_version = manifest["version"]
    if args.set_version is not None:
        parse_version(args.set_version)
        target_version = args.set_version
    else:
        target_version = bump_part(current_version, args.part)
    old_version = write_packaging_version(manifest_path, target_version)
    run_sync(repo_root, data["sync_command"])

    emit_yaml(
        {
            "package_id": data["package_id"],
            "old_version": old_version,
            "new_version": target_version,
            "packaging_manifest_path": str(manifest_path),
            "sync_command": data["sync_command"],
        }
    )


if __name__ == "__main__":
    main()
