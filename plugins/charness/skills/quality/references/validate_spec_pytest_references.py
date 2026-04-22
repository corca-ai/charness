#!/usr/bin/env python3
"""Reference validator for `Covered by pytest:` notes.

Honesty rule:
This validator proves that the referenced pytest target still collects. It does
not prove that the target's behavior fully matches the spec note. Say that out
loud in repo docs and gate descriptions.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SPECS_DIR = REPO_ROOT / "specs"
INDEX_SPEC = "index.spec.md"
NOTE_START_RE = re.compile(r"Covered by pytest:")
REF_RE = re.compile(r"`(tests/[^`]+)`")


def note_body(text: str, start: int) -> str:
    buffer: list[str] = []
    in_tick = False
    index = start
    while index < len(text):
        char = text[index]
        if char == "`":
            in_tick = not in_tick
            buffer.append(char)
        elif char == "." and not in_tick:
            break
        else:
            buffer.append(char)
        index += 1
    return "".join(buffer)


@dataclass(frozen=True)
class Reference:
    spec_path: Path
    target: str


def extract_references(spec_path: Path) -> tuple[list[Reference], list[str]]:
    text = spec_path.read_text(encoding="utf-8")
    refs: list[Reference] = []
    skipped: list[str] = []
    for match in NOTE_START_RE.finditer(text):
        body = note_body(text, match.end())
        found = REF_RE.findall(body)
        if not found:
            skipped.append(f"{spec_path.name}: unparseable `Covered by pytest:` note")
            continue
        for target in found:
            refs.append(Reference(spec_path=spec_path, target=target))
    return refs, skipped


def target_collects(target: str) -> tuple[bool, str]:
    proc = subprocess.run(
        ["python3", "-m", "pytest", "--collect-only", "-q", target],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    output = (proc.stdout + proc.stderr).strip()
    if proc.returncode != 0 or "no tests collected" in output:
        return False, output
    return True, ""


def documentation_only_specs(spec_paths: list[Path]) -> list[Path]:
    docs_only: list[Path] = []
    for spec_path in spec_paths:
        if spec_path.name == INDEX_SPEC:
            continue
        text = spec_path.read_text(encoding="utf-8")
        if "Covered by pytest:" not in text and "> check:contract" not in text:
            docs_only.append(spec_path)
    return docs_only


def main() -> int:
    spec_paths = sorted(SPECS_DIR.glob("*.spec.md"))
    if not spec_paths:
        raise SystemExit(f"FAIL: no specs found under {SPECS_DIR}")

    refs: list[Reference] = []
    skipped: list[str] = []
    for spec_path in spec_paths:
        extracted, skipped_notes = extract_references(spec_path)
        refs.extend(extracted)
        skipped.extend(skipped_notes)

    stale: list[tuple[Reference, str]] = []
    for ref in refs:
        ok, detail = target_collects(ref.target)
        if not ok:
            stale.append((ref, detail))

    print(f"Validated {len(refs)} pytest reference(s) across {len(spec_paths)} spec file(s).")
    for reason in skipped:
        print(f"SKIP: {reason}")
    docs_only = documentation_only_specs(spec_paths)
    for spec_path in docs_only:
        print(f"WARN: documentation-only spec: {spec_path.relative_to(REPO_ROOT)}")

    if stale:
        print("FAIL: stale pytest references detected:")
        for ref, detail in stale:
            print(f"  - {ref.spec_path.relative_to(REPO_ROOT)} -> {ref.target}")
            if detail:
                for line in detail.splitlines():
                    if line.strip():
                        print(f"      {line}")
        return 1

    print("OK: every pytest reference still collects.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
