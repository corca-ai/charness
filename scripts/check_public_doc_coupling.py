#!/usr/bin/env python3
"""Advisory scan keeping exported reusable guidance free of hard coupling.

Exported reusable guidance should state portable, current guidance; issue
anchors and charness self-version pins couple it to mutable tracker and
release history. Skill packages under skills/public|support already get the
blocking issue-anchor sweep from validate_skill_ergonomics, so this gate
covers the remaining exported surfaces (shared references, generated docs)
with the same canonical anchor rule, plus the self-version-pin class across
all exported guidance. Record-layer artifacts and tracking ledgers are out of
scope by design: docs/conventions/provenance-placement.md owns the placement
policy. The pin pattern is bound to the charness v0.x release family plus
`charness <semver>` mentions, so external tools versioned 1.x and above (for
example a pinned runner release) are out of pattern; an external tool still
in its own 0.x family does match, and that finding stays a judgment call for
the reader. Revisit the pattern if charness leaves the 0.x family.

Always exits 0; findings print as `ADVISORY:` lines for run-quality attention.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from runtime_bootstrap import load_path_module, repo_root_from_script

try:
    from scripts.repo_file_listing import iter_matching_repo_files
except ModuleNotFoundError:
    from repo_file_listing import iter_matching_repo_files

LIB_ROOT = repo_root_from_script(__file__)
ANCHOR_PATTERNS = ("skills/shared/references/**/*.md", "docs/generated/**/*.md")
PIN_PATTERNS = (
    "skills/public/**/*.md",
    "skills/support/**/*.md",
    "skills/shared/references/**/*.md",
    "docs/generated/**/*.md",
)
SELF_VERSION_PIN_RE = re.compile(
    r"(?<![A-Za-z0-9.])v0\.\d+\.\d+\b|\bcharness\s+v?\d+\.\d+\.\d+\b", re.IGNORECASE
)


def _load_text_quality_lib():
    candidates = (
        LIB_ROOT / "skills" / "public" / "quality" / "scripts" / "skill_text_quality_lib.py",
        LIB_ROOT / "skills" / "quality" / "scripts" / "skill_text_quality_lib.py",
    )
    for candidate in candidates:
        if candidate.is_file():
            return load_path_module("skill_text_quality_lib_coupling", candidate)
    raise SystemExit(
        "missing skill_text_quality_lib helper; expected it under "
        "`skills/public/quality/scripts/` or `skills/quality/scripts/`"
    )


def _line_findings(
    repo_root: Path,
    patterns: tuple[str, ...],
    kind: str,
    matcher,
    *,
    require_git: bool = False,
) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []
    for path in iter_matching_repo_files(repo_root, patterns, require_git=require_git):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for index, line in enumerate(lines, start=1):
            if matcher(line):
                findings.append(
                    {
                        "kind": kind,
                        "path": path.relative_to(repo_root).as_posix(),
                        "line": index,
                        "excerpt": line.strip()[:160],
                    }
                )
    return findings


def find_coupling(repo_root: Path, *, require_git: bool = False) -> list[dict[str, object]]:
    lib = _load_text_quality_lib()

    def anchor_match(line: str) -> bool:
        return bool(lib.ISSUE_ANCHOR_RE.search(line)) and not lib.is_allowed_issue_anchor_context(line)

    findings = _line_findings(
        repo_root, ANCHOR_PATTERNS, "issue_anchor", anchor_match, require_git=require_git
    )
    findings.extend(
        _line_findings(
            repo_root,
            PIN_PATTERNS,
            "self_version_pin",
            lambda line: bool(SELF_VERSION_PIN_RE.search(line)),
            require_git=require_git,
        )
    )
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--require-git-file-listing", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    findings = find_coupling(repo_root, require_git=args.require_git_file_listing)
    if args.json:
        print(json.dumps({"status": "clean" if not findings else "coupled", "findings": findings}, indent=2))
        return 0
    if not findings:
        print("public-doc coupling: exported reusable guidance is clean")
        return 0
    print(f"ADVISORY: public-doc-coupling found {len(findings)} hard-coupling reference(s) in exported reusable guidance:")
    for finding in findings:
        print(f"- {finding['path']}:{finding['line']} [{finding['kind']}] {finding['excerpt']}")
    print("Move provenance to the record layer per docs/conventions/provenance-placement.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
