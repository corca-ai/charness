#!/usr/bin/env python3
"""Critique prepare packet runner.

Reads `.agents/critique-adapter.yaml`, executes each declared
`packet_sections` entry (static include or script command), and emits
two artifacts under the adapter `output_dir`:

- `<slug>-packet.json` — `charness.critique_prepare_packet.v1` envelope
- `<slug>-packet.md` — human-readable render that fresh-eye reviewers
  consume before broad repo sampling

Schema lives in
`skills/public/critique/references/prepare-packet.md`.
"""
from __future__ import annotations

import argparse
import runpy
import shlex
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_critique_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.critique_adapter_lib"
)
_critique_packet_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.critique_packet_lib"
)
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
load_adapter = _critique_adapter_lib.load_adapter
adapter_has_sections = _critique_adapter_lib.adapter_has_sections
build_packet = _critique_packet_lib.build_packet
parse_changed_ref = _critique_packet_lib.parse_changed_ref
substrate_refusal = _critique_packet_lib.substrate_refusal
packet_result_payload = _critique_packet_lib.packet_result_payload
ReviewedInputError = _critique_packet_lib.ReviewedInputError
write_packet = _critique_packet_lib.write_packet
packet_file_sha256 = _critique_packet_lib.packet_file_sha256
render_markdown = _critique_packet_lib.render_markdown


def _default_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def _verification_command(repo_root: Path, binding: dict[str, object]) -> str:
    verifier = Path(__file__).resolve().with_name("verify_packet.py")
    try:
        verifier_arg = verifier.relative_to(repo_root).as_posix()
    except ValueError:
        verifier_arg = str(verifier)
    return shlex.join(
        [
            "python3",
            verifier_arg,
            "--repo-root",
            ".",
            "--packet-path",
            str(binding["packet_path"]),
            "--packet-sha256",
            str(binding["packet_sha256"]),
            "--identity-sha256",
            str(binding["identity_sha256"]),
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the critique prepare-packet runner")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root to build the critique packet from")
    parser.add_argument("--prepared-for", default="working tree",
                        help="Short label describing what this packet covers (e.g. commit range)")
    parser.add_argument("--changed-ref", default=None,
                        help="Git commit or range that script packet sections should inspect")
    parser.add_argument(
        "--substrate-mode",
        choices=("working-tree", "committed-ref"),
        default=None,
        help="Explicit review substrate; committed-ref requires --changed-ref",
    )
    parser.add_argument("--commit", default=None,
                        help="Convenience alias for --changed-ref when reviewing one commit")
    parser.add_argument("--range", dest="changed_range", default=None,
                        help="Convenience alias for --changed-ref when reviewing an endpoint diff range")
    parser.add_argument("--slug", default=None,
                        help="Slug for the output artifacts (default: ISO datetime)")
    parser.add_argument(
        "--reviewed-path",
        action="append",
        default=None,
        help="Repo-relative path declared as reviewed (repeatable; defaults to changed paths).",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    changed_ref = parse_changed_ref(
        parser,
        changed_ref=args.changed_ref,
        commit=args.commit,
        changed_range=args.changed_range,
    )
    substrate_mode = args.substrate_mode or ("committed-ref" if changed_ref else "working-tree")
    refusal = substrate_refusal(substrate_mode=substrate_mode, changed_ref=changed_ref)
    if refusal is not None:
        yaml_output.emit_yaml(refusal)
        return 1
    prepared_for = args.prepared_for
    if prepared_for == "working tree" and changed_ref:
        prepared_for = changed_ref
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        yaml_output.emit_yaml({"ok": False, "error": "critique adapter invalid", "adapter": adapter})
        return 1
    if not adapter_has_sections(adapter):
        adapter_path = adapter.get("path")
        if isinstance(adapter_path, str) and adapter_path:
            try:
                adapter_name = Path(adapter_path).resolve().relative_to(repo_root).as_posix()
            except ValueError:
                adapter_name = adapter_path
        else:
            adapter_name = ".agents/critique-adapter.yaml"
        warning = (
            f"critique adapter `{adapter_name}` declares no packet_sections; "
            "the packet carries no semantic review input"
        )
        yaml_output.emit_yaml(
            {
                "ok": False,
                "status": "refused",
                "reason_code": "adapter-no-sections",
                "scope_status": "adapter-no-sections",
                "adapter_path": adapter_name,
                "section_count": 0,
                "usable": False,
                "warning": warning,
                "error": warning,
                "remedy": (
                    f"Declare at least one packet_sections entry in `{adapter_name}` "
                    "and rerun; no packet was written."
                ),
            }
        )
        return 1
    output_dir = repo_root / adapter["data"].get("output_dir", "charness-artifacts/critique")
    slug = args.slug or _default_slug()
    excluded_paths = [
        (output_dir / f"{slug}-packet.json").relative_to(repo_root).as_posix(),
        (output_dir / f"{slug}-packet.md").relative_to(repo_root).as_posix(),
    ]
    collisions = sorted(set(args.reviewed_path or []) & set(excluded_paths))
    if collisions:
        parser.error(f"--reviewed-path collides with packet output: {', '.join(collisions)}")
    # The review record is not a reviewed input: the auto sweep drops every
    # artifact under the critique output dir — the artifact being authored, and any
    # packet already written this session — so writing the record cannot stale the
    # binding that describes it. Explicit `--reviewed-path` still wins.
    excluded_prefixes = [f"{output_dir.relative_to(repo_root).as_posix()}/"]
    try:
        packet = build_packet(
            adapter=adapter,
            repo_root=repo_root,
            prepared_for=prepared_for,
            changed_ref=changed_ref,
            substrate_mode=substrate_mode,
            reviewed_paths=args.reviewed_path,
            excluded_reviewed_paths=excluded_paths,
            excluded_reviewed_prefixes=excluded_prefixes,
        )
    except ReviewedInputError as exc:
        refusal = {
            "ok": False,
            "status": "refused",
            "reason_code": exc.code,
            "error": str(exc),
            "substrate_mode": substrate_mode,
            "changed_ref": changed_ref,
            "recovery": {
                "kind": "correct-review-substrate",
                "message": (
                    "Correct the substrate mode/ref/path declaration and rerun; "
                    "no packet was written."
                ),
            },
        }
        refusal.update(exc.details)
        yaml_output.emit_yaml(refusal)
        return 1

    json_path, md_path = write_packet(packet, output_dir=output_dir, slug=slug)
    identity = packet["reviewed_input_identity"]
    binding = {
        "packet_path": str(json_path.relative_to(repo_root)),
        "packet_sha256": packet_file_sha256(json_path),
        "identity_sha256": identity["identity_sha256"],
        "reviewed_paths": identity.get("reviewed_paths", []),
        # Auto-sweep drops, reported so a narrowed binding is never silently narrow.
        "auto_excluded_paths": identity.get("auto_excluded_paths", []),
    }
    binding["verify_command"] = _verification_command(repo_root, binding)
    md_path.write_text(
        render_markdown(packet, verification_command=str(binding["verify_command"])),
        encoding="utf-8",
    )
    if not identity.get("reviewed_paths"):
        # A zero-path binding digests to the same constant everywhere and can never
        # go stale, so it would verify as current while proving nothing. Say so here
        # rather than let the three hex fields read as a checked review.
        binding["usable"] = False
        binding["warning"] = (
            "binding covers zero reviewed paths and proves nothing; re-run with "
            "explicit --reviewed-path values for what was actually reviewed"
        )
        binding["reason_code"] = "empty-reviewed-paths"
        binding["scope_status"] = "empty-reviewed-input"
        binding["error"] = "packet reviewed input covers zero paths and carries no semantic review input"
        binding["remedy"] = "Provide at least one explicit or changed reviewed path and rerun"
    result = packet_result_payload(
        packet, repo_root=repo_root, json_path=json_path, md_path=md_path
    )
    result["substrate_mode"] = packet["substrate_mode"]
    result["reviewed_input_binding"] = binding
    yaml_output.emit_yaml(result)
    return 0 if packet["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
