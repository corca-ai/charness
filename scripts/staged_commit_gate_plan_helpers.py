from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

from runtime_bootstrap import import_repo_module

_artifact_preflight = import_repo_module(__file__, "scripts.check_artifact_surface_preflight")


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


def any_starts(paths: list[str], prefix: str) -> bool:
    return any(path.startswith(prefix) for path in paths)


def timing_pull_gate(repo_root: Path, label: str, script: str, *args: str) -> list[GateCommand]:
    """Return a pulled timing-layer guard only when the repo owns the script."""
    if not (repo_root / script).is_file():
        return []
    return [GateCommand(label, ("python3", script, *args))]


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


def mirror_drift_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
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


def skill_core_headroom_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Pull the changed-SKILL.md core-headroom ratchet to the commit boundary."""
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


def artifact_shape_gates(repo_root: Path, paths: list[str]) -> list[GateCommand]:
    """Relocate changed artifact-shape validator verdicts to commit time."""
    matched = [
        path
        for path in paths
        if (surface := _artifact_preflight.surface_for_path(Path(path).as_posix())) is not None
        and surface.commit_boundary
    ]
    if not matched:
        return []
    return [
        GateCommand(
            "check-artifact-shape (staged)",
            (
                "python3",
                "scripts/check_artifact_surface_preflight.py",
                "--repo-root",
                str(repo_root),
                "--changed-artifacts",
                *matched,
            ),
        )
    ]
