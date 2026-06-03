from __future__ import annotations

import json
from pathlib import Path

from tests.quality_gates.support import ROOT, run_script, skill_package_text

VALIDATOR = "skills/public/issue/scripts/validate_proposal_fields.py"
RESOLVE = "skills/public/issue/scripts/resolve_adapter.py"

PRESENT_VAGUE = """\
Structural pattern: something is sometimes not great and could be better.
Triggering instance(s): it happened once.
Destination: repo-local
"""

BULLET_STYLE = """\
- **Structural pattern:** helpers that commit before evaluating a trigger lose its input.
- **Triggering instance(s):** the release helper on 2026-06-01.
- **Destination:** upstream-harness
"""

MISSING_STRUCTURAL = """\
Triggering instance(s): it happened once.
Destination: repo-local
"""

# Label present but value blank: must be treated as MISSING, not silently steal
# the next line's text as the value (regression guard for the presence contract).
EMPTY_STRUCTURAL_VALUE = """\
Structural pattern:
Triggering instance(s): it happened once.
Destination: repo-local
"""

BAD_DESTINATION = """\
Structural pattern: a real generalized pattern.
Triggering instance(s): the incident.
Destination: somewhere-else
"""


def _run_validator(tmp_path: Path, body: str):
    proposal = tmp_path / "proposal.md"
    proposal.write_text(body, encoding="utf-8")
    return run_script(VALIDATOR, "--file", str(proposal))


def test_present_but_vague_passes(tmp_path: Path) -> None:
    # Presence-only: a vague-but-present pattern must pass. The check never
    # judges whether the generalization is good.
    result = _run_validator(tmp_path, PRESENT_VAGUE)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["missing"] == []
    assert payload["destination"] == "repo-local"


def test_markdown_bullet_style_passes(tmp_path: Path) -> None:
    result = _run_validator(tmp_path, BULLET_STYLE)
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["destination"] == "upstream-harness"


def test_missing_structural_pattern_fails(tmp_path: Path) -> None:
    result = _run_validator(tmp_path, MISSING_STRUCTURAL)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "Structural pattern" in payload["missing"]


def test_empty_value_treated_as_missing(tmp_path: Path) -> None:
    # A blank value must not backtrack across the newline and capture the next
    # line as the field value.
    result = _run_validator(tmp_path, EMPTY_STRUCTURAL_VALUE)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "Structural pattern" in payload["missing"]
    # the stolen-value bug would have set this to "Triggering instance(s):"
    assert "Structural pattern" not in payload["present"]


def test_bad_destination_enum_fails(tmp_path: Path) -> None:
    result = _run_validator(tmp_path, BAD_DESTINATION)
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any("Destination must be one of" in err for err in payload["errors"])


def _write_adapter(tmp_path: Path, harness_upstream: str | None) -> None:
    agents = tmp_path / ".agents"
    agents.mkdir(parents=True, exist_ok=True)
    lines = ["version: 1"]
    if harness_upstream is not None:
        lines.append(f"harness_upstream: {harness_upstream}")
    (agents / "issue-adapter.yaml").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_resolve_destination_collapse_when_current_is_harness(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "corca-ai/charness")
    result = run_script(
        RESOLVE, "--repo-root", str(tmp_path), "resolve-destination", "--current", "corca-ai/charness"
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "collapse"
    assert payload["collapsed"] is True
    assert payload["upstream_target"] == "corca-ai/charness"
    assert payload["local_target"] == "corca-ai/charness"


def test_resolve_destination_consumer_repo(tmp_path: Path) -> None:
    _write_adapter(tmp_path, "corca-ai/charness")
    result = run_script(
        RESOLVE, "--repo-root", str(tmp_path), "resolve-destination", "--current", "corca-ai/consumer-app"
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "consumer"
    assert payload["collapsed"] is False
    assert payload["upstream_target"] == "corca-ai/charness"
    assert payload["local_target"] == "corca-ai/consumer-app"


def test_resolve_destination_unknown_without_pointer(tmp_path: Path) -> None:
    _write_adapter(tmp_path, None)
    result = run_script(
        RESOLVE, "--repo-root", str(tmp_path), "resolve-destination", "--current", "corca-ai/consumer-app"
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["mode"] == "unknown"
    assert payload["ambiguous"] is True
    assert payload["upstream_target"] is None
    assert payload["local_target"] == "corca-ai/consumer-app"


def test_skill_surfaces_reference_the_shared_contract() -> None:
    # A4-lite: each of the three skills points at the shared contract so the
    # axes do not drift across them.
    shared = (ROOT / "skills/shared/references/retro-issue-destination-split.md").read_text(encoding="utf-8")
    assert "Structural pattern:" in shared and "Destination:" in shared
    for skill_id in ("retro", "achieve", "issue"):
        text = skill_package_text(skill_id)
        assert "retro-issue-destination-split.md" in text, skill_id
