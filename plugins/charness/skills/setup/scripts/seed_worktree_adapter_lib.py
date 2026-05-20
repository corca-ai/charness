"""Detection and template rendering for `.agents/worktree-adapter.yaml` seeds.

Kept separate from `seed_worktree_adapter.py` so detection branches stay unit-testable
without subprocess plumbing.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

PACKAGE_MANAGER_PRIORITY: tuple[tuple[str, str], ...] = (
    ("pnpm-lock.yaml", "pnpm"),
    ("yarn.lock", "yarn"),
    ("bun.lockb", "bun"),
    ("package-lock.json", "npm"),
)


@dataclass(frozen=True)
class WorktreeAdapterDetection:
    package_manager: str | None
    package_manager_evidence: str | None
    package_manager_variant: str | None
    hook_system: str | None
    hook_system_evidence: str | None
    hook_install_argv: tuple[str, ...] | None
    has_package_json: bool


def _detect_yarn_variant(repo_root: Path, package: dict | None) -> str:
    """Return "berry" for Yarn 2.x-4.x setups, else "classic".

    Berry-shaped signals (any one is enough):
      * `.yarnrc.yml` exists (Berry's config; classic Yarn 1 uses `.yarnrc`).
      * `package.json` declares `packageManager: "yarn@2..."` or higher.
      * `.yarn/` directory exists (Berry caches releases here).
    """
    if (repo_root / ".yarnrc.yml").is_file():
        return "berry"
    if (repo_root / ".yarn").is_dir():
        return "berry"
    if package is not None:
        pm_field = package.get("packageManager")
        if isinstance(pm_field, str) and pm_field.startswith("yarn@"):
            version = pm_field.removeprefix("yarn@")
            if version and version[0].isdigit() and not version.startswith("1."):
                return "berry"
    return "classic"


def detect_package_manager(repo_root: Path) -> tuple[str | None, str | None]:
    for lockfile, pm in PACKAGE_MANAGER_PRIORITY:
        if (repo_root / lockfile).is_file():
            return pm, lockfile
    if (repo_root / "package.json").is_file():
        return "npm", "package.json (no lockfile)"
    return None, None


def _read_package_json(repo_root: Path) -> dict | None:
    path = repo_root / "package.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _git_config(repo_root: Path, key: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "config", "--get", key],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _repo_owned_hooks(
    repo_root: Path,
    package: dict | None,
    hooks_path: str | None,
) -> tuple[str, ...] | None:
    """Return install argv for a repo-owned hooks installer, or None.

    Recognized shapes:
      * `core.hooksPath` is set in git config and `package.json` exposes a
        `scripts.hooks:install` (or `install:hooks`) entry.
      * The conventional `.githooks/` directory exists alongside the same
        package script.
    """
    if package is None:
        return None
    scripts = package.get("scripts")
    if not isinstance(scripts, dict):
        return None
    if not any(name in scripts for name in ("hooks:install", "install:hooks")):
        return None
    githooks_dir_exists = (repo_root / ".githooks").is_dir()
    if not hooks_path and not githooks_dir_exists:
        return None
    script_name = "hooks:install" if "hooks:install" in scripts else "install:hooks"
    return ("__pm__", "run", script_name)


def detect_hook_system(
    repo_root: Path,
    package_manager: str | None,
) -> tuple[str | None, str | None, tuple[str, ...] | None]:
    """Return (hook_system, evidence, install_argv_template) or (None, None, None).

    `install_argv_template` uses the literal token `__pm__` where the resolved
    package manager binary should be substituted. Returning a template lets
    detection stay pure even when the package manager is unknown.
    """
    package = _read_package_json(repo_root)
    hooks_path = _git_config(repo_root, "core.hooksPath")
    repo_owned = _repo_owned_hooks(repo_root, package, hooks_path)
    if repo_owned is not None:
        script_name = repo_owned[2]
        evidence_parts = [f"package.json: scripts.{script_name}"]
        if hooks_path:
            evidence_parts.append(f"git core.hooksPath={hooks_path}")
        elif (repo_root / ".githooks").is_dir():
            evidence_parts.append(".githooks/")
        return "repo-owned", ", ".join(evidence_parts), repo_owned
    for filename in ("lefthook.yml", "lefthook.yaml"):
        if (repo_root / filename).is_file():
            return "lefthook", filename, ("__pm__", "exec", "lefthook", "install")
    if (repo_root / ".husky").is_dir():
        return "husky", ".husky/", ("__pm__", "exec", "husky", "install")
    if package is not None and "simple-git-hooks" in package:
        return "simple-git-hooks", "package.json: simple-git-hooks", ("npx", "simple-git-hooks")
    return None, None, None


def detect(repo_root: Path) -> WorktreeAdapterDetection:
    package_manager, pm_evidence = detect_package_manager(repo_root)
    package = _read_package_json(repo_root)
    variant: str | None = None
    if package_manager == "yarn":
        variant = _detect_yarn_variant(repo_root, package)
    hook_system, hook_evidence, install_argv = detect_hook_system(repo_root, package_manager)
    resolved_argv: tuple[str, ...] | None = None
    if install_argv is not None:
        pm_token = package_manager or "npm"
        resolved_argv = tuple(pm_token if token == "__pm__" else token for token in install_argv)
    return WorktreeAdapterDetection(
        package_manager=package_manager,
        package_manager_evidence=pm_evidence,
        package_manager_variant=variant,
        hook_system=hook_system,
        hook_system_evidence=hook_evidence,
        hook_install_argv=resolved_argv,
        has_package_json=(repo_root / "package.json").is_file(),
    )


def _install_deps_argv(detection: WorktreeAdapterDetection) -> tuple[str, ...] | None:
    pm = detection.package_manager
    if pm == "pnpm":
        return ("pnpm", "install", "--frozen-lockfile")
    if pm == "yarn":
        # Yarn 2+ (Berry) renamed --frozen-lockfile to --immutable and rejects
        # the legacy flag outright; Yarn 1 (classic) still uses the old flag.
        flag = "--immutable" if detection.package_manager_variant == "berry" else "--frozen-lockfile"
        return ("yarn", "install", flag)
    if pm == "bun":
        return ("bun", "install", "--frozen-lockfile")
    if pm == "npm":
        return ("npm", "ci")
    return None


def _argv_block(indent: str, argv: tuple[str, ...]) -> str:
    return "\n".join(f"{indent}- {item}" for item in argv)


def _render_install_deps(detection: WorktreeAdapterDetection) -> str:
    argv = _install_deps_argv(detection)
    pm = detection.package_manager
    if argv is None:
        return (
            "    # No package manager lockfile or package.json detected; replace this\n"
            "    # block with the install command your repo actually uses.\n"
            "    # - id: install-deps\n"
            "    #   description: \"Install workspace dependencies for this worktree.\"\n"
            "    #   timeout_seconds: 600\n"
            "    #   argv:\n"
            "    #     - <your-package-manager>\n"
            "    #     - install"
        )
    evidence = detection.package_manager_evidence or "auto-detected"
    return (
        f"    # Package manager auto-detected from {evidence} (pm={pm}).\n"
        "    - id: install-deps\n"
        f"      description: \"Install workspace dependencies via {pm}.\"\n"
        "      timeout_seconds: 600\n"
        "      argv:\n"
        f"{_argv_block('        ', argv)}"
    )


def _render_install_hooks(detection: WorktreeAdapterDetection) -> str:
    if detection.hook_install_argv is None:
        return (
            "    # No hook system detected. If your repo installs git hooks per worktree\n"
            "    # (lefthook, husky, simple-git-hooks, or a repo-owned `hooks:install`\n"
            "    # script), uncomment and adjust the block below.\n"
            "    # - id: install-hooks\n"
            "    #   description: \"Re-run hook installer for this worktree.\"\n"
            "    #   timeout_seconds: 60\n"
            "    #   argv:\n"
            "    #     - <your-package-manager>\n"
            "    #     - exec\n"
            "    #     - <your-hook-tool>\n"
            "    #     - install"
        )
    evidence = detection.hook_system_evidence or "auto-detected"
    return (
        f"    # Hook system auto-detected from {evidence} (hook_system={detection.hook_system}).\n"
        "    - id: install-hooks\n"
        "      description: \"Re-run hook installer for this worktree.\"\n"
        "      timeout_seconds: 60\n"
        "      argv:\n"
        f"{_argv_block('        ', detection.hook_install_argv)}"
    )


def _render_doctor_block(detection: WorktreeAdapterDetection) -> str:
    if detection.hook_system != "lefthook":
        return (
            "# Optional manifest-defined doctor checks layered on top of the canonical suite.\n"
            "# Add entries here when you have a repo-specific readiness probe; otherwise the\n"
            "# canonical suite (git_common_dir, hooks_path, lefthook_shim, husky_dir) is enough.\n"
            "# doctor:\n"
            "#   checks: []\n"
        )
    pm = detection.package_manager or "pnpm"
    return (
        "# Optional manifest-defined doctor checks layered on top of the canonical suite\n"
        "# (git_common_dir, hooks_path, lefthook_shim, husky_dir).\n"
        "# doctor:\n"
        "#   checks:\n"
        "#     - id: lefthook_self_check\n"
        "#       description: \"Confirm lefthook resolves from this worktree.\"\n"
        "#       next_action_hint: \"Run `charness worktree prepare` to install hooks.\"\n"
        "#       timeout_seconds: 10\n"
        "#       argv:\n"
        f"#         - {pm}\n"
        "#         - exec\n"
        "#         - lefthook\n"
        "#         - version\n"
    )


def render_template(detection: WorktreeAdapterDetection) -> str:
    return (
        "# charness worktree adapter - declares how `charness worktree prepare` makes a\n"
        "# freshly-created git worktree usable, and which extra `charness worktree doctor`\n"
        "# checks decide whether the worktree is ready.\n"
        "#\n"
        "# argv lists must use block-style YAML (charness's repo-local loader does not\n"
        "# parse inline `[a, b]` arrays). Edit the auto-detected commands below if the\n"
        "# detection picked the wrong tool for this repo.\n"
        "version: 1\n"
        "\n"
        "prepare:\n"
        "  commands:\n"
        f"{_render_install_deps(detection)}\n"
        f"{_render_install_hooks(detection)}\n"
        "  skip_if_doctor_passes: true\n"
        "\n"
        f"{_render_doctor_block(detection)}"
    )
