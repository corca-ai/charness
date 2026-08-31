"""Frozen checkout shapes for tests.

A test that needs a Git story installs a named shape by copy. Git runs once
when the seed is built, not once per test. Unique tails (an extra dirty file,
a second commit, a remote) still speak Git; the shared prefix does not.
"""

from __future__ import annotations

import hashlib
import shutil
from collections.abc import Mapping, Sequence
from pathlib import Path

from tests.seed_cache import get_or_build


def _file_digest(
    files: Mapping[str, str],
    *,
    message: str,
    branch: str,
    author_date: str | None,
    executable: Sequence[str],
) -> str:
    digest = hashlib.sha256()
    digest.update(branch.encode())
    digest.update(b"\0")
    digest.update(message.encode())
    digest.update(b"\0")
    digest.update((author_date or "").encode())
    digest.update(b"\0")
    for relative in sorted(executable):
        digest.update(b"x")
        digest.update(relative.encode())
        digest.update(b"\0")
    for relative in sorted(files):
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(files[relative].encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()[:20]


def _committed_seed(
    files: Mapping[str, str],
    *,
    message: str,
    branch: str,
    author_date: str | None,
    executable: Sequence[str],
) -> Path:
    from tests.quality_gates.seeding_support import _install_empty_git_dir, git, write_text

    key = _file_digest(
        files, message=message, branch=branch, author_date=author_date, executable=executable
    )

    def build(seed_root: Path) -> None:
        repo = seed_root / "repo"
        repo.mkdir()
        _install_empty_git_dir(repo, branch=branch)
        for relative, contents in files.items():
            path = write_text(repo / relative, contents)
            if relative in executable:
                path.chmod(0o755)
        extra: dict[str, str] = {}
        if author_date:
            extra["GIT_AUTHOR_DATE"] = author_date
            extra["GIT_COMMITTER_DATE"] = author_date
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message, env=extra or None)

    return get_or_build(f"shape-one-commit-{key}", build) / "repo"


def _copytree_into_empty(source: Path, dest: Path) -> Path:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        if any(dest.iterdir()):
            raise ValueError(f"refusing to install a checkout into a non-empty path: {dest}")
        dest.rmdir()
    shutil.copytree(source, dest)
    return dest


def install_committed_repo(
    dest: Path,
    files: Mapping[str, str],
    *,
    message: str = "seed",
    branch: str = "main",
    author_date: str | None = None,
    executable: Sequence[str] = (),
) -> Path:
    """Install a one-commit checkout with exactly ``files`` at HEAD.

    Same file set reuses one frozen seed. Test-time Git count is zero.
    """
    source = _committed_seed(
        files,
        message=message,
        branch=branch,
        author_date=author_date,
        executable=executable,
    )
    return _copytree_into_empty(source, dest)


def _head_oid(repo: Path) -> str:
    pointer = (repo / ".git" / "HEAD").read_text(encoding="ascii").strip()
    if pointer.startswith("ref: "):
        return (repo / ".git" / pointer[5:]).read_text(encoding="ascii").strip()
    return pointer


def _worktree_files(root: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    files: dict[str, str] = {}
    executable: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if relative.parts[:1] == (".git",):
            continue
        if not path.is_file():
            continue
        key = relative.as_posix()
        files[key] = path.read_text(encoding="utf-8")
        if path.stat().st_mode & 0o111:
            executable.append(key)
    return files, tuple(executable)


def replace_with_committed_repo(
    dest: Path,
    *,
    message: str = "seed",
    branch: str = "main",
    author_date: str | None = None,
    executable: Sequence[str] | None = None,
) -> Path:
    """Replace an already-written tree with a frozen one-commit checkout of it."""
    dest = Path(dest)
    files, discovered = _worktree_files(dest)
    if not files:
        raise ValueError(f"refusing to freeze an empty tree: {dest}")
    modes = discovered if executable is None else tuple(executable)
    shutil.rmtree(dest)
    return install_committed_repo(
        dest,
        files,
        message=message,
        branch=branch,
        author_date=author_date,
        executable=modes,
    )


def _two_commit_digest(
    first: Mapping[str, str],
    second: Mapping[str, str],
    *,
    first_message: str,
    second_message: str,
    branch: str,
) -> str:
    digest = hashlib.sha256()
    digest.update(branch.encode())
    digest.update(b"\0")
    digest.update(first_message.encode())
    digest.update(b"\0")
    digest.update(second_message.encode())
    digest.update(b"\0")
    for label, files in (("1", first), ("2", second)):
        digest.update(label.encode())
        digest.update(b"\0")
        for relative in sorted(files):
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(files[relative].encode("utf-8"))
            digest.update(b"\0")
    return digest.hexdigest()[:20]


def install_two_commit_repo(
    dest: Path,
    first: Mapping[str, str],
    second: Mapping[str, str],
    *,
    first_message: str = "base",
    second_message: str = "head",
    branch: str = "main",
) -> tuple[Path, str, str]:
    """Install a two-commit checkout. Same snapshots reuse one frozen seed."""
    from tests.quality_gates.seeding_support import _install_empty_git_dir, git, write_text

    key = _two_commit_digest(
        first,
        second,
        first_message=first_message,
        second_message=second_message,
        branch=branch,
    )

    def build(seed_root: Path) -> None:
        repo = seed_root / "repo"
        repo.mkdir()
        _install_empty_git_dir(repo, branch=branch)
        for relative, contents in first.items():
            write_text(repo / relative, contents)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", first_message)
        first_oid = _head_oid(repo)
        for relative, contents in second.items():
            write_text(repo / relative, contents)
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", second_message)
        (seed_root / "oids.txt").write_text(
            f"{first_oid}\n{_head_oid(repo)}\n",
            encoding="ascii",
        )

    bundle = get_or_build(f"shape-two-commit-{key}", build)
    dest = _copytree_into_empty(bundle / "repo", dest)
    first_oid, second_oid = (bundle / "oids.txt").read_text(encoding="ascii").splitlines()[:2]
    return dest, first_oid, second_oid


_DEFAULT_SUPERPROJECT = {"root.txt": "r\n"}
_DEFAULT_SUBMODULE = {"f.txt": "v1\n"}


def _submodule_digest(
    files: Mapping[str, str],
    submodule_files: Mapping[str, str],
    *,
    message: str,
    submodule_message: str,
    add_message: str,
    submodule_path: str,
    branch: str,
) -> str:
    digest = hashlib.sha256()
    for part in (branch, message, submodule_message, add_message, submodule_path):
        digest.update(part.encode())
        digest.update(b"\0")
    for label, snapshot in (("super", files), ("sub", submodule_files)):
        digest.update(label.encode())
        digest.update(b"\0")
        for relative in sorted(snapshot):
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(snapshot[relative].encode("utf-8"))
            digest.update(b"\0")
    return digest.hexdigest()[:20]


def install_submodule_repo(
    dest: Path,
    files: Mapping[str, str] | None = None,
    submodule_files: Mapping[str, str] | None = None,
    *,
    message: str = "init",
    submodule_message: str = "v1",
    add_message: str = "add submodule",
    submodule_path: str = "sub",
    branch: str = "main",
) -> tuple[Path, Path]:
    """Install a superproject with an initialized submodule by copy.

    ``dest`` is the superproject. Its sibling ``upstream/`` is the submodule
    origin. Same snapshots reuse one frozen seed. Test-time Git count is zero.
    Unique tails (moving the checked-out submodule HEAD, dropping the gitlink,
    cloning without init) still speak Git.

    Origin URLs are rewritten to paths relative to the submodule worktree so a
    copied bundle fetches its own sibling, not the seed.
    """
    from tests.quality_gates.seeding_support import git

    super_files = dict(_DEFAULT_SUPERPROJECT if files is None else files)
    nested_files = dict(_DEFAULT_SUBMODULE if submodule_files is None else submodule_files)
    key = _submodule_digest(
        super_files,
        nested_files,
        message=message,
        submodule_message=submodule_message,
        add_message=add_message,
        submodule_path=submodule_path,
        branch=branch,
    )

    def build(seed_root: Path) -> None:
        install_committed_repo(
            seed_root / "upstream", nested_files, message=submodule_message, branch=branch
        )
        install_committed_repo(seed_root / "repo", super_files, message=message, branch=branch)
        repo = seed_root / "repo"
        git(
            repo,
            "-c",
            "protocol.file.allow=always",
            "submodule",
            "add",
            "-q",
            "../upstream",
            submodule_path,
        )
        git(repo, "config", f"submodule.{submodule_path}.url", "../upstream")
        origin = "../" * (len(Path(submodule_path).parts) + 1) + "upstream"
        git(
            repo,
            "config",
            "--file",
            f".git/modules/{submodule_path}/config",
            "remote.origin.url",
            origin,
        )
        git(repo, "commit", "-q", "-m", add_message)

    bundle = get_or_build(f"shape-submodule-{key}", build)
    dest = Path(dest)
    upstream = dest.parent / "upstream"
    dest = _copytree_into_empty(bundle / "repo", dest)
    _copytree_into_empty(bundle / "upstream", upstream)
    return dest, upstream
