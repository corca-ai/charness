"""Git metadata and repo-shape fixtures shared by quality-gate tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# Bound at import so tests that wrap production ``subprocess.run`` cannot
# intercept fixture Git and poison the shared empty-git seed on disk.
_run = subprocess.run


def _empty_git_seed() -> Path:
    """Return one immutable empty ``.git`` tree shared by pytest workers."""
    from tests.seed_cache import get_or_build

    def build(seed_root: Path) -> None:
        seed_repo = seed_root / "repo"
        seed_repo.mkdir()
        _run(
            ["git", "init"],
            cwd=seed_repo,
            check=True,
            capture_output=True,
            text=True,
        )

    return get_or_build("quality-gates-empty-git-dir-seed", build) / "repo" / ".git"


def init_git_repo(repo: Path, *tracked_paths: str) -> None:
    """Install isolated Git metadata, then stage only the requested paths."""
    # Fixtures already have their working-tree files. Copy only the immutable,
    # empty metadata seed; this preserves the exact git-add boundary while
    # removing one process spawn per synthetic repository.
    git_dir = repo / ".git"
    if not git_dir.exists():
        shutil.copytree(_empty_git_seed(), git_dir)
    else:
        # Preserve the old behavior for callers intentionally reusing an
        # existing repository (including linked-worktree `.git` files).
        _run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    if tracked_paths:
        _run(
            ["git", "add", *tracked_paths],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )


MIRROR_RELATIVE = Path("plugins") / "charness"
GUARD_SCRIPT = "exported-copy-guard.sh"


def install_repo_root_script(repo: Path, script_name: str) -> tuple[Path, Path]:
    """Place `script_name` at the repo root AND in the generated mirror, byte-identical.

    `scripts/check_staged_mirror_drift.py` and `.githooks/pre-push` enforce that byte identity,
    so the mirrored copy is never a different program: whatever the source copy does, right or
    wrong, the mirror does too. Both copies are therefore under test here.
    """
    source = repo / "scripts" / script_name
    mirror = repo / MIRROR_RELATIVE / "scripts" / script_name
    source.parent.mkdir(parents=True, exist_ok=True)
    mirror.parent.mkdir(parents=True, exist_ok=True)
    if script_name in {"check-python-lint.sh", "run-quality.sh"}:
        (repo / ".githooks").mkdir(exist_ok=True)
        shutil.copy2(
            ROOT / ".githooks" / "runtime-env.sh",
            repo / ".githooks" / "runtime-env.sh",
        )
    # The guard travels with every gate that sources it, in BOTH copies. Shipping it to
    # only one side would make these tests measure "the guard file is missing" instead of
    # "the guard refused", which is a different green.
    #
    # Repo-owned Python HELPERS a gate shells out to are deliberately NOT installed
    # here. Their dependency closure reaches back into `scripts/` as a package
    # (`scripts.core.repo_file_listing` and onward), so installing them means reproducing the
    # repo, which is the thing this fixture exists to avoid. A test whose subject
    # is the gate's COMPOSITION stubs those helpers exactly as it stubs the external
    # tool; a test whose subject is a helper's own output belongs in that helper's
    # test file.
    #
    # Blind class: a gate run from this fixture without such a stub reaches a MISSING
    # helper, and gates that treat a helper's non-zero exit as an advisory will report
    # that absence as an advisory rather than as a failure. Callers asserting on
    # advisory text must install a stub.
    for name in (script_name, GUARD_SCRIPT):
        shutil.copy2(ROOT / "scripts" / name, source.parent / name)
        shutil.copy2(ROOT / "scripts" / name, mirror.parent / name)
    return source, mirror


def charness_shaped_repo(tmp_path: Path, script_name: str) -> tuple[Path, Path, Path]:
    """A git repo shaped like this one: root-level docs, plus a `plugins/charness` mirror.

    This is the canonical alternative to cloning the real checkout. A gate that measures a
    repo-root population needs a repo SHAPE, not this repository's contents, and the two are
    not interchangeable: a fixture that IS the checkout has no fixed input, so its verdict
    moves with unrelated repo content. `test_python_and_security_gates.py` already lost an
    assertion that way -- a wrapped inline code span in `docs/index.md` broke a test about
    markdownlint's exit code, and the repair was to delete the assertion, because the
    assertion had only ever encoded "every checked-in Markdown file happens to be clean".
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("# Agents\n", encoding="utf-8")
    (repo / "README.md").write_text("# Readme\n", encoding="utf-8")
    docs = repo / "docs"
    docs.mkdir()
    (docs / "nested.md").write_text("# Nested\n", encoding="utf-8")
    mirror_docs = repo / MIRROR_RELATIVE / "docs"
    mirror_docs.mkdir(parents=True)
    (mirror_docs / "mirrored.md").write_text("# Mirrored\n", encoding="utf-8")
    source, mirror = install_repo_root_script(repo, script_name)
    init_git_repo(repo)
    _run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    return repo, source, mirror
