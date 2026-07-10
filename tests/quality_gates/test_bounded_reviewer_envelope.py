"""The bounded-reviewer envelope definition stays read-only.

Frontmatter-drift regression for the typed reviewer envelope (rail 2):
`.claude/agents/bounded-reviewer.md` must declare exactly the read-only tool
set. Envelope *binding* is a per-host live-probe claim and is intentionally
not asserted here; recorded probe results live under charness-artifacts/probe/.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ENVELOPE = REPO_ROOT / ".claude" / "agents" / "bounded-reviewer.md"
READ_ONLY_TOOLS = {"Read", "Grep", "Glob"}


def _frontmatter() -> dict[str, str]:
    text = ENVELOPE.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, "bounded-reviewer.md must start with YAML frontmatter"
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def test_envelope_frontmatter_pins_read_only_tool_set() -> None:
    fields = _frontmatter()
    assert fields["name"] == "bounded-reviewer"
    tools = {item.strip() for item in fields["tools"].split(",")}
    assert tools == READ_ONLY_TOOLS


def test_envelope_body_instructs_unbound_self_report() -> None:
    text = ENVELOPE.read_text(encoding="utf-8")
    assert "envelope-unbound" in text
