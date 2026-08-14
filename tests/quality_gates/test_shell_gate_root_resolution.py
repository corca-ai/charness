"""Where the repo-root shell gates root themselves, and what they measure from there.

Issue #618: `scripts/check-markdown.sh` self-located to `$(dirname $0)/..` and `cd`ed there.
In the generated mirror copy at `plugins/charness/scripts/` that is `plugins/charness`, a plain
subdirectory of this repo -- so `git ls-files` (cwd-scoped) never offered `AGENTS.md`,
`README.md`, `CLAUDE.md` or `docs/**`, the `:(exclude)` pathspecs became cwd-relative and matched
nothing, and the repo's only `.markdownlint-cli2.jsonc` was never resolved.

A package root is the right root for module resolution and the wrong root for a git population or
a config lookup: package-root != git-root != lint-config-root. These tests pin BOTH halves of that
distinction, for every gate in the class rather than the one that got filed:

* from a real repo root the measured population contains root-level files -- the assertion the
  mirrored cwd silently made false, and the one a `plugins/charness/.markdownlint-cli2.jsonc`
  would have left false while turning the verdict green;
* from a root that git says is not the toplevel, each gate REFUSES loudly instead of measuring a
  narrower scope, and `install-git-hooks.sh` refuses BEFORE it can repoint the enclosing
  repository's `core.hooksPath`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .support import ROOT, run_shell_script, write_executable

MIRROR_RELATIVE = Path("plugins") / "charness"

TRACKED_MARKDOWN_ARGV = [
    "ls-files",
    "--",
    "*.md",
    ":(exclude)charness-artifacts/**",
    ":(exclude).charness/**",
    ":(exclude).cautilus/**",
    ":(exclude).pytest_cache/**",
]


def _install_script(repo: Path, script_name: str) -> tuple[Path, Path]:
    """Place `script_name` at the repo root AND in the generated mirror, byte-identical.

    `scripts/check_staged_mirror_drift.py` and `.githooks/pre-push` enforce that byte identity,
    so the mirrored copy is never a different program: whatever the source copy does, right or
    wrong, the mirror does too. Both copies are therefore under test here.
    """

    source = repo / "scripts" / script_name
    mirror = repo / MIRROR_RELATIVE / "scripts" / script_name
    source.parent.mkdir(parents=True, exist_ok=True)
    mirror.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "scripts" / script_name, source)
    shutil.copy2(ROOT / "scripts" / script_name, mirror)
    return source, mirror


def _charness_shaped_repo(tmp_path: Path, script_name: str) -> tuple[Path, Path, Path]:
    """A git repo shaped like this one: root-level docs, plus a `plugins/charness` mirror."""

    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    (repo / "docs").mkdir()
    (repo / "docs" / "nested.md").write_text("# Nested\n", encoding="utf-8")
    (repo / MIRROR_RELATIVE / "docs").mkdir(parents=True)
    (repo / MIRROR_RELATIVE / "docs" / "mirrored.md").write_text("# Mirrored\n", encoding="utf-8")
    source, mirror = _install_script(repo, script_name)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    return repo, source, mirror


def _argv_logging_bin(tmp_path: Path, name: str) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / f"{name}-argv.txt"
    write_executable(bin_dir / name, '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$TEST_OUTPUT"\n')
    return bin_dir, log


def _env(bin_dir: Path, log: Path, **extra: str) -> dict[str, str]:
    return {
        **os.environ,
        "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        "TEST_OUTPUT": str(log),
        **extra,
    }


def test_repo_root_markdown_listing_contains_root_level_files() -> None:
    """Against THIS repo, not a fixture: the same listing command, two cwds, two populations.

    This is the mechanism of #618 stated as an assertion. It reads git only; it does not run the
    mirrored script, so it does not depend on when the `plugins/` mirror was last synced.
    """

    from_root = subprocess.run(
        ["git", *TRACKED_MARKDOWN_ARGV], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    from_mirror = subprocess.run(
        ["git", *TRACKED_MARKDOWN_ARGV],
        cwd=ROOT / MIRROR_RELATIVE,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()

    assert "AGENTS.md" in from_root
    assert "README.md" in from_root
    assert "CLAUDE.md" in from_root
    assert any(path.startswith("docs/") for path in from_root)
    # The narrowed population is not a subset problem to be papered over with a mirror-local
    # config; it is a different tree that happens to also be markdown.
    assert "AGENTS.md" not in from_mirror
    assert len(from_mirror) < len(from_root)


def test_check_markdown_lints_root_level_files_from_the_repo_root(tmp_path: Path) -> None:
    repo, source, _mirror = _charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(source, cwd=repo, env=_env(bin_dir, log))

    assert result.returncode == 0, result.stdout + result.stderr
    linted = log.read_text(encoding="utf-8").splitlines()
    assert "AGENTS.md" in linted
    assert "README.md" in linted
    assert "docs/nested.md" in linted


def test_check_markdown_refuses_from_the_generated_mirror(tmp_path: Path) -> None:
    repo, _source, mirror = _charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(mirror, cwd=repo, env=_env(bin_dir, log))

    assert result.returncode == 1
    assert "check-markdown: refusing to run from an exported copy." in result.stderr
    assert str(repo / MIRROR_RELATIVE) in result.stderr
    assert "CHARNESS_REPO_ROOT" in result.stderr
    # A refusal, not a narrowed measurement: markdownlint was never handed the mirror's own
    # `docs/mirrored.md` and no verdict was rendered over it.
    assert not log.exists()


def test_check_markdown_honors_charness_repo_root_from_the_mirror(tmp_path: Path) -> None:
    repo, _source, mirror = _charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(mirror, cwd=repo, env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo)))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "AGENTS.md" in log.read_text(encoding="utf-8").splitlines()


def _shell_gate_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo, source, mirror = _charness_shaped_repo(tmp_path, "check-shell.sh")
    (repo / "init.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "tests" / "fixtures").mkdir(parents=True)
    (repo / "tests" / "fixtures" / "fake-tool.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-commit").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    return repo, source, mirror


def test_check_shell_lints_root_hook_and_test_files_from_the_repo_root(tmp_path: Path) -> None:
    repo, source, _mirror = _shell_gate_repo(tmp_path)
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")

    result = run_shell_script(source, cwd=repo, env=_env(bin_dir, log))

    assert result.returncode == 0, result.stderr
    linted = log.read_text(encoding="utf-8").splitlines()
    assert "./init.sh" in linted
    assert "tests/fixtures/fake-tool.sh" in linted
    assert ".githooks/pre-commit" in linted
    assert "scripts/check-shell.sh" in linted


def test_check_shell_refuses_from_the_generated_mirror(tmp_path: Path) -> None:
    """The worst of the three, because its narrowed run was GREEN.

    From the mirror the gate used to lint the ten mirrored `scripts/*.sh` and exit 0, never
    seeing `init.sh`, `tests/**/*.sh`, or `.githooks/*` -- a silent scope shrink under a passing
    verdict, which nothing downstream can distinguish from a real pass.
    """

    repo, _source, mirror = _shell_gate_repo(tmp_path)
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")

    result = run_shell_script(mirror, cwd=repo, env=_env(bin_dir, log))

    assert result.returncode == 1
    assert "check-shell: refusing to run from an exported copy." in result.stderr
    assert "CHARNESS_REPO_ROOT" in result.stderr
    assert not log.exists()


def test_check_shell_fails_when_a_verified_root_discovers_nothing(tmp_path: Path) -> None:
    """An empty population is green only while the root is unconfirmed.

    From a root we know, discovery cannot honestly come back empty -- the gate is itself a
    `scripts/*.sh` file -- so exiting 0 there would restate the false green the root guard closes.
    """

    repo, source, _mirror = _shell_gate_repo(tmp_path)
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")
    write_executable(bin_dir / "find", "#!/usr/bin/env bash\nexit 0\n")

    result = run_shell_script(source, cwd=repo, env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo)))

    assert result.returncode == 1
    assert "check-shell: no shell files discovered under" in result.stderr
    assert "it is wrong, not the tree" in result.stderr
    assert not log.exists()


def test_check_links_external_refuses_from_the_generated_mirror(tmp_path: Path) -> None:
    repo, _source, mirror = _charness_shaped_repo(tmp_path, "check-links-external.sh")

    result = run_shell_script(mirror, cwd=repo, env={**os.environ})

    assert result.returncode == 1
    assert "check-links-external: refusing to run from an exported copy." in result.stderr
    assert "CHARNESS_REPO_ROOT" in result.stderr
    # The refusal precedes the `lychee` availability probe: an unrunnable root is a worse fault
    # than a missing linker, and reporting the missing tool first would hide it.
    assert "lychee is required" not in result.stderr


def _hookspath(repo: Path) -> str:
    result = subprocess.run(
        ["git", "config", "--get", "core.hooksPath"],
        cwd=repo,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def test_install_git_hooks_refuses_from_the_mirror_without_touching_hookspath(tmp_path: Path) -> None:
    """`git config` is repo-scoped, not directory-scoped.

    Run bare from the mirror, the installer took its same-root branch and ran
    `git -C plugins/charness config core.hooksPath plugins/charness/.githooks`, disabling the
    WHOLE repository's pre-commit/pre-push hooks while printing a success line. The refusal must
    therefore land before any mutation: no config write, and no `.githooks/` left behind.
    """

    repo, _source, mirror = _charness_shaped_repo(tmp_path, "install-git-hooks.sh")
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-commit").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    subprocess.run(
        ["git", "config", "core.hooksPath", str(repo / ".githooks")],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    result = run_shell_script(mirror, cwd=repo, env={**os.environ})

    assert result.returncode == 1
    assert "install-git-hooks: refusing to configure hooks from a subdirectory" in result.stderr
    assert "git config is repo-scoped, not directory-scoped" in result.stderr
    assert _hookspath(repo) == str(repo / ".githooks")
    assert not (repo / MIRROR_RELATIVE / ".githooks").exists()


def test_install_git_hooks_refuses_a_repo_root_argument_inside_a_repository(tmp_path: Path) -> None:
    """The flag is not a way around the rule: `--repo-root <subdir>` is the same destructive
    write with an explicit argument, so both branches are validated, not just the default one."""

    repo, source, _mirror = _charness_shaped_repo(tmp_path, "install-git-hooks.sh")
    subdir = repo / "docs"

    result = run_shell_script(source, "--repo-root", str(subdir), cwd=repo, env={**os.environ})

    assert result.returncode == 1
    assert "install-git-hooks: refusing to configure hooks from a subdirectory" in result.stderr
    assert _hookspath(repo) == ""
    assert not (subdir / ".githooks").exists()


def test_install_git_hooks_refuses_a_target_that_is_not_a_repository(tmp_path: Path) -> None:
    source_tree = tmp_path / "source"
    (source_tree / "scripts").mkdir(parents=True)
    shutil.copy2(
        ROOT / "scripts" / "install-git-hooks.sh", source_tree / "scripts" / "install-git-hooks.sh"
    )

    result = run_shell_script(
        source_tree / "scripts" / "install-git-hooks.sh", cwd=source_tree, env={**os.environ}
    )

    assert result.returncode == 1
    assert "install-git-hooks: refusing to configure hooks for a non-repository." in result.stderr
    assert not (source_tree / ".githooks").exists()
