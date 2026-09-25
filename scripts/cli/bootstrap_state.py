"""Standalone-copy version-state, tool-root, and runtime-bridge closure."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli import bootstrap as _bootstrap  # noqa: E402
from scripts.cli.bootstrap import (  # noqa: E402
    PACKAGE_ID,
    REPO_URL,
    CharnessError,
    default_cli_path,
    default_state_root,
    ensure_checkout,
    has_source_manifest,
    is_git_checkout,
    managed_checkout_root,
    packaging_version,
    resolve_repo_root,
    run,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    _parse_prerelease_identifier as _parse_prerelease_identifier,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    build_self_update_notice as build_self_update_notice,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    compare_semver_like as compare_semver_like,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    compute_update_available as compute_update_available,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    extract_version as extract_version,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    fixture_release as fixture_release,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    latest_release_cache_is_fresh as latest_release_cache_is_fresh,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    normalize_release_payload as normalize_release_payload,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    normalize_version_token as normalize_version_token,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    parse_iso_timestamp as parse_iso_timestamp,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    parse_semver_like as parse_semver_like,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    probe_self_release as probe_self_release,
)
from scripts.cli.bootstrap_probe import (  # noqa: E402
    self_release_repo as self_release_repo,
)


def _runtime_bootstrap_module(repo_root: Path):
    """Load the single runtime-environment owner without writing startup bytecode."""
    candidates = [repo_root.resolve()]
    if _bootstrap.EMBEDDED_REPO_ROOT is not None:
        candidates.append(_bootstrap.EMBEDDED_REPO_ROOT)
    candidates.append(managed_checkout_root(default_home_root()))
    source_root = next(
        (
            candidate
            for candidate in candidates
            if (candidate / "scripts" / "runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if source_root is None:
        return None
    source_text = str(source_root)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        from scripts import runtime_bootstrap
    finally:
        sys.dont_write_bytecode = previous
    return runtime_bootstrap


def _configure_runtime_for_repo(repo_root: Path, *, required: bool = True) -> bool:
    runtime_bootstrap = _runtime_bootstrap_module(repo_root)
    if runtime_bootstrap is None:
        if required:
            raise CharnessError(
                "Charness runtime owner is unavailable; initialize the managed checkout first"
            )
        return False
    runtime_bootstrap.configure_runtime_environment(repo_root)
    return True


def _runtime_repo_for_args(args: argparse.Namespace) -> Path:
    explicit = getattr(args, "repo_root", None)
    if explicit is not None:
        return Path(explicit).resolve()
    if _bootstrap.EMBEDDED_REPO_ROOT is not None:
        return _bootstrap.EMBEDDED_REPO_ROOT
    return Path.cwd().resolve()


def render_yaml(payload: object) -> str:
    """Render one portable YAML document for the public CLI boundary."""
    normalized = json.loads(json.dumps(payload, ensure_ascii=False, allow_nan=False))
    try:
        import yaml
    except ImportError:
        # JSON is valid YAML. Keep the copied standalone CLI usable before the
        # managed bootstrap runtime has provisioned PyYAML.
        return json.dumps(normalized, ensure_ascii=False, separators=(",", ":")) + "\n"
    return yaml.safe_dump(normalized, allow_unicode=True, sort_keys=False)


def emit_yaml(payload: object) -> None:
    print(render_yaml(payload), end="")


def default_home_root() -> Path:
    return Path.home().resolve()


def default_version_state_path(home_root: Path) -> Path:
    return default_state_root(home_root) / "version-state.json"


def git_head(path: Path) -> str | None:
    if not is_git_checkout(path):
        return None
    result = run(["git", "rev-parse", "--short", "HEAD"], cwd=path)
    if result.returncode != 0:
        return None
    head = result.stdout.strip()
    return head or None


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def bool_env(name: str) -> bool:
    # The FIFTH copy of the table owned by `scripts/core/env_bypass.py`, and the one
    # copy that cannot import its owner. This file is the installed standalone
    # CLI: `source_root` above returns None when no charness source tree is
    # present, so `scripts` is not importable here in the case this entry point
    # exists to serve. The duplication is deliberate and load-bearing.
    #
    # It is still the same contract, so it keeps the same allowlist: bare
    # truthiness would make `CHARNESS_NO_UPDATE_CHECK=0` -- the spelling an
    # operator uses to keep the check ON -- switch it off. If the table in
    # `scripts/core/env_bypass.py` ever changes, change it here too.
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def read_version_state(home_root: Path) -> dict[str, object]:
    path = default_version_state_path(home_root)
    if not path.is_file():
        return {"state_version": 1}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"state_version": 1}
    if not isinstance(payload, dict):
        return {"state_version": 1}
    payload.setdefault("state_version", 1)
    return payload


def write_version_state(
    home_root: Path,
    *,
    provenance: dict[str, object] | None = None,
    latest_release: dict[str, object] | None = None,
) -> dict[str, object]:
    path = default_version_state_path(home_root)
    state = read_version_state(home_root)
    if provenance is not None:
        state["version_provenance"] = provenance
    if latest_release is not None:
        state["latest_release"] = latest_release
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except OSError:
        # Version probes must stay usable even when host-local state is read-only.
        return state
    return state


def build_version_provenance(
    *,
    home_root: Path,
    repo_root: Path,
    managed_checkout: bool,
    cli_path: Path,
) -> dict[str, object]:
    runtime_path = _bootstrap.SCRIPT_PATH.resolve()
    configured_cli_path = cli_path.resolve()
    checkout_present = has_source_manifest(repo_root)
    invocation_kind = "custom-cli"
    install_method: str | None = None

    if runtime_path == configured_cli_path:
        invocation_kind = "installed-cli"
        install_method = "managed-local-cli" if managed_checkout else "custom-cli"
    elif checkout_present and runtime_path == (repo_root / "charness").resolve():
        invocation_kind = "source-checkout"
        install_method = "checkout"

    eligible = bool(
        invocation_kind == "installed-cli"
        and managed_checkout
        and checkout_present
        and packaging_version(repo_root)
    )

    return {
        "checked_at": now_iso(),
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "checkout_present": checkout_present,
        "current_version": packaging_version(repo_root) if checkout_present else None,
        "current_git_head": git_head(repo_root) if checkout_present else None,
        "runtime_path": str(runtime_path),
        "configured_cli_path": str(configured_cli_path),
        "invocation_kind": invocation_kind,
        "install_method": install_method,
        "eligible_for_auto_update_check": eligible,
    }


def refresh_self_release_state(
    *,
    home_root: Path,
    current_version: str | None,
) -> dict[str, object]:
    latest_release = probe_self_release()
    latest_release["checked_at"] = now_iso()
    latest_release["current_version"] = current_version
    latest_release["update_available"] = compute_update_available(
        current_version, latest_release.get("latest_version")
    )
    return write_version_state(home_root, latest_release=latest_release)


def should_auto_refresh_self_release(
    args: argparse.Namespace, provenance: dict[str, object]
) -> bool:
    if provenance.get("eligible_for_auto_update_check") is not True:
        return False
    if bool_env("CHARNESS_NO_UPDATE_CHECK"):
        return False
    if bool_env("CI"):
        return False
    if getattr(args, "command", None) == "version" and getattr(args, "check", False):
        return False
    if bool_env("CHARNESS_FORCE_UPDATE_CHECK"):
        return True
    return sys.stdout.isatty() and sys.stderr.isatty()


def maybe_record_self_version_state(args: argparse.Namespace) -> None:
    if getattr(args, "command", None) == "task":
        return
    home_root = getattr(args, "home_root", default_home_root()).resolve()
    repo_root, managed_checkout = resolve_repo_root(home_root, getattr(args, "repo_root", None))
    cli_arg = getattr(args, "cli_path", None)
    cli_path = cli_arg.resolve() if isinstance(cli_arg, Path) else default_cli_path(home_root)
    provenance = build_version_provenance(
        home_root=home_root,
        repo_root=repo_root,
        managed_checkout=managed_checkout,
        cli_path=cli_path,
    )
    state = write_version_state(home_root, provenance=provenance)
    latest_release = state.get("latest_release")
    current_version = provenance.get("current_version")
    if getattr(args, "command", None) == "update":
        return
    if should_auto_refresh_self_release(args, provenance):
        if not isinstance(latest_release, dict) or not latest_release_cache_is_fresh(
            latest_release, current_version
        ):
            state = refresh_self_release_state(
                home_root=home_root,
                current_version=current_version if isinstance(current_version, str) else None,
            )
            latest_release = state.get("latest_release")
        notice = build_self_update_notice(latest_release)
        if notice:
            print(notice, file=sys.stderr)


def build_version_payload(
    *,
    home_root: Path,
    repo_root: Path,
    managed_checkout: bool,
    cli_path: Path,
    check: bool,
) -> dict[str, object]:
    provenance = build_version_provenance(
        home_root=home_root,
        repo_root=repo_root,
        managed_checkout=managed_checkout,
        cli_path=cli_path,
    )
    state = write_version_state(home_root, provenance=provenance)
    if check:
        state = refresh_self_release_state(
            home_root=home_root,
            current_version=provenance.get("current_version")
            if isinstance(provenance.get("current_version"), str)
            else None,
        )
    latest_release = state.get("latest_release")
    payload = {
        "package_id": PACKAGE_ID,
        "current_version": provenance.get("current_version"),
        "current_git_head": provenance.get("current_git_head"),
        "repo_root": str(repo_root),
        "managed_checkout": managed_checkout,
        "version_state_path": str(default_version_state_path(home_root)),
        "version_provenance": provenance,
        "latest_release_check": latest_release,
        "update_notice": build_self_update_notice(latest_release),
    }
    return payload


def resolve_tool_repo_root(args: argparse.Namespace) -> tuple[Path, bool]:
    home_root = args.home_root.resolve()
    repo_root, managed_checkout = resolve_repo_root(home_root, args.repo_root)
    ensure_checkout(
        repo_root,
        managed=managed_checkout,
        repo_url=getattr(args, "repo_url", REPO_URL),
        allow_clone=False,
        allow_pull=False,
    )
    return repo_root, managed_checkout


def _source_checkout_under_work(args: argparse.Namespace) -> Path | None:
    """The parent repo itself, when it is a charness source checkout.

    `charness task run --repo-root .` inside this repository must run THIS
    checkout's task runner, not the managed checkout under `~/.agents/src`:
    on 2026-09-02 a runner fix (the worktree `.agents/` sandbox grant) sat
    unused for a session because the installed CLI loaded the stale managed
    copy. An explicit `--charness-checkout` still wins; a parent that is not a
    source checkout falls through to the managed resolution.
    """
    parent = getattr(args, "repo_root", None)
    if parent is None:
        return None
    candidate = Path(parent).resolve()
    if (candidate / "packaging" / f"{PACKAGE_ID}.json").is_file() and (
        candidate / "scripts" / "task_run" / "task_run.py"
    ).is_file():
        return candidate
    return None


def _resolve_worktree_lib_root(args: argparse.Namespace) -> Path:
    if _bootstrap.EMBEDDED_REPO_ROOT is not None:
        return _bootstrap.EMBEDDED_REPO_ROOT
    explicit = getattr(args, "charness_checkout", None)
    if explicit is None:
        own = _source_checkout_under_work(args)
        if own is not None:
            return own
    home_root = getattr(args, "home_root", default_home_root()).resolve()
    repo_root, _managed = resolve_repo_root(home_root, explicit)
    if not (repo_root / "packaging" / f"{PACKAGE_ID}.json").is_file():
        raise CharnessError(
            "`charness worktree` could not locate a charness source checkout. "
            f"Expected `{repo_root}` to contain `packaging/{PACKAGE_ID}.json`. "
            "Run `charness init` to install the managed checkout, or pass `--charness-checkout <path>`."
        )
    return repo_root
