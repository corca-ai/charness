#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.core.subprocess_guard"
).run_process


_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter
_adapter_version_verdict = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.adapter_version_verdict"
)
_fresh_checkout_module = SKILL_RUNTIME.load_local_skill_module(
    __file__, "check_fresh_checkout_probes"
)
build_fresh_checkout_payload = _fresh_checkout_module.build_payload
_yaml_output_module = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.yaml_output"
)
emit_yaml = _yaml_output_module.emit_yaml


def _read_json(path: Path) -> dict[str, object] | None:
    """`None` when the file cannot be read or is not valid JSON. A half-written
    `plugin.json` is exactly what a failed sync leaves, and raising here killed the drift
    check that exists to notice it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _version_at(path: Path) -> str | None:
    if not path.is_file():
        return None
    data = _read_json(path)
    if data is None:
        return None
    version = data.get("version")
    return version if isinstance(version, str) else None


def _marketplace_versions(repo_root: Path, package_id: str) -> dict[str, str | None]:
    claude_marketplace = repo_root / ".claude-plugin" / "marketplace.json"
    codex_marketplace = repo_root / ".agents" / "plugins" / "marketplace.json"
    claude_version: str | None = None
    codex_catalog_name: str | None = None
    if claude_marketplace.is_file():
        claude_data = _read_json(claude_marketplace) or {}
        metadata = claude_data.get("metadata", {})
        if isinstance(metadata, dict):
            version = metadata.get("version")
            if isinstance(version, str):
                claude_version = version
    if codex_marketplace.is_file():
        codex_data = _read_json(codex_marketplace) or {}
        plugins = codex_data.get("plugins", [])
        if isinstance(plugins, list):
            for plugin in plugins:
                if isinstance(plugin, dict) and plugin.get("name") == package_id:
                    source = plugin.get("source", {})
                    if isinstance(source, dict):
                        path = source.get("path")
                        if isinstance(path, str):
                            codex_catalog_name = path
                    break
    return {
        "claude_marketplace_version": claude_version,
        "codex_marketplace_source_path": codex_catalog_name,
    }


def _git_status(repo_root: Path) -> list[str]:
    result = run_process(
        ["git", "status", "--short"],
        cwd=repo_root,
        timeout_seconds=None,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def _declared_list(value: object) -> list[str]:
    """A declared surface list, or `[]`. A scalar YAML value used to iterate as
    characters, turning one typo into a garbled per-character warning."""
    return [s for s in value if isinstance(s, str)] if isinstance(value, list) else []


def _absence_verdict(
    data: dict, absent: list[str], declarable: tuple[str, ...]
) -> dict[str, object]:
    """Read the two declaration fields and judge what an absent surface means.

    `required_release_surfaces` means "these must exist", so declaring an absent surface
    there makes it drift -- it cannot be the remedy for not publishing it.
    `unpublished_release_surfaces` is the separate opt-out: the repo states once which
    surfaces it does not ship, and their absence stops being an unexplained pass.

    D48's recorded defect is disarm-by-deletion: "deleting those four adapter lines
    disarms it with nothing corroborating them". This check cannot tell "this consumer
    never publishes codex" from "a failed sync deleted the codex plugin.json" -- that is
    D48's whole point -- so it does not guess. It states the epistemic status of the
    pass, and the teeth go where a wrong answer escapes:
    `publish_release_preflight.release_surface_blocker` refuses to publish while
    corroboration is `uncorroborated`. `drift` is unchanged, so the read-only status call
    still reddens nobody's un-shipped lane.

    Scoped to DECLARABLE absences: `packaging_manifest` is prepended to `absent` and is
    deliberately not declarable, so including it would report "declared" over an absence
    nothing named and nothing could name.
    """
    declared = _declared_list(data.get("required_release_surfaces"))
    declared_unpublished = _declared_list(data.get("unpublished_release_surfaces"))
    required = [s for s in declared if s in declarable]
    unpublished = [s for s in declared_unpublished if s in declarable]
    absent_declarable = [s for s in absent if s in declarable]
    undeclared_absent = [s for s in absent_declarable if s not in required and s not in unpublished]
    warnings: list[str] = []
    # Both fields warn on an unreadable name. A silently discarded
    # `unpublished_release_surfaces: [codex-plugin]` (hyphen) opts out of nothing and
    # leaves the operator staring at a refusal with no hint that their line was dropped.
    for field, names in (
        ("required_release_surfaces", declared),
        ("unpublished_release_surfaces", declared_unpublished),
    ):
        unknown = [s for s in names if s not in declarable]
        if unknown:
            warnings.append(
                f"{field} names surface(s) this check does not read: {unknown}. "
                f"Known surfaces: {list(declarable)}."
            )
    contradictory = [s for s in required if s in unpublished]
    if contradictory:
        warnings.append(
            f"surface(s) named as BOTH required and unpublished: {contradictory}. "
            "`required_release_surfaces` wins (fail-closed), but the adapter contradicts "
            "itself: a surface cannot both have to exist and not be shipped."
        )
    return {
        "payload": {
            "required_release_surfaces": required,
            "unpublished_release_surfaces": unpublished,
            "undeclared_absent_surfaces": undeclared_absent,
            "absence_corroboration": (
                "not-applicable"
                if not absent_declarable
                else "uncorroborated"
                if undeclared_absent
                else "declared"
            ),
        },
        "warnings": warnings,
    }


def build_payload(repo_root: Path) -> dict[str, object]:
    # GUARDED AT THE READ SITE. Three modules import `build_payload` directly
    # (`publish_release_cli`, `publish_release_plan`, `plan_release_run`).
    #
    # A round-1 bounded review REFUTED the "all three" harm claim this comment used to
    # carry. Under an unhonored declaration the first two stop earlier, at
    # `publish_release_cli._valid_adapter_data`. ONE genuinely reached a charness default
    # here: `plan_release_run` calls this function UNCONDITIONALLY, ahead of its own
    # validity gates. So read-site placement removes one measured live harm, and buys
    # positional independence for the rest.
    #
    # WHAT IT COSTS TO BE UNGUARDED, measured on the real CLI: a repo declaring
    # `package_id: acme-harness`, `packaging_manifest_path: vendor/mypkg/manifest.json`
    # and `materialized_plugin_root: vendor/mypkg` under a refused version got back
    # `package_id: <its own directory name>` and two paths under `packaging/` and
    # `plugins/` that do not exist -- exit 0. This surface answers "which package is this
    # release, and where does it live", and it answered with a charness guess while
    # printing `valid: false` in the same payload. Echoing the flag and acting on the
    # defaults anyway is the exact shape the census's `safe-checks-errors` boundary is
    # about: a read is not a check.
    refusal = _adapter_version_verdict.unspeakable_version_message(
        load_adapter, repo_root, adapter_name="release-adapter.yaml"
    )
    if refusal is not None:
        raise SystemExit(refusal)
    adapter = load_adapter(repo_root)
    data = adapter["data"]
    manifest_path = repo_root / data["packaging_manifest_path"]
    package_id = data["package_id"]
    plugin_root = repo_root / data["materialized_plugin_root"]
    payload: dict[str, object] = {
        "adapter": {
            "found": adapter["found"],
            "valid": adapter["valid"],
            "path": adapter["path"],
            "warnings": adapter["warnings"],
        },
        "package_id": package_id,
        "packaging_manifest_path": str(manifest_path),
        "materialized_plugin_root": str(plugin_root),
        "surface_versions": {
            "packaging_manifest": _version_at(manifest_path),
            "claude_plugin": _version_at(plugin_root / ".claude-plugin" / "plugin.json"),
            "codex_plugin": _version_at(plugin_root / ".codex-plugin" / "plugin.json"),
        },
        "git_status": _git_status(repo_root),
        "fresh_checkout_probes": build_fresh_checkout_payload(repo_root, run_probes=False),
    }
    payload["surface_versions"].update(_marketplace_versions(repo_root, package_id))
    expected = payload["surface_versions"]["packaging_manifest"]
    versioned_surfaces = ("claude_plugin", "codex_plugin", "claude_marketplace_version")
    # The codex marketplace is a PRESENCE surface, not a versioned one — it carries a
    # source path, never a version — but the sweep row names it, so it is declarable and
    # reportable on the same axis. Leaving it out is how "deleted by a failed sync" stayed
    # invisible for it.
    presence_surfaces = ("codex_marketplace_source_path",)
    payload["versioned_surfaces"] = ["packaging_manifest", *versioned_surfaces]
    payload["presence_surfaces"] = list(presence_surfaces)
    # `packaging_manifest` is deliberately NOT declarable: its absence is drift whether or
    # not anyone declares it, so accepting the declaration would be a silent no-op that
    # reads like it was honored.
    declarable = (*versioned_surfaces, *presence_surfaces)

    # A surface whose version is None is one nothing read a version out of: the file is
    # missing, unreadable, or has no `version`. The drift loop below used to skip those
    # (it needed `actual is not None`), so a codex plugin.json that a failed sync never
    # wrote was indistinguishable from one that matches (sweep row S35) — and `drift` is
    # the gate `publish_release_cli` refuses on and `plan_release_run_packets` routes on.
    # Absence is now legible for every surface INCLUDING the packaging manifest the others
    # are compared against, and becomes drift only for the surfaces the repo's own adapter
    # declares it publishes: a consumer that ships claude-only must not be turned red by a
    # list it never wrote. That declaration is self-authored and defaults to empty — see
    # the closure note on S35; this repair does not claim to have solved that.
    def _state(surface: str) -> str:
        """`absent` when nothing is there to read, `unreadable` when the file exists but
        is not parseable JSON, `no-version` when it parses but yields no usable value.
        Printing `<absent>` for the last two would be a false claim about the filesystem,
        and collapsing unreadable into no-version is the S28 distinction unmade."""
        if surface == "packaging_manifest":
            path = manifest_path
        elif surface == "claude_plugin":
            path = plugin_root / ".claude-plugin" / "plugin.json"
        elif surface == "codex_plugin":
            path = plugin_root / ".codex-plugin" / "plugin.json"
        elif surface == "claude_marketplace_version":
            path = repo_root / ".claude-plugin" / "marketplace.json"
        else:
            path = repo_root / ".agents" / "plugins" / "marketplace.json"
        if not path.is_file():
            return "absent"
        return "no-version" if _read_json(path) is not None else "unreadable"

    all_surfaces = (*versioned_surfaces, *presence_surfaces)
    # `absent_surfaces` means the file is not there — NOT merely that no version came out
    # of it. Building it from the `None` test would report a file that is right on disk as
    # absent, in the one field named for the distinction `_state` exists to make.
    absent = [
        s
        for s in all_surfaces
        if payload["surface_versions"].get(s) is None and _state(s) == "absent"
    ]
    if expected is None and _state("packaging_manifest") == "absent":
        absent = ["packaging_manifest", *absent]
    payload["absent_surfaces"] = absent
    verdict = _absence_verdict(data, absent, declarable)
    payload.update(verdict["payload"])
    required = verdict["payload"]["required_release_surfaces"]
    unpublished = verdict["payload"]["unpublished_release_surfaces"]
    payload["adapter"]["warnings"] = [*payload["adapter"]["warnings"], *verdict["warnings"]]
    drift: list[str] = []
    if expected is None:
        # The reference input is missing, so no surface can be compared. Reporting an
        # empty drift list here would render "everything matches" over a deleted or
        # half-written manifest — the batch's own rule, at the top of the chain.
        drift.append(
            f"packaging_manifest=<{_state('packaging_manifest')}>; no expected version to "
            "compare the generated surfaces against"
        )
    for surface in all_surfaces:
        actual = payload["surface_versions"].get(surface)
        if actual is None:
            state = _state(surface)
            if state in ("unreadable", "no-version") and surface not in unpublished:
                # The state a failed sync actually leaves (a half-written `{"version": `),
                # which never entered `absent_surfaces` and so escaped the declared-only
                # arm whenever the declaration was deleted. It fires without
                # `required_release_surfaces`, so deleting that list cannot disarm it.
                #
                # But it IS exemptable, and the first cut of this repair was wrong to say
                # otherwise ("a repo that does not ship the lane has no file at all").
                # The two marketplace surfaces are per-REPO files, not per-package: a
                # `.agents/plugins/marketplace.json` that lists some other product parses
                # fine and yields nothing for this package, i.e. `no-version`, with no
                # corruption anywhere. `version` is also optional in an upstream
                # plugin.json. Without this exemption those consumers were permanently
                # red through `drift` -- which `plan_release_run_packets` has always
                # routed on -- with no adapter line able to clear it.
                drift.append(f"{surface}=<{state}>")
                continue
            if surface in required:
                suffix = f" != packaging_manifest={expected}" if expected is not None else ""
                drift.append(f"{surface}=<{_state(surface)}>{suffix}")
            continue
        if expected is not None and surface in versioned_surfaces and actual != expected:
            drift.append(f"{surface}={actual} != packaging_manifest={expected}")
    payload["drift"] = drift
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root used to resolve the release adapter",
    )
    args = parser.parse_args()
    emit_yaml(build_payload(args.repo_root.resolve()))


if __name__ == "__main__":
    main()
