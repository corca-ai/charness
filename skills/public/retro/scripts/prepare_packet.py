#!/usr/bin/env python3
"""Retro prepare packet runner.

Reads `retro-adapter.yaml`, executes declared `packet_sections`, and emits
one deterministic packet for retros to consume before writing lessons.
"""

from __future__ import annotations

import argparse
import json
import runpy
import sys
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
    __file__, "scripts.critique_packet_lib"
)
load_adapter = _resolve_adapter.load_adapter
build_packet = _packet_lib.build_packet
write_packet = _packet_lib.write_packet

RETRO_PACKET_KIND = "charness.retro_prepare_packet"


def _default_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="retro prepare_packet")
    parser = argparse.ArgumentParser(description="Run the retro prepare-packet runner")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--prepared-for", default="working tree")
    parser.add_argument("--changed-ref", default=None)
    parser.add_argument("--commit", default=None)
    parser.add_argument("--range", dest="changed_range", default=None)
    parser.add_argument("--slug", default=None)
    parser.add_argument("--json", action="store_true")
    try:
        args = parser.parse_args()
        changed_targets = [value for value in (args.changed_ref, args.commit, args.changed_range) if value]
        if len(changed_targets) > 1:
            parser.error("use only one of --changed-ref, --commit, or --range")
        changed_ref = changed_targets[0] if changed_targets else None
        prepared_for = changed_ref if args.prepared_for == "working tree" and changed_ref else args.prepared_for
        repo_root = args.repo_root.resolve()
        adapter = load_adapter(repo_root)
        if not adapter["valid"]:
            json.dump(
                {"ok": False, "error": "retro adapter invalid", "adapter": adapter},
                sys.stdout,
                indent=2,
                ensure_ascii=False,
                sort_keys=True,
            )
            sys.stdout.write("\n")
            return 1

        packet = build_packet(
            adapter=adapter,
            repo_root=repo_root,
            prepared_for=prepared_for,
            changed_ref=changed_ref,
            packet_kind=RETRO_PACKET_KIND,
            include_reviewer_tier=False,
            changed_ref_env_var="CHARNESS_RETRO_CHANGED_REF",
        )
        if args.json:
            json.dump(packet, sys.stdout, indent=2, ensure_ascii=False)
            sys.stdout.write("\n")
            return 0 if packet["ok"] else 1

        output_dir = repo_root / adapter["data"].get("output_dir", "charness-artifacts/retro")
        slug = args.slug or _default_slug()
        json_path, md_path = write_packet(packet, output_dir=output_dir, slug=slug)
        json.dump(
            {
                "ok": packet["ok"],
                "section_count": packet["section_count"],
                "json_path": str(json_path.relative_to(repo_root)),
                "md_path": str(md_path.relative_to(repo_root)),
                "changed_ref": packet["changed_ref"],
                "adapter_path": packet["adapter_path"],
            },
            sys.stdout,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0 if packet["ok"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
