"""The forward-looking-prose rule, each refusal observed FAILING.

The rule already existed and was broad-armed on the repository's configured
surfaces. These tests pin that arming, the staged commit-boundary advisory, the
record-versus-forward-looking seam, and the two escape hatches the rule
deliberately keeps open (a command in inline code, and a linked artifact) --
because a gate that refuses the replacement it recommends trains avoidance
rather than the habit.
"""

from __future__ import annotations

import re
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from .seeding_support import load_module

ROOT = Path(__file__).resolve().parents[2]
SKILL_SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
_bootstrap = SimpleNamespace(**runpy.run_path(str(ROOT / "scripts" / "skill_runtime_bootstrap.py")))
lib = _bootstrap.load_local_skill_module(str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "regenerable_facts_lib")


def _load_gate():
    """Import the CLI in-process so coverage observes its refusal branches."""
    path = SKILL_SCRIPTS / "check_regenerable_facts.py"
    return load_module("check_regenerable_facts_under_test", path)


gate = _load_gate()


def _hits(text: str) -> list[str]:
    return [literal for _line, literal, _label, _remedy in lib.scan_text(text)]


def _diagnostics_text(payload: dict) -> str:
    """The diagnostics prose as one whitespace-collapsed string.

    Output is YAML now, so a long diagnostic is line-wrapped by the emitter.
    Asserting a sentence against the raw stdout would pass or fail on where the
    wrap landed; the payload list is the stable surface, joined here so a
    sentence can still be asserted whole.
    """
    return re.sub(r"\s+", " ", " ".join(payload["diagnostics"]))


def test_missing_runtime_bootstrap_is_an_explicit_import_error(monkeypatch) -> None:
    real_is_file = Path.is_file

    def hide_runtime_bootstrap(path: Path) -> bool:
        if path.name == "skill_runtime_bootstrap.py":
            return False
        return real_is_file(path)

    monkeypatch.setattr(Path, "is_file", hide_runtime_bootstrap)

    with pytest.raises(ImportError, match="skill_runtime_bootstrap.py not found"):
        gate._load_skill_runtime_bootstrap()


def test_unreasoned_exemptions_carry_the_refusal_in_the_payload() -> None:
    # The refusal used to be a rendered line. It is now `status` plus the same
    # sentence in `diagnostics`, and BOTH have to name the offending files --
    # a bare status word would drop which exemption the author must repair.
    explained = gate.explain(
        {
            "adapter_refusal": None,
            "checked": 1,
            "exempted": [],
            "unreasoned_exemptions": ["docs/a.md", "docs/b.md"],
            "findings": [],
        }
    )

    assert explained["status"] == "unreasoned-exemptions"
    assert explained["diagnostics"] == [
        "regenerable-facts: exemption(s) with no recorded reason: docs/a.md, docs/b.md"
        " -- an unexplained exemption is the claim this rule exists to remove"
    ]


def test_findings_carry_the_unclassified_docs_nonclaim() -> None:
    explained = gate.explain(
        {
            "adapter_refusal": None,
            "checked": 1,
            "exempted": [],
            "unreasoned_exemptions": [],
            "findings": [
                {
                    "path": "AGENTS.md",
                    "line": 7,
                    "label": "transcribed version",
                    "literal": "v4.0.0",
                    "remedy": "carry the recount command",
                }
            ],
            "unclassified_docs": ["docs/history.md"],
        }
    )

    assert explained["status"] == "findings"
    assert explained["diagnostics"][-1] == (
        "NON-CLAIM: 1 docs file(s) were not classified by the conservative defaults; "
        "this failure verdict covers only the named default surfaces."
    )


@pytest.mark.parametrize(
    ("error", "detail"),
    [(StopIteration(), "StopIteration"), (RuntimeError("broken adapter"), "RuntimeError: broken adapter")],
)
def test_adapter_load_errors_are_structured_refusals_in_process(
    monkeypatch, capsys, error: Exception, detail: str
) -> None:
    # The point is unchanged by the YAML migration: an adapter that cannot load
    # surfaces as a NAMED refusal in the payload, not as a traceback and not as a
    # scan over a scope nobody declared.
    def fail_adapter(_repo_root: Path):
        raise error

    monkeypatch.setattr(gate, "load_adapter", fail_adapter)
    monkeypatch.setattr(sys, "argv", ["check_regenerable_facts.py", "--repo-root", str(ROOT)])

    assert gate.main() == 1

    report = yaml.safe_load(capsys.readouterr().out)
    assert report["adapter_refusal"] == (
        f"quality adapter could not be loaded ({detail}); declared surfaces are unknown"
    )
    assert report["checked"] == 0
    assert report["status"] == "adapter-refusal"


def test_git_listing_failure_falls_back_to_the_declared_glob(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    surface = repo / "AGENTS.md"
    surface.write_text("# Demo\n", encoding="utf-8")

    def fail_listing(_repo_root: Path):
        raise OSError("git unavailable")

    monkeypatch.setattr(lib, "visible_repo_files", fail_listing)

    assert lib.visible_matching_files(repo, ("AGENTS.md",)) == [surface]


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
    assert {f["path"] for f in bare["findings"]} == {"AGENTS.md"}

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


def test_arbitrary_docs_trees_are_out_of_scope_by_default() -> None:
    # The default cannot know whether docs/ is a current manual or a dated
    # request/implementation/lessons ledger. A hard gate must not guess.
    assert not any(surface.startswith("charness-artifacts") for surface in lib.DEFAULT_SURFACES)
    assert all("retro" not in surface and "critique" not in surface for surface in lib.DEFAULT_SURFACES)
    assert all(not surface.startswith("docs/") for surface in lib.DEFAULT_SURFACES)


def test_a_historical_docs_record_does_not_hard_fail_an_unconfigured_consumer(tmp_path: Path) -> None:
    repo = tmp_path / "consumer"
    (repo / "docs" / "requests").mkdir(parents=True)
    (repo / "README.md").write_text("# Consumer\n", encoding="utf-8")
    record = repo / "docs" / "requests" / "2026-07-27-readiness.md"
    record.write_text("The decision was taken after 172 tests.\n", encoding="utf-8")

    code, payload = _run(repo)

    assert code == 0, payload
    assert payload["status"] == "not-configured-for-docs"
    assert len(payload["unclassified_docs"]) == 1
    assert "1 docs file(s) remain unclassified" in _diagnostics_text(payload)
    # The dated record's transcribed count is NOT reported as a finding.
    assert payload["findings"] == []
    explicit = lib.scan_repo(
        repo,
        {"data": {"regenerable_facts": {"surfaces": ["docs/**/*.md"], "exemptions": {}}}},
    )
    assert [finding["path"] for finding in explicit["findings"]] == [
        "docs/requests/2026-07-27-readiness.md"
    ]


def test_a_current_docs_claim_cannot_hide_behind_a_clean_default_file(tmp_path: Path) -> None:
    repo = tmp_path / "current-docs"
    (repo / "docs").mkdir(parents=True)
    (repo / "README.md").write_text("# Clean entrypoint\n", encoding="utf-8")
    (repo / "docs" / "status.md").write_text(
        "# Operative state\n\nThe current suite has 145 tests.\n", encoding="utf-8"
    )

    code, payload = _run(repo)

    assert code == 0, payload
    # `not-configured-for-docs`, not `clean`: a clean default file must not buy a
    # clean verdict over a docs tree the gate never classified.
    assert payload["status"] == "not-configured-for-docs"
    assert "no regenerable facts" not in _diagnostics_text(payload)


def test_an_explicit_empty_surface_list_refuses_instead_of_falling_back(tmp_path: Path) -> None:
    repo = tmp_path / "empty-declaration"
    (repo / ".agents").mkdir(parents=True)
    (repo / "README.md").write_text("# Clean entrypoint\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nregenerable_facts:\n  surfaces: []\n", encoding="utf-8"
    )

    code, payload = _run(repo)

    assert code == 1, payload
    assert payload["status"] == "declared-surfaces-matched-nothing"
    assert "declared `regenerable_facts.surfaces` matched 0 files" in _diagnostics_text(payload)


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


def _run(repo: Path, *extra: str) -> tuple[int, dict]:
    """Run the gate and return its exit code with the parsed YAML payload.

    Output is unconditionally YAML since the `--json` removal, and the verdict the
    old rendered lines carried now lives in `status`/`diagnostics` inside that same
    payload. These tests read the payload rather than the raw stdout because the
    emitter line-wraps long diagnostics: a substring assertion would then pass or
    fail on where the wrap landed rather than on what the gate decided.
    """
    import subprocess
    import sys

    completed = subprocess.run(
        [sys.executable, str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "--repo-root", str(repo), *extra],
        capture_output=True,
        text=True,
    )
    payload = yaml.safe_load(completed.stdout)
    assert isinstance(payload, dict), f"stdout was not a YAML mapping: {completed.stdout!r} {completed.stderr!r}"
    return completed.returncode, payload


def _staged_repo(tmp_path: Path, rel: str, text: str) -> Path:
    repo = tmp_path / "staged"
    path = repo / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "--", rel], cwd=repo, check=True)
    return repo


def _run_staged(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SKILL_SCRIPTS / "check_regenerable_facts.py"), "--repo-root", str(repo), "--staged-paths"],
        capture_output=True,
        text=True,
    )


def test_staged_finding_is_an_advisory_with_the_rule_and_exit_zero(tmp_path: Path) -> None:
    repo = _staged_repo(tmp_path, "docs/current.md", "The suite carries 12 tests.\n")

    result = _run_staged(repo)

    assert result.returncode == 0, result.stderr
    assert "ADVISORY:" in result.stdout
    assert "12 tests" in result.stdout
    assert "rule:" in result.stdout
    assert lib.RULE_TEXT in result.stdout


def test_staged_file_outside_the_three_advisory_surfaces_is_silent(tmp_path: Path) -> None:
    repo = _staged_repo(tmp_path, "notes.md", "The suite carries 12 tests.\n")

    result = _run_staged(repo)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_no_staged_advisory_surface_produces_no_verdict(tmp_path: Path) -> None:
    repo = tmp_path / "unstaged"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "current.md").write_text("The suite carries 12 tests.\n", encoding="utf-8")

    result = _run_staged(repo)

    assert result.returncode == 0
    assert result.stdout == ""
    assert result.stderr == ""


def test_a_staged_surface_with_no_index_blob_is_reported_without_blocking(tmp_path: Path) -> None:
    """An unavailable check is announced, never converted into a silent pass.

    The case is a staged DELETION: `git diff --cached --name-only` still names the
    path, and `git show :<path>` has nothing to return. This test used to delete the
    file from the WORKTREE, which stopped being an obstacle once the advisory started
    reading the index -- the right repair for the surface, and it made the old
    premise unreachable rather than the guard unnecessary.
    """
    repo = _staged_repo(tmp_path, "README.md", "The suite carries 12 tests.\n")
    subprocess.run(["git", "commit", "-qm", "seed"], cwd=repo, check=True)
    subprocess.run(["git", "rm", "-q", "README.md"], cwd=repo, check=True)

    result = _run_staged(repo)

    assert result.returncode == 0
    assert "ADVISORY:" in result.stdout
    assert "unavailable" in result.stdout


def test_pre_commit_arms_the_advisory_without_a_silent_drop() -> None:
    hook = (ROOT / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    invocation = (
        'if ! python3 -B skills/public/quality/scripts/check_regenerable_facts.py '
        '--repo-root "$REPO_ROOT" --staged-paths; then'
    )

    assert invocation in hook
    assert hook.index(invocation) < hook.index("python3 -B scripts/check_git_identity.py")
    assert "|| true" not in hook
    assert "|| :" not in hook
    assert "2>/dev/null" not in hook


def test_an_unconfigured_repo_reports_NO_GATE_rather_than_clean_or_red(tmp_path: Path) -> None:
    # Round 1's blocker was that scanning nothing returned a CLEAN verdict. The
    # first repair failed instead -- which reddened every consumer's first quality
    # run and the runner's own fixture repos. The honest split is by who chose the
    # scope: an unconfigured repo gets "no gate here", stated, not claimed clean.
    repo = tmp_path / "empty"
    repo.mkdir()
    (repo / "NOTES.md").write_text("# nothing in scope\n", encoding="utf-8")

    code, payload = _run(repo)

    assert code == 0, payload
    assert payload["status"] == "not-configured"
    assert "NOT CONFIGURED" in _diagnostics_text(payload)
    assert payload["status"] != "clean", "an unscanned repo must not read as clean"
    assert "no regenerable facts" not in _diagnostics_text(payload)


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

    code, payload = _run(repo)

    assert code == 1, payload
    assert payload["status"] == "declared-surfaces-matched-nothing"
    assert "matched 0 files" in _diagnostics_text(payload)


def test_an_invalid_adapter_is_REFUSED_rather_than_silently_replaced_by_defaults(tmp_path: Path) -> None:
    # Falling back to defaults would DISCARD the surfaces and exemptions the repo
    # declared and then report clean over a scope nobody chose.
    repo = tmp_path / "bad"
    (repo / ".agents").mkdir(parents=True)
    (repo / "AGENTS.md").write_text("clean prose\n", encoding="utf-8")
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nartifact_class: not-a-real-class\n", encoding="utf-8"
    )

    code, payload = _run(repo)

    assert code == 1, payload
    assert payload["status"] == "adapter-refusal"
    assert "adapter is invalid" in payload["adapter_refusal"]
    assert payload["surfaces"] == [], "a refused adapter must not report a scope nobody chose"


def test_findings_map_to_exit_one(tmp_path: Path) -> None:
    repo = tmp_path / "dirty"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("The tree holds 12 skills.\n", encoding="utf-8")

    code, payload = _run(repo)

    assert code == 1, payload
    assert payload["status"] == "findings"
    assert [finding["literal"] for finding in payload["findings"]] == ["12 skills"]


def test_a_clean_repo_in_scope_exits_zero(tmp_path: Path) -> None:
    repo = tmp_path / "clean"
    repo.mkdir()
    (repo / "AGENTS.md").write_text("Recount with `git log --oneline`.\n", encoding="utf-8")

    code, payload = _run(repo)

    assert code == 0, payload
    assert payload["status"] == "clean"
    assert payload["checked"] == 1
    assert "no regenerable facts in 1 forward-looking file(s)" in _diagnostics_text(payload)


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
    # `#24 issues` is a reference, not an as-of count. The sibling document
    # validator guards this with a lookbehind; this one did not.
    assert _hits("Tracked as #24 issues go.") == []
    assert _hits("The backlog holds 24 issues.") == ["24 issues"]


def test_the_conservative_default_surfaces_are_pinned_not_merely_configured() -> None:
    # Canonical defaults and the deliberate docs omission are both executable
    # contract. This repo opts its own docs tree in through its adapter below.
    assert {"AGENTS.md", "CLAUDE.md", "README.md"} <= set(lib.DEFAULT_SURFACES)
    assert "docs/**/*.md" not in lib.DEFAULT_SURFACES
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
    assert any(p.startswith("docs/") for p in scanned), "the docs tree must be in scope"
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


def test_an_exemptions_only_block_preserves_absent_surfaces() -> None:
    errors, validated = _validate({"exemptions": {"README.md": "historical fixture"}})

    assert errors == []
    assert validated["regenerable_facts"] == {"exemptions": {"README.md": "historical fixture"}}


def test_an_absent_block_leaves_the_key_unset() -> None:
    errors, validated = _validate(None)

    assert errors == []
    assert "regenerable_facts" not in validated


def test_an_all_exempted_repo_is_not_reported_as_matching_nothing(tmp_path: Path) -> None:
    """Exempted is not unmatched, and the gate must not confuse the two.

    Found by a bounded reviewer and reproduced live: one README at the DEFAULT
    surfaces, exempted with a reason, no `surfaces` declared. The undeclared
    branch was tested first, so the gate reported "no file matched the default
    surfaces" about a file it had matched and read. That is a statement about a
    scope it did look at -- the class this gate exists to refuse, inside the
    gate itself.
    """
    repo = tmp_path / "all-exempted"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\n\nThe suite has 42 tests.\n", encoding="utf-8")
    (repo / ".agents").mkdir()
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nregenerable_facts:\n  exemptions:\n"
        '    README.md: "anti-example prose, deliberately shows the banned shape"\n',
        encoding="utf-8",
    )

    code, payload = _run(repo)

    diagnostics = _diagnostics_text(payload)
    assert payload["status"] == "all-matched-files-exempted"
    assert "every matched file is exempted" in diagnostics
    assert "1 of them" in diagnostics
    assert len(payload["exempted"]) == 1
    assert "no file matched the default surfaces" not in diagnostics, "matched-then-exempted is not unmatched"
    assert payload["status"] != "not-configured"
    assert "NOT CONFIGURED" not in diagnostics
    # Exit code deliberately unchanged: every exemption already carries a
    # required reason, so this is a documented opt-out, not a silent green.
    assert code == 0, payload


def test_the_advisory_reads_the_staged_blob_not_the_worktree(tmp_path: Path) -> None:
    """A partially staged file makes the index and the worktree different documents.

    The advisory is about the COMMIT, so it must read what git will commit. Reading
    the worktree instead let an unstaged repair hide a staged finding, and let a
    finding be reported at a line number that exists in no commit.
    """
    repo = _staged_repo(tmp_path, "docs/current.md", "The suite carries 12 tests.\n")
    # Stage a finding, then repair it ONLY in the worktree.
    (repo / "docs" / "current.md").write_text(
        "The suite size is reported by the test runner.\n", encoding="utf-8"
    )

    result = _run_staged(repo)

    assert result.returncode == 0, result.stderr
    # The staged bytes still carry the number, so the advisory must still fire.
    assert "12 tests" in result.stdout, (
        "an unstaged repair hid a finding that is still in the commit"
    )


def test_a_worktree_only_number_is_not_reported_as_committed(tmp_path: Path) -> None:
    """The inverse: an UNSTAGED number must not be reported as if it were committed."""
    repo = _staged_repo(tmp_path, "docs/current.md", "The suite size is measured.\n")
    (repo / "docs" / "current.md").write_text(
        "The suite size is measured.\nThe suite carries 12 tests.\n", encoding="utf-8"
    )

    result = _run_staged(repo)

    assert result.returncode == 0, result.stderr
    assert "12 tests" not in result.stdout, (
        "reported a finding that exists only in the worktree, not in the commit"
    )
