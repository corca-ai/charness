"""Entry slice E5: real-subprocess coverage for leftover `charness` changed lines.

Slices E1-E4 covered the fallback bodies their scenarios reach. The
release changed-line lane still reports 48 uncovered changed lines in the
root entry, in four groups, each covered here with a real spawn of the
in-repo entry (inherited env, never a replaced env, never a copied entry;
in-process exec/import of the entry attributes zero coverage lines):

- installed-CLI auto-update gates (``should_auto_refresh_self_release``):
  eligibility needs ``--cli-path`` pointing at the running entry plus a
  managed install state; ``version --check`` and ``update`` then walk the
  NO_UPDATE_CHECK / CI / FORCE / tty branches for real.
- re-exec guard rails (``maybe_reexec_refreshed_cli``): a wrapper process
  sets the re-exec guard to its own pid and image-replaces into the entry,
  so the inner run observes a re-exec child; an over-long checkout path
  would fail execve, and an oversized environment makes it fail
  deterministically (E2BIG) while the run degrades to a warning.
- diverged managed checkouts (``_diverged_checkout_detail``): a seeded
  local origin plus clone gives real ahead/behind divergence, so
  standalone ``update`` renders the unique/redundant/truncated detail.
- tool-doctor resolver (``resolve_tool_repo_root``): refusing
  ``scripts.cli.tool_commands`` on top of the bootstrap block drives the
  ``_load_feature`` fallback ``check`` path for real.
- stale current release (``compare_semver_like`` left-greater): a fixture
  older than the packaged version walks the downgrade branch.

Lines that no measured spawn can reach (unembedded-entry-only branches,
the ``required=True`` raise with a sole ``required=False`` caller, the
impossible empty semver core, the in-process-only ``__getattr__`` raise)
carry ``# pragma: no cover`` in the entry with the reason inline; the
dead ``cmd_train_stats`` entry shim (no callers, uncallable via dispatch)
was deleted instead.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

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
_REEXEC_GUARD_ENV = "CHARNESS_CLI_REEXECUTED"

# Same two-hit blocker contract as slice E4: the entry attempts the bootstrap
# import twice during startup (both refused, so the fallback copies run) and
# init/update phase 2 re-imports a third time from the ensured checkout.
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


def _write_release_fixture(home: Path) -> str:
    payload = {
        "corca-ai/charness": {
            "tag_name": f"v{CURRENT_VERSION}",
            "html_url": f"https://github.com/corca-ai/charness/releases/tag/v{CURRENT_VERSION}",
            "published_at": "2026-01-01T00:00:00Z",
            "assets": [],
        }
    }
    path = home / "release-fixtures.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def _spawn(
    *argv: str,
    home: Path,
    cwd: Path,
    extra_env: dict[str, str] | None = None,
    drop_vars: tuple[str, ...] = (),
    block: str | None = _STANDALONE_BLOCK,
) -> subprocess.CompletedProcess[str]:
    fixture = _write_release_fixture(home)
    userbase = _stage_userbase(home.parent)
    userbase_env = {"PYTHONUSERBASE": str(userbase)}
    if block:
        userbase_env[BLOCK_ENV] = block
    if _COVERAGE_SITE_DIR is not None:
        userbase_env["PYTHONPATH"] = os.pathsep.join(
            [_COVERAGE_SITE_DIR, os.environ.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)
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
    for var in drop_vars:
        env.pop(var, None)
    # The release battery exports CHARNESS_FORCE_UPDATE_CHECK; without
    # scrubbing, the auto-update gate tests below would take the forced
    # branch instead of the opt-out / CI / tty branches they name.
    env.pop("CHARNESS_FORCE_UPDATE_CHECK", None)
    return subprocess.run(
        [sys.executable, str(ENTRY), *argv],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT_SECONDS,
    )


def _isolated_dirs(tmp_path: Path, name: str) -> tuple[Path, Path]:
    home = tmp_path / f"{name}-home"
    cwd = tmp_path / f"{name}-cwd"
    home.mkdir(parents=True)
    cwd.mkdir(parents=True)
    return home, cwd


def _minimal_tree(dest: Path) -> Path:
    """The checkout content init/update phase 2 needs, rooted at ``dest``."""
    (dest / "packaging").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / "packaging" / "charness.json",
        dest / "packaging" / "charness.json",
    )
    shutil.copyfile(
        REPO_ROOT / "packaging" / "bootstrap-python.json",
        dest / "packaging" / "bootstrap-python.json",
    )
    os.symlink(REPO_ROOT / "scripts", dest / "scripts")
    for relative in ("README.md", "skills", "profiles", "presets"):
        os.symlink(REPO_ROOT / relative, dest / relative)
    (dest / "integrations" / "locks").mkdir(parents=True)
    os.symlink(REPO_ROOT / "integrations" / "tools", dest / "integrations" / "tools")
    (dest / ".claude-plugin").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / ".claude-plugin" / "marketplace.json",
        dest / ".claude-plugin" / "marketplace.json",
    )
    (dest / ".agents" / "plugins").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / ".agents" / "plugins" / "marketplace.json",
        dest / ".agents" / "plugins" / "marketplace.json",
    )
    return dest


def _seed_managed(home: Path) -> Path:
    """A managed checkout plus install state pointing at it.

    Makes the run an installed-CLI one (with ``--cli-path`` naming the
    running entry): the version provenance then marks the auto-update
    check eligible, which is the only way to reach its env branches. The
    checkout carries the full minimal tree because update phase 2 loads
    the ensured tree's payload modules.
    """
    managed = _minimal_tree(home / ".agents" / "src" / "charness")
    state_dir = home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "install-state.json").write_text(
        json.dumps({"repo_root": str(managed), "managed_checkout": True}),
        encoding="utf-8",
    )
    return managed


def _git(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.email=e5@example.com",
            "-c",
            "user.name=e5",
            "-c",
            "init.defaultBranch=main",
            *args,
        ],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


def _commit(repo: Path, name: str, content: str) -> None:
    (repo / name).write_text(content, encoding="utf-8")
    _git("add", "-A", cwd=repo)
    _git("commit", "-m", name, "--no-gpg-sign", cwd=repo)


def _seed_diverged(tmp_path: Path, name: str, kind: str) -> tuple[Path, Path]:
    """A managed checkout diverged from its local origin.

    ``kind`` selects the divergence shape the detail renderer branches on:
    ``unique`` (genuinely new local commit), ``many`` (eleven local commits,
    so the listing truncates), ``redundant`` (a local commit patch-identical
    to an upstream one, so nothing is unique). All git traffic stays local.
    """
    home, cwd = _isolated_dirs(tmp_path, name)
    origin = tmp_path / f"{name}-origin"
    seed = tmp_path / f"{name}-seed"
    _git("init", "--bare", "-b", "main", str(origin))
    _git("init", "-b", "main", str(seed))
    (seed / "packaging").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / "packaging" / "charness.json",
        seed / "packaging" / "charness.json",
    )
    _git("add", "-A", cwd=seed)
    _git("commit", "-m", "seed", "--no-gpg-sign", cwd=seed)
    if kind == "redundant":
        # The clone below needs two commits: the redundant case steps the
        # clone off the tip before re-applying it, and resetting a
        # single-commit checkout has no HEAD~1.
        _commit(seed, "base-note.txt", "base content\n")
    _git("remote", "add", "origin", str(origin), cwd=seed)
    _git("push", "-u", "origin", "main", cwd=seed)
    managed = home / ".agents" / "src" / "charness"
    _git("clone", str(origin), str(managed))
    state_dir = home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "install-state.json").write_text(
        json.dumps({"repo_root": str(managed), "managed_checkout": True}),
        encoding="utf-8",
    )
    if kind == "redundant":
        _commit(seed, "upstream-note.txt", "shared content\n")
        _git("push", cwd=seed)
        # Step off the tip first: cherry-picking the tip onto itself is an
        # empty change git refuses. Re-applying it one commit down leaves a
        # local-only SHA with an upstream-identical patch.
        _git("reset", "--hard", "HEAD~1", cwd=managed)
        # Pin the committer date: replaying a just-created commit within the
        # same second recreates a byte-identical SHA (same tree, parents,
        # message, and timestamps), which would fast-forward instead of
        # diverging. The patch stays identical, so `git cherry` still
        # reports it redundant while the SHA stays local-only.
        _git(
            "cherry-pick",
            "origin/main",
            cwd=managed,
            env={"GIT_COMMITTER_DATE": "2026-02-01T00:00:00+00:00"},
        )
    else:
        count = 11 if kind == "many" else 1
        for i in range(count):
            _commit(managed, f"local-{i}.txt", f"local content {i}\n")
        _commit(seed, "upstream-note.txt", "shared content\n")
        _git("push", cwd=seed)
    return home, cwd


# --- installed-CLI auto-update gates ----------------------------------------


def test_version_check_honors_no_update_check(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "check-noupdate")
    _seed_managed(home)
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 0, result.stderr


def test_version_check_without_opt_outs_reaches_tty_gate(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "check-tty")
    _seed_managed(home)
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        home=home,
        cwd=cwd,
        drop_vars=("CHARNESS_NO_UPDATE_CHECK",),
    )

    assert result.returncode == 0, result.stderr


def test_version_check_under_ci_skips_refresh(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "check-ci")
    _seed_managed(home)
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        home=home,
        cwd=cwd,
        drop_vars=("CHARNESS_NO_UPDATE_CHECK",),
        extra_env={"CI": "1"},
    )

    assert result.returncode == 0, result.stderr


def test_init_without_opt_outs_reaches_tty_gate(tmp_path: Path) -> None:
    """An installed-CLI init walks the auto-update tty gate.

    ``maybe_record_self_version_state`` returns early for ``update``, so
    only a non-update command (here ``init`` on the managed checkout)
    reaches the final tty branch once every opt-out is unset.
    """
    home, cwd = _isolated_dirs(tmp_path, "init-tty")
    _seed_managed(home)
    target = tmp_path / "init-tty-target"
    target.mkdir()
    result = _spawn(
        "init",
        "--home-root",
        str(home),
        "--cli-path",
        str(ENTRY),
        "--skip-cli-install",
        "--target-repo-root",
        str(target),
        home=home,
        cwd=cwd,
        drop_vars=("CHARNESS_NO_UPDATE_CHECK",),
    )

    assert result.returncode == 0, result.stderr
    assert "event: init" in result.stdout


def test_verbose_version_with_tagless_state_renders_no_notice(tmp_path: Path) -> None:
    """A state file without release tags walks the notice's missing-tag branch."""
    home, cwd = _isolated_dirs(tmp_path, "version-tagless")
    state_dir = home / ".local" / "state" / "charness"
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "version-state.json").write_text(
        json.dumps(
            {
                "state_version": 1,
                "latest_release": {
                    "status": "ok",
                    "update_available": True,
                    "current_version": "1.0",
                },
            }
        ),
        encoding="utf-8",
    )
    result = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        home=home,
        cwd=cwd,
    )

    assert result.returncode == 0, result.stderr
    assert CURRENT_VERSION in result.stdout


def test_check_with_older_fixture_reports_no_update(tmp_path: Path) -> None:
    """A fixture older than the packaged version walks the downgrade branch."""
    home, cwd = _isolated_dirs(tmp_path, "check-stale")
    checkout = tmp_path / "co"
    (checkout / "packaging").mkdir(parents=True)
    (checkout / "packaging" / "charness.json").write_text(
        json.dumps({"version": CURRENT_VERSION}), encoding="utf-8"
    )
    stale = tmp_path / "stale.json"
    stale.write_text(json.dumps({"corca-ai/charness": {"tag_name": "v0.0.1"}}), encoding="utf-8")
    result = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        home=home,
        cwd=cwd,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": str(stale)},
    )

    assert result.returncode == 0, result.stderr
    assert "update_available: false" in result.stdout


# --- re-exec guard rails ----------------------------------------------------

_WRAPPER = (
    "import os, sys; "
    f"os.environ[{_REEXEC_GUARD_ENV!r}] = str(os.getpid()); "
    f"os.execv(sys.executable, [sys.executable, {str(ENTRY)!r}] + sys.argv[1:])"
)


def _spawn_via_wrapper(*argv: str, home: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run the entry through a same-pid wrapper that arms the re-exec guard.

    ``os.execv`` keeps the process id, so the inner entry observes a
    re-exec child and takes the already-re-executed branches for real.
    """
    fixture = _write_release_fixture(home)
    userbase = _stage_userbase(home.parent)
    env = {
        **os.environ,
        "HOME": str(home),
        "PYTHONUSERBASE": str(userbase),
        BLOCK_ENV: _STANDALONE_BLOCK,
        "CHARNESS_STATE_HOME": str(home / ".local" / "state"),
        "CHARNESS_NO_UPDATE_CHECK": "1",
        "CHARNESS_RELEASE_PROBE_FIXTURES": fixture,
        "CI": "",
    }
    if _COVERAGE_SITE_DIR is not None:
        env["PYTHONPATH"] = os.pathsep.join(
            [_COVERAGE_SITE_DIR, os.environ.get("PYTHONPATH", "")]
        ).rstrip(os.pathsep)
    return subprocess.run(
        [sys.executable, "-c", _WRAPPER, *argv],
        env=env,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=_SPAWN_TIMEOUT_SECONDS,
    )


def _write_checkout_cli(repo: Path, content: bytes, mode: int) -> Path:
    cli = repo / "charness"
    cli.write_bytes(content)
    os.chmod(cli, mode)
    return cli


def _minimal_repo(tmp_path: Path, name: str) -> Path:
    repo = tmp_path / name
    (repo / "packaging").mkdir(parents=True)
    shutil.copyfile(
        REPO_ROOT / "packaging" / "charness.json",
        repo / "packaging" / "charness.json",
    )
    shutil.copyfile(
        REPO_ROOT / "packaging" / "bootstrap-python.json",
        repo / "packaging" / "bootstrap-python.json",
    )
    os.symlink(REPO_ROOT / "scripts", repo / "scripts")
    for relative in ("README.md", "skills", "profiles", "presets"):
        os.symlink(REPO_ROOT / relative, repo / relative)
    (repo / "integrations" / "locks").mkdir(parents=True)
    os.symlink(REPO_ROOT / "integrations" / "tools", repo / "integrations" / "tools")
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


def test_reexec_child_with_identical_cli_reports_reexecuted(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "reexec-same")
    repo = _minimal_repo(tmp_path, "reexec-same-source")
    _write_checkout_cli(repo, ENTRY.read_bytes(), 0o755)
    result = _spawn_via_wrapper(
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

    assert result.returncode == 0, result.stderr
    assert "DONE: update complete" in result.stderr


def test_reexec_child_with_differing_cli_skips_second_exec(tmp_path: Path) -> None:
    home, cwd = _isolated_dirs(tmp_path, "reexec-once")
    repo = _minimal_repo(tmp_path, "reexec-once-source")
    _write_checkout_cli(repo, b"#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n", 0o755)
    result = _spawn_via_wrapper(
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

    assert result.returncode == 0, result.stderr
    assert "after one re-exec" in result.stderr
    assert "DONE: update complete" in result.stderr


# --- tool-doctor resolver fallback ------------------------------------------


def test_tool_doctor_without_tree_reports_import_failure(tmp_path: Path) -> None:
    """Refusing the tool payload drives the ``_load_feature`` check path."""
    home, cwd = _isolated_dirs(tmp_path, "tool-doctor-hard")
    repo = _minimal_repo(tmp_path, "tool-doctor-hard-source")
    result = _spawn(
        "tool",
        "doctor",
        "--repo-root",
        str(repo),
        "--home-root",
        str(home),
        home=home,
        cwd=cwd,
        block=_STANDALONE_BLOCK + ",scripts.cli.tool_commands",
    )

    assert result.returncode != 0
    assert result.stderr.strip() != ""


# --- diverged managed checkouts ---------------------------------------------


def test_update_diverged_checkout_reports_unique_commits(tmp_path: Path) -> None:
    home, cwd = _seed_diverged(tmp_path, "div-unique", "unique")
    result = _spawn(
        "update",
        "--home-root",
        str(home),
        "--skip-cli-install",
        home=home,
        cwd=cwd,
    )

    assert result.returncode != 0
    assert "diverged" in result.stderr


def test_update_diverged_checkout_truncates_long_listings(tmp_path: Path) -> None:
    home, cwd = _seed_diverged(tmp_path, "div-many", "many")
    result = _spawn(
        "update",
        "--home-root",
        str(home),
        "--skip-cli-install",
        home=home,
        cwd=cwd,
    )

    assert result.returncode != 0
    assert "diverged" in result.stderr
    assert "more" in result.stderr


def test_update_diverged_checkout_reports_redundant_commits(tmp_path: Path) -> None:
    home, cwd = _seed_diverged(tmp_path, "div-redundant", "redundant")
    result = _spawn(
        "update",
        "--home-root",
        str(home),
        "--skip-cli-install",
        home=home,
        cwd=cwd,
    )

    assert result.returncode != 0
    assert "diverged" in result.stderr
    assert "patch-equivalent" in result.stderr
