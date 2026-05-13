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
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_critique_adapter_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.critique_adapter_lib"
)
_critique_packet_lib = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.critique_packet_lib"
)
load_adapter = _critique_adapter_lib.load_adapter
build_packet = _critique_packet_lib.build_packet
write_packet = _critique_packet_lib.write_packet


def _default_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the critique prepare-packet runner")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--prepared-for", default="working tree",
                        help="Short label describing what this packet covers (e.g. commit range)")
    parser.add_argument("--slug", default=None,
                        help="Slug for the output artifacts (default: ISO datetime)")
    parser.add_argument("--json", action="store_true",
                        help="Emit the packet JSON to stdout instead of writing artifacts")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        json.dump(
            {"ok": False, "error": "critique adapter invalid", "adapter": adapter},
            sys.stdout, indent=2, ensure_ascii=False, sort_keys=True,
        )
        sys.stdout.write("\n")
        return 1

    packet = build_packet(adapter=adapter, repo_root=repo_root, prepared_for=args.prepared_for)

    if args.json:
        json.dump(packet, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0 if packet["ok"] else 1

    output_dir = repo_root / adapter["data"].get("output_dir", "charness-artifacts/critique")
    slug = args.slug or _default_slug()
    json_path, md_path = write_packet(packet, output_dir=output_dir, slug=slug)
    json.dump(
        {
            "ok": packet["ok"],
            "section_count": packet["section_count"],
            "json_path": str(json_path.relative_to(repo_root)),
            "md_path": str(md_path.relative_to(repo_root)),
            "adapter_path": adapter["path"],
        },
        sys.stdout, indent=2, ensure_ascii=False, sort_keys=True,
    )
    sys.stdout.write("\n")
    return 0 if packet["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
