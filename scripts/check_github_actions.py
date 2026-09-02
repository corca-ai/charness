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

from scripts.runtime_bootstrap import import_repo_module, repo_root_from_script  # noqa: E402
from scripts.yaml_output import render_yaml  # noqa: E402

REPO_ROOT = repo_root_from_script(__file__)

_scripts_github_actions_lib_module = import_repo_module(__file__, "scripts.github_actions_lib")
collect_github_actions_drift = _scripts_github_actions_lib_module.collect_github_actions_drift

# Folded in from the deleted human renderer. Output is unconditionally YAML now,
# so the remedy prose has to live in the payload or it is simply gone: a drift
# finding that names the offending action without saying WHICH major to move to,
# or that the rollout env vars are short-lived escape hatches, is a finding an
# operator cannot act on.
_CATEGORY_REASON = {
    "node24_incompatible": "below the Node 24-ready floor",
}
_DEFAULT_REASON = "behind the current documented major"
_GUIDANCE = (
    "Prefer direct major upgrades in the workflow file.",
    "Use `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` only as a short-lived rollout check.",
    "Use `ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION=true` only as a temporary escape hatch "
    "while removing old majors.",
)


def report(payload: dict) -> dict:
    """Fold the verdict-explaining text into the payload the gate emits."""
    out = dict(payload)
    if not payload["workflow_files"]:
        out["summary"] = "No GitHub Actions workflows detected."
        return out
    if not payload["findings"]:
        out["summary"] = (
            f"Validated GitHub Actions majors in {len(payload['workflow_files'])} workflow file(s)."
        )
        return out
    out["summary"] = "GitHub Actions major drift detected."
    out["remedies"] = [
        {
            "path": finding["path"],
            "line": finding["line"],
            "observed": f"{finding['action']}@{finding['reference']}",
            "use_instead": f"@{finding['recommended_reference']}",
            "reason": _CATEGORY_REASON.get(finding["category"], _DEFAULT_REASON),
            "node24_floor": f"v{finding['node24_major']}",
        }
        for finding in payload["findings"]
    ]
    out["guidance"] = list(_GUIDANCE)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()

    payload = collect_github_actions_drift(args.repo_root.resolve())
    # Stream choice predates the output-format migration and is preserved: a
    # failing run's report belongs on stderr, where the runner shows it.
    stream = sys.stderr if payload["findings"] else sys.stdout
    stream.write(render_yaml(report(payload)))
    return 1 if payload["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
