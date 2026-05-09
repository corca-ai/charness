#!/usr/bin/env python3
"""Detect silent cross-namespace mentions between charness public skills.

Each public skill owns its `charness-artifacts/<skill-id>/` namespace and its
`.agents/<skill-id>-adapter.yaml` adapter file. When a SKILL.md, references,
or scripts under one skill mention another skill's namespace, the boundary
must be explicit -- either documented as a known cross-skill write (seed,
init-repo bootstrap) or as a known read (cite, spill target, evidence) --
via the allowlist at scripts/check_skill_ownership_overlap.allowlist.txt.

Silent overlap creates drift the next operator hits. This validator surfaces
the overlap so the boundary becomes a deliberate choice instead of prose-only
verification in create-skill/portable-authoring.md.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ART_RE = re.compile(r"charness-artifacts/([a-z][a-z0-9-]*)/")
ADP_RE = re.compile(r"\.agents/([a-z][a-z0-9-]*)-adapter\.yaml")

ALLOWLIST_PATH = Path("scripts/check_skill_ownership_overlap.allowlist.txt")


def parse_allowlist(path: Path) -> set[tuple[str, str, str]]:
    if not path.is_file():
        return set()
    out: set[tuple[str, str, str]] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split(":", 3)]
        if len(parts) < 3:
            continue
        out.add((parts[0], parts[1], parts[2]))
    return out


def _scan_file(text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for m in ART_RE.finditer(text):
        found.append(("artifact", m.group(1)))
    for m in ADP_RE.finditer(text):
        found.append(("adapter", m.group(1)))
    return found


def scan(repo_root: Path, allowlist: set[tuple[str, str, str]]) -> dict:
    public_root = repo_root / "skills" / "public"
    findings: list[dict] = []
    if not public_root.is_dir():
        return {"findings": findings, "scanned_skills": 0}
    skill_count = 0
    for skill_dir in sorted(public_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        sid = skill_dir.name
        skill_count += 1
        files: list[Path] = []
        skill_md = skill_dir / "SKILL.md"
        if skill_md.is_file():
            files.append(skill_md)
        for sub in ("scripts", "references"):
            sub_dir = skill_dir / sub
            if sub_dir.is_dir():
                for p in sorted(sub_dir.iterdir()):
                    if p.is_file() and p.suffix in {".py", ".md"}:
                        files.append(p)
        for f in files:
            text = f.read_text(encoding="utf-8")
            for kind, owner in _scan_file(text):
                if owner == sid:
                    continue
                if (sid, kind, owner) in allowlist:
                    continue
                findings.append(
                    {
                        "skill": sid,
                        "file": str(f.relative_to(repo_root)),
                        "kind": kind,
                        "owner": owner,
                        "allowlist_entry": f"{sid}:{kind}:{owner}:<reason>",
                    }
                )
    return {"findings": findings, "scanned_skills": skill_count}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    repo_root = args.repo_root.resolve()
    allowlist = parse_allowlist(repo_root / ALLOWLIST_PATH)
    result = scan(repo_root, allowlist)
    if args.json:
        print(json.dumps({**result, "allowlist_size": len(allowlist)}, indent=2))
    else:
        if not result["findings"]:
            print(
                f"check_skill_ownership_overlap: ok "
                f"({result['scanned_skills']} skills, allowlist={len(allowlist)})"
            )
            return 0
        print("check_skill_ownership_overlap: violations")
        for f in result["findings"]:
            print(f"  [{f['skill']}] -> {f['kind']}/{f['owner']} in {f['file']}")
            print(f"    allowlist suggestion: {f['allowlist_entry']}")
    return 0 if not result["findings"] else 2


if __name__ == "__main__":
    sys.exit(main())
