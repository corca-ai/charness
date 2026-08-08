"""The forward-looking-prose rule, each refusal observed FAILING.

The rule already existed and was armed on exactly one file. These tests pin the
repo-wide arming, the record-versus-forward-looking seam, and the two escape
hatches the rule deliberately keeps open (a command in inline code, and a linked
artifact) -- because a gate that refuses the replacement it recommends trains
avoidance rather than the habit.
"""

from __future__ import annotations

import runpy
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
_bootstrap = SimpleNamespace(**runpy.run_path(str(ROOT / "scripts" / "skill_runtime_bootstrap.py")))
lib = _bootstrap.load_local_skill_module(str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "regenerable_facts_lib")


def _hits(text: str) -> list[str]:
    return [literal for _line, literal, _label, _remedy in lib.scan_text(text)]


def test_a_transcribed_version_is_refused() -> None:
    assert _hits("The installed plugin is v4.0.0 today.") == ["v4.0.0"]


def test_a_transcribed_sha_is_refused() -> None:
    assert _hits("Fixed in ec67291e, which shipped the release.") == ["ec67291e"]


def test_a_transcribed_count_is_refused() -> None:
    assert _hits("The suite carries 26 tests.") == ["26 tests"]


def test_a_command_in_inline_code_is_NOT_refused() -> None:
    # The rule tells the author to carry a command; refusing the command it just
    # recommended is the failure mode that teaches authors to avoid the gate.
    assert _hits("Recount with `git log --oneline -26 origin/main..HEAD`.") == []


def test_a_link_target_is_NOT_refused_but_link_text_is() -> None:
    # A path or URL carrying digits is machinery. Link TEXT is prose a reader
    # believes, so it stays in scope.
    assert _hits("See [the census](../charness-artifacts/audit/2026-08-09-census.md).") == []
    assert _hits("See [the 90 checks](../a.md) for detail.") == ["90 checks"]


def test_a_fenced_block_is_NOT_refused() -> None:
    assert _hits("before\n```\nv1.2.3 and 40 files\n```\nafter") == []


def test_a_number_list_is_not_mistaken_for_a_count() -> None:
    # `#24, issue #13` is a list of identifiers. An earlier pattern swallowed the
    # comma and reported it as an as-of count.
    assert _hits("Tracked as #24, issue #13 covers the rest.") == []


def test_the_rule_reads_surfaces_and_exemptions_from_the_adapter(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("The tree holds 12 skills.\n", encoding="utf-8")
    (repo / "docs" / "notes.md").write_text("Pinned at v1.2.3.\n", encoding="utf-8")

    bare = lib.scan_repo(repo, None)
    assert {f["path"] for f in bare["findings"]} == {"AGENTS.md", "docs/notes.md"}

    adapter = {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md"], "exemptions": {}}}}
    narrowed = lib.scan_repo(repo, adapter)
    assert {f["path"] for f in narrowed["findings"]} == {"AGENTS.md"}, "surfaces must come from the adapter"

    exempted = lib.scan_repo(
        repo,
        {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md"], "exemptions": {"AGENTS.md": "a reason"}}}},
    )
    assert exempted["findings"] == []
    assert exempted["exempted"] == [{"path": "AGENTS.md", "reason": "a reason"}]


def test_an_exemption_without_a_reason_is_reported_not_honoured(tmp_path: Path) -> None:
    # An unexplained exemption is the same unfalsifiable claim the rule removes.
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("The tree holds 12 skills.\n", encoding="utf-8")

    report = lib.scan_repo(
        repo, {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md"], "exemptions": {"AGENTS.md": ""}}}}
    )

    assert report["unreasoned_exemptions"] == ["AGENTS.md"]


def test_dated_record_directories_are_out_of_scope_by_default() -> None:
    # The seam: a number in a retro or critique describes one moment and that is
    # what it is for. They are absent from the default surfaces entirely, rather
    # than exempted, so no repo has to remember to exclude them.
    assert not any(surface.startswith("charness-artifacts") for surface in lib.DEFAULT_SURFACES)
    assert all("retro" not in surface and "critique" not in surface for surface in lib.DEFAULT_SURFACES)


def test_this_repo_is_currently_clean_under_its_own_adapter() -> None:
    # The live arming. If this fails, a forward-looking surface gained a
    # transcribed fact -- carry the command, or link the artifact that measured it.
    load_adapter = _bootstrap.load_local_skill_module(
        str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "resolve_adapter"
    ).load_adapter
    report = lib.scan_repo(ROOT, load_adapter(ROOT))

    assert report["unreasoned_exemptions"] == []
    assert report["findings"] == [], report["findings"][:5]
    assert report["checked"] > 0, "the surfaces glob matched nothing; the gate would be vacuously green"
