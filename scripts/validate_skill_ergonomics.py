#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import load_path_module  # noqa: E402
from scripts.yaml_output import emit_yaml  # noqa: E402


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parent.parent


def _helper_path(repo_root: Path) -> Path:
    candidates = (
        repo_root / "skills" / "public" / "quality" / "scripts" / "validate_skill_ergonomics.py",
        repo_root / "skills" / "quality" / "scripts" / "validate_skill_ergonomics.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "missing quality ergonomics helper; expected one of "
        "`skills/public/quality/scripts/validate_skill_ergonomics.py` or "
        "`skills/quality/scripts/validate_skill_ergonomics.py`"
    )


REPO_ROOT = _runtime_root()
HELPER_PATH = _helper_path(REPO_ROOT)
HELPER = load_path_module("validate_skill_ergonomics_entrypoint", HELPER_PATH)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    report = HELPER.evaluate(args.repo_root.resolve())
    # Unconditional YAML. The retired `HELPER._format_human` rendering was a strict
    # projection of the report's own `adapter_errors`, `rules`, `warnings`,
    # `discovery_errors`, and `violations` entries, which the payload carries.
    emit_yaml(report)
    return 1 if HELPER.has_failures(report) else 0


if __name__ == "__main__":
    sys.exit(main())
