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

import pytest

from .seeding_support import write_quality_adapter
from .support import (
    GUARD_SCRIPT,
    MIRROR_RELATIVE,
    ROOT,
    charness_shaped_repo,
    run_shell_script,
    write_executable,
)

TRACKED_MARKDOWN_ARGV = [
    "ls-files",
    "--",
    "*.md",
    ":(exclude)charness-artifacts/**",
    ":(exclude).charness/**",
    ":(exclude).pytest_cache/**",
]


def _argv_logging_bin(tmp_path: Path, name: str) -> tuple[Path, Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / f"{name}-argv.txt"
    write_executable(
        bin_dir / name, '#!/usr/bin/env bash\nprintf \'%s\\n\' "$@" > "$TEST_OUTPUT"\n'
    )
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
    repo, source, _mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(source, cwd=repo, env=_env(bin_dir, log))

    assert result.returncode == 0, result.stdout + result.stderr
    linted = log.read_text(encoding="utf-8").splitlines()
    assert "AGENTS.md" in linted
    assert "README.md" in linted
    assert "docs/nested.md" in linted


def test_check_markdown_refuses_from_the_generated_mirror(tmp_path: Path) -> None:
    repo, _source, mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
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
    repo, _source, mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(
        mirror, cwd=repo, env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo))
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "AGENTS.md" in log.read_text(encoding="utf-8").splitlines()


def _shell_gate_repo(tmp_path: Path) -> tuple[Path, Path, Path]:
    repo, source, mirror = charness_shaped_repo(tmp_path, "check-shell.sh")
    (repo / "init.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    (repo / "tests" / "fixtures").mkdir(parents=True)
    (repo / "tests" / "fixtures" / "fake-tool.sh").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-commit").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
    return repo, source, mirror


def test_check_shell_lints_root_hook_and_test_files_from_the_repo_root(tmp_path: Path) -> None:
    repo, source, _mirror = _shell_gate_repo(tmp_path)
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")

    result = run_shell_script(
        ROOT / "scripts" / "check-shell.sh",
        cwd=repo,
        env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo)),
    )

    assert result.returncode == 0, result.stderr
    linted = log.read_text(encoding="utf-8").splitlines()
    assert "init.sh" in linted
    assert "tests/fixtures/fake-tool.sh" in linted
    assert ".githooks/pre-commit" in linted
    assert "scripts/check-shell.sh" in linted


def test_check_shell_uses_adapter_shell_sources(tmp_path: Path) -> None:
    repo, _source, _mirror = _shell_gate_repo(tmp_path)
    (repo / "bin").mkdir()
    (repo / "bin" / "declared.sh").write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
    write_quality_adapter(repo, ["universes:", "  shell_sources:", "    - bin/*.sh"])
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")

    result = run_shell_script(
        ROOT / "scripts" / "check-shell.sh",
        cwd=repo,
        env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo)),
    )

    assert result.returncode == 0, result.stdout + result.stderr
    linted = log.read_text(encoding="utf-8").splitlines()
    assert "bin/declared.sh" in linted
    assert "init.sh" not in linted
    assert "scripts/check-shell.sh" not in linted


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


def test_check_shell_fails_when_a_declared_root_discovers_nothing(tmp_path: Path) -> None:
    """A declared empty adapter universe refuses before shellcheck is invoked."""

    repo, _source, _mirror = _shell_gate_repo(tmp_path)
    bin_dir, log = _argv_logging_bin(tmp_path, "shellcheck")
    (repo / ".agents").mkdir(exist_ok=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: test\nlanguage: en\noutput_dir: quality\nuniverses:\n"
        "  shell_sources: []\n",
        encoding="utf-8",
    )

    result = run_shell_script(
        ROOT / "scripts" / "check-shell.sh",
        cwd=repo,
        env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo)),
    )

    assert result.returncode == 1
    assert "check-shell: shell universe resolution failed." in result.stderr
    assert "check-shell: refusing empty declared universe" in result.stderr
    assert not log.exists()


def test_check_links_external_refuses_from_the_generated_mirror(tmp_path: Path) -> None:
    repo, _source, mirror = charness_shaped_repo(tmp_path, "check-links-external.sh")

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


def test_install_git_hooks_refuses_from_the_mirror_without_touching_hookspath(
    tmp_path: Path,
) -> None:
    """`git config` is repo-scoped, not directory-scoped.

    Run bare from the mirror, the installer took its same-root branch and ran
    `git -C plugins/charness config core.hooksPath plugins/charness/.githooks`, disabling the
    WHOLE repository's pre-commit/pre-push hooks while printing a success line. The refusal must
    therefore land before any mutation: no config write, and no `.githooks/` left behind.
    """

    repo, _source, mirror = charness_shaped_repo(tmp_path, "install-git-hooks.sh")
    (repo / ".githooks").mkdir()
    (repo / ".githooks" / "pre-commit").write_text(
        "#!/usr/bin/env bash\nexit 0\n", encoding="utf-8"
    )
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

    repo, source, _mirror = charness_shaped_repo(tmp_path, "install-git-hooks.sh")
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


# Every repo-root shell gate that measures or drives work from its own root. Membership is
# the detector: adding a tenth gate without the guard fails here rather than shipping a
# copy that measures the export. `install-git-hooks.sh` is deliberately absent -- it takes
# an explicit `--repo-root` and refuses a non-repository on its own terms, so it owns no
# `CHARNESS_REPO_ROOT` hatch to share.
GUARDED_GATES = (
    "check-links-external.sh",
    "check-links-internal.sh",
    "check-markdown.sh",
    "check-python-lint.sh",
    "check-secrets.sh",
    "check-shell.sh",
    "run-quality.sh",
    "self-validate-install-update.sh",
)


def test_every_repo_root_shell_gate_sources_the_one_guard() -> None:
    """The rule had six hand-copied homes and three gates that never got one.

    `check-python-lint.sh`, `run-quality.sh` and `self-validate-install-update.sh` each
    carried a COMMENT saying they cannot run from the export, and no code that said so to
    the operator -- so from the mirror they died naming absent directories rather than the
    reason those directories are absent, and `run-quality.sh` would have driven the whole
    standing lane against the plugin tree. A retyped rule has whatever coverage the last
    author remembered; this asks one question of the whole class.
    """
    missing = []
    for name in GUARDED_GATES:
        text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        if GUARD_SCRIPT not in text or 'GATE_NAME="' not in text:
            missing.append(name)
    assert not missing, f"repo-root shell gates not sourcing {GUARD_SCRIPT}: {missing}"


def test_no_repo_root_shell_gate_still_carries_a_hand_copied_guard() -> None:
    """One home, or the drift this consolidation removed comes straight back.

    A gate that re-inlines the `git rev-parse --show-toplevel` comparison is a second
    implementation of the rule, and the next fix lands in only one of them.
    """
    inlined = []
    for name in GUARDED_GATES:
        # CODE lines only. A gate may — and check-markdown.sh does — name the rejected
        # `git rev-parse --show-toplevel` approach in a comment while carrying none of it.
        code = [
            line
            for line in (ROOT / "scripts" / name).read_text(encoding="utf-8").splitlines()
            if not line.lstrip().startswith("#")
        ]
        if any("rev-parse --show-toplevel" in line for line in code):
            inlined.append(name)
    assert not inlined, f"gates carrying their own copy of the root guard: {inlined}"


def test_the_three_newly_guarded_gates_refuse_from_the_generated_mirror(tmp_path: Path) -> None:
    """The gates the class inventory named as uncovered, proven one at a time.

    `run-quality.sh` is the widest blast radius of the three: unguarded, the exported copy
    self-locates to `plugins/charness/` and drives ~85 gates against the plugin tree.
    """
    for name, gate in (
        ("check-python-lint.sh", "check-python-lint"),
        ("run-quality.sh", "run-quality"),
        ("self-validate-install-update.sh", "self-validate-install-update"),
    ):
        case_root = tmp_path / name
        case_root.mkdir()
        repo, _source, mirror = charness_shaped_repo(case_root, name)

        result = run_shell_script(mirror, cwd=repo, env={**os.environ})

        assert result.returncode == 1, (name, result.stdout, result.stderr)
        assert f"{gate}: refusing to run from an exported copy." in result.stderr, name
        assert "CHARNESS_REPO_ROOT" in result.stderr, name


@pytest.mark.boundary_contract(
    reason="the exported run-quality shell boundary must refuse by gate name outside any repo"
)
def test_exported_run_quality_refuses_by_name_outside_any_repo(tmp_path: Path) -> None:
    installed = tmp_path / "installed" / "scripts"
    installed.mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / "run-quality.sh", installed / "run-quality.sh")
    shutil.copy2(ROOT / "scripts" / "exported-copy-guard.sh", installed / "exported-copy-guard.sh")

    result = run_shell_script(
        installed / "run-quality.sh", cwd=tmp_path, env={**os.environ}
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "run-quality: refusing to run from an installed/exported copy" in result.stderr
    assert "No such file or directory" not in result.stderr


def test_the_guard_refuses_a_caller_that_forgot_to_name_itself(tmp_path: Path) -> None:
    """A gate sourcing the guard without `GATE_NAME` would emit `: refusing to run`.

    Anonymous refusals are how an operator ends up unable to tell which gate stopped, so
    the miswiring fails at the guard instead of producing one.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts" / GUARD_SCRIPT, repo / "scripts" / GUARD_SCRIPT)
    caller = repo / "scripts" / "nameless.sh"
    caller.write_text(
        "#!/usr/bin/env bash\nset -euo pipefail\n"
        'source "$(dirname "${BASH_SOURCE[0]}")/exported-copy-guard.sh"\n',
        encoding="utf-8",
    )

    result = run_shell_script(caller, cwd=repo, env={**os.environ})

    assert result.returncode == 2, result.stdout + result.stderr
    assert "sourced without GATE_NAME" in result.stderr


def test_the_repo_root_hatch_refuses_a_driver_only_on_DISAGREEMENT(tmp_path: Path) -> None:
    """A remedy a gate cannot honor is worse than no remedy -- but presence is not misuse.

    `run-quality.sh`, `check-python-lint.sh` and `self-validate-install-update.sh` each
    run a fixed path list belonging to the charness source checkout, so RETARGETING
    their root only moves where they fail. Refusing on the variable's mere PRESENCE,
    though, reds a run whose asserted root, derived root and git toplevel all agree --
    and an operator who exports it in a shell profile then gets a red on `--help`,
    indistinguishable from a gate failure. Status 2, not 1: a receipt has to tell
    caller misuse from a verdict.
    """
    (tmp_path / "driver").mkdir()
    (tmp_path / "agree").mkdir()
    repo, source, mirror = charness_shaped_repo(tmp_path / "driver", "run-quality.sh")

    retargeted = run_shell_script(
        mirror, cwd=repo, env={**os.environ, "CHARNESS_REPO_ROOT": str(repo)}
    )
    assert retargeted.returncode == 2, retargeted.stdout + retargeted.stderr
    assert "does not accept one" in retargeted.stderr

    # Same tree: not misuse, so the guard steps aside and the gate runs its own course.
    agreeing, agree_source, _ = charness_shaped_repo(tmp_path / "agree", "run-quality.sh")
    proceeded = run_shell_script(
        agree_source, cwd=agreeing, env={**os.environ, "CHARNESS_REPO_ROOT": str(agreeing)}
    )
    assert "does not accept one" not in proceeded.stderr
    assert "refusing to run from an exported copy" not in proceeded.stderr


def test_an_absent_repo_root_hatch_refuses_by_name(tmp_path: Path) -> None:
    """A typo'd `CHARNESS_REPO_ROOT` used to die on a bare `cd:` error with no gate name.

    It is the one input path the operator typed by hand, and it was missing the
    refuse-by-name property the prelude exists to protect.
    """
    repo, source, _mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")

    result = run_shell_script(
        source, cwd=repo, env={**os.environ, "CHARNESS_REPO_ROOT": str(tmp_path / "nope")}
    )

    assert result.returncode == 2, result.stdout + result.stderr
    assert "check-markdown: CHARNESS_REPO_ROOT does not name a directory." in result.stderr


def test_an_asserted_root_is_compared_the_same_way_a_derived_one_is(tmp_path: Path) -> None:
    """The hatch was the one input path with zero cross-checking.

    `CHARNESS_REPO_ROOT=$PWD/plugins/charness` used to be accepted in silence and marked
    verified, which reproduces the original narrowed-population defect with the flag
    asserting the opposite. Agreement is the rule; it does not stop applying because a
    human typed the root instead of the script deriving it.
    """
    repo, source, _mirror = charness_shaped_repo(tmp_path, "check-markdown.sh")
    bin_dir, log = _argv_logging_bin(tmp_path, "markdownlint-cli2")

    result = run_shell_script(
        source,
        cwd=repo,
        env=_env(bin_dir, log, CHARNESS_REPO_ROOT=str(repo / MIRROR_RELATIVE)),
    )

    assert result.returncode == 1, result.stdout + result.stderr
    assert "check-markdown: refusing to run from an exported copy." in result.stderr
    assert "asserted root" in result.stderr
    assert not log.exists()


def test_a_gate_that_cannot_find_the_guard_refuses_by_name(tmp_path: Path) -> None:
    """Sourcing must not trade a gate-named refusal for a bash missing-file error.

    A relocated or symlinked copy reaches this: `BASH_SOURCE[0]` names a directory the
    guard does not sit in, and without the existence check the run died with
    `./exported-copy-guard.sh: No such file or directory` and no gate name at all.
    """
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    relocated = repo / "check-shell.sh"
    shutil.copy2(ROOT / "scripts" / "check-shell.sh", relocated)

    result = run_shell_script(relocated, cwd=repo, env={**os.environ})

    assert result.returncode == 2, result.stdout + result.stderr
    assert "check-shell: cannot locate exported-copy-guard.sh beside this script" in result.stderr
