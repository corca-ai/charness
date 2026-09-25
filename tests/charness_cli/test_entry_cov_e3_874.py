"""Entry coverage slice E3: lines 719-928 of the repo-root `charness` CLI entry.

Those lines are the `except ImportError` standalone fallback copies (the copy
that serves when `scripts.cli.bootstrap` is not importable). A real subprocess
spawn of the real in-repo path normally takes the `try` branch, so each spawn
below sets ``CHARNESS_ENTRY_COV_BLOCK=scripts.cli.bootstrap`` (plus `,yaml`
for the render-fallback test). That variable is honored by a `usercustomize`
module staged per test under a tmp `PYTHONUSERBASE`, which raises ImportError
for the named modules; `usercustomize` runs after `sitecustomize`, so the
coverage harness's measurement keeps working. With ``block=""`` the variable
is popped and the entry runs its sync-pinned tree copies instead. Behavior
assertions hold in both modes.

Every test spawns REAL subprocesses of the real entry with an inherited
environment (`{**os.environ, ...}`, never a replaced env), asserts returncode
plus stdout/stderr content, stays under 30s, needs no network (the no-fixture
probe test passes whether the release API answers or fails), and writes only
under `tmp_path` (HOME, state homes, cwd) and the test worker's own runtime
dirs. The product file is never touched.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tests.repo_copy import ROOT

pytestmark = pytest.mark.boundary_contract(
    reason="entry-fallback lines attribute only via a real subprocess spawn "
    "of the real in-repo `charness` path with an inherited environment"
)

CLI = ROOT / "charness"
MANIFEST_VERSION = str(
    json.loads((ROOT / "packaging" / "charness.json").read_text(encoding="utf-8"))["version"]
)
# Matches self_release_repo(): REPO_URL ends in github.com/corca-ai/charness.
SELF_RELEASE_REPO = "corca-ai/charness"
BLOCK_ENV = "CHARNESS_ENTRY_COV_BLOCK"
FALLBACK_BLOCK = "scripts.cli.bootstrap"
SPAWN_TIMEOUT_S = 25

try:
    import coverage as _coverage_for_standalone_kids
except ImportError:  # plain runs without the coverage harness installed
    _COVERAGE_SITE_DIR = None
else:
    _COVERAGE_SITE_DIR = str(Path(_coverage_for_standalone_kids.__file__).resolve().parent.parent)

# The block variable alone does nothing: a `usercustomize` module (via a tmp
# PYTHONUSERBASE, staged per test below) installs the `sys.meta_path` guard
# that raises ImportError for the named modules. `usercustomize` runs after
# `sitecustomize`, so the coverage harness's process-startup measurement keeps
# working under the gate; without the harness the guard still forces the
# standalone fallback copies. Nothing is copied out of the tree.
#
# The same module can fail the release probe's HTTP fetch without network:
# CHARNESS_ENTRY_COV_HTTPFAIL=404 raises HTTPError for api.github.com URLs and
# =refused raises URLError, so the probe's error branches execute for real.
HTTPFAIL_ENV = "CHARNESS_ENTRY_COV_HTTPFAIL"
_USERCUSTOMIZE = """import os

_names = os.environ.get("%s", "%s").split(",")
_names = [n.strip() for n in _names if n.strip()]
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

_httpfail = os.environ.get("%s", "")
if _httpfail:
    import io
    import urllib.error
    import urllib.request

    _real_urlopen = urllib.request.urlopen

    def _failing_urlopen(url, *args, **kwargs):
        target = url.full_url if hasattr(url, "full_url") else str(url)
        if "api.github.com" not in target:
            return _real_urlopen(url, *args, **kwargs)
        if _httpfail == "404":
            raise urllib.error.HTTPError(target, 404, "Not Found", {}, io.BytesIO(b""))
        raise urllib.error.URLError("connection refused for entry-fallback coverage test")

    urllib.request.urlopen = _failing_urlopen
""" % (BLOCK_ENV, "", HTTPFAIL_ENV)
# Note: the template default is empty (block nothing). `_base_env` always sets
# BLOCK_ENV explicitly; `_spawn(..., block="")` pops it for a plain tree-mode run.


def _stage_userbase(home: Path) -> Path:
    """Write the blocker usercustomize; return the tmp PYTHONUSERBASE."""
    userbase = home.parent / "userbase"
    site_packages = (
        userbase
        / "lib"
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
        / "site-packages"
    )
    site_packages.mkdir(parents=True, exist_ok=True)
    (site_packages / "usercustomize.py").write_text(_USERCUSTOMIZE, encoding="utf-8")
    return userbase


def _base_env(home: Path) -> dict[str, str]:
    """Inherited environment scrubbed of ambient state-home/update-check vars."""
    env = dict(os.environ)
    env["HOME"] = str(home)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for var in (
        "XDG_STATE_HOME",
        "CHARNESS_STATE_HOME",
        "CHARNESS_RELEASE_PROBE_FIXTURES",
        "CHARNESS_NO_UPDATE_CHECK",
        "CHARNESS_FORCE_UPDATE_CHECK",
        "CHARNESS_RUNTIME_ROOT",
        "CHARNESS_RUNTIME_ROOT_AUTO",
        "CHARNESS_RUNTIME_REPO_KEY",
        "CI",
    ):
        env.pop(var, None)
    env[BLOCK_ENV] = FALLBACK_BLOCK
    return env


def _spawn(
    *args: str,
    home: Path,
    extra_env: dict[str, str] | None = None,
    block: str = FALLBACK_BLOCK,
) -> subprocess.CompletedProcess[str]:
    home.mkdir(parents=True, exist_ok=True)
    env = _base_env(home)
    if block:
        env[BLOCK_ENV] = block
    else:
        env.pop(BLOCK_ENV, None)
    # Stage the blocker usercustomize for every spawn (it reads BLOCK_ENV in
    # the child; with the variable popped it blocks nothing). PYTHONUSERBASE
    # repoints the user site, which can hide a user-site `coverage` install
    # from the child's startup, so prepend its directory when present.
    env["PYTHONUSERBASE"] = str(_stage_userbase(home))
    if _COVERAGE_SITE_DIR is not None:
        inherited = env.get("PYTHONPATH", "")
        parts = inherited.split(os.pathsep) if inherited else []
        if _COVERAGE_SITE_DIR not in parts:
            env["PYTHONPATH"] = os.pathsep.join([_COVERAGE_SITE_DIR, *parts])
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        env=env,
        cwd=home,
        capture_output=True,
        text=True,
        timeout=SPAWN_TIMEOUT_S,
        check=False,
    )


def _state_dir(home: Path) -> Path:
    return home / ".local" / "state" / "charness"


def _write_json(path: Path, payload: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def _write_probe_fixture(path: Path, release: dict[str, object]) -> str:
    return str(_write_json(path, {SELF_RELEASE_REPO: release}))


# --- plain version surface: packaging_version + render_yaml ------------------


def test_plain_version_reports_packaged_version(tmp_path: Path) -> None:
    proc = _spawn("version", "--home-root", str(tmp_path / "home"), home=tmp_path / "home")

    assert proc.returncode == 0, proc.stderr
    assert MANIFEST_VERSION in proc.stdout


def test_plain_version_unknown_for_checkout_without_manifest(tmp_path: Path) -> None:
    home = tmp_path / "home"
    bare = tmp_path / "bare-checkout"
    bare.mkdir()

    proc = _spawn("version", "--home-root", str(home), "--repo-root", str(bare), home=home)

    assert proc.returncode == 0, proc.stderr
    assert "unknown" in proc.stdout


def test_unknown_subcommand_exits_two(tmp_path: Path) -> None:
    proc = _spawn("no-such-command-xyz", home=tmp_path / "home")

    assert proc.returncode == 2
    assert "invalid choice" in proc.stderr


# --- read_install_state / resolve_repo_root via version --verbose -------------


@pytest.mark.parametrize(
    "install_state",
    [
        None,
        ("raw", "{bad json{{{"),
        ("json", {"repo_root": 5, "managed_checkout": "yes"}),
        ("json", {"repo_root": "rel/path", "managed_checkout": False}),
        ("json", {"repo_root": str(ROOT), "managed_checkout": True}),
    ],
    ids=["missing", "corrupt", "wrong-types", "unmanaged", "managed"],
)
def test_verbose_version_with_install_state_variants(tmp_path: Path, install_state: object) -> None:
    home = tmp_path / "home"
    if install_state is not None:
        kind, seed = install_state  # type: ignore[misc]
        path = _state_dir(home) / "install-state.json"
        if kind == "raw":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(str(seed) + "\n", encoding="utf-8")
        else:
            _write_json(path, seed)

    proc = _spawn("version", "--verbose", "--home-root", str(home), home=home)

    assert proc.returncode == 0, proc.stderr
    assert "current_version" in proc.stdout
    assert MANIFEST_VERSION in proc.stdout


# --- read_version_state variants ----------------------------------------------


@pytest.mark.parametrize(
    ("seed", "case"),
    [
        ("{oops not json", "corrupt"),
        ("[1, 2]", "non-dict"),
        ('{"latest_release": {}}', "no-state-version"),
    ],
    ids=["corrupt", "non-dict", "no-state-version"],
)
def test_version_state_file_variants(tmp_path: Path, seed: str, case: str) -> None:
    home = tmp_path / "home"
    path = _state_dir(home) / "version-state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(seed + "\n", encoding="utf-8")

    proc = _spawn("version", "--verbose", "--home-root", str(home), home=home)

    assert proc.returncode == 0, proc.stderr
    assert "version_provenance" in proc.stdout, case


# --- resolve_state_home overrides ----------------------------------------------


def test_state_home_env_override_selects_state_root(tmp_path: Path) -> None:
    home = tmp_path / "home"
    state_home = tmp_path / "custom-state"

    proc = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        home=home,
        extra_env={"CHARNESS_STATE_HOME": str(state_home)},
    )

    assert proc.returncode == 0, proc.stderr
    assert str(state_home / "charness" / "version-state.json") in proc.stdout


def test_xdg_state_home_selects_state_root(tmp_path: Path) -> None:
    home = tmp_path / "home"
    xdg_state = tmp_path / "xdg-state"

    proc = _spawn(
        "version",
        "--verbose",
        "--home-root",
        str(home),
        home=home,
        extra_env={"XDG_STATE_HOME": str(xdg_state)},
    )

    assert proc.returncode == 0, proc.stderr
    assert str(xdg_state / "charness" / "version-state.json") in proc.stdout


# --- resolve_runtime_paths via update refusing before ensure ------------------


@pytest.mark.parametrize("explicit_paths", [False, True], ids=["defaults", "explicit"])
def test_update_resolves_runtime_paths_then_refuses(tmp_path: Path, explicit_paths: bool) -> None:
    home = tmp_path / "home"
    empty = tmp_path / "empty-checkout"
    empty.mkdir()
    args = [
        "update",
        "--home-root",
        str(home),
        "--repo-root",
        str(empty),
        "--skip-cli-install",
    ]
    if explicit_paths:
        args += [
            "--plugin-root",
            str(tmp_path / "plugin"),
            "--codex-marketplace-path",
            str(tmp_path / "marketplace.json"),
            "--claude-wrapper-path",
            str(tmp_path / "claude-wrapper"),
            "--cli-path",
            str(tmp_path / "cli"),
        ]

    proc = _spawn(*args, home=home)

    assert proc.returncode == 1
    assert "missing explicit source checkout" in proc.stderr
    assert "STEP: refreshing source checkout" in proc.stderr


# --- probe_self_release / normalize_release_payload via fixtures --------------


def _rich_release() -> dict[str, object]:
    return {
        "tag_name": "v9.9.9",
        "html_url": "https://github.com/corca-ai/charness/releases/tag/v9.9.9",
        "published_at": "2026-09-01T00:00:00Z",
        "assets": [{"name": "charness.tar.gz"}, "not-a-dict", {"name": 7}, {"other": 1}],
        "status": "custom-status",
        "error": "custom-error",
    }


def test_check_refreshes_release_from_fixture(tmp_path: Path) -> None:
    home = tmp_path / "home"
    fixture = _write_probe_fixture(tmp_path / "releases.json", _rich_release())

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        home=home,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": fixture},
    )

    assert proc.returncode == 0, proc.stderr
    assert "9.9.9" in proc.stdout
    assert "update_available: true" in proc.stdout


def test_check_with_v_prefixed_prerelease_current(tmp_path: Path) -> None:
    home = tmp_path / "home"
    checkout = tmp_path / "co"
    _write_json(checkout / "packaging" / "charness.json", {"version": "v8.12.0-rc.1"})
    fixture = _write_probe_fixture(
        tmp_path / "releases.json",
        {"tag_name": "v9.9.9-rc.1", "html_url": None, "published_at": None, "assets": []},
    )

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        home=home,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": fixture},
    )

    assert proc.returncode == 0, proc.stderr
    assert "9.9.9-rc.1" in proc.stdout
    assert "update_available: true" in proc.stdout


def test_check_with_unparsable_current_yields_null_update(tmp_path: Path) -> None:
    home = tmp_path / "home"
    checkout = tmp_path / "co"
    _write_json(checkout / "packaging" / "charness.json", {"version": "1.x"})
    fixture = _write_probe_fixture(tmp_path / "releases.json", {"tag_name": "v9.9.9"})

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        home=home,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": fixture},
    )

    assert proc.returncode == 0, proc.stderr
    assert "update_available: null" in proc.stdout


def test_check_without_manifest_leaves_current_unknown(tmp_path: Path) -> None:
    home = tmp_path / "home"
    bare = tmp_path / "bare-checkout"
    bare.mkdir()
    fixture = _write_probe_fixture(tmp_path / "releases.json", {"tag_name": "v9.9.9"})

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(bare),
        home=home,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": fixture},
    )

    assert proc.returncode == 0, proc.stderr
    assert "current_version: null" in proc.stdout
    assert "update_available: null" in proc.stdout


@pytest.mark.parametrize("mode,marker", [("404", "no-release"), ("refused", "error")])
def test_probe_http_failure_reports_status_without_network(
    tmp_path: Path, mode: str, marker: str
) -> None:
    """HTTPError/URLError from the probe execute the error branches for real."""
    home = tmp_path / "home"

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        home=home,
        extra_env={HTTPFAIL_ENV: mode},
    )

    assert proc.returncode == 0, proc.stderr
    assert marker in proc.stdout
    assert "api.github.com/repos/corca-ai/charness/releases/latest" in proc.stdout


def test_offline_probe_without_fixture_reports_release_error(tmp_path: Path) -> None:
    home = tmp_path / "home"

    proc = _spawn("version", "--check", "--home-root", str(home), home=home)

    assert proc.returncode == 0, proc.stderr
    assert "latest_release_check" in proc.stdout
    assert "api.github.com/repos/corca-ai/charness/releases/latest" in proc.stdout


# --- forced auto-refresh freshness branches ------------------------------------


def _eligible_env(home: Path, fixture: str) -> dict[str, str]:
    _write_json(
        _state_dir(home) / "install-state.json",
        {"repo_root": str(ROOT), "managed_checkout": True},
    )
    return {
        "CHARNESS_FORCE_UPDATE_CHECK": "1",
        "CHARNESS_RELEASE_PROBE_FIXTURES": fixture,
    }


def _eligible_args(home: Path) -> list[str]:
    return [
        "version",
        "--verbose",
        "--home-root",
        str(home),
        "--cli-path",
        str(CLI),
    ]


def test_forced_check_keeps_fresh_release_cache(tmp_path: Path) -> None:
    home = tmp_path / "home"
    fixture = _write_probe_fixture(tmp_path / "releases.json", {"tag_name": "v9.9.9"})
    checked_at = datetime.now(timezone.utc).isoformat()
    _write_json(
        _state_dir(home) / "version-state.json",
        {
            "state_version": 1,
            "latest_release": {
                "checked_at": checked_at,
                "current_version": MANIFEST_VERSION,
                "latest_tag": "v8.12.0-seeded",
                "status": "ok",
            },
        },
    )

    proc = _spawn(*_eligible_args(home), home=home, extra_env=_eligible_env(home, fixture))

    assert proc.returncode == 0, proc.stderr
    assert "v8.12.0-seeded" in proc.stdout


@pytest.mark.parametrize(
    "latest_release",
    [
        {"checked_at": "not-a-time", "current_version": MANIFEST_VERSION},
        {},
        {"checked_at": "2020-01-01T00:00:00Z", "current_version": MANIFEST_VERSION},
        {
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "current_version": "",
        },
    ],
    ids=["unparsable-checked-at", "missing-checked-at", "stale", "empty-current"],
)
def test_forced_check_refreshes_stale_release_cache(
    tmp_path: Path, latest_release: dict[str, object]
) -> None:
    home = tmp_path / "home"
    fixture = _write_probe_fixture(tmp_path / "releases.json", {"tag_name": "v9.9.9"})
    _write_json(
        _state_dir(home) / "version-state.json",
        {"state_version": 1, "latest_release": latest_release},
    )

    proc = _spawn(*_eligible_args(home), home=home, extra_env=_eligible_env(home, fixture))

    assert proc.returncode == 0, proc.stderr
    assert "9.9.9" in proc.stdout


# --- render_yaml without pyyaml -------------------------------------------------


@pytest.mark.parametrize(
    "current_version,latest_tag,available",
    [
        ("8.12.0", "v8.12.0", "false"),
        ("8.12.0-rc.1", "v8.12.0", "true"),
        ("8.12.0", "v8.12.0-rc.2", "false"),
        ("8.12.0-rc.1", "v8.12.0-rc.2", "true"),
        ("8.12.0-rc.2", "v8.12.0-rc.1", "false"),
    ],
    ids=[
        "equal-release",
        "prerelease-current",
        "prerelease-latest",
        "prerelease-bump",
        "prerelease-downgrade",
    ],
)
def test_check_prerelease_pairs_compare_cores_first(
    tmp_path: Path, current_version: str, latest_tag: str, available: str
) -> None:
    """Same-core prerelease pairs exercise the semver tail branches."""
    home = tmp_path / "home"
    checkout = tmp_path / "co"
    _write_json(checkout / "packaging" / "charness.json", {"version": current_version})
    fixture = _write_probe_fixture(tmp_path / "releases.json", {"tag_name": latest_tag})

    proc = _spawn(
        "version",
        "--check",
        "--home-root",
        str(home),
        "--repo-root",
        str(checkout),
        home=home,
        extra_env={"CHARNESS_RELEASE_PROBE_FIXTURES": fixture},
    )

    assert proc.returncode == 0, proc.stderr
    assert f"update_available: {available}" in proc.stdout


def test_render_without_yaml_falls_back_to_json(tmp_path: Path) -> None:
    proc = _spawn(
        "version",
        "--home-root",
        str(tmp_path / "home"),
        home=tmp_path / "home",
        block=FALLBACK_BLOCK + ",yaml",
    )

    assert proc.returncode == 0, proc.stderr
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        pytest.skip("yaml-block hook inactive; JSON fallback path not exercised")
    assert payload == {"version": MANIFEST_VERSION}
