#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace
from typing import Any

ADAPTER_RELATIVE_PATH = Path(".agents/retro-adapter.yaml")
SUMMARY_RELATIVE_PATH = Path("charness-artifacts/retro/recent-lessons.md")
GITIGNORE_RELATIVE_PATH = Path(".gitignore")
GITIGNORE_RUNTIME_LINES = (".charness/retro/",)
LEDGER_RELATIVE_PATH = Path("charness-artifacts/retro/lesson-ledger.json")


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


# Loaded eagerly, unlike `_opt_in_command`'s defensive runtime probe below: the
# report is only ever DELIVERED through this renderer, so a layout that cannot
# reach it has no output channel to degrade into.
emit_yaml = _load_skill_runtime_bootstrap().load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
).emit_yaml

# The same three words `check_auto_trigger.py` and the session-start lesson block
# speak. No fourth spelling: `available`, `wired`, and a bare `enabled: false` are
# how two surfaces end up describing the same repo differently.
STATE_EVALUATED = "evaluated"
STATE_NOT_CONFIGURED = "not-configured"
STATE_NOT_ESTABLISHED = "not-established"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repo root whose retro selection-index memory should be seeded")
    return parser.parse_args()


def adapter_text(repo_name: str) -> str:
    # The two auto-retro trigger keys are seeded COMMENTED OUT, not as `[]`.
    #
    # A literal `[]` is read by `list_field_state` as `explicit-empty`, which
    # `check_auto_trigger.py` reports as `intentional-empty` — an opt-out — and then
    # suppresses its own remediation for. Seeding that meant setup recorded a decision
    # the repo had never made, and the probe then reported the unmade decision as
    # `triggered: false`: two mechanisms agreeing on the wrong default, and a retro
    # trigger that was never wired in a repo where nothing looked wrong.
    #
    # Commented, the keys are `unset`, the probe answers `not-established` instead of
    # `no`, and the remediation fires until a human picks one of the two real answers.
    # Deliberately NOT seeded with non-empty defaults: this repo cannot know a
    # consumer's trigger surfaces, and a guessed glob is the same unmade decision in
    # the opposite direction.
    return "\n".join(
        [
            "version: 1",
            f"repo: {repo_name}",
            "language: en",
            "output_dir: charness-artifacts/retro",
            "preset_id: portable-defaults",
            "customized_from: portable-defaults",
            "summary_path: charness-artifacts/retro/recent-lessons.md",
            "evidence_paths: []",
            "metrics_commands: []",
            "",
            "# Auto-retro triggers: DECIDE, do not leave unanswered.",
            "# Uncomment and fill in the surfaces/globs whose change should force a short",
            "# session retro, or set BOTH to [] to record an intentional opt-out. While both",
            "# stay commented out, check_auto_trigger.py reports `not-established` (exit 3)",
            "# rather than a `triggered: false` that would look like a judged answer.",
            "# auto_session_trigger_surfaces: []",
            "# auto_session_trigger_path_globs: []",
            "",
        ]
    )


def summary_text() -> str:
    return "\n".join(
        [
            "# Recent Retro Lessons",
            "",
            "## Current Focus",
            "",
            "- No durable retro summary yet. Refresh this file after the first meaningful retro.",
            "",
            "## Repeat Traps",
            "",
            "- None recorded yet.",
            "",
            "## Next-Time Checklist",
            "",
            "- Run `retro` after a meaningful slice and refresh this digest from the latest durable artifact.",
            "",
            "## Sources",
            "",
            "- none yet",
            "",
        ]
    )


def write_if_missing(path: Path, text: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def ensure_gitignore_lines(path: Path, lines: tuple[str, ...]) -> bool:
    existing = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    missing = [line for line in lines if line not in existing]
    if not missing:
        return False
    updated = [*existing, *missing]
    path.write_text("\n".join(updated) + "\n", encoding="utf-8")
    return True


def _opt_in_command(repo_root: Path) -> tuple[str | None, str | None]:
    """The runnable ledger opt-in command, resolved by the validator that owns it.

    Delegated rather than re-derived: `validate_retro_artifact` already resolves
    repo-local `scripts/` first and the installed plugin copy otherwise, and a
    second copy here is how setup starts telling a consuming repo to run a path it
    does not have. Loaded defensively -- setup runs in repos and hosts whose
    layout need not expose the repo-root modules, and a report that cannot name
    the command must say so rather than take the seam bootstrap down with it.
    """
    try:
        runtime = _load_skill_runtime_bootstrap()
        validator = runtime.load_repo_module_from_skill_script(
            __file__, "scripts.validate_retro_artifact"
        )
        return validator.lesson_ledger_bootstrap_command(repo_root), None
    except Exception as exc:  # host layout / import surface, never a verdict
        return None, f"{type(exc).__name__}: {exc}"


def lesson_loop_report(repo_root: Path) -> dict[str, Any]:
    """Report whether this repo declares a lesson evaluator. Create NOTHING.

    Deliberately a REPORT. `init_lesson_ledger.py` states that the opt-in must be
    an operator command rather than a side effect of `seed_retro_memory.py` or
    `persist_retro_artifact.py`, because declaring an evaluator turns on a
    per-retro disposition duty -- a repo-level commitment, not something a setup
    run should do to someone. Without this line the state was invisible: the
    SessionStart lesson block stays silent for an un-opted-in repo (correctly, it
    is a real opt-out), so nothing anywhere told a consuming repo the evaluating
    half of the lesson lifecycle existed and was reachable.

    `not-established` is reserved for a ledger path that exists but is not a
    readable JSON file. Full validation is NOT attempted here: it needs the ledger
    library and a live retro corpus, and setup must not report a repo's evaluator
    as broken on the strength of a probe it could not run. The retro planner and
    the continuity gate own that verdict.
    """
    ledger = repo_root / LEDGER_RELATIVE_PATH
    command, unavailable = _opt_in_command(repo_root)
    report: dict[str, Any] = {"ledger_path": str(LEDGER_RELATIVE_PATH)}
    if unavailable is not None:
        report["opt_in_command_unavailable_reason"] = unavailable
    if not ledger.is_file():
        return {
            **report,
            "state": STATE_NOT_CONFIGURED,
            "created": False,
            "reason": (
                "no lesson evaluator is declared, so the retro disposition floor is inert and "
                "the session-start lesson block injects nothing"
            ),
            "opt_in_command": command,
        }
    try:
        json.loads(ledger.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {
            **report,
            "state": STATE_NOT_ESTABLISHED,
            "created": False,
            "reason": "a lesson ledger exists but could not be read as JSON",
            "undetermined": [f"{type(exc).__name__}: {exc}"],
        }
    return {
        **report,
        "state": STATE_EVALUATED,
        "created": False,
        "reason": (
            "a lesson evaluator is declared; every eligible retro owes a `Lesson evaluation:` "
            "disposition and the session-start hook injects the lesson list"
        ),
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    adapter_path = repo_root / ADAPTER_RELATIVE_PATH
    summary_path = repo_root / SUMMARY_RELATIVE_PATH
    gitignore_path = repo_root / GITIGNORE_RELATIVE_PATH
    created_adapter = write_if_missing(adapter_path, adapter_text(repo_root.name))
    created_summary = write_if_missing(summary_path, summary_text())
    updated_gitignore = ensure_gitignore_lines(gitignore_path, GITIGNORE_RUNTIME_LINES)
    emit_yaml(
        {
            "adapter_path": str(ADAPTER_RELATIVE_PATH),
            "summary_path": str(SUMMARY_RELATIVE_PATH),
            "gitignore_path": str(GITIGNORE_RELATIVE_PATH),
            "created": {
                "adapter": created_adapter,
                "summary": created_summary,
                "gitignore": updated_gitignore,
            },
            "lesson_loop": lesson_loop_report(repo_root),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
