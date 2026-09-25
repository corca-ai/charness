"""Entry slice E1: real-subprocess coverage probes for the `charness` CLI entry.

Every test here spawns the REAL in-repo entry (``REPO_ROOT / "charness"``)
as a subprocess with an INHERITED environment. In-process exec/import of the
entry attributes zero coverage lines, out-of-tree copies are dropped from
coverage, and an env-replacing ``env=`` would cut off COVERAGE_PROCESS_START,
so all three are avoided: ``env={**os.environ, ...}`` always.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRY = REPO_ROOT / "charness"
PACKAGING_VERSION = json.loads(
    (REPO_ROOT / "packaging" / "charness.json").read_text(encoding="utf-8")
)["version"]
BLOCK_ENV = "CHARNESS_ENTRY_COV_BLOCK"
_STANDALONE_BLOCK = "scripts.cli.bootstrap"

try:
    import coverage as _coverage_for_standalone_kids
except ImportError:  # plain runs without the coverage harness installed
    _COVERAGE_SITE_DIR = None
else:
    _COVERAGE_SITE_DIR = str(Path(_coverage_for_standalone_kids.__file__).resolve().parent.parent)

# A `usercustomize` module (via a tmp PYTHONUSERBASE, staged per spawn)
# installs a `sys.meta_path` guard that raises ImportError for the modules
# named by BLOCK_ENV, forcing the entry's `except ImportError` standalone
# fallback copies. `usercustomize` runs after `sitecustomize`, so the coverage
# harness's measurement keeps working; nothing is copied out of the tree.
_USERCUSTOMIZE = """import os

_names = [n.strip() for n in os.environ.get("%s", "").split(",") if n.strip()]
if _names:
    import sys

    class _CharnessEntryCovBlocker:
        def find_spec(self, fullname, path=None, target=None):
            if fullname in _names or any(
                fullname == n or fullname.startswith(n + ".") for n in _names
            ):
                raise ImportError("blocked for entry-fallback coverage test: " + fullname)
            return None

    sys.meta_path.insert(0, _CharnessEntryCovBlocker())
""" % (BLOCK_ENV,)


def _stage_userbase(tmp_path: Path) -> Path:
    """Write the blocker usercustomize; return the tmp PYTHONUSERBASE."""
    userbase = tmp_path / "userbase"
    site_packages = (
        userbase
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    site_packages.mkdir(parents=True, exist_ok=True)
    (site_packages / "usercustomize.py").write_text(_USERCUSTOMIZE, encoding="utf-8")
    return userbase


def spawn(
    *args: str,
    tmp_path: Path,
    cwd: Path | None = None,
    block: bool = True,
) -> subprocess.CompletedProcess[str]:
    """Spawn the real entry with inherited env and tmp-isolated state homes.

    With ``block`` (the default) the entry's `scripts.cli.bootstrap` import
    is refused so the standalone fallback copies execute; with
    ``block=False`` the spawn runs in plain tree mode.
    """
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "HOME": str(home),
        "CHARNESS_STATE_HOME": str(home / ".local" / "state"),
    }
    if block:
        env[BLOCK_ENV] = _STANDALONE_BLOCK
    else:
        env.pop(BLOCK_ENV, None)
    # Stage the blocker usercustomize for every spawn (it reads BLOCK_ENV in
    # the child; with the variable popped it blocks nothing). PYTHONUSERBASE
    # repoints the user site, which can hide a user-site `coverage` install
    # from the child's startup, so prepend its directory when present.
    env["PYTHONUSERBASE"] = str(_stage_userbase(tmp_path))
    if _COVERAGE_SITE_DIR is not None:
        inherited = env.get("PYTHONPATH", "")
        parts = inherited.split(os.pathsep) if inherited else []
        if _COVERAGE_SITE_DIR not in parts:
            env["PYTHONPATH"] = os.pathsep.join([_COVERAGE_SITE_DIR, *parts])
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        env=env,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=25,
    )


def test_entry_top_help(tmp_path: Path) -> None:
    result = spawn("--help", tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "usage: charness" in result.stdout
    assert "version" in result.stdout


def test_entry_version_alias(tmp_path: Path) -> None:
    result = spawn("--version", tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().startswith(f"version: {PACKAGING_VERSION}"), result.stdout


def test_entry_version_subcommand_with_tmp_home(tmp_path: Path) -> None:
    home_root = tmp_path / "version-home"
    home = tmp_path / "home"
    home.mkdir(parents=True, exist_ok=True)
    env = {
        **os.environ,
        "HOME": str(home),
        "CHARNESS_STATE_HOME": str(home / ".local" / "state"),
    }
    result = subprocess.run(
        [sys.executable, str(ENTRY), "version", "--home-root", str(home_root)],
        env=env,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=25,
    )

    assert result.returncode == 0, result.stderr
    assert PACKAGING_VERSION in result.stdout


def test_entry_version_subcommand_help(tmp_path: Path) -> None:
    result = spawn("version", "--help", tmp_path=tmp_path)

    assert result.returncode == 0, result.stderr
    assert "--home-root" in result.stdout


def test_entry_unknown_subcommand_fails(tmp_path: Path) -> None:
    result = spawn("boguscmd-e1-probe", tmp_path=tmp_path)

    assert result.returncode == 2, (result.returncode, result.stdout, result.stderr)
    assert "invalid choice" in result.stderr


def test_entry_version_bad_flag_fails(tmp_path: Path) -> None:
    result = spawn("version", "--no-such-flag-e1", tmp_path=tmp_path)

    assert result.returncode == 2, (result.returncode, result.stdout, result.stderr)
    assert "unrecognized arguments" in result.stderr


def test_entry_cwd_isolated_spawn_stays_in_tree_mode(tmp_path: Path) -> None:
    """Even with cwd outside the tree, the entry still resolves its own dir.

    ``python <path>/charness`` puts the script's directory (the repo root) on
    ``sys.path[0]``, so ``from scripts.cli import ...`` keeps succeeding and
    the ``except ImportError`` standalone fallbacks never trigger. This pins
    that behavior: a cwd-isolated spawn still reports the tree version.
    """
    isolated = tmp_path / "cwd"
    isolated.mkdir(parents=True, exist_ok=True)
    result = spawn(
        "version",
        "--home-root",
        str(tmp_path / "iso-home"),
        tmp_path=tmp_path,
        cwd=isolated,
        block=False,
    )

    assert result.returncode == 0, result.stderr
    assert PACKAGING_VERSION in result.stdout
