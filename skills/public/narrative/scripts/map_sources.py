#!/usr/bin/env python3
from __future__ import annotations

import argparse
import runpy
import subprocess
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process


def _run_git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return run_process(["git", *args], cwd=repo_root, timeout_seconds=None)


def _git_freshness(repo_root: Path, remote_name: str) -> dict[str, object]:
    if not (repo_root / ".git").exists():
        return {
            "status": "not-git",
            "remote_name": remote_name,
            "ahead_count": 0,
            "ahead_examples": [],
        }

    remote_result = _run_git(repo_root, "remote", "get-url", remote_name)
    if remote_result.returncode != 0:
        return {
            "status": "missing-remote",
            "remote_name": remote_name,
            "ahead_count": 0,
            "ahead_examples": [],
            "detail": (remote_result.stderr or remote_result.stdout).strip(),
        }

    upstream_result = _run_git(
        repo_root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
    )
    upstream_ref = (
        upstream_result.stdout.strip()
        if upstream_result.returncode == 0 and upstream_result.stdout.strip()
        else f"{remote_name}/main"
    )

    count_result = _run_git(repo_root, "rev-list", "--count", f"HEAD..{upstream_ref}")
    if count_result.returncode != 0:
        return {
            "status": "unavailable",
            "remote_name": remote_name,
            "upstream_ref": upstream_ref,
            "ahead_count": 0,
            "ahead_examples": [],
            "detail": (count_result.stderr or count_result.stdout).strip(),
        }

    ahead_count = int((count_result.stdout or "0").strip() or "0")
    log_result = _run_git(repo_root, "log", "--oneline", "-n", "5", f"HEAD..{upstream_ref}")
    ahead_examples = [line for line in log_result.stdout.splitlines() if line.strip()]
    return {
        "status": "ahead" if ahead_count else "current",
        "remote_name": remote_name,
        "upstream_ref": upstream_ref,
        "ahead_count": ahead_count,
        "ahead_examples": ahead_examples,
    }


def _status_lines(repo_root: Path, paths: list[str]) -> list[str]:
    if not paths:
        return []
    result = _run_git(repo_root, "status", "--short", "--", *paths)
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root to map narrative source documents in",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    # GUARDED AT THE READ SITE. This command's whole output is a map OF THE REPO'S OWN
    # narrative sources, so an unhonored declaration does not degrade it -- it maps a
    # different set of documents and says nothing about the substitution. Measured on the
    # real CLI at `724fe8a55`: a repo declaring `source_documents: [docs/mine-narrative.md]`
    # under `version: 9` reported `source_documents: [README.md]`, the inferred default,
    # exit 0. The census row notes the emitted payload does not even carry an adapter
    # validity field, so no consumer of this map could tell.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="narrative-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    source_documents = list(data.get("source_documents", []))
    mutable_documents = set(data.get("mutable_documents", []))
    status_lines = _status_lines(repo_root, source_documents)
    payload = {
        "artifact_path": adapter["artifact_path"],
        "adapter_path": adapter["path"],
        "source_documents": [
            {
                "path": path,
                "exists": (repo_root / path).is_file(),
                "mutable": path in mutable_documents,
            }
            for path in source_documents
        ],
        "dirty_paths": status_lines,
        "freshness": _git_freshness(repo_root, str(data.get("remote_name", "origin"))),
    }
    yaml_output.emit_yaml(payload)


if __name__ == "__main__":
    main()
