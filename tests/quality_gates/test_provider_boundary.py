"""Provider-boundary gate (#418).

Portable model-facing skill surfaces — and their `plugins/charness/` mirror — must
not carry direct credentialed-org-provider routes (raw provider tokens or the
removed charness-owned credentialed gather runtimes). A downstream consumer such
as Ceal materializes these surfaces verbatim, so a leaked `SLACK_BOT_TOKEN` route
or `gather-slack`/`gather-notion` reference reintroduces exactly the non-portable
assumption #417/#418 removed: gather is public-source only, and credentialed org
data flows through the consuming runtime's own capability/connector.

Two layers, both with fixture coverage:

1. Literal markers (the exact removed surfaces) must not reappear on ANY
   consumer-materialized surface — source skills, the packaged mirror, the
   integrations manifests where the deleted locks lived, or the `charness` CLI
   that scaffolds capability config.
2. A generic org bot/api-token pattern must not appear in model-facing skill
   GUIDANCE (SKILL.md / references / capability metadata / adapter examples), so
   the *class* cannot recur through a newly-added credentialed provider. This is
   scoped to guidance files, not scripts, so maintainer-local eval tooling
   (`OPENAI_API_KEY` in `scripts/agent-runtime/`) is intentionally out of scope.
"""

from __future__ import annotations

import re
from pathlib import Path

from .support import ROOT

# Layer 1: exact removed surfaces. Broad reach — these must never reappear on any
# surface a consumer materializes.
LITERAL_MARKERS = (
    "SLACK_BOT_TOKEN",
    "gather-slack",
    "gather-notion",
    "advise_slack_path",
)
LITERAL_SCAN_ROOTS = (
    "skills",
    "plugins/charness/skills",
    "plugins/charness/support",
    "plugins/charness/shared",
    "plugins/charness/integrations",
    "integrations",
)
# The single-file `charness` CLI scaffolds `.charness/local|example` capability
# config, so it is scanned too (the leak the critique caught lived here).
LITERAL_SCAN_FILES = ("charness",)

# Layer 2: generic credentialed org bot/api token names on a MODEL-FACING guidance
# surface. `API_KEY`/`ACCESS_KEY` are deliberately excluded: `OPENAI_API_KEY` in
# the maintainer-local codex eval runtime is intentionally retained, and `GH_TOKEN`
# (bare `_TOKEN`) is a portable capability alias, not a raw org route.
GUIDANCE_TOKEN_RE = re.compile(r"\b[A-Z][A-Z0-9]*_(?:BOT_TOKEN|API_TOKEN|ACCESS_TOKEN)\b")
GUIDANCE_SCAN_ROOTS = (
    "skills",
    "plugins/charness/skills",
    "plugins/charness/support",
    "plugins/charness/shared",
)
GUIDANCE_SUFFIXES = {".md", ".json", ".yaml", ".yml"}

_SKIP_DIR_NAMES = {"__pycache__", ".git"}
_TEXT_SUFFIXES = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".mjs", ".js", ".sh", ".toml", ""}


def _iter_files(root: Path, suffixes: set[str]):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIR_NAMES for part in path.parts):
            continue
        if path.suffix.lower() not in suffixes:
            continue
        yield path


def scan_literal_markers(root: Path) -> list[tuple[str, str]]:
    """Return (relative_path, marker) literal-marker violations under ``root``."""
    violations: list[tuple[str, str]] = []
    if not root.is_dir():
        return violations
    for path in _iter_files(root, _TEXT_SUFFIXES):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in LITERAL_MARKERS:
            if marker in text:
                violations.append((str(path.relative_to(root)), marker))
    return violations


def scan_guidance_tokens(root: Path) -> list[tuple[str, str]]:
    """Return (relative_path, matched_token) generic-token violations in guidance."""
    violations: list[tuple[str, str]] = []
    if not root.is_dir():
        return violations
    for path in _iter_files(root, GUIDANCE_SUFFIXES):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in GUIDANCE_TOKEN_RE.finditer(text):
            violations.append((str(path.relative_to(root)), match.group(0)))
    return violations


def test_no_credentialed_provider_route_in_skill_surfaces() -> None:
    found: list[str] = []
    for scan_root in LITERAL_SCAN_ROOTS:
        for rel, marker in scan_literal_markers(ROOT / scan_root):
            found.append(f"{scan_root}/{rel}: `{marker}`")
    for scan_file in LITERAL_SCAN_FILES:
        path = ROOT / scan_file
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            for marker in LITERAL_MARKERS:
                if marker in text:
                    found.append(f"{scan_file}: `{marker}`")
    assert found == [], (
        "credentialed-org-provider leak on a consumer-materialized surface (gather "
        "is public-source only; credentialed org data belongs to the consuming "
        "runtime's capability/connector):\n" + "\n".join(found)
    )


def test_no_credentialed_org_token_in_skill_guidance() -> None:
    found: list[str] = []
    for scan_root in GUIDANCE_SCAN_ROOTS:
        for rel, token in scan_guidance_tokens(ROOT / scan_root):
            found.append(f"{scan_root}/{rel}: `{token}`")
    assert found == [], (
        "credentialed org bot/api token named on a model-facing skill guidance "
        "surface; route provider access through the runtime capability/connector "
        "instead of a raw token:\n" + "\n".join(found)
    )


def test_gate_covers_both_source_and_packaged_mirror() -> None:
    # Guard against the scan silently skipping a tree: the source skills root and
    # the packaged plugin mirror must both exist and be scanned.
    assert (ROOT / "skills").is_dir()
    assert (ROOT / "plugins" / "charness" / "skills").is_dir()


def test_scanner_catches_credentialed_token_in_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "skills" / "public" / "demo"
    fixture.mkdir(parents=True)
    (fixture / "SKILL.md").write_text(
        "# Demo\n\nExport the thread with `SLACK_BOT_TOKEN` before gathering.\n",
        encoding="utf-8",
    )
    assert ("skills/public/demo/SKILL.md", "SLACK_BOT_TOKEN") in scan_literal_markers(tmp_path)


def test_scanner_catches_removed_runtime_reference_in_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "support" / "example"
    fixture.mkdir(parents=True)
    (fixture / "capability.json").write_text(
        '{"provider": "gather-notion", "note": "advise_slack_path route"}\n',
        encoding="utf-8",
    )
    markers = {marker for _, marker in scan_literal_markers(tmp_path)}
    assert "gather-notion" in markers
    assert "advise_slack_path" in markers


def test_generic_token_scanner_catches_new_credentialed_token(tmp_path: Path) -> None:
    # A NEW credentialed provider (never named in LITERAL_MARKERS) must still trip
    # the class-level guidance gate.
    fixture = tmp_path / "public" / "demo"
    fixture.mkdir(parents=True)
    (fixture / "SKILL.md").write_text(
        "# Demo\n\nSet `NOTION_API_TOKEN` to reach the workspace.\n",
        encoding="utf-8",
    )
    tokens = {token for _, token in scan_guidance_tokens(tmp_path)}
    assert "NOTION_API_TOKEN" in tokens


def test_generic_token_scanner_ignores_portable_aliases_and_eval_tooling(tmp_path: Path) -> None:
    fixture = tmp_path / "public" / "demo"
    fixture.mkdir(parents=True)
    # GH_TOKEN (portable capability alias) and OPENAI_API_KEY (eval tooling, and
    # not a guidance surface) must NOT be flagged by the generic guidance gate.
    (fixture / "SKILL.md").write_text(
        "# Demo\n\nThe runtime aliases `GH_TOKEN`; the codex eval runner reads "
        "`OPENAI_API_KEY`.\n",
        encoding="utf-8",
    )
    assert scan_guidance_tokens(tmp_path) == []


def test_scanner_passes_clean_fixture(tmp_path: Path) -> None:
    fixture = tmp_path / "skills" / "public" / "demo"
    fixture.mkdir(parents=True)
    (fixture / "SKILL.md").write_text(
        "# Demo\n\nGather is public-source only. Credentialed org data flows "
        "through the consuming runtime's capability/connector.\n",
        encoding="utf-8",
    )
    assert scan_literal_markers(tmp_path) == []
    assert scan_guidance_tokens(tmp_path) == []
