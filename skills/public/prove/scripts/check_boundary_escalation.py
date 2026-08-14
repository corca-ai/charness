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

Exit contract. `triggered` is a VERDICT KEY and is emitted only when the probe
actually ran; ``state`` is always emitted and is the key to read first:

- ``0`` + ``state: evaluated``       -> ``triggered: true|false`` is a real answer;
- ``0`` + ``state: not-configured``  -> ``triggered: false``, the opt-in design (DBD-4);
- ``3`` + ``state: not-established`` -> NO ``triggered`` key at all; the probe could not
  tell, and a caller that treats this as "no" is skipping the escalation on a failure
  mode rather than on a finding.

3, not 1, matching `scripts/run-quality.sh`'s ``UNESTABLISHED_EXIT``: "ran, established
nothing" is neither a pass nor a failure. The payload still goes to STDOUT so a `--detail`
caller parses one document in every state; the byte, not the stream, carries the refusal.
Undetermined is deliberately NOT reported as ``triggered: true``: escalating on absence
would convert one silent miss into a universal false escalation.
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


UNDETERMINED_EXIT = 3

_REASON = {
    _boundary_probe_lib.PROBE_NOT_CONFIGURED: (
        "this repo declares no cross-surface probe (`boundary_cross_surface_globs` / "
        "`boundary_cross_surface_surfaces`), so the objective override is off by design — "
        "the always-brief + closeout presence-floor still apply"
    ),
    _boundary_probe_lib.PROBE_NOT_ESTABLISHED: (
        "the cross-surface probe is CONFIGURED but could not be evaluated, so this run has no "
        "answer either way — do not read it as `no escalation`; fix the cause below, or re-run "
        "with an explicit --changed-path/--changed-ref, then decide"
    ),
}


def build_payload(repo_root: Path, changed_path, changed_ref) -> dict:
    state, changed, probe = _boundary_probe_lib.resolve_probe_state(
        repo_root, changed_path=changed_path, changed_ref=changed_ref
    )
    # `state` first, `triggered` second and ONLY when the probe ran. The old payload led
    # with `triggered: false` in all three worlds, and the non---detail path printed just
    # that line, so an unconfigured probe and an unresolvable one read exactly like a
    # judged miss. A verdict key carries only verdicts.
    payload: dict = {"state": state["state"]}
    if state["state"] != _boundary_probe_lib.PROBE_NOT_ESTABLISHED:
        payload["triggered"] = state["hit"]
    payload["changed_paths"] = changed
    payload["probe"] = probe
    payload["reason"] = _REASON.get(
        state["state"],
        "changed paths match the repo cross-surface probe — escalate this slice to a standalone "
        "critique so the boundary presence-floor records a typed disposition (the objective override)"
        if state["hit"]
        else f"the cross-surface probe was evaluated over {state['scanned_paths']} changed path(s) "
        "and none matched — the always-brief + closeout presence-floor still apply",
    )
    if state["undetermined_reasons"]:
        payload["undetermined"] = state["undetermined_reasons"]
    if state["unresolved_surfaces"]:
        payload["unresolved_surfaces"] = state["unresolved_surfaces"]
    return payload


def main() -> int:
    args = parse_args()
    payload = build_payload(args.repo_root.resolve(), args.changed_path, args.changed_ref)
    if args.detail:
        yaml_output.emit_yaml(payload)
    else:
        print(payload["reason"])
        print(f"state: {payload['state']}")
        for undetermined in payload.get("undetermined", []):
            print(f"undetermined: {undetermined}")
        if "triggered" in payload:
            print(f"triggered: {str(payload['triggered']).lower()}")
    return (
        UNDETERMINED_EXIT
        if payload["state"] == _boundary_probe_lib.PROBE_NOT_ESTABLISHED
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
