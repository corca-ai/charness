from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

_subprocess_guard = import_repo_module(__file__, "scripts.subprocess_guard")
run_process = _subprocess_guard.run_process

_PLAN_HELPERS_ROOT = repo_root_from_script(__file__)
_artifact_preflight = import_repo_module(__file__, "scripts.check_artifact_surface_preflight")


@dataclass(frozen=True)
class GateCommand:
    label: str
    argv: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {"label": self.label, "argv": list(self.argv)}


def _git_stdout(repo_root: Path, args: list[str], failure: str) -> str:
    """Run a read-only git query, raising with git's own message on failure.

    Bytes, not ``text=True``: the ``-z`` caller needs RAW path bytes (git stops
    C-quoting under ``-z``), so a strict locale decode would take the pre-commit
    hook down with a traceback on a latin-1 filename.
    """
    result = run_process(["git", *args], cwd=repo_root, timeout_seconds=None)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or failure)
    return result.stdout


def collect_staged_scope_paths(repo_root: Path) -> list[str]:
    """Every path this commit TOUCHES, including deletions and both rename sides.

    A deletion-only or rename-only commit has no A/C/M entry at all, so every
    surface predicate saw an empty list and the hook exited 0 having scheduled
    nothing, while the suppressed mirror-drift gate would have reported that the
    materialized plugin export no longer matched its source.
    """
    stdout = _git_stdout(
        repo_root,
        ["diff", "--cached", "--name-status", "--find-renames", "-z"],
        "failed to list staged path scope",
    )
    # `-z` because a path with a space or quote is otherwise C-quoted and would be
    # silently mis-prefixed. Fields: STATUS NUL PATH NUL, except rename/copy, which
    # is STATUS NUL SOURCE NUL DEST NUL -- both sides are touched.
    fields = [field for field in stdout.split("\0") if field]
    paths: list[str] = []
    index = 0
    while index < len(fields):
        status = fields[index]
        follows = 2 if status[:1] in {"R", "C"} else 1
        for offset in range(1, follows + 1):
            if index + offset < len(fields):
                paths.append(fields[index + offset])
        index += follows + 1
    return sorted(dict.fromkeys(paths))


def any_starts(paths: list[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in paths)


def timing_pull_gate(repo_root: Path, label: str, script: str, *args: str) -> list[GateCommand]:
    """Return a pulled timing-layer guard only when the repo owns the script."""
    if not (repo_root / script).is_file():
        return []
    return [GateCommand(label, _script_argv(script, *args))]


def provenance_contract_self_test_gate(repo_root: Path) -> list[GateCommand]:
    """Run the owning test as a second channel for the provenance checker."""
    if not (repo_root / "tests/test_provenance_contract.py").is_file():
        return []
    return [
        GateCommand(
            "check-provenance-contract-self-test",
            (
                "python3",
                "-m",
                "pytest",
                "-q",
                "tests/test_provenance_contract.py::test_contract_checker_executes_source_fixtures_in_process",
            ),
        )
    ]


def present_gate(repo_root: Path, label: str, script: str, *args: str) -> list[GateCommand]:
    """A repo-owned gate, scheduled only while its script is on disk.

    ``tools/`` modules have one supported carrier: ``python3 -m tools.<name>``.
    Keeping that rule here prevents the staged planner from reintroducing a
    path-based invocation when a moved gate is pulled to the commit boundary.
    """
    script_path = Path(script)
    path = (
        repo_root / script_path
        if script_path.parts[:1] == ("tools",)
        else repo_root / "scripts" / script
    )
    if not path.exists():
        return []
    return [GateCommand(label, _script_argv(script, *args))]


def _script_argv(script: str, *args: str) -> tuple[str, ...]:
    script_path = Path(script)
    if script_path.parts[:1] == ("tools",):
        module = script_path.with_suffix("").as_posix().replace("/", ".")
        return ("python3", "-m", module, *args)
    return ("python3", script, *args)


_INDEX_HYGIENE_GATES = (
    ("check-staged-reversion", "check_staged_reversion.py"),
    ("check-git-identity", "check_git_identity.py"),
    ("staged-worktree-consistency", "check_staged_worktree_consistency.py"),
)


def index_hygiene_gates(repo_root: Path) -> list[GateCommand]:
    """The index-state guards every non-empty staged set gets.

    Each is presence-guarded: a deletion-only commit now schedules gates, so a commit
    that removes one of these scripts would otherwise refuse itself on the missing
    file with no way forward but `--no-verify`.
    """
    return [
        GateCommand(label, ("python3", f"scripts/{script}", "--repo-root", str(repo_root)))
        for label, script in _INDEX_HYGIENE_GATES
        if (repo_root / "scripts" / script).exists()
    ]


def skill_core_headroom_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Pull the changed-SKILL.md core-headroom ratchet to the commit boundary."""
    # `is_file` here, not at the caller: this gate hands paths to a validator, and
    # the callers that pass one collapsed list (the structural sweep, the full
    # closeout) have always carried deletions. Filtering at the argv site makes the
    # existing-file invariant hold for every caller shape rather than one.
    staged_skill_md = [
        path
        for path in paths
        if path.startswith(("skills/public/", "skills/support/"))
        and path.endswith("/SKILL.md")
        and path.count("/") == 3
        and (repo_root / path).is_file()
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


def artifact_shape_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Relocate changed artifact-shape validator verdicts to commit time."""
    matched = [
        path
        for path in paths
        if (surface := _artifact_preflight.surface_for_path(Path(path).as_posix())) is not None
        and surface.commit_boundary
        # Same argv-site rule as `skill_core_headroom_gates`: a deleted artifact
        # scheduled its own shape validator, which then failed on the missing file.
        and (repo_root / path).is_file()
    ]
    if not matched:
        return []
    # Absolute when this tree has the script: the command runs with cwd=repo_root,
    # and charness is consumed as a plugin, so a bare relative path only resolves
    # when the target repo IS the charness source tree. Mirrors
    # `check_artifact_surface_preflight._validator_argv_path`; falls back to the
    # relative form so an unusual layout keeps the old behavior.
    preflight_rel = "scripts/check_artifact_surface_preflight.py"
    preflight_local = _PLAN_HELPERS_ROOT / preflight_rel
    preflight = str(preflight_local) if preflight_local.is_file() else preflight_rel
    return [
        GateCommand(
            "check-artifact-shape (staged)",
            (
                "python3",
                preflight,
                "--repo-root",
                str(repo_root),
                "--changed-artifacts",
                *matched,
            ),
        )
    ]
