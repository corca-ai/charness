#!/usr/bin/env python3
"""impl stop-gate cross-surface escalation probe (the objective ownership override).

If the slice's changed paths match this repo's cross-surface probe — the same
critique-adapter config the critique validator's severity upgrade reads — emit
``triggered: true`` so the impl stop gate escalates the slice to a standalone
`critique`. That produces the durable artifact the boundary presence-floor bites,
even when the agent self-judged the change a small local slice (cadence rung 2)
— exactly the path a symptom-driven local fix takes when it looks finished
because a unit test at the nearest surface passes. An empty probe config never
triggers (opt-in): a repo that configures no cross-surface probe keeps the
always-brief + closeout presence-floor without this objective override.
"""

from __future__ import annotations

import argparse
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

_boundary_probe_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.boundary_probe_lib")
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="impl cross-surface escalation probe (ownership override)")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root used to resolve probe config and changed paths.",
    )
    parser.add_argument("--changed-path", nargs="*", help="Explicit changed paths (bypasses git).")
    parser.add_argument("--changed-ref", help="Git ref/range for changed-path discovery (else working-tree diff).")
    parser.add_argument("--detail", action="store_true", help="Emit the full payload as YAML.")
    return parser.parse_args()


def build_payload(repo_root: Path, changed_path, changed_ref) -> dict:
    triggered, changed, probe = _boundary_probe_lib.resolve_hit(
        repo_root, changed_path=changed_path, changed_ref=changed_ref
    )
    reason = (
        "changed paths match the repo cross-surface probe — escalate this slice to a standalone "
        "critique so the boundary presence-floor records a typed disposition (the objective override)"
        if triggered
        else "no cross-surface probe hit (empty config or no match) — the always-brief + closeout "
        "presence-floor still apply"
    )
    return {"triggered": triggered, "changed_paths": changed, "probe": probe, "reason": reason}


def main() -> int:
    args = parse_args()
    payload = build_payload(args.repo_root.resolve(), args.changed_path, args.changed_ref)
    if args.detail:
        yaml_output.emit_yaml(payload)
    else:
        print(payload["reason"])
        print(f"triggered: {str(payload['triggered']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
