"""Init command."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.cli.bootstrap import (  # noqa: E402
    emit_progress,
)
from scripts.cli.bootstrap_state import (  # noqa: E402
    build_version_provenance,
    write_version_state,
)
from scripts.cli.cmd_task import (  # noqa: E402
    project_runtime_response,
)
from scripts.cli.common import (  # noqa: E402
    emit_operational_response,
)
from scripts.cli.doctor_payload import (  # noqa: E402
    _mark_host_delivery_failure,
    build_doctor_payload,
    install_surface,
)
from scripts.cli.host_codex import (  # noqa: E402
    _record_post_delivery_readback,
    maybe_install_codex_host,
)
from scripts.cli.install_delivery import (  # noqa: E402
    _host_delivery_failed,
    write_host_state,
    write_install_state,
)


def finish_init(
    args: argparse.Namespace,
    *,
    home_root: Path,
    managed_checkout: bool,
    target_repo_root: Path,
    plugin_root: Path,
    codex_marketplace_path: Path,
    claude_wrapper_path: Path,
    cli_path: Path,
    checkout: dict[str, object],
    cli_reexec_state: dict[str, object] | None,
    script_path: Path,
    embedded_repo_root: Path | None,
) -> int:
    selected_wrapper_path = None if args.skip_claude_wrapper else claude_wrapper_path
    payload = install_surface(
        Path(checkout["repo_root"]),
        home_root=home_root,
        plugin_root=plugin_root,
        codex_marketplace_path=codex_marketplace_path,
        claude_wrapper_path=selected_wrapper_path,
        cli_path=None if args.skip_cli_install else cli_path,
        update=False,
    )
    payload["home_root"] = str(home_root)
    payload["repo_root"] = str(Path(checkout["repo_root"]))
    if cli_reexec_state is not None:
        payload["cli_reexec"] = cli_reexec_state
    if (
        embedded_repo_root is None
        and not args.skip_cli_install
        and cli_path.is_file()
        and cli_path.resolve() != script_path
        and cli_path.read_bytes() != script_path.read_bytes()
    ):
        # pragma: no cover - os.execv replaces the process image; untestable in-process.
        os.execv(str(cli_path), [str(cli_path)] + sys.argv[1:])  # pragma: no cover
    initial_doctor_payload = build_doctor_payload(
        home_root=home_root,
        repo_root=Path(checkout["repo_root"]),
        managed_checkout=managed_checkout,
        target_repo_root=target_repo_root,
        plugin_root=plugin_root,
        codex_marketplace_path=codex_marketplace_path,
        cli_path=cli_path,
        claude_wrapper_path=claude_wrapper_path,
    )
    codex_host_install = maybe_install_codex_host(
        home_root=home_root,
        codex_marketplace_path=codex_marketplace_path,
        doctor_payload=initial_doctor_payload,
        skip=False,
    )
    doctor_payload = initial_doctor_payload
    if codex_host_install.get("status") == "attempted":
        doctor_payload = build_doctor_payload(
            home_root=home_root,
            repo_root=Path(checkout["repo_root"]),
            managed_checkout=managed_checkout,
            target_repo_root=target_repo_root,
            plugin_root=plugin_root,
            codex_marketplace_path=codex_marketplace_path,
            cli_path=cli_path,
            claude_wrapper_path=claude_wrapper_path,
            include_latest_host_operation=False,
        )
        codex_host_install["post_install_cache_manifest_version"] = doctor_payload.get(
            "codex_cache_manifest_version"
        )
        codex_host_install["post_install_host_status"] = doctor_payload.get(
            "codex_host_guidance", {}
        ).get("status")
        _record_post_delivery_readback(codex_host_install, doctor_payload, phase="init")
        if (
            codex_host_install.get("delivery_verified") is not True
            or doctor_payload.get("codex_cache_manifest_status") != "valid"
            or doctor_payload.get("codex_host_guidance", {}).get("status") != "installed"
            or doctor_payload.get("codex_source_cache_drift")
        ):
            codex_host_install["status"] = "failed"
            codex_host_install["reason"] = "install-incomplete"
            codex_host_install["error"] = (
                "Codex app-server plugin/install returned success, but charness still does not appear as an installed current local plugin."
            )
        else:
            codex_host_install["status"] = "installed"
            payload.setdefault("completed_actions", []).append("codex_host_installed")
    payload["codex_host_install"] = codex_host_install
    payload["codex_host_guidance"] = doctor_payload["codex_host_guidance"]
    payload["claude_host_guidance"] = doctor_payload["claude_host_guidance"]
    payload["grok_host_guidance"] = doctor_payload.get("grok_host_guidance") or {}
    payload["repo_onboarding"] = doctor_payload["repo_onboarding"]
    payload["host_next_steps"] = {
        **payload.get("host_next_steps", {}),
        **doctor_payload["host_next_steps"],
    }
    payload["next_action"] = doctor_payload["next_action"]
    payload["checkout_version"] = doctor_payload["checkout_version"]
    payload["codex_source_version"] = doctor_payload["codex_source_version"]
    payload["codex_cache_manifest_version"] = doctor_payload["codex_cache_manifest_version"]
    payload["codex_cache_manifest_status"] = doctor_payload.get("codex_cache_manifest_status")
    payload["codex_source_cache_drift"] = doctor_payload["codex_source_cache_drift"]
    payload["target_repo_root"] = str(target_repo_root)
    if _host_delivery_failed(codex_host_install):
        _mark_host_delivery_failure(doctor_payload, codex_host_install, command="init")
        payload["codex_host_guidance"] = doctor_payload["codex_host_guidance"]
        payload["host_next_steps"] = doctor_payload["host_next_steps"]
        payload["next_action"] = doctor_payload["next_action"]
    if managed_checkout:
        write_install_state(home_root, repo_root=Path(checkout["repo_root"]), managed_checkout=True)
    write_version_state(
        home_root,
        provenance=build_version_provenance(
            home_root=home_root,
            repo_root=Path(checkout["repo_root"]),
            managed_checkout=managed_checkout,
            cli_path=cli_path,
        ),
    )
    init_failed = _host_delivery_failed(codex_host_install)
    write_host_state(
        home_root,
        key="last_init",
        payload=doctor_payload,
        delivery=codex_host_install,
        operation_status="failed" if init_failed else "success",
        operation_scope="self",
    )
    payload["checkout"] = checkout
    emit_operational_response(
        args,
        payload,
        event="init",
        projector=lambda data: project_runtime_response(data, event="init"),
    )
    if init_failed:
        emit_progress(
            "FAILED: init incomplete; inspect the typed YAML result and retry with `charness init --detail`"
        )
    return 1 if init_failed else 0
