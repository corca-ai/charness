#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import Any


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
_resolve_adapter_module = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter_module.load_adapter


REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Scope",
    "## Verification",
    "## Release State",
    "## Public Release Verification",
)

REQUIRED_STATE_LEDGER_LABELS: tuple[str, ...] = (
    "local release mutation",
    "branch/tag push",
    "GitHub release record",
    "public release surface verification",
    "audit narrative",
)


def _release_state_block(artifact_text: str) -> str | None:
    lines = artifact_text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Release State")
    except StopIteration:
        return None
    block: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        block.append(line)
    return "\n".join(block)


def _audit_artifact(artifact_path: Path, *, target_tag: str) -> list[str]:
    blockers: list[str] = []
    if not artifact_path.is_file():
        blockers.append(f"durable release artifact missing: {artifact_path}")
        return blockers
    text = artifact_path.read_text(encoding="utf-8")
    if target_tag not in text:
        blockers.append(
            f"release artifact {artifact_path} does not mention target tag `{target_tag}`; "
            "the audit narrative may be stale relative to this publish"
        )
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            blockers.append(f"release artifact {artifact_path} is missing section `{heading}`")
    state_block = _release_state_block(text)
    if state_block is None:
        return blockers
    for label in REQUIRED_STATE_LEDGER_LABELS:
        if label not in state_block:
            blockers.append(
                f"release state ledger in {artifact_path} is missing required entry `{label}`"
            )
    return blockers


_MUTABLE_TAG_POINTER_RE = re.compile(
    r"/(?:blob|tree|raw)/(?P<tag>[^/\s)]+)/(?P<path>charness-artifacts/[^\s)]+)"
)


def audit_notes_file(notes_file: Path, *, target_tag: str) -> list[str]:
    blockers: list[str] = []
    if not notes_file.is_file():
        blockers.append(f"public release notes file missing: {notes_file}")
        return blockers
    text = notes_file.read_text(encoding="utf-8")
    for match in _MUTABLE_TAG_POINTER_RE.finditer(text):
        tag = match.group("tag")
        path = match.group("path")
        if tag == target_tag or tag == f"v{target_tag}" or tag.lstrip("v") == target_tag.lstrip("v"):
            blockers.append(
                f"public release notes points at mutable source-tree record `{path}` "
                f"at tag `{tag}`; replace with self-contained content or audited reference"
            )
    return blockers


def build_payload(
    repo_root: Path,
    *,
    target_tag: str,
    artifact_path: Path | None = None,
    notes_file: Path | None = None,
) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        return {
            "status": "blocked",
            "blockers": [f"release adapter is invalid: {adapter['errors']}"],
            "target_tag": target_tag,
        }
    output_dir = adapter["data"]["output_dir"]
    resolved_artifact = artifact_path or (repo_root / output_dir / "latest.md")
    blockers: list[str] = []
    blockers.extend(_audit_artifact(resolved_artifact, target_tag=target_tag))
    notes_blockers: list[str] = []
    if notes_file is not None:
        notes_blockers = audit_notes_file(notes_file, target_tag=target_tag)
        blockers.extend(notes_blockers)
    return {
        "status": "blocked" if blockers else "passed",
        "blockers": blockers,
        "target_tag": target_tag,
        "artifact_path": str(resolved_artifact),
        "notes_file": str(notes_file) if notes_file is not None else None,
        "notes_blockers": notes_blockers,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root used to resolve the release adapter")
    parser.add_argument("--target-tag", required=True, help="Release tag the audit narrative must reference")
    parser.add_argument("--artifact-path", type=Path, help="Path to the release audit artifact (defaults to adapter output_dir/latest.md)")
    parser.add_argument("--notes-file", type=Path, help="Path to the public release notes file to audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    payload = build_payload(
        repo_root,
        target_tag=args.target_tag,
        artifact_path=args.artifact_path.resolve() if args.artifact_path else None,
        notes_file=args.notes_file.resolve() if args.notes_file else None,
    )
    if args.json or payload["status"] == "passed":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("public release narrative audit blocked:")
        for blocker in payload["blockers"]:
            print(f"- {blocker}")
    return 0 if payload["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
