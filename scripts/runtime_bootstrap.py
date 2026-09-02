from __future__ import annotations

import hashlib
import importlib
import importlib.util
import os
import shlex
import sys
import tempfile
from collections.abc import MutableMapping
from pathlib import Path
from types import ModuleType

_ORIGINAL_DONT_WRITE_BYTECODE = sys.dont_write_bytecode
MANAGED_RUNTIME_PATH_KEYS = (
    "CHARNESS_RUNTIME_ROOT",
    "CHARNESS_RUNTIME_ROOT_AUTO",
    "CHARNESS_RUNTIME_REPO_KEY",
    "PYTHONPYCACHEPREFIX",
    "TMPDIR",
    "TMP",
    "TEMP",
    "PYTEST_DEBUG_TEMPROOT",
    "CHARNESS_PYTEST_CACHE_DIR",
    "RUFF_CACHE_DIR",
    "COVERAGE_FILE",
    "XDG_CACHE_HOME",
    "PIP_CACHE_DIR",
    "NPM_CONFIG_CACHE",
    "npm_config_cache",
)
# The import machinery decides this module's cache path before executing its
# body. Suppress only this early window; configure_runtime_environment restores
# normal bytecode caching after it has installed the external prefix.
if not _ORIGINAL_DONT_WRITE_BYTECODE:
    sys.dont_write_bytecode = True


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _bootstrap_pycache_prefix() -> None:
    """Choose a safe bytecode prefix before this module's first local import."""
    if sys.dont_write_bytecode:
        return
    configured = os.environ.get("PYTHONPYCACHEPREFIX", "").strip()
    repo_root = Path(__file__).resolve().parent.parent
    if configured and not _is_inside(Path(configured).expanduser().resolve(), repo_root):
        return
    base = (
        Path(
            os.environ.get("XDG_CACHE_HOME", "").strip()
            or os.environ.get("TMPDIR", "").strip()
            or tempfile.gettempdir()
        )
        .expanduser()
        .resolve()
    )
    if _is_inside(base, repo_root):
        base = Path(tempfile.gettempdir()).resolve()
    if _is_inside(base, repo_root):
        base = Path("/tmp").resolve()
    key = hashlib.sha256(str(repo_root).encode("utf-8")).hexdigest()[:16]
    sys.pycache_prefix = str(base / "charness" / "runtime" / key / "pycache")


_bootstrap_pycache_prefix()


class RuntimeEnvironmentError(RuntimeError):
    """The runtime was explicitly pointed at a repo-local output path."""


def _repo_runtime_key(repo_root: Path) -> str:
    return hashlib.sha256(str(repo_root.resolve()).encode("utf-8")).hexdigest()[:16]


def _runtime_root(repo_root: Path, env: MutableMapping[str, str]) -> tuple[Path, bool]:
    runtime_key = _repo_runtime_key(repo_root)
    configured = env.get("CHARNESS_RUNTIME_ROOT", "").strip()
    auto_root = env.get("CHARNESS_RUNTIME_ROOT_AUTO") == "1"
    if configured and not (auto_root and env.get("CHARNESS_RUNTIME_REPO_KEY") != runtime_key):
        root = Path(configured).expanduser().resolve()
        if _is_inside(root, repo_root.resolve()):
            raise RuntimeEnvironmentError(
                "CHARNESS_RUNTIME_ROOT must be outside the repository: "
                f"{root} (repo: {repo_root.resolve()})"
            )
        # Preserve the auto-root marker when this is the same repo's second
        # bootstrap call. Dropping it here made a later fixture/worktree reuse
        # the first repo's runtime root, so run records and caches crossed
        # boundaries despite the key-aware branch above.
        return root, auto_root

    base_text = (
        env.get("XDG_CACHE_HOME", "").strip()
        or env.get("TMPDIR", "").strip()
        or tempfile.gettempdir()
    )
    base = Path(base_text).expanduser().resolve()
    if _is_inside(base, repo_root.resolve()):
        base = Path(tempfile.gettempdir()).resolve()
    if _is_inside(base, repo_root.resolve()):
        base = Path("/tmp").resolve()
    return base / "charness" / "runtime" / runtime_key, True


def runtime_root(repo_root: str | Path, env: MutableMapping[str, str] | None = None) -> Path:
    """Return the external runtime root without creating any directories."""
    root = Path(repo_root).expanduser().resolve()
    target = os.environ if env is None else env
    return _runtime_root(root, target)[0]


def _external_setting(
    env: MutableMapping[str, str],
    key: str,
    default: Path,
    repo_root: Path,
) -> str:
    raw = env.get(key, "").strip()
    if raw in {"", ":memory:"}:
        return str(default.resolve()) if raw == "" else raw
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute() or _is_inside(candidate.resolve(), repo_root.resolve()):
        return str(default.resolve())
    return str(candidate.resolve())


def configure_runtime_environment(
    repo_root: str | Path,
    env: MutableMapping[str, str] | None = None,
) -> dict[str, str]:
    """Route interpreter and tool scratch output outside ``repo_root``.

    The returned mapping is also written into ``env``. With no mapping supplied,
    the real process environment and Python's active bytecode prefix are updated so
    direct repo scripts and their children share the same external runtime root.
    """
    root = Path(repo_root).expanduser().resolve()
    target = os.environ if env is None else env
    runtime_root, auto_root = _runtime_root(root, target)
    paths = {
        "CHARNESS_RUNTIME_ROOT": runtime_root,
        "PYTHONPYCACHEPREFIX": runtime_root / "pycache",
        "TMPDIR": runtime_root / "tmp",
        "TMP": runtime_root / "tmp",
        "TEMP": runtime_root / "tmp",
        "PYTEST_DEBUG_TEMPROOT": runtime_root / "pytest-tmp",
        "CHARNESS_PYTEST_CACHE_DIR": runtime_root / "pytest-cache",
        "RUFF_CACHE_DIR": runtime_root / "ruff",
        "COVERAGE_FILE": runtime_root / "coverage" / ".coverage",
        "XDG_CACHE_HOME": runtime_root / "xdg-cache",
        "PIP_CACHE_DIR": runtime_root / "pip",
        "NPM_CONFIG_CACHE": runtime_root / "npm",
    }
    for key, default in paths.items():
        if key == "CHARNESS_RUNTIME_ROOT":
            value = str(default)
        else:
            value = _external_setting(target, key, default, root)
        target[key] = value
    if auto_root:
        target["CHARNESS_RUNTIME_ROOT_AUTO"] = "1"
        target["CHARNESS_RUNTIME_REPO_KEY"] = _repo_runtime_key(root)
    else:
        target.pop("CHARNESS_RUNTIME_ROOT_AUTO", None)
        target.pop("CHARNESS_RUNTIME_REPO_KEY", None)

    for key in (
        "CHARNESS_RUNTIME_ROOT",
        "PYTHONPYCACHEPREFIX",
        "TMPDIR",
        "TMP",
        "TEMP",
        "PYTEST_DEBUG_TEMPROOT",
        "CHARNESS_PYTEST_CACHE_DIR",
        "RUFF_CACHE_DIR",
        "XDG_CACHE_HOME",
        "PIP_CACHE_DIR",
        "NPM_CONFIG_CACHE",
    ):
        Path(target[key]).mkdir(parents=True, exist_ok=True)
    target["npm_config_cache"] = target["NPM_CONFIG_CACHE"]
    # pytest has no standard environment variable for its cache directory. Keep
    # the override at the one Python execution boundary so every Charness-owned
    # Python entrypoint gives its children the same external cache. A later
    # explicit command-line option remains the caller's choice.
    pytest_cache_option = shlex.join(["-o", f"cache_dir={target['CHARNESS_PYTEST_CACHE_DIR']}"])
    existing_addopts = target.get("PYTEST_ADDOPTS", "").strip()
    if pytest_cache_option not in existing_addopts:
        target["PYTEST_ADDOPTS"] = f"{existing_addopts} {pytest_cache_option}".strip()
    coverage_file = target["COVERAGE_FILE"]
    if coverage_file != ":memory:":
        Path(coverage_file).parent.mkdir(parents=True, exist_ok=True)

    if env is None:
        if hasattr(sys, "pycache_prefix"):
            sys.pycache_prefix = target["PYTHONPYCACHEPREFIX"]
        tempfile.tempdir = target["TMPDIR"]
        if not _ORIGINAL_DONT_WRITE_BYTECODE:
            sys.dont_write_bytecode = False
    return dict(target)


def repo_root_from_script(script_file: str | Path) -> Path:
    override = os.environ.get("CHARNESS_REPO_ROOT")
    if override:
        root = Path(override).expanduser().resolve()
    else:
        script_path = Path(script_file).resolve()
        root = next(
            (
                ancestor
                for ancestor in script_path.parents
                if (ancestor / "scripts" / "adapter_lib.py").is_file()
            ),
            None,
        )
        if root is None:
            raise RuntimeError(
                f"cannot resolve a repository root for script {script_path}: "
                "no ancestor contains `scripts/adapter_lib.py`"
            )
    configure_runtime_environment(root)
    return root


def import_repo_module(script_file: str | Path, module_name: str) -> ModuleType:
    repo_root = repo_root_from_script(script_file)
    repo_root_text = str(repo_root)
    if repo_root_text not in sys.path:
        sys.path.insert(0, repo_root_text)
    return importlib.import_module(module_name)


def load_path_module(module_name: str, module_path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module spec for {module_name} from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def skill_script(repo_root: Path, skill: str, name: str) -> Path:
    """A script inside a skill package, in the dev tree OR in the collapsed export.

    `skills/public/<skill>/scripts/` in this repo; `skills/<skill>/scripts/` once
    exported, because the export collapses the `public` segment. Every caller that
    reaches into another skill's scripts needs both spellings, and each one had
    grown its own copy of this four-line search with its own error string.
    """
    for candidate in (
        repo_root / "skills" / "public" / skill / "scripts" / name,
        repo_root / "skills" / skill / "scripts" / name,
    ):
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"{skill} script {name} not found under {repo_root}")


def arm_cli_timeout(
    *,
    label: str,
    default_seconds: int = 10,
):
    module = import_repo_module(__file__, "scripts.core.script_timeout")
    return module.arm_cli_timeout(label=label, default_seconds=default_seconds)


def require_repo_local_helper(script_file: str | Path, repo_root: str | Path, **kwargs) -> dict:
    """Refuse a write helper that belongs to a different, drifted charness tree.

    Lazily loaded from the running script's own tree, like ``arm_cli_timeout``, so
    the guard is always the copy that shipped with the helper being guarded.
    """

    module = import_repo_module(__file__, "scripts.core.helper_provenance_lib")
    return module.require_repo_local_helper(script_file, repo_root, **kwargs)
