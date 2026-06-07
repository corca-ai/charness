#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from runtime_bootstrap import import_repo_module

_surfaces_lib = import_repo_module(__file__, "scripts.surfaces_lib")

# Single source of truth (#314) for the fast structural checkers that must run
# in BOTH the per-slice aggregate (run_slice_closeout) and the literal git
# pre-commit gate. Both paths draw the subset from surface verify_commands; this
# allowlist is the reconciliation point so "passes the aggregate" and "passes
# pre-commit" become one guarantee. Entries MUST be cheap (<1s), deterministic,
# and path-scoped -- never a broad pytest in the pre-commit path.
FAST_SURFACE_VERIFY_COMMANDS: dict[str, str] = {
    "python3 scripts/validate_skill_ergonomics.py --repo-root .": "validate-skill-ergonomics",
    "python3 scripts/check_boundary_bypass_ratchet.py --repo-root .": "check-boundary-bypass-ratchet",
}


@dataclass(frozen=True)
class GateCommand:
    label: str
    argv: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"label": self.label, "argv": list(self.argv)}


def collect_staged_paths(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to list staged paths")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _any_starts(paths: list[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in paths)


def fast_surface_verify_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Fast structural checkers from matched surface verify_commands (#314).

    Reconciles the pre-commit gate with the per-slice aggregate: when a touched
    surface lists one of ``FAST_SURFACE_VERIFY_COMMANDS`` in its verify_commands,
    that same cheap checker runs at the literal git pre-commit boundary, so the
    aggregate and pre-commit agree on the fast gate subset. Degrades to no extra
    gates when the surfaces manifest is absent or unreadable (e.g. tmp repos).
    """
    if not paths:
        return []
    try:
        manifest = _surfaces_lib.load_surfaces(repo_root, required=False)
        if manifest is None:
            return []
        matched = _surfaces_lib.match_surfaces(manifest, paths)
    except _surfaces_lib.SurfaceError:
        return []
    gates: list[GateCommand] = []
    seen: set[str] = set()
    for command in matched["verify_commands"]:
        label = FAST_SURFACE_VERIFY_COMMANDS.get(command)
        if label is None or label in seen:
            continue
        seen.add(label)
        gates.append(GateCommand(label, tuple(shlex.split(command))))
    return gates


_MIRROR_PREFIXES = (
    "scripts/",
    "skills/",
    "profiles/",
    "presets/",
    "integrations/",
    "plugins/",
    ".claude-plugin/",
    ".codex-plugin/",
    ".agents/plugins/",
)


def _mirror_drift_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    touches_mirror = any(
        path.startswith(_MIRROR_PREFIXES)
        or path == "README.md"
        or path in {"runtime_bootstrap.py", "skill_runtime_bootstrap.py"}
        for path in paths
    )
    if not touches_mirror:
        return []
    return [
        GateCommand(
            "staged-plugin-mirror-drift",
            ("python3", "scripts/check_staged_mirror_drift.py", "--repo-root", str(repo_root)),
        )
    ]


def _skill_core_headroom_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """#319: gate changed public/support SKILL.md cores against the core_nonempty
    >=4 headroom buffer at the commit boundary (a ratchet that grandfathers
    existing under-buffer skills), so authoring to the 160 hard limit no longer
    passes the per-slice gate and fails only the broad core-headroom test.
    """
    staged_skill_md = [
        path
        for path in paths
        if path.startswith(("skills/public/", "skills/support/"))
        and path.endswith("/SKILL.md")
        and path.count("/") == 3
    ]
    if not staged_skill_md:
        return []
    return [
        GateCommand(
            "check-skill-core-headroom (staged)",
            (
                "python3",
                "scripts/check_skill_surface_preflight.py",
                "--repo-root",
                str(repo_root),
                "--changed-skill-md",
                *staged_skill_md,
            ),
        )
    ]


def staged_commit_gate_plan(
    repo_root: Path,
    staged_paths: list[str] | None = None,
    *,
    ruff_path: str | None = None,
) -> list[GateCommand]:
    paths = staged_paths if staged_paths is not None else collect_staged_paths(repo_root)
    staged_py = [path for path in paths if path.endswith(".py")]
    ruff = shutil.which("ruff") if ruff_path is None else ruff_path
    plan: list[GateCommand] = []

    if paths:
        plan.append(
            GateCommand(
                "check-staged-reversion",
                ("python3", "scripts/check_staged_reversion.py", "--repo-root", str(repo_root)),
            )
        )

    if staged_py:
        plan.append(GateCommand("py_compile (staged)", ("python3", "-m", "py_compile", *staged_py)))
        if ruff:
            plan.append(GateCommand("ruff (staged)", ("ruff", "check", *staged_py)))
        plan.append(
            GateCommand(
                "check-python-lengths (staged)",
                (
                    "python3",
                    "scripts/check_python_lengths.py",
                    "--repo-root",
                    str(repo_root),
                    "--paths",
                    *staged_py,
                ),
            )
        )

    if any(path.endswith(".py") and (path.startswith("scripts/") or path.startswith("skills/")) for path in paths):
        plan.append(
            GateCommand(
                "validate-attention-state-visibility",
                (
                    "python3",
                    "scripts/validate_attention_state_visibility.py",
                    "--repo-root",
                    str(repo_root),
                    "--scan-root",
                    "scripts",
                    "--scan-root",
                    "skills",
                    "--scan-root-map",
                    "../charness-support=skills/support",
                ),
            )
        )

    if _any_starts(paths, "skills/"):
        plan.append(GateCommand("validate-skills", ("python3", "scripts/validate_skills.py", "--repo-root", str(repo_root))))
        plan.append(GateCommand("run-evals", ("python3", "scripts/run_evals.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "profiles/"):
        plan.append(GateCommand("validate-profiles", ("python3", "scripts/validate_profiles.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, ".agents/"):
        plan.append(GateCommand("validate-adapters", ("python3", "scripts/validate_adapters.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "presets/"):
        plan.append(GateCommand("validate-presets", ("python3", "scripts/validate_presets.py", "--repo-root", str(repo_root))))
    if _any_starts(paths, "integrations/"):
        plan.append(GateCommand("validate-integrations", ("python3", "scripts/validate_integrations.py", "--repo-root", str(repo_root))))

    plan.extend(_mirror_drift_gates(repo_root, paths))

    if any(path.endswith(".md") for path in paths):
        plan.append(GateCommand("check-doc-links", ("python3", "scripts/check_doc_links.py", "--repo-root", str(repo_root))))
        plan.append(GateCommand("check-markdown", ("./scripts/check-markdown.sh",)))

    plan.extend(_skill_core_headroom_gates(repo_root, paths))

    # #314: append the fast surface verify checkers so the literal pre-commit gate
    # agrees with the per-slice aggregate on the cheap structural subset.
    plan.extend(fast_surface_verify_gates(repo_root, paths))

    return plan


# #332: the cheap structural sweep -- the presence/structural gates a new
# skill-package or scripts/*.py edit must NOT be able to defer to the slow broad
# gate (the recurring #308/#325/#329 class). Selected by label from
# staged_commit_gate_plan so the plan stays the single source of truth (no
# parallel gate list): ergonomics (skill packages), attention-state visibility
# (scripts/**+skills/** *.py), and the SKILL.md authoring preflight. The full
# run_slice_closeout path runs this subset FIRST, fail-fast, so the cheap verdict
# precedes surface-match / cautilus / broad pytest -- reconciling the broad path
# with the --predict-commit boundary instead of reaching the gates only late.
STRUCTURAL_SWEEP_LABELS: frozenset[str] = frozenset(
    {
        "validate-attention-state-visibility",
        "validate-skill-ergonomics",
        "check-skill-core-headroom (staged)",
    }
)


def structural_sweep_gates(repo_root: Path, paths: list[str] | None = None) -> list[GateCommand]:
    """The #332 cheap structural-sweep subset of ``staged_commit_gate_plan``.

    Reuses ``staged_commit_gate_plan`` (single source of truth) and filters to
    the presence/structural gates named in the #332 goal, so the full closeout
    runs the same cheap verdict first without re-running ruff/lengths/skills/
    run-evals from the verify phase. Empty for changes that touch no structural
    file class (e.g. docs-only), so it is a no-op there.
    """
    return [
        command
        for command in staged_commit_gate_plan(repo_root, paths)
        if command.label in STRUCTURAL_SWEEP_LABELS
    ]


def structural_sweep_planned_commands(repo_root: Path, paths: list[str]) -> list[dict[str, str]]:
    """#332: the structural sweep rendered as ``--plan-only`` planned commands,
    prepended to the full closeout plan so plan output reflects what runs first."""
    return [
        {"phase": "structural-sweep", "command": shlex.join(gate.argv)}
        for gate in structural_sweep_gates(repo_root, paths)
    ]


def run_structural_sweep_preflight(repo_root: Path, paths: list[str], *, run_command) -> dict[str, object]:
    """Run the #332 cheap structural sweep fail-fast (first non-zero gate stops).

    Returns a payload with ``status`` (``ok``/``failed``), the planned gate
    labels, executed results, and the first ``failed_label``.
    """
    gates = structural_sweep_gates(repo_root, paths)
    executed: list[dict[str, object]] = []
    for command in gates:
        result = run_command(repo_root, shlex.join(command.argv), "structural-sweep")
        executed.append(result)
        if result["returncode"] != 0:
            return {
                "status": "failed",
                "planned": [gate.label for gate in gates],
                "executed": executed,
                "failed_label": command.label,
            }
    return {
        "status": "ok",
        "planned": [gate.label for gate in gates],
        "executed": executed,
        "failed_label": None,
    }


def block_on_structural_sweep(
    repo_root: Path,
    payload: dict[str, object],
    *,
    as_json: bool,
    plan_only: bool,
    run_command,
    emit_payload,
) -> int | None:
    """#332 fail-fast guard for the full ``run_slice_closeout`` path.

    Runs the cheap structural sweep FIRST so its verdict precedes surface-match /
    cautilus / broad pytest. Mirrors the ``_maybe_block_on_*`` helpers: returns
    an exit code when blocking, else ``None``. No-op in ``plan_only`` (the sweep
    commands are surfaced through the planned output instead).
    """
    if plan_only:
        return None
    sweep = run_structural_sweep_preflight(repo_root, list(payload["changed_paths"]), run_command=run_command)
    payload["structural_sweep"] = sweep
    if sweep["status"] != "failed":
        return None
    payload["status"] = "blocked"
    payload["error"] = (
        f"cheap structural sweep failed at `{sweep['failed_label']}` (#332): the "
        "#329-class commit-boundary gate must not defer to the broad gate; fix and rerun"
    )
    if not as_json:
        failing = sweep["executed"][-1]
        for stream, target in ((failing["stdout"], sys.stdout), (failing["stderr"], sys.stderr)):
            if stream:
                print(stream, end="" if stream.endswith("\n") else "\n", file=target)
    return emit_payload(payload, as_json=as_json, stderr_message=payload["error"])


def run_predict_commit(
    repo_root: Path,
    *,
    paths: list[str] | None,
    as_json: bool,
    plan_only: bool,
    run_command,
    emit_payload,
    advisory_provider=None,
) -> int:
    selected_paths = paths if paths is not None else collect_staged_paths(repo_root)
    command_plan = staged_commit_gate_plan(repo_root, selected_paths)
    # Advisory providers emit exit-0 informational lines (e.g. the RCA-link nudge)
    # that never block the commit; staged_commit_gate_plan stays surface-agnostic.
    advisories = list(advisory_provider(repo_root, selected_paths)) if advisory_provider else []
    payload: dict[str, object] = {
        "status": "planned" if plan_only else "completed",
        "changed_paths": selected_paths,
        "planned_commands": [
            {"phase": "pre-commit", "label": command.label, "argv": list(command.argv)}
            for command in command_plan
        ],
        "executed_commands": [],
        "advisories": advisories,
    }
    if not as_json:
        for line in advisories:
            print(line)
    if plan_only:
        if as_json:
            return emit_payload(payload, as_json=as_json)
        for command in command_plan:
            print(f"charness pre-commit: {command.label}")
        return 0
    if not command_plan and not as_json:
        return 0
    for command in command_plan:
        if not as_json:
            print(f"charness pre-commit: {command.label}")
        result = run_command(repo_root, shlex.join(command.argv), "pre-commit")
        payload["executed_commands"].append(result)
        if result["returncode"] != 0:
            payload["status"] = "failed"
            if as_json:
                return emit_payload(payload, as_json=as_json)
            if result["stdout"]:
                print(result["stdout"], end="" if result["stdout"].endswith("\n") else "\n")
            if result["stderr"]:
                print(result["stderr"], end="" if result["stderr"].endswith("\n") else "\n", file=sys.stderr)
            return 1
    if not as_json:
        print("charness pre-commit: ok")
        return 0
    return emit_payload(payload, as_json=as_json)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--paths", nargs="*")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-ruff", action="store_true", help="Plan as if ruff is unavailable.")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    paths = args.paths if args.paths is not None else None
    ruff_path = "" if args.no_ruff else None
    plan = staged_commit_gate_plan(repo_root, paths, ruff_path=ruff_path)
    if args.json:
        print(json.dumps([command.as_dict() for command in plan], indent=2))
    else:
        for command in plan:
            print(command.label)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
