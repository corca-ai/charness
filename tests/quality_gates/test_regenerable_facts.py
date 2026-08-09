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


def _run(repo: Path, *extra: str) -> tuple[int, str]:
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "--repo-root", str(repo), *extra],
        capture_output=True,
        text=True,
    )
    return completed.returncode, completed.stdout + completed.stderr


def test_an_unconfigured_repo_reports_NO_GATE_rather_than_clean_or_red(tmp_path: Path) -> None:
    # Round 1's blocker was that scanning nothing returned a CLEAN verdict. The
    # first repair failed instead -- which reddened every consumer's first quality
    # run and the runner's own fixture repos. The honest split is by who chose the
    # scope: an unconfigured repo gets "no gate here", stated, not claimed clean.
    repo = tmp_path / "empty"
    repo.mkdir()
    (repo / "NOTES.md").write_text("# nothing in scope\n", encoding="utf-8")

    code, out = _run(repo)

    assert code == 0, out
    assert "NOT CONFIGURED" in out
    assert "no regenerable facts" not in out, "an unscanned repo must not read as clean"


def test_a_DECLARED_scope_that_matches_nothing_is_REFUSED(tmp_path: Path) -> None:
    # The other half: the repo chose these globs and they match nothing, so the
    # config is broken and the gate must say so rather than pass.
    repo = tmp_path / "declared"
    (repo / ".agents").mkdir(parents=True)
    (repo / "NOTES.md").write_text("# prose\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nregenerable_facts:\n  surfaces:\n    - docs/nowhere/*.md\n",
        encoding="utf-8",
    )

    code, out = _run(repo)

    assert code == 1, out
    assert "matched 0 files" in out


def test_an_invalid_adapter_is_REFUSED_rather_than_silently_replaced_by_defaults(tmp_path: Path) -> None:
    # Falling back to defaults would DISCARD the surfaces and exemptions the repo
    # declared and then report clean over a scope nobody chose.
    repo = tmp_path / "bad"
    (repo / ".agents").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("clean prose\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nartifact_class: not-a-real-class\n", encoding="utf-8"
    )

    code, out = _run(repo)

    assert code == 1, out
    assert "adapter is invalid" in out


def test_findings_map_to_exit_one(tmp_path: Path) -> None:
    repo = tmp_path / "dirty"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("The tree holds 12 skills.\n", encoding="utf-8")

    code, out = _run(repo)

    assert code == 1, out
    assert "12 skills" in out


def test_a_clean_repo_in_scope_exits_zero(tmp_path: Path) -> None:
    repo = tmp_path / "clean"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("Recount with `git log --oneline`.\n", encoding="utf-8")

    code, out = _run(repo)

    assert code == 0, out
    assert "no regenerable facts in 1" in out


def test_a_whitespace_only_exemption_reason_is_not_honoured(tmp_path: Path) -> None:
    # `"   "` is truthy, so it silently exempted the file and was not reported.
    repo = tmp_path / "ws"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("The tree holds 12 skills.\n", encoding="utf-8")

    report = lib.scan_repo(
        repo, {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md"], "exemptions": {"AGENTS.md": "   "}}}}
    )

    assert report["unreasoned_exemptions"] == ["AGENTS.md"]
    assert report["exempted"] == []


def test_an_identifier_keeps_its_own_digits() -> None:
    # `#24 issues` is a reference, not an as-of count. The sibling engine in
    # validate_handoff_artifact guards this with a lookbehind; this one did not.
    assert _hits("Tracked as #24 issues go.") == []
    assert _hits("The backlog holds 24 issues.") == ["24 issues"]


def test_the_widened_surfaces_are_pinned_not_merely_configured() -> None:
    # Round 2's blocker: the widening was defended by nothing. Deleting CLAUDE.md,
    # the recursive docs glob, or skill prose from either the defaults or this
    # repo's adapter left all tests green, so the stance in operating-contract.md
    # rested on a config line no executable check defended.
    assert {"AGENTS.md", "CLAUDE.md", "docs/**/*.md"} <= set(lib.DEFAULT_SURFACES)
    assert any(s.endswith("SKILL.md") for s in lib.DEFAULT_SURFACES), "shipped skill prose must be a default surface"
    assert any("references" in s for s in lib.DEFAULT_SURFACES)


def test_this_repos_adapter_actually_covers_its_forward_looking_prose() -> None:
    # The stance names agent prompt files, the docs tree, and shipped skill prose.
    # Assert the CONFIGURED scope reaches all three, so narrowing the adapter back
    # under the contract sentence fails here rather than silently.
    load_adapter = _bootstrap.load_local_skill_module(
        str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "resolve_adapter"
    ).load_adapter
    surfaces, _exemptions = lib.resolve_config(load_adapter(ROOT))
    scanned = {p.relative_to(ROOT).as_posix() for glob in surfaces for p in ROOT.glob(glob) if p.is_file()}

    assert "AGENTS.md" in scanned and "CLAUDE.md" in scanned, "agent prompt files must be in scope"
    assert any(p.startswith("docs/conventions/") for p in scanned), "the docs tree must be in scope"
    assert any(p.endswith("/SKILL.md") for p in scanned), "shipped skill prose must be in scope"
    assert any("/references/" in p for p in scanned)
    # And the seam holds: dated records stay out, by construction rather than exemption.
    assert not any(p.startswith("charness-artifacts/") for p in scanned)


def test_a_comma_grouped_count_without_an_identifier_prefix_is_still_a_count() -> None:
    # Round 2: after the lookbehind landed, the end-in-digit clause became
    # unpinned -- `#24` is blocked by the `#` alone. These cover the clause.
    assert _hits("The corpus holds 1,234 tests.") == ["1,234 tests"]
    assert _hits("Tracked as 24, issue 13 covers the rest.") == []


def test_gitignored_files_are_not_this_repos_prose(tmp_path: Path) -> None:
    # A bare filesystem walk reads node_modules/ and build output -- files no
    # reader treats as the repo's prose and the author cannot fix. Caught by
    # inventory-gitignore-scan-hygiene when this gate was first pushed.
    import subprocess

    repo = tmp_path / "git"
    (repo / "docs").mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / ".gitignore").write_text("docs/vendored.md\n", encoding="utf-8")
    (repo / "AGENTS.md").write_text("clean prose\n", encoding="utf-8")
    (repo / "docs" / "vendored.md").write_text("Pinned at v9.9.9 by a vendor.\n", encoding="utf-8")

    report = lib.scan_repo(repo, {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md", "docs/**/*.md"]}}})

    assert report["findings"] == [], "a gitignored file is not this repo's prose"
    assert report["checked"] == 1

    # And the filter must not swallow tracked files: the same content, tracked, IS a finding.
    (repo / "docs" / "owned.md").write_text("Pinned at v9.9.9 by us.\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    tracked = lib.scan_repo(repo, {"data": {"regenerable_facts": {"surfaces": ["AGENTS.md", "docs/**/*.md"]}}})
    assert [f["path"] for f in tracked["findings"]] == ["docs/owned.md"]


def _validate(block: object) -> tuple[list[str], dict]:
    from runtime_bootstrap import import_repo_module

    qlib = import_repo_module(ROOT / "scripts" / "quality_adapter_lib.py", "scripts.quality_adapter_lib")
    validated: dict = {}
    errors: list[str] = []
    qlib._apply_regenerable_facts({"regenerable_facts": block}, validated, errors, [])
    return errors, validated


def test_the_adapter_validator_refuses_each_malformed_block() -> None:
    # Every refusal branch. Without these the validator's messages are unproven,
    # and a consumer's malformed adapter would surface as a silent default.
    assert _validate("not-a-mapping")[0] == ["regenerable_facts must be a mapping"]
    assert _validate({"surfaces": "docs/*.md"})[0] == [
        "regenerable_facts.surfaces must be a list of glob strings"
    ]
    assert _validate({"surfaces": ["ok.md", 7]})[0] == [
        "regenerable_facts.surfaces must be a list of glob strings"
    ]
    assert _validate({"exemptions": ["a.md"]})[0] == [
        "regenerable_facts.exemptions must be a mapping of path -> reason"
    ]
    errors, _ = _validate({"exemptions": {"b.md": "  ", "a.md": None}})
    assert errors == ["regenerable_facts.exemptions needs a reason for: a.md, b.md"]


def test_the_adapter_validator_accepts_a_well_formed_block() -> None:
    errors, validated = _validate({"surfaces": ["AGENTS.md"], "exemptions": {"a.md": " why  "}})

    assert errors == []
    assert validated["regenerable_facts"] == {"surfaces": ["AGENTS.md"], "exemptions": {"a.md": "why"}}


def test_an_absent_block_leaves_the_key_unset() -> None:
    errors, validated = _validate(None)

    assert errors == []
    assert "regenerable_facts" not in validated
