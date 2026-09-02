#!/usr/bin/env python3
"""Retro prepare packet runner.

Reads `retro-adapter.yaml`, executes declared `packet_sections`, and emits
one deterministic packet for retros to consume before writing lessons.
"""

from __future__ import annotations

import argparse
import runpy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
_packet_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.review.critique_packet_lib"
)
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
load_adapter = _resolve_adapter.load_adapter
build_packet = _packet_lib.build_packet
parse_changed_ref = _packet_lib.parse_changed_ref
packet_result_payload = _packet_lib.packet_result_payload
write_packet = _packet_lib.write_packet

RETRO_PACKET_KIND = "charness.retro_prepare_packet"


def _default_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="retro prepare_packet")
    parser = argparse.ArgumentParser(description="Run the retro prepare-packet runner")
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repository root used to resolve the retro adapter and packet output path.",
    )
    parser.add_argument(
        "--prepared-for",
        default="working tree",
        help="Human label for the work under review when no explicit changed ref is supplied.",
    )
    parser.add_argument(
        "--changed-ref",
        default=None,
        help="Single Git ref whose changed files should define the packet scope.",
    )
    parser.add_argument(
        "--commit",
        default=None,
        help="Single commit whose changed files should define the packet scope.",
    )
    parser.add_argument(
        "--range",
        dest="changed_range",
        default=None,
        help="Git revision range whose changed files should define the packet scope.",
    )
    parser.add_argument(
        "--slug",
        default=None,
        help="Output filename slug; defaults to the current UTC timestamp.",
    )
    try:
        args = parser.parse_args()
        changed_ref = parse_changed_ref(
            parser,
            changed_ref=args.changed_ref,
            commit=args.commit,
            changed_range=args.changed_range,
        )
        prepared_for = changed_ref if args.prepared_for == "working tree" and changed_ref else args.prepared_for
        repo_root = args.repo_root.resolve()
        adapter = load_adapter(repo_root)
        if not adapter["valid"]:
            yaml_output.emit_yaml({"ok": False, "error": "retro adapter invalid", "adapter": adapter})
            return 1

        packet = build_packet(
            adapter=adapter,
            repo_root=repo_root,
            prepared_for=prepared_for,
            changed_ref=changed_ref,
            packet_kind=RETRO_PACKET_KIND,
            include_reviewer_tier=False,
            include_reviewed_input_identity=False,
            changed_ref_env_var="CHARNESS_RETRO_CHANGED_REF",
        )
        output_dir = repo_root / adapter["data"].get("output_dir", "charness-artifacts/retro")
        slug = args.slug or _default_slug()
        json_path, md_path = write_packet(packet, output_dir=output_dir, slug=slug)
        yaml_output.emit_yaml(
            packet_result_payload(packet, repo_root=repo_root, json_path=json_path, md_path=md_path)
        )
        return 0 if packet["ok"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
