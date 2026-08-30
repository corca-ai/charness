from __future__ import annotations

import os
import subprocess
import sys
from functools import cache
from pathlib import Path

from tests.script_main import load_script_module, run_loaded_script_main

ROOT = Path(__file__).resolve().parents[2]

# Keep this exception narrow: only deliberately reviewed quality-gate semantic
# entry points are listed here. Other scripts retain their process contract
# unless they are explicitly reviewed and added to this mapping.
_IN_PROCESS_SCRIPT_MODULES = {
    "scripts/check_code_lengths.py": (
        "tests.quality_gates.support_check_code_lengths",
        ROOT / "scripts" / "check_code_lengths.py",
    ),
    "scripts/validate_retro_artifact.py": (
        "tests.quality_gates.support_validate_retro_artifact",
        ROOT / "scripts" / "validate_retro_artifact.py",
    ),
    "skills/public/retro/scripts/audit_codex_session.py": (
        "tests.quality_gates.support_audit_codex_session",
        ROOT / "skills" / "public" / "retro" / "scripts" / "audit_codex_session.py",
    ),
    "skills/public/quality/scripts/check_dup_ratchet.py": (
        "tests.quality_gates.support_check_dup_ratchet",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_dup_ratchet.py",
    ),
    "scripts/check_issue_closeout_commit_msg.py": (
        "tests.quality_gates.support_check_issue_closeout_commit_msg",
        ROOT / "scripts" / "check_issue_closeout_commit_msg.py",
    ),
    "scripts/validate_skills.py": (
        "tests.quality_gates.support_validate_skills",
        ROOT / "scripts" / "validate_skills.py",
    ),
    "scripts/check_spec_evidence_durability.py": (
        "tests.quality_gates.support_check_spec_evidence_durability",
        ROOT / "scripts" / "check_spec_evidence_durability.py",
    ),
    "scripts/validate_current_pointer_freshness.py": (
        "tests.quality_gates.support_validate_current_pointer_freshness",
        ROOT / "scripts" / "validate_current_pointer_freshness.py",
    ),
    "skills/public/quality/scripts/check_changed_line_coverage.py": (
        "tests.quality_gates.support_check_changed_line_coverage",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_changed_line_coverage.py",
    ),
    "scripts/validate_critique_artifacts.py": (
        "tests.quality_gates.support_validate_critique_artifacts",
        ROOT / "scripts" / "validate_critique_artifacts.py",
    ),
    "skills/public/quality/scripts/check_runtime_budget.py": (
        "tests.quality_gates.support_check_runtime_budget",
        ROOT / "skills" / "public" / "quality" / "scripts" / "check_runtime_budget.py",
    ),
    "scripts/check_changed_line_mutation_coverage.py": (
        "tests.quality_gates.support_check_changed_line_mutation_coverage",
        ROOT / "scripts" / "check_changed_line_mutation_coverage.py",
    ),
}


def _repo_script_key(script: Path) -> str | None:
    """Return the stable allowlist key for a repo-owned script path."""
    candidate = script if script.is_absolute() else ROOT / script
    try:
        resolved = candidate.resolve()
    except OSError:
        return None
    for key, (_module_name, module_path) in _IN_PROCESS_SCRIPT_MODULES.items():
        try:
            if resolved == module_path.resolve():
                return key
        except OSError:
            continue
    return None


@cache
def _load_allowlisted_script(key: str) -> object:
    """Lazily load one allowlisted module, once per test worker."""
    module_name, module_path = _IN_PROCESS_SCRIPT_MODULES[key]
    return load_script_module(module_name, module_path)


def run_allowlisted_script(
    script: Path,
    args: tuple[str, ...],
    *,
    cwd: Path | None,
    env: dict[str, str] | None,
) -> subprocess.CompletedProcess[str] | None:
    """Run an allowlisted CLI main while retaining subprocess-like isolation."""
    key = _repo_script_key(script)
    if key is None:
        return None
    previous_cwd = Path.cwd()
    try:
        # `run_script` defaults child processes to ROOT; mirror that when pytest
        # itself was launched from another directory, then restore it on failure too.
        os.chdir(cwd or ROOT)
        result = run_loaded_script_main(
            str(script),
            _load_allowlisted_script(key),
            *args,
            env=env,
        )
    finally:
        os.chdir(previous_cwd)
    return subprocess.CompletedProcess(
        [sys.executable, str(script), *args],
        result.returncode,
        result.stdout,
        result.stderr,
    )
