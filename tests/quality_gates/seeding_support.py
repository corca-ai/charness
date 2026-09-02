"""Small, behavior-neutral primitives for synthetic quality-gate fixtures."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[2]


def make_repo(tmp_path: Path, name: str = "repo", *, parents: bool = False) -> Path:
    """Create and return a fresh temporary repository directory."""
    repo = tmp_path / name
    repo.mkdir(parents=parents)
    return repo


def write_text(path: Path, contents: str) -> Path:
    """Write a fixture file, creating its parent directory when needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    return path


def write_lines(path: Path, lines: Sequence[str]) -> Path:
    """Write a newline-terminated line fixture with its parent directory."""
    return write_text(path, "\n".join(lines) + "\n")


def write_json(path: Path, payload: object, *, indent: int | None = 2) -> Path:
    """Write a newline-terminated JSON fixture."""
    return write_text(path, json.dumps(payload, indent=indent) + "\n")


def write_skill(
    repo: Path,
    body: Sequence[str],
    *,
    skill_id: str = "demo",
    description: str = "Demo skill.",
    package: str = "public",
    title: str | None = None,
) -> Path:
    """Write a small skill with the shared package front matter."""
    skill_dir = repo / "skills" / package / skill_id
    title = title or skill_id.replace("-", " ").title()
    lines = [
        "---",
        f"name: {skill_id}",
        f'description: "{description}"',
        "---",
        "",
        f"# {title}",
        "",
        *body,
    ]
    return write_text(skill_dir / "SKILL.md", "\n".join(lines) + "\n")


def write_quality_adapter(
    repo: Path,
    lines: Sequence[str],
    *,
    repo_name: str = "repo",
    language: str | None = None,
) -> Path:
    """Write a quality adapter with the shared fixture defaults."""
    adapter_lines = [
        "version: 1",
        f"repo: {repo_name}",
        *([f"language: {language}"] if language is not None else []),
        "output_dir: charness-artifacts/quality",
        *lines,
    ]
    return write_text(
        repo / ".agents" / "quality-adapter.yaml",
        "\n".join(adapter_lines) + "\n",
    )


def write_surface(
    repo: Path,
    surface_id: str,
    description: str,
    source_paths: Sequence[str],
    *,
    derived_paths: Sequence[str] = (),
) -> Path:
    """Write one small surface declaration for repository fixture tests."""
    surface = {
        "surface_id": surface_id,
        "description": description,
        "source_paths": list(source_paths),
        "derived_paths": list(derived_paths),
        "sync_commands": [],
        "verify_commands": [],
        "notes": [],
    }
    return write_json(repo / ".agents" / "surfaces.json", {"version": 1, "surfaces": [surface]})


def write_release_adapter(
    repo: Path,
    lines: Sequence[str] = (),
    *,
    repo_name: str = "demo",
    language: str | None = "en",
    output_dir: str = "charness-artifacts/release",
) -> Path:
    """Write the compact release adapter shared by publish fixtures."""
    adapter_lines = ["version: 1", f"repo: {repo_name}"]
    if language is not None:
        adapter_lines.append(f"language: {language}")
    adapter_lines.extend([f"output_dir: {output_dir}", *lines])
    return write_lines(repo / ".agents" / "release-adapter.yaml", adapter_lines)


def write_mutation_score_adapter(repo: Path, *, score_break: int = 50) -> Path:
    """Write the compact mutation-score adapter shared by score fixtures."""
    return write_quality_adapter(
        repo,
        [
            "mutation_testing:",
            f"  score_break: {score_break}",
            "  report_paths:",
            "    summary_md: reports/mutation/summary.md",
        ],
        repo_name="testrepo",
        language="en",
    )


def write_retro_adapter(repo: Path, *, include_summary_path: bool = True) -> Path:
    """Create the standard retro output directory and adapter fixture."""
    (repo / "charness-artifacts" / "retro").mkdir(parents=True, exist_ok=True)
    lines = [
        "version: 1",
        "repo: demo",
        "language: en",
        "output_dir: charness-artifacts/retro",
    ]
    if include_summary_path:
        lines.append("summary_path: charness-artifacts/retro/recent-lessons.md")
    lines.extend(["evidence_paths: []", "metrics_commands: []"])
    return write_text(repo / ".agents" / "retro-adapter.yaml", "\n".join(lines) + "\n")


def write_executable(path: Path, contents: str) -> Path:
    """Write an executable fixture script and return its path."""
    write_text(path, contents)
    path.chmod(0o755)
    return path


def write_python_executable(path: Path, body: Sequence[str]) -> Path:
    """Write a Python fixture executable with its standard interpreter line."""
    return write_executable(
        path,
        "\n".join(["#!/usr/bin/env python3", *body, ""]),
    )


def write_json_executable(
    path: Path, payload: Mapping[str, object], *, trigger: str = "view"
) -> Path:
    """Write a fake command that emits a fixed JSON payload for one operation."""
    payload_text = json.dumps(payload)
    return write_python_executable(
        path,
        ["import sys", f"if {trigger!r} in sys.argv: print({payload_text!r})"],
    )


def write_view_executable(path: Path, output: str, *, exit_code: int = 0) -> Path:
    """Write a fake command that returns a fixed preflight view result."""
    return write_python_executable(
        path,
        [
            "import sys",
            "if 'view' in sys.argv:",
            f"    print({output!r})",
            f"    raise SystemExit({exit_code})",
            "print('unexpected mutation')",
        ],
    )


def write_issue_close_fake(
    bin_dir: Path,
    *,
    name: str = "gh",
    log_env: str = "GH_LOG",
    number: int = 42,
    state: str = "CLOSED",
    repo: str = "corca-ai/charness",
) -> Path:
    """Write the argv-logging close/comment/view fake shared by issue tests."""
    fake = bin_dir / name
    body = [
        "import json, os, sys",
        "from pathlib import Path",
        f"log = Path(os.environ[{log_env!r}])",
        "entries = json.loads(log.read_text()) if log.exists() else []",
        "entries.append(sys.argv[1:])",
        "log.write_text(json.dumps(entries))",
        "if 'comment' in sys.argv: print('commented')",
        "if 'close' in sys.argv: print('closed')",
        (
            f"if 'view' in sys.argv: print(json.dumps({{'number': {number}, "
            f"'state': {state!r}, 'url': 'https://github.com/{repo}/issues/{number}'}}))"
        ),
    ]
    return write_python_executable(fake, body)


def load_module(module_name: str, module_path: Path, *, register: bool = False) -> ModuleType:
    """Load a script from a path, preserving the caller's registration choice."""
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    if register:
        sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def run_main(main: Callable[[], int], argv0: str, *args: str) -> SimpleNamespace:
    """Run a loaded CLI main with captured streams, without a child process."""
    out, err = io.StringIO(), io.StringIO()
    saved_argv = sys.argv
    sys.argv = [argv0, *args]
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main()
    finally:
        sys.argv = saved_argv
    return SimpleNamespace(returncode=code, stdout=out.getvalue(), stderr=err.getvalue())


# Bound at import so tests that wrap production ``subprocess.run`` cannot
# intercept fixture Git and poison the shared empty-git seed on disk.
_run = subprocess.run


def git(repo: Path, *args: str, env: Mapping[str, str] | None = None) -> str:
    """Run a fixture-repository git command and return trimmed stdout."""
    merged = None if env is None else {**os.environ, **env}
    return _run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env=merged,
    ).stdout.strip()


def _build_empty_git_dir_seed(seed_root: Path) -> None:
    repo = seed_root / "repo"
    repo.mkdir()
    git(repo, "init", "-q")


def _empty_git_dir_seed() -> Path:
    from tests.seed_cache import get_or_build

    return (
        get_or_build(
            "quality-gates-empty-git-dir-seed",
            _build_empty_git_dir_seed,
        )
        / "repo"
        / ".git"
    )


def _install_empty_git_dir(repo: Path, *, branch: str | None = None) -> None:
    shutil.copytree(_empty_git_dir_seed(), repo / ".git")
    if branch is not None:
        (repo / ".git" / "HEAD").write_text(
            f"ref: refs/heads/{branch}\n",
            encoding="utf-8",
        )


def _build_staged_readme_seed(seed_root: Path) -> None:
    """Build the common pre-commit index used by variable-message fixtures."""
    repo = seed_root / "repo"
    repo.mkdir()
    _install_empty_git_dir(repo)
    write_text(repo / "README.md", "# Test\n")
    git(repo, "add", "README.md")


def _staged_readme_seed() -> Path:
    from tests.seed_cache import get_or_build

    return (
        get_or_build(
            "quality-gates-staged-readme-seed",
            _build_staged_readme_seed,
        )
        / "repo"
        / ".git"
    )


def _install_staged_readme(repo: Path, *, branch: str | None = None) -> None:
    shutil.copytree(_staged_readme_seed(), repo / ".git")
    write_text(repo / "README.md", "# Test\n")
    if branch is not None:
        (repo / ".git" / "HEAD").write_text(
            f"ref: refs/heads/{branch}\n",
            encoding="utf-8",
        )


def init_git_repo(tmp_path: Path, name: str = "repo") -> Path:
    """Create a temporary repository and initialize its git metadata."""
    repo = make_repo(tmp_path, name)
    _install_empty_git_dir(repo)
    return repo


def seed_two_changed_pool_files(tmp_path: Path) -> tuple[Path, str, str]:
    """Create the shared two-file git history used by changed-line tests."""
    from tests.seed_cache import get_or_build

    def build(seed_root: Path) -> None:
        repo = seed_root / "repo"
        repo.mkdir()
        scripts = repo / "scripts"
        scripts.mkdir()
        _install_empty_git_dir(repo)
        for name in ("foo.py", "bar.py"):
            write_text(scripts / name, "def a():\n    return 1\n")
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "base")
        branch_ref = (repo / ".git" / "HEAD").read_text(encoding="ascii").strip()[5:]
        (seed_root / "base").write_text(
            (repo / ".git" / branch_ref).read_text(encoding="ascii").strip(),
            encoding="ascii",
        )
        for name in ("foo.py", "bar.py"):
            write_text(
                scripts / name,
                "def a():\n    return 1\n\n\ndef b():\n    return 2\n",
            )
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", "head")
        (seed_root / "head").write_text(
            (repo / ".git" / branch_ref).read_text(encoding="ascii").strip(),
            encoding="ascii",
        )

    seed = get_or_build("quality-gates-two-changed-pool-seed", build)
    repo = tmp_path / "repo"
    shutil.copytree(seed / "repo", repo)
    base = (seed / "base").read_text(encoding="ascii")
    head = (seed / "head").read_text(encoding="ascii")
    return repo, base, head


def seed_commit(repo: Path, body: str) -> None:
    """Create the small main-branch commit used by closeout fixtures."""
    _install_staged_readme(repo, branch="main")
    command = ["commit", "-m", "Resolve issue"]
    for paragraph in body.split("\n\n"):
        command.extend(["-m", paragraph])
    git(repo, *command)


def environment_with_path(
    path: Path,
    *,
    base: Mapping[str, str] | None = None,
    path_tail: str | None = None,
    **updates: str,
) -> dict[str, str]:
    """Copy an environment, control its fixture PATH, and add fixture variables."""
    environment = dict(os.environ if base is None else base)
    tail = path_tail if path_tail is not None else environment.get("PATH", "")
    environment["PATH"] = f"{path}:{tail}"
    environment.update(updates)
    return environment


def close_comment_args(
    repo_root: Path,
    body_file: Path,
    *,
    number: int = 42,
    classification: str = "question",
    repo: str = "corca-ai/charness",
) -> list[str]:
    """Build the stable issue close-with-comment argv used by fixture tests."""
    return [
        "close-with-comment",
        "--repo",
        repo,
        "--number",
        str(number),
        "--body-file",
        str(body_file),
        "--classification",
        classification,
        "--repo-root",
        str(repo_root),
    ]


def verify_closeout_args(
    repo_root: Path,
    *,
    numbers: Sequence[int] = (42,),
    classification: str = "bug",
    carrier: str = "direct-commit",
    commit_ref: str | None = None,
    body_file: Path | None = None,
    manual_fallback_reason: str | None = None,
    expect_state: str | None = None,
) -> list[str]:
    """Build the stable issue verify-closeout argv used by fixture tests."""
    args = [
        "verify-closeout",
        "--repo-root",
        str(repo_root),
        "--repo",
        "corca-ai/charness",
    ]
    for number in numbers:
        args.extend(["--number", str(number)])
    args.extend(["--classification", classification, "--carrier", carrier])
    if commit_ref is not None:
        args.extend(["--commit-ref", commit_ref])
    if body_file is not None:
        args.extend(["--body-file", str(body_file)])
    if manual_fallback_reason is not None:
        args.extend(["--manual-fallback-reason", manual_fallback_reason])
    if expect_state is not None:
        args.extend(["--expect-state", expect_state])
    return args


def _packaged_script(real_name: str) -> Path:
    """Where a repo script lives now: flat under scripts/ or inside a concept package."""
    flat = ROOT / "scripts" / real_name
    if flat.is_file():
        return flat
    found = sorted(p for p in (ROOT / "scripts").rglob(real_name) if p.is_file())
    if not found:
        raise FileNotFoundError(f"scripts/**/{real_name} is not in this checkout")
    return found[0]


def _seed_path(target_dir: Path, filename: str) -> Path:
    """Where a seeded script goes: the packaged path its real twin has, else flat.

    The declared gate rows spell `scripts/<pkg>/<name>.py` since the concept
    packaging, so a stub must sit where the row points or the runner reports a
    missing file instead of the stub's verdict.
    """
    real = ROOT / "scripts" / filename
    if not real.is_file() and target_dir.name == "scripts":
        found = sorted(p for p in (ROOT / "scripts").rglob(filename) if p.is_file())
        if found:
            relative = found[0].relative_to(ROOT / "scripts")
            path = target_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            for package_dir in relative.parents:
                if str(package_dir) != ".":
                    (target_dir / package_dir / "__init__.py").touch()
            return path
    path = target_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
