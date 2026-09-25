"""Entry slice E4: real-subprocess coverage for `charness` CLI entry lines.

Every test spawns the real in-repo `charness` entry as a subprocess with an
inherited-plus environment (never a replaced env, never a copied entry), with
an isolated tmp HOME/state-home and tmp cwd. Each test asserts real behavior
(returncode plus stdout/stderr content), not mere execution.
"""

from __future__ import annotations

import json
import os
import shutil
import site
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ENTRY = REPO_ROOT / "charness"

CURRENT_VERSION = json.loads(
    (REPO_ROOT / "packaging" / "charness.json").read_text(encoding="utf-8")
)["version"]

_SPAWN_TIMEOUT_SECONDS = 28

try:
    import coverage as _coverage_for_standalone_kids
except ImportError:  # plain runs without the coverage harness installed
    _COVERAGE_SITE_DIR = None
else:
    _COVERAGE_SITE_DIR = str(Path(_coverage_for_standalone_kids.__file__).resolve().parent.parent)

BLOCK_ENV = "CHARNESS_ENTRY_COV_BLOCK"
_STANDALONE_BLOCK = "scripts.cli.bootstrap"

# A `usercustomize` module (via a tmp PYTHONUSERBASE, staged per spawn when
# blocking) installs a `sys.meta_path` guard refusing the named modules, so
# the entry runs its `except ImportError` standalone fallback copies.
# `usercustomize` runs after `sitecustomize`, so coverage measurement keeps
# working; nothing is copied out of the tree.
#
# The guard refuses only the first two hits per name: the entry attempts the
# bootstrap import twice during startup, and init/update phase 2 re-imports
# it a third time from the checkout the run just ensured (the standalone-copy
# contract). Later hits load the checkout's tree.
_USERCUSTOMIZE = """import os

_names = [n.strip() for n in os.environ.get("%s", "").split(",") if n.strip()]
_hits = {}
if _names:
    import sys

    class _CharnessEntryCovBlocker:
        def find_spec(self, fullname, path=None, target=None):
            for n in _names:
                if fullname == n or fullname.startswith(n + "."):
                    seen = _hits.get(fullname, 0)
                    _hits[fullname] = seen + 1
                    if seen < 2:
                        raise ImportError(
                            "blocked for entry-fallback coverage test: " + fullname
                        )
                    return None
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


def _write_release_fixture(path: Path) -> str:
    payload = {
        "corca-ai/charness": {
            "tag_name": f"v{CURRENT_VERSION}",
            "html_url": f"https://github.com/corca-ai/charness/releases/tag/v{CURRENT_VERSION}",
            "published_at": "2026-01-01T00:00:00Z",
            "assets": [],
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _spawn(
    *argv: str,
    home: Path,
    cwd: Path,
    extra_env: dict[str, str] | None = None,
    block: bool = False,
) -> subprocess.CompletedProcess[str]:
    fixture = _write_release_fixture(home / "release-fixtures.json")
    # The tmp HOME below hides the real user site-packages (where `coverage`
    # lives), which would break subprocess coverage startup under the
    # COVERAGE_PROCESS_START recipe with "Error in sitecustomize". Pointing
    # PYTHONUSERBASE at the real user base keeps measurement working without
    # changing any CLI-resolved path (state still goes under tmp HOME).
    # With block=True the user base is a staged tmp dir whose usercustomize
    # refuses scripts.cli.bootstrap (standalone fallback copies); the real
    # user site is then re-exposed on PYTHONPATH for coverage startup.
    if block:
        userbase = _stage_userbase(home.parent)
        userbase_env = {
            "PYTHONUSERBASE": str(userbase),
            BLOCK_ENV: _STANDALONE_BLOCK,
        }
        if _COVERAGE_SITE_DIR is not None:
            userbase_env["PYTHONPATH"] = os.pathsep.join(
                [_COVERAGE_SITE_DIR, os.environ.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep)
    else:
        userbase_env = {"PYTHONUSERBASE": site.getuserbase()}
    env = {
        **os.environ,
        "HOME": str(home),
        **userbase_env,
        "CHARNESS_STATE_HOME": str(home / ".local" / "state"),
        "CHARNESS_NO_UPDATE_CHECK": "1",
        "CHARNESS_RELEASE_PROBE_FIXTURES": fixture,
        "CI": "",
        **(extra_env or {}),
    }
    return subprocess.run(
        [sys.executable, str(ENTRY), *argv],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT_SECONDS,
    )


def _real_repo_locks() -> set[str]:
    """Names under the real repo's (gitignored) lock dir.

    init/update upsert tool locks into their target checkout. Pointed at the
    real repo, a passing run leaves tmp-path locks behind; the next doctor
    run then reports support-sync "missing" for paths that no longer exist.
    The hermetic tests above must never add entries here.
    """
    locks_dir = REPO_ROOT / "integrations" / "locks"
    if not locks_dir.is_dir():
        return set()
    return {path.name for path in locks_dir.iterdir()}


def _isolated_dirs(tmp_path: Path, name: str) -> tuple[Path, Path]:
    home = tmp_path / f"{name}-home"
    cwd = tmp_path / f"{name}-cwd"
    home.mkdir(parents=True)
    cwd.mkdir(parents=True)
    return home, cwd


def test_version_with_explicit_repo_root_reports_packaging_version(
    tmp_path: Path,
) -> None:
    home, cwd = _isolated_dirs(tmp_path, "version")
    result = _spawn(
        "version",
        "--repo-root",
        str(REPO_ROOT),
        "--home-root",
        str(home),
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 0, result.stderr
    assert yaml.safe_load(result.stdout) == {"version": CURRENT_VERSION}


def test_reset_on_empty_home_reports_nothing_removed(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "reset")
    result = _spawn("reset", "--home-root", str(home), home=home, cwd=cwd)

    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["package_id"] == "charness"
    assert payload["removed_codex_marketplace_entry"] is False
    assert payload["removed_plugin_root"] is False


def _minimal_repo(tmp_path: Path, name: str) -> Path:
    """A hand-built checkout: manifest, contract, and a git repo.

    init/update regenerate the checkout's plugin mirror (and upsert its tool
    locks). A full seed clone keeps that off the real repo but trips the
    copy-heavy invariant; pointing at the real repo races sibling xdist
    workers syncing the same mirror (FileNotFoundError on
    plugins/charness/skills/<name> in the release battery).

    `scripts/` is a symlink to the real tree: install_surface invokes the
    checkout's own scripts, and chasing their import closure file by file
    snowballs. Reads resolve to the pinned tree (the same code a real-repo
    run would execute); every write the commands perform -- plugin mirror,
    tool locks, state, bytecode caches -- lands under the minimal repo or
    tmp HOME. `packaging/` stays real files (manifest + bootstrap contract).
    """
    repo = tmp_path / name
    (repo / "packaging").mkdir(parents=True)
    # The real manifest: init/update validate it against plugin.schema.json,
    # and the version assertion below pins CURRENT_VERSION, which the real
    # manifest carries by construction.
    shutil.copyfile(
        REPO_ROOT / "packaging" / "charness.json",
        repo / "packaging" / "charness.json",
    )
    shutil.copyfile(
        REPO_ROOT / "packaging" / "bootstrap-python.json",
        repo / "packaging" / "bootstrap-python.json",
    )
    os.symlink(REPO_ROOT / "scripts", repo / "scripts")
    # The manifest validator resolves the manifest's referenced source paths
    # (readme, skills, profiles, presets). Symlinks keep reads on the pinned
    # tree; writes (plugin mirror, tool locks) target repo-relative dirs that
    # stay real below.
    for relative in ("README.md", "skills", "profiles", "presets"):
        os.symlink(REPO_ROOT / relative, repo / relative)
    # integrations/tools holds read-only source manifests; integrations/locks
    # stays a real dir because init/update upsert tool locks into it.
    (repo / "integrations" / "locks").mkdir(parents=True)
    os.symlink(REPO_ROOT / "integrations" / "tools", repo / "integrations" / "tools")
    # The plugin marketplace manifests are validated (content generated from
    # the shared manifest, so the real copies match) but never rewritten by
    # init/update; real copies keep the validator quiet.
    (repo / ".claude-plugin").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
        repo / ".claude-plugin" / "marketplace.json",
    )
    (repo / ".agents" / "plugins").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        repo / ".agents" / "plugins" / "marketplace.json",
    )
    subprocess.run(["git", "init", "-b", "main", str(repo)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(repo), "commit", "-m", "seed", "--no-gpg-sign"],
        check=True,
        capture_output=True,
    )
    return repo


def test_init_from_explicit_checkout_refreshes_surface(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "init")
    repo = _minimal_repo(tmp_path, "init-source")
    locks_before = _real_repo_locks()
    target = tmp_path / "init-target"
    target.mkdir()
    result = _spawn(
        "init",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--target-repo-root",
        str(target),
        home=home,
        cwd=cwd,
    )
    assert _real_repo_locks() == locks_before

    assert result.returncode == 0, result.stderr
    assert "package_id: charness" in result.stdout
    assert f"checkout_version: {CURRENT_VERSION}" in result.stdout


def test_init_manifest_only_checkout_reports_bootstrap_failure(
    tmp_path: Path,
) -> None:
    home, cwd = _isolated_dirs(tmp_path, "init-fake")
    fake_checkout = tmp_path / "manifest-only-checkout"
    (fake_checkout / "packaging").mkdir(parents=True)
    (fake_checkout / "packaging" / "charness.json").write_text(
        json.dumps({"version": "0.0.0-e4probe"}), encoding="utf-8"
    )
    result = _spawn(
        "init",
        "--repo-root",
        str(fake_checkout),
        "--home-root",
        str(home),
        "--skip-cli-install",
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 1, result.stdout
    assert "bootstrap runtime for" in result.stderr
    assert "No such file or directory" in result.stderr


def test_update_from_explicit_checkout_refreshes_surface(tmp_path: Path) -> None:
    # Same hermeticity as the init test above (see _minimal_repo).
    home, cwd = _isolated_dirs(tmp_path, "update")
    repo = _minimal_repo(tmp_path, "update-source")
    locks_before = _real_repo_locks()
    result = _spawn(
        "update",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
    )
    assert _real_repo_locks() == locks_before

    assert result.returncode == 0, result.stderr
    assert "package_id: charness" in result.stdout
    assert "DONE: update complete" in result.stderr
    assert "STEP: refreshing source checkout" in result.stderr


def test_init_standalone_fallback_refreshes_surface(tmp_path: Path) -> None:
    """Standalone init covers the entry's `except ImportError` fallback bodies.

    With scripts.cli.bootstrap refused, init runs the fallback copies of the
    checkout/update plumbing instead of the tree modules.
    """
    home, cwd = _isolated_dirs(tmp_path, "init-standalone")
    repo = _minimal_repo(tmp_path, "init-standalone-source")
    locks_before = _real_repo_locks()
    target = tmp_path / "init-standalone-target"
    target.mkdir()
    result = _spawn(
        "init",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--target-repo-root",
        str(target),
        home=home,
        cwd=cwd,
        block=True,
    )
    assert _real_repo_locks() == locks_before

    assert result.returncode == 0, result.stderr
    assert "package_id: charness" in result.stdout
    # The standalone path reports the summary payload without the tree-only
    # DONE progress marker; the hermeticity assertions above are the point.
    assert "event: init" in result.stdout


def test_update_standalone_fallback_refreshes_surface(tmp_path: Path) -> None:
    """Standalone update covers the fallback refresh/reexec bodies."""
    home, cwd = _isolated_dirs(tmp_path, "update-standalone")
    repo = _minimal_repo(tmp_path, "update-standalone-source")
    locks_before = _real_repo_locks()
    result = _spawn(
        "update",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
        block=True,
    )
    assert _real_repo_locks() == locks_before

    assert result.returncode == 0, result.stderr
    assert "package_id: charness" in result.stdout
    assert "DONE: update complete" in result.stderr


def _write_checkout_cli(repo: Path, content: bytes, mode: int) -> Path:
    """Drop a `charness` binary into the checkout and set its mode."""
    cli = repo / "charness"
    cli.write_bytes(content)
    os.chmod(cli, mode)
    return cli


def test_update_identical_checkout_cli_skips_reexec(tmp_path: Path) -> None:
    """A byte-identical checkout CLI takes the no-reexec branch."""
    home, cwd = _isolated_dirs(tmp_path, "update-samecli")
    repo = _minimal_repo(tmp_path, "update-samecli-source")
    _write_checkout_cli(repo, ENTRY.read_bytes(), 0o755)
    result = _spawn(
        "update",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
        block=True,
    )

    assert result.returncode == 0, result.stderr
    assert "DONE: update complete" in result.stderr


def test_update_differing_checkout_cli_reexecutes(tmp_path: Path) -> None:
    """A differing checkout CLI re-execs into it (which then exits cleanly)."""
    home, cwd = _isolated_dirs(tmp_path, "update-diffcli")
    repo = _minimal_repo(tmp_path, "update-diffcli-source")
    _write_checkout_cli(repo, b"#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", 0o755)
    result = _spawn(
        "update",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
        block=True,
    )

    assert result.returncode == 0, result.stderr
    assert "re-executing the checkout's CLI" in result.stderr


def test_update_unexecutable_checkout_cli_continues(tmp_path: Path) -> None:
    """An unexecutable (but readable) checkout CLI degrades to a warning."""
    home, cwd = _isolated_dirs(tmp_path, "update-noexeccli")
    repo = _minimal_repo(tmp_path, "update-noexeccli-source")
    _write_checkout_cli(repo, b"#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", 0o644)
    result = _spawn(
        "update",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
        block=True,
    )

    # The failed re-exec degrades to a warning return: no DONE marker, but
    # the run still exits cleanly.
    assert result.returncode == 0, result.stderr
    assert "re-executing the checkout's CLI" in result.stderr


def test_update_unreadable_checkout_cli_returns_none(tmp_path: Path) -> None:
    """An unreadable checkout CLI takes the OSError branch (no re-exec)."""
    home, cwd = _isolated_dirs(tmp_path, "update-noreadcli")
    repo = _minimal_repo(tmp_path, "update-noreadcli-source")
    cli = _write_checkout_cli(repo, b"#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", 0o000)
    try:
        result = _spawn(
            "update",
            "--repo-root",
            str(repo),
            "--home-root",
            str(home),
            "--skip-cli-install",
            "--no-pull",
            home=home,
            cwd=cwd,
            block=True,
        )
    finally:
        os.chmod(cli, 0o644)

    assert result.returncode == 0, result.stderr
    assert "DONE: update complete" in result.stderr


def test_tool_doctor_standalone_resolves_tool_roots(tmp_path: Path) -> None:
    """Standalone `tool doctor` covers the fallback tool-root resolver."""
    home, cwd = _isolated_dirs(tmp_path, "tool-doctor")
    repo = _minimal_repo(tmp_path, "tool-doctor-source")
    locks_before = _real_repo_locks()
    result = _spawn(
        "tool",
        "doctor",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        home=home,
        cwd=cwd,
        block=True,
    )
    assert _real_repo_locks() == locks_before

    assert result.returncode == 0, result.stderr


def test_train_stats_reports_empty_payload(tmp_path: Path) -> None:
    """`train --stats` covers the entry's train-stats shim (tree mode)."""
    home, cwd = _isolated_dirs(tmp_path, "train-stats")
    repo = _minimal_repo(tmp_path, "train-stats-source")
    result = _spawn(
        "train",
        "--stats",
        "--repo-root",
        str(repo),
        "--window",
        "3h",
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 0, result.stderr
    assert "lands_in_window" in result.stdout


def test_version_verbose_readonly_state_dir_returns_state(tmp_path: Path) -> None:
    """An unwritable state dir covers the version-state OSError fallback."""
    home, cwd = _isolated_dirs(tmp_path, "version-readonly")
    state_dir = home / ".local" / "state"
    state_dir.mkdir(parents=True)
    os.chmod(state_dir, 0o555)
    try:
        result = _spawn(
            "version",
            "--verbose",
            "--home-root",
            str(home),
            home=home,
            cwd=cwd,
            block=True,
        )
    finally:
        os.chmod(state_dir, 0o755)

    assert result.returncode == 0, result.stderr
    assert CURRENT_VERSION in result.stdout


def test_update_manifest_only_checkout_reports_bootstrap_failure(
    tmp_path: Path,
) -> None:
    home, cwd = _isolated_dirs(tmp_path, "update-fake")
    fake_checkout = tmp_path / "manifest-only-checkout"
    (fake_checkout / "packaging").mkdir(parents=True)
    (fake_checkout / "packaging" / "charness.json").write_text(
        json.dumps({"version": "0.0.0-e4probe"}), encoding="utf-8"
    )
    result = _spawn(
        "update",
        "--repo-root",
        str(fake_checkout),
        "--home-root",
        str(home),
        "--skip-cli-install",
        "--no-pull",
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 1, result.stdout
    assert "STEP: refreshing source checkout" in result.stderr
    assert "bootstrap runtime for" in result.stderr
