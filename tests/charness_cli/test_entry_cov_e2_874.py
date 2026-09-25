"""Standalone-entry coverage for `charness` fallback lines 429-718 (slice 2).

The assigned lines live in the root entry's `except ImportError` fallback
copies of `scripts/cli/bootstrap*.py` (the standalone-copy contract pinned by
`test_cli_bootstrap_sync_873.py`). A plain spawn of the in-repo entry imports
the real `scripts.cli.bootstrap`, so the fallback never runs and none of these
lines is attributed.

Each test spawns the REAL in-repo entry (`sys.executable`, `ROOT / "charness"`)
with an inherited environment plus additions, in a mode that reproduces the
standalone condition the fallback exists for: a `usercustomize` module (via a
tmp `PYTHONUSERBASE`) installs a `sys.meta_path` guard that raises ImportError
for `scripts.cli.bootstrap` only. Nothing is copied out of the tree, `HOME`
and `CHARNESS_STATE_HOME` point at `tmp_path`, and `git` is a fixture script,
so no test touches the real home, the network, or the repo.

Every test asserts real behavior (returncode plus stdout/stderr content).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from .support import ROOT, build_test_path, make_release_fixture, pin_state_home

try:
    import coverage as _coverage_for_standalone_kids
except ImportError:  # plain runs without the coverage harness installed
    _COVERAGE_SITE_DIR = None
else:
    _COVERAGE_SITE_DIR = str(Path(_coverage_for_standalone_kids.__file__).resolve().parent.parent)

ENTRY = ROOT / "charness"
_STANDALONE_FLAG = "CHARNESS_ENTRY_STANDALONE_TEST"
_BLOCKED_MESSAGE = "blocked for standalone-entry coverage test"
_SPAWN_TIMEOUT = 25

_PACKAGING_VERSION = json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))[
    "version"
]

_USERCUSTOMIZE = f"""import os

if os.environ.get("{_STANDALONE_FLAG}") == "1":
    import sys

    class _CharnessStandaloneBlocker:
        def find_spec(self, fullname, path=None, target=None):
            if fullname == "scripts.cli.bootstrap":
                raise ImportError("{_BLOCKED_MESSAGE}")
            return None

    sys.meta_path.insert(0, _CharnessStandaloneBlocker())
"""

_FAKE_GIT = """#!/bin/sh
mode="${FAKE_GIT_MODE:-clean}"
case "$1 $2" in
  "status --short")
    if [ "$mode" = dirty ]; then echo " M dirty.py"; fi
    exit 0;;
  "pull --ff-only")
    # Divergence handling only runs when the fast-forward fails.
    if [ "$mode" = clean ]; then exit 0; fi
    exit 1;;
  "rev-parse --short")
    if [ "$mode" = revparse-fail ]; then exit 1; fi
    echo "abc1234"; exit 0;;
  "rev-parse --abbrev-ref")
    if [ "$mode" = no-upstream ]; then exit 1; fi
    echo "origin/main"; exit 0;;
  "rev-list --left-right")
    case "$mode" in
      revlist-fail) exit 1;;
      revlist-malformed) echo "0"; exit 0;;
      revlist-nonint) echo "a b"; exit 0;;
      diverged) echo "3 2"; exit 0;;
      *) echo "0 0"; exit 0;;
    esac;;
esac
if [ "$1" = clone ]; then
  mkdir -p "$3/packaging"
  printf '{"version":"0.0.0-fake"}' > "$3/packaging/charness.json"
  exit 0
fi
exit 1
"""


def _stage_carriers(tmp_path: Path) -> tuple[Path, Path]:
    """Write the usercustomize blocker and the fake git; return (userbase, bindir)."""
    userbase = tmp_path / "userbase"
    site_packages = (
        userbase
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    site_packages.mkdir(parents=True)
    (site_packages / "usercustomize.py").write_text(_USERCUSTOMIZE, encoding="utf-8")
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_git = fake_bin / "git"
    fake_git.write_text(_FAKE_GIT, encoding="utf-8")
    fake_git.chmod(0o755)
    return userbase, fake_bin


def _child_env(
    home: Path,
    userbase: Path,
    fake_bin: Path,
    extra: dict[str, str] | None = None,
) -> dict[str, str]:
    env = dict(os.environ)
    env["HOME"] = str(home)
    pin_state_home(env, home)
    env["PYTHONUSERBASE"] = str(userbase)
    env[_STANDALONE_FLAG] = "1"
    # PYTHONUSERBASE repoints the user site, which hides a user-site `coverage`
    # install from the child's sitecustomize startup. Prepending its directory
    # keeps process-startup measurement working under the coverage harness;
    # without the harness the variable is simply absent and nothing changes.
    if _COVERAGE_SITE_DIR is not None:
        inherited = env.get("PYTHONPATH", "")
        parts = inherited.split(os.pathsep) if inherited else []
        if _COVERAGE_SITE_DIR not in parts:
            env["PYTHONPATH"] = os.pathsep.join([_COVERAGE_SITE_DIR, *parts])
    env["PATH"] = build_test_path(fake_bin)
    env.pop("XDG_STATE_HOME", None)
    # Hermetic default: the release-probe fixture is opt-in per test, so a test
    # that needs the no-fixture probe path cannot inherit one from the ambient env.
    env.pop("CHARNESS_RELEASE_PROBE_FIXTURES", None)
    if extra:
        env.update(extra)
    return env


def _spawn(*args: str, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ENTRY), *args],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT,
        check=False,
    )


def _fresh_home(tmp_path: Path, name: str) -> tuple[Path, Path]:
    home = tmp_path / name
    work = tmp_path / f"{name}-work"
    home.mkdir(parents=True)
    work.mkdir(parents=True)
    return home, work


def _write_install_state(home: Path, repo_root: Path, *, managed: bool = True) -> Path:
    state_dir = home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True, exist_ok=True)
    path = state_dir / "install-state.json"
    path.write_text(
        json.dumps({"repo_root": str(repo_root), "managed_checkout": managed}) + "\n",
        encoding="utf-8",
    )
    return path


def _write_manifest(checkout: Path, version: str = "0.0.0-test") -> Path:
    packaging = checkout / "packaging"
    packaging.mkdir(parents=True, exist_ok=True)
    path = packaging / "charness.json"
    path.write_text(json.dumps({"version": version}) + "\n", encoding="utf-8")
    return path


def _newer_tag() -> str:
    major = str(_PACKAGING_VERSION).split(".")[0]
    return f"v{int(major) + 1}.0.0"


def _write_untagged_fixture(tmp_path: Path) -> Path:
    path = tmp_path / "untagged-fixtures.json"
    path.write_text(
        json.dumps(
            {
                "corca-ai/charness": {
                    "html_url": "https://example.invalid/r",
                    "published_at": "2026-01-01T00:00:00Z",
                    "assets": [],
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _seed_fresh_release_state(home: Path, tag: str, *, checked_at: str | None = None) -> Path:
    state_dir = home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True, exist_ok=True)
    version = tag.lstrip("v")
    if checked_at is None:
        checked_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    path = state_dir / "version-state.json"
    path.write_text(
        json.dumps(
            {
                "state_version": 1,
                "latest_release": {
                    "status": "ok",
                    "update_available": True,
                    "current_version": _PACKAGING_VERSION,
                    "latest_tag": tag,
                    "latest_version": version,
                    "html_url": "https://example.invalid/r",
                    "asset_names": [],
                    "checked_at": checked_at,
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def _refresh_env(home: Path, fixture: Path) -> dict[str, str]:
    return {
        "CI": "0",
        "CHARNESS_FORCE_UPDATE_CHECK": "1",
        "CHARNESS_RELEASE_PROBE_FIXTURES": str(fixture),
    }


# --- carrier self-checks: fail loudly if the standalone simulation breaks ---


def test_entry_cov_e2_usersite_carrier_active(tmp_path: Path) -> None:
    """PYTHONUSERBASE usercustomize loads in the child env (else nothing below covers)."""
    userbase, _ = _stage_carriers(tmp_path)
    env = dict(os.environ)
    env["PYTHONUSERBASE"] = str(userbase)
    result = subprocess.run(
        [sys.executable, "-c", "import site, sys; sys.exit(0 if site.ENABLE_USER_SITE else 1)"],
        env=env,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_entry_cov_e2_bootstrap_blocked(tmp_path: Path) -> None:
    """The guard makes `scripts.cli.bootstrap` unimportable while leaving the tree usable."""
    userbase, _ = _stage_carriers(tmp_path)
    env = dict(os.environ)
    env["PYTHONUSERBASE"] = str(userbase)
    env[_STANDALONE_FLAG] = "1"
    result = subprocess.run(
        [sys.executable, "-c", "import scripts.cli.bootstrap"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT,
        check=False,
    )
    assert result.returncode != 0
    assert _BLOCKED_MESSAGE in result.stderr


# --- side-effect-free surface: help, version, unknown subcommand ---


def test_entry_cov_e2_help(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-help")
    userbase, fake_bin = _stage_carriers(tmp_path)
    result = _spawn("--help", cwd=work, env=_child_env(home, userbase, fake_bin))
    assert result.returncode == 0
    assert "usage: charness" in result.stdout


def test_entry_cov_e2_unknown_subcommand(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-unknown")
    userbase, fake_bin = _stage_carriers(tmp_path)
    result = _spawn("frobnicate", cwd=work, env=_child_env(home, userbase, fake_bin))
    assert result.returncode == 2
    assert "invalid choice" in result.stderr


def test_entry_cov_e2_version_plain(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-version")
    userbase, fake_bin = _stage_carriers(tmp_path)
    result = _spawn(
        "version", "--home-root", str(home), cwd=work, env=_child_env(home, userbase, fake_bin)
    )
    assert result.returncode == 0, result.stderr
    assert f"version: {_PACKAGING_VERSION}" in result.stdout


def test_entry_cov_e2_version_verbose_provenance(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-verbose")
    userbase, fake_bin = _stage_carriers(tmp_path)
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        cwd=work,
        env=_child_env(home, userbase, fake_bin),
    )
    assert result.returncode == 0, result.stderr
    assert f"current_version: {_PACKAGING_VERSION}" in result.stdout
    assert "current_git_head: abc1234" in result.stdout


def test_entry_cov_e2_version_verbose_no_git_checkout(tmp_path: Path) -> None:
    checkout = tmp_path / "manifest-only"
    _write_manifest(checkout)
    home, work = _fresh_home(tmp_path, "home-nogit")
    userbase, fake_bin = _stage_carriers(tmp_path)
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        cwd=work,
        env=_child_env(home, userbase, fake_bin),
    )
    assert result.returncode == 0, result.stderr
    assert "current_version: 0.0.0-test" in result.stdout
    assert "current_git_head: null" in result.stdout


def test_entry_cov_e2_version_verbose_rev_parse_fails(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-revparse-fail")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin, {"FAKE_GIT_MODE": "revparse-fail"})
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "current_git_head: null" in result.stdout


def test_entry_cov_e2_version_check_refreshes_from_fixture(tmp_path: Path) -> None:
    tag = _newer_tag()
    fixture = make_release_fixture(tmp_path, charness_tag=tag)
    home, work = _fresh_home(tmp_path, "home-check")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin, {"CHARNESS_RELEASE_PROBE_FIXTURES": str(fixture)})
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(ROOT),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert f"latest_version: {tag.lstrip('v')}" in result.stdout
    assert "update_available: true" in result.stdout


def test_entry_cov_e2_version_check_without_fixture_probes_live(tmp_path: Path) -> None:
    """Without a fixture the probe attempts the network and records the failure.

    The loopback proxies refuse instantly, so no external traffic happens and the
    command still reports rc 0 with a recorded error payload.
    """
    home, work = _fresh_home(tmp_path, "home-nofixture")
    userbase, fake_bin = _stage_carriers(tmp_path)
    dead_proxy = "http://127.0.0.1:1"
    env = _child_env(
        home,
        userbase,
        fake_bin,
        {
            "HTTP_PROXY": dead_proxy,
            "HTTPS_PROXY": dead_proxy,
            "http_proxy": dead_proxy,
            "https_proxy": dead_proxy,
        },
    )
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(ROOT),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "latest_release_check" in result.stdout
    assert "update_available" in result.stdout
    state_path = home / ".local" / "state" / "charness" / "version-state.json"
    assert state_path.is_file()


# --- maybe_record_self_version_state refresh paths (version --verbose) ---


def _managed_refresh_base(tmp_path: Path, name: str) -> tuple[Path, Path, Path, Path]:
    home, work = _fresh_home(tmp_path, name)
    userbase, fake_bin = _stage_carriers(tmp_path)
    _write_install_state(home, ROOT)
    return home, work, userbase, fake_bin


def test_entry_cov_e2_version_verbose_refresh_newer_release(tmp_path: Path) -> None:
    tag = _newer_tag()
    fixture = make_release_fixture(tmp_path, charness_tag=tag)
    home, work, userbase, fake_bin = _managed_refresh_base(tmp_path, "home-refresh")
    env = _child_env(home, userbase, fake_bin, _refresh_env(home, fixture))
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "charness release available" in result.stderr
    state = json.loads(
        (home / ".local" / "state" / "charness" / "version-state.json").read_text(encoding="utf-8")
    )
    assert state["latest_release"]["update_available"] is True


def test_entry_cov_e2_version_verbose_refresh_untagged_release(tmp_path: Path) -> None:
    fixture = _write_untagged_fixture(tmp_path)
    home, work, userbase, fake_bin = _managed_refresh_base(tmp_path, "home-untagged")
    env = _child_env(home, userbase, fake_bin, _refresh_env(home, fixture))
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "update_available: null" in result.stdout
    assert "release available" not in result.stderr


def test_entry_cov_e2_version_verbose_fresh_cache_skips_probe(tmp_path: Path) -> None:
    tag = _newer_tag()
    home, work, userbase, fake_bin = _managed_refresh_base(tmp_path, "home-fresh")
    _seed_fresh_release_state(home, tag)
    env = _child_env(
        home,
        userbase,
        fake_bin,
        {
            "CI": "0",
            "CHARNESS_FORCE_UPDATE_CHECK": "1",
            # A probe would crash on this missing file; rc 0 proves it never runs.
            "CHARNESS_RELEASE_PROBE_FIXTURES": str(tmp_path / "does-not-exist.json"),
        },
    )
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "charness release available" in result.stderr


def test_entry_cov_e2_version_verbose_stale_cache_refreshes(tmp_path: Path) -> None:
    tag = _newer_tag()
    fixture = make_release_fixture(tmp_path, charness_tag=tag)
    home, work, userbase, fake_bin = _managed_refresh_base(tmp_path, "home-stale")
    stale = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat().replace("+00:00", "Z")
    _seed_fresh_release_state(home, tag, checked_at=stale)
    env = _child_env(home, userbase, fake_bin, _refresh_env(home, fixture))
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "charness release available" in result.stderr


# --- update error and pull matrix (fake git, tmp HOME) ---


def _update(
    tmp_path: Path,
    name: str,
    *args: str,
    fake_mode: str = "clean",
    install_state: bool = False,
) -> subprocess.CompletedProcess[str]:
    home, work = _fresh_home(tmp_path, name)
    userbase, fake_bin = _stage_carriers(tmp_path)
    if install_state:
        _write_install_state(home, ROOT)
    env = _child_env(home, userbase, fake_bin, {"FAKE_GIT_MODE": fake_mode})
    return _spawn("update", "--home-root", str(home), *args, cwd=work, env=env)


def test_entry_cov_e2_update_missing_checkout(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-missing")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "STEP: refreshing source checkout" in result.stderr
    assert "missing source checkout" in result.stderr


def test_entry_cov_e2_update_noncheckout_dir(tmp_path: Path) -> None:
    claimed = tmp_path / "claimed"
    claimed.mkdir()
    (claimed / "stray.txt").write_text("not a checkout\n", encoding="utf-8")
    home, work = _fresh_home(tmp_path, "home-noncheckout")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn(
        "update",
        "--home-root",
        str(home),
        "--repo-root",
        str(claimed),
        "--skip-cli-install",
        cwd=work,
        env=env,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "is not a charness source checkout" in result.stderr


def test_entry_cov_e2_update_empty_dir(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    home, work = _fresh_home(tmp_path, "home-empty")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn(
        "update",
        "--home-root",
        str(home),
        "--repo-root",
        str(empty),
        "--skip-cli-install",
        cwd=work,
        env=env,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "missing explicit source checkout" in result.stderr


def test_entry_cov_e2_update_manifest_without_git(tmp_path: Path) -> None:
    checkout = tmp_path / "manifest-nogit"
    _write_manifest(checkout)
    home, work = _fresh_home(tmp_path, "home-notgit")
    userbase, fake_bin = _stage_carriers(tmp_path)
    _write_install_state(home, checkout)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn("update", "--home-root", str(home), cwd=work, env=env)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "is not a git checkout" in result.stderr


def test_entry_cov_e2_update_dirty_checkout_refused(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-dirty", fake_mode="dirty", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "has tracked local changes" in result.stderr


def test_entry_cov_e2_update_pull_clean_then_phase_two_import_error(
    tmp_path: Path,
) -> None:
    """Pull succeeds via fake git; phase two cannot import the blocked module."""
    result = _update(tmp_path, "home-clean", fake_mode="clean", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "STEP: refreshing source checkout" in result.stderr
    assert "ImportError" in result.stderr


def test_entry_cov_e2_update_diverged_checkout_refused(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-diverged", fake_mode="diverged", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "diverged from" in result.stderr


def test_entry_cov_e2_update_no_pull_skips_fetch(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-nopull", "--no-pull", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "STEP: refreshing source checkout" in result.stderr
    assert "ImportError" in result.stderr


def test_entry_cov_e2_update_without_upstream(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-noupstream", fake_mode="no-upstream", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "failed with exit code 1" in result.stderr


def test_entry_cov_e2_update_rev_list_fails(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-revfail", fake_mode="revlist-fail", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "failed with exit code 1" in result.stderr


def test_entry_cov_e2_update_rev_list_malformed(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-revmal", fake_mode="revlist-malformed", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "failed with exit code 1" in result.stderr


def test_entry_cov_e2_update_rev_list_non_integer(tmp_path: Path) -> None:
    result = _update(tmp_path, "home-revint", fake_mode="revlist-nonint", install_state=True)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "failed with exit code 1" in result.stderr


# --- init paths: contract, clone, re-exec ---


def test_entry_cov_e2_init_proof_run_from_checkout(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-init")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn(
        "init",
        "--home-root",
        str(home),
        "--repo-root",
        str(ROOT),
        "--skip-cli-install",
        cwd=work,
        env=env,
    )
    assert result.returncode == 1
    assert result.stdout == ""
    assert "ImportError" in result.stderr


def test_entry_cov_e2_init_clones_managed_checkout(tmp_path: Path) -> None:
    home, work = _fresh_home(tmp_path, "home-clone")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn("init", "--home-root", str(home), "--skip-cli-install", cwd=work, env=env)
    assert result.returncode == 1
    assert "ImportError" in result.stderr
    cloned = home / ".agents" / "src" / "charness"
    assert (cloned / "packaging" / "charness.json").is_file()


def test_entry_cov_e2_init_reexec_unreadable_checkout_cli(tmp_path: Path) -> None:
    checkout = tmp_path / "unreadable-checkout"
    _write_manifest(checkout)
    cli_copy = checkout / "charness"
    cli_copy.write_bytes(b"unreadable")
    cli_copy.chmod(0o000)
    home, work = _fresh_home(tmp_path, "home-unreadable")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    try:
        result = _spawn(
            "init",
            "--home-root",
            str(home),
            "--repo-root",
            str(checkout),
            "--skip-cli-install",
            cwd=work,
            env=env,
        )
    finally:
        cli_copy.chmod(0o644)
    assert result.returncode == 1
    assert "ImportError" in result.stderr


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read mode-000 files")
def test_entry_cov_e2_init_reexec_unreadable_is_oserror(tmp_path: Path) -> None:
    """The unreadable checkout CLI must fail at read time, before any re-exec."""
    checkout = tmp_path / "unreadable-checkout2"
    _write_manifest(checkout)
    cli_copy = checkout / "charness"
    cli_copy.write_bytes(b"unreadable")
    cli_copy.chmod(0o000)
    home, work = _fresh_home(tmp_path, "home-unreadable2")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    try:
        result = _spawn(
            "init",
            "--home-root",
            str(home),
            "--repo-root",
            str(checkout),
            "--skip-cli-install",
            cwd=work,
            env=env,
        )
    finally:
        cli_copy.chmod(0o644)
    assert result.returncode == 1
    assert "re-executing the checkout" not in result.stderr


def test_entry_cov_e2_task_command_skips_version_state(tmp_path: Path) -> None:
    """`task` payloads never record version state; the loader refuses first."""
    home, work = _fresh_home(tmp_path, "home-task")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn("task", "status", cwd=work, env=env)
    assert result.returncode == 1
    assert result.stdout == ""
    assert "ImportError" in result.stderr
    assert not (home / ".local" / "state" / "charness" / "version-state.json").exists()


def test_entry_cov_e2_init_reexec_runs_checkout_cli(tmp_path: Path) -> None:
    """A differing checkout CLI is re-executed; the child owns the run afterwards."""
    checkout = tmp_path / "live-checkout"
    _write_manifest(checkout)
    (checkout / "charness").write_text(
        "#!/usr/bin/env python3\nprint('mini-checkout-cli')\n", encoding="utf-8"
    )
    home, work = _fresh_home(tmp_path, "home-reexec")
    userbase, fake_bin = _stage_carriers(tmp_path)
    env = _child_env(home, userbase, fake_bin)
    result = _spawn(
        "init",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        "--skip-cli-install",
        cwd=work,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "mini-checkout-cli" in result.stdout
    assert "re-executing the checkout" in result.stderr
