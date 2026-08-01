"""Sweep rows S9, S10, S12, S13: what the audited content says about itself is not proof.

Four surfaces, one shape. An artifact's own `Date:` line decided whether its floor ran.
A field name's presence stood in for engaging with the field. An issue reference stood in
for the proof it points at. And a missing `Closeout mode:` line granted `standalone` —
the strongest claim in the taxonomy — by silence.

Each test names the pre-repair verdict it pins against, observed in the parent on
2026-08-01 before any repair was written.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .support import ROOT, _load_script_module

INVENTORY = _load_script_module(
    "validate_inventory_consumption_under_test",
    ROOT / "scripts" / "validate_inventory_consumption.py",
)
DELEGATION = _load_script_module(
    "goal_artifact_closeout_delegation_declaration",
    ROOT / "skills" / "public" / "achieve" / "scripts" / "goal_artifact_closeout_delegation.py",
)

_CITED = "`python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root .`"


def _artifact(body: str, date: str = "2026-08-01") -> str:
    return f"# Quality Review\n\nDate: {date}\n\n## Findings\n\n{body}\n\n## Commands Run\n\n- {_CITED}\n"


def _write_repo(tmp_path: Path, text: str, *, git: bool, commit_date: str | None = None) -> tuple[Path, Path]:
    repo = tmp_path / "repo"
    repo.mkdir()
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"
    (repo / "fields.json").write_text(fields.read_text(encoding="utf-8"), encoding="utf-8")
    artifact = repo / "artifact.md"
    artifact.write_text(text, encoding="utf-8")
    if git:
        env = {
            **{k: v for k, v in __import__("os").environ.items()},
            "GIT_AUTHOR_NAME": "T", "GIT_AUTHOR_EMAIL": "t@e.x",
            "GIT_COMMITTER_NAME": "T", "GIT_COMMITTER_EMAIL": "t@e.x",
        }
        if commit_date:
            env["GIT_COMMITTER_DATE"] = commit_date
            env["GIT_AUTHOR_DATE"] = commit_date
        subprocess.run(["git", "init", "-q", "."], cwd=repo, check=True, env=env)
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True, env=env)
        subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=repo, check=True, env=env)
    return repo, artifact


def _run(repo: Path, artifact: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "validate_inventory_consumption.py"),
            "--repo-root", str(repo),
            "--artifact-path", str(artifact),
            "--consumer-fields-path", str(repo / "fields.json"),
        ],
        capture_output=True, text=True,
    )


# --- S9: a self-declared date must not decide whether the floor runs -----------------


_FAILING_BODY = "- Everything looked fine."


def test_s9_a_backdated_artifact_committed_under_the_contract_is_refused(tmp_path):
    # Pre-repair: exit 0, "predates contract start; skipped" — the same bytes dated today
    # produced six distinct violations. The `Date:` line alone flipped the verdict.
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY, date="2020-01-01"), git=True)

    result = _run(repo, artifact)

    assert result.returncode == 1
    assert "git records its most recent commit as" in result.stderr
    assert "does not exempt itself by declaring an earlier date" in result.stderr


def test_s9_a_genuinely_old_artifact_stays_exempt(tmp_path):
    # The exemption exists for a real reason — rewriting frozen retros to satisfy a later
    # gate is Goodhart. Corroboration keeps it for artifacts git agrees are old.
    repo, artifact = _write_repo(
        tmp_path, _artifact(_FAILING_BODY, date="2020-01-01"), git=True,
        commit_date="2020-01-02T12:00:00 +0000",
    )

    result = _run(repo, artifact)

    assert result.returncode == 0
    assert "Corroborated: last committed 2020-01-02" in result.stdout


def test_s9_an_uncorroboratable_artifact_says_so_instead_of_claiming_proof(tmp_path):
    # A check that could not run is not a check that passed. The pre-existing behavior
    # stands — this is NOT silently upgraded to a refusal — and the output says why.
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY, date="2020-01-01"), git=False)

    result = _run(repo, artifact)

    assert result.returncode == 0
    assert "NOT CORROBORATED" in result.stdout


def test_s9_a_current_artifact_is_unaffected_by_the_corroboration_arm(tmp_path):
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY), git=True)

    result = _run(repo, artifact)

    assert result.returncode == 1
    assert "predates contract start" not in result.stdout


# --- S10: a token's presence must not stand in for engaging with it ------------------


_STUB_BODY = """- I did not read scope_status or finding_status at all.
- Target boundary: n/a
- Ambient repo findings: n/a
- prose review result: n/a
- structural review result: n/a
- prose_review_status: n/a"""


def test_s10_stub_values_no_longer_satisfy_the_floors(tmp_path):
    # Pre-repair: exit 0, "Validated inventory consumption for 1 declared inventory
    # citation(s)". Five `n/a` stubs and an explicit negation satisfied the contract.
    repo, artifact = _write_repo(tmp_path, _artifact(_STUB_BODY), git=True)

    result = _run(repo, artifact)

    assert result.returncode == 1
    assert "declining to engage, spelled as engagement" in result.stderr


_ERGONOMICS_FIELDS = ("scope_status", "finding_status", "prose_review_status")


def test_s10_an_explicit_negation_still_counts_as_engagement(tmp_path):
    """The half that does NOT close, pinned so the closure statement stays honest.

    `I did not read scope_status or finding_status at all.` scores 18 after every declared
    field name is stripped — above the floor. A length floor refuses a stub, not a lie.
    This is sweep row S11's class, and S10 closes NARROWED because of it.
    """
    body = "- I did not read scope_status or finding_status at all."
    repo, artifact = _write_repo(tmp_path, _artifact(body), git=True)

    engaged = [
        field for field in ("scope_status", "finding_status")
        if INVENTORY._engages(body, field, _ERGONOMICS_FIELDS)
    ]

    assert engaged == ["scope_status", "finding_status"]
    # It still fails overall, but on the skill-ergonomics label floors, not on this.
    assert "engages with 0 of its declared" not in _run(repo, artifact).stderr


def test_s10_a_quoted_stub_does_not_clear_the_floor():
    # The first cut counted every surviving character, so `"n/a"` scored exactly 5 — the
    # floor — and the five stub lines passed verbatim once quoted.
    assert INVENTORY.residual_chars(' "n/a"', "") < INVENTORY.MIN_ENGAGEMENT_RESIDUAL_CHARS


def test_s10_a_multi_word_stub_does_not_clear_the_floor():
    # The per-token stub test could never match a phrase, so `not applicable` scored 13.
    for phrase in (" not applicable", " none found", " no findings", " nothing"):
        assert INVENTORY.residual_chars(phrase, "") == 0, phrase


def test_s10_a_bare_enumeration_of_field_names_engages_nothing():
    # Only the queried field was stripped, so a line naming three declared fields scored
    # each against the other two and engaged all three while observing nothing.
    line = "- scope_status finding_status prose_review_status"
    engaged = [f for f in _ERGONOMICS_FIELDS if INVENTORY._engages(line, f, _ERGONOMICS_FIELDS)]

    assert engaged == []


def test_s10_a_real_observation_still_passes(tmp_path):
    body = (
        "- The inventory reported `finding_status=heuristics_present` and "
        "`scope_status=complete` across 41 skills.\n"
        "- Target boundary: the four public skills changed this slice.\n"
        "- Ambient repo findings: two overlong reference files, both pre-existing.\n"
        "- prose review result: clean, no rewrites needed.\n"
        "- structural review result: clean.\n"
        "- prose_review_status reported `not_a_prose_review`, which is the honest value."
    )
    repo, artifact = _write_repo(tmp_path, _artifact(body), git=True)

    assert _run(repo, artifact).returncode == 0


def test_s10_residual_ignores_the_field_name_and_stub_tokens():
    assert INVENTORY.residual_chars("- prose_review_status: n/a", "prose_review_status") == 0
    assert INVENTORY.residual_chars("`heuristic_finding_count=17`, all from", "heuristic_finding_count") == 9


def test_s9_an_uncommitted_artifact_cannot_self_exempt(tmp_path):
    # The arm that matters most and that the first cut missed: `git log -1 -- <path>`
    # exits 0 with EMPTY stdout for a file git has never seen, which collapsed into the
    # same "git cannot answer" state as having no git at all. A freshly authored artifact
    # is in exactly that state when the gate runs before the commit.
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY), git=True)
    backdated = repo / "later.md"
    backdated.write_text(_artifact(_FAILING_BODY, date="2020-01-01"), encoding="utf-8")

    result = _run(repo, backdated)

    assert result.returncode == 1
    assert "has never been committed" in result.stderr


def test_s9_a_dirty_artifact_cannot_self_exempt(tmp_path):
    # git dates the last COMMITTED version; it says nothing about the bytes on disk. An
    # old artifact rewritten in place would otherwise be reported "Corroborated" over
    # content git has never seen — the same rolling-pointer argument that rules out using
    # the first-commit date.
    repo, artifact = _write_repo(
        tmp_path, _artifact(_FAILING_BODY, date="2020-01-01"), git=True,
        commit_date="2020-01-02T12:00:00 +0000",
    )
    (repo / "newer.txt").write_text("later work\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "later"], cwd=repo, check=True)
    artifact.write_text(artifact.read_text(encoding="utf-8") + "\n- edited now.\n", encoding="utf-8")

    result = _run(repo, artifact)

    assert result.returncode == 1
    assert "has uncommitted modifications" in result.stderr


def test_the_validator_reports_a_path_outside_the_repo_instead_of_crashing(tmp_path):
    # Three `relative_to` calls raised ValueError for any path outside the root, so the
    # validator died with a traceback instead of a verdict — a false RED that also made
    # these very tests unwritable.
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY), git=True)
    outside = tmp_path / "elsewhere.md"
    outside.write_text(artifact.read_text(encoding="utf-8"), encoding="utf-8")

    result = _run(repo, outside)

    assert "Traceback" not in result.stderr
    assert result.returncode == 1


# --- S12 / S13: a pointer is not proof, and silence is not a declaration -------------


def test_s12_an_item_that_says_it_is_not_done_is_not_resolved():
    # Pre-repair: `_item_resolved` returned True — `#412` matched, and nothing read the
    # rest of the sentence.
    item = "push to CI and confirm green for PR #412 — NOT DONE, still pending"

    assert DELEGATION._item_resolved(item) is False


def test_s12_a_bare_reference_still_resolves_an_item_that_does_not_deny_itself():
    # The row's claim that a runbook step number or heading anchor also resolves an item
    # is FALSE and was corrected in the sweep: `_ISSUE_REF` matches `#\\d+` and
    # `issue \\d+`, nothing else.
    assert DELEGATION._item_resolved("provider live proof — tracked in issue #501") is True
    assert DELEGATION._item_resolved("instance apply/restart — see runbook step 3") is False


def test_s12_an_explicitly_verified_item_still_resolves():
    assert DELEGATION._item_resolved("provider live proof — verified: readback matched") is True


def test_s13_a_declared_section_with_no_mode_line_is_refused():
    # Pre-repair: mode='standalone', report ok never set, two delegated items ignored.
    body = "## Closeout Delegation\n\nDelegated proof:\n- final push/CI green\n- provider live proof\n"

    parsed = DELEGATION.parse_closeout_delegation(body)
    report: dict = {}
    DELEGATION.apply_closeout_delegation(report, body)

    assert parsed["mode"] == "undeclared"
    assert report["ok"] is False
    # The channel `check_goal_artifact` and `describe_goal_closeout_shape` actually read.
    assert any(
        "absent or blank" in failure
        for failure in report["closeout_delegation"]["failures"]
    )


def test_s13_a_blank_mode_line_is_refused_too():
    body = "## Closeout Delegation\n\nCloseout mode:\nDelegated proof:\n- x\n"
    report: dict = {}

    DELEGATION.apply_closeout_delegation(report, body)

    assert report["ok"] is False


def test_s13_a_goal_with_no_section_at_all_is_still_standalone():
    # The documented default survives: absence of the SECTION means standalone; absence
    # of the MODE inside a present section does not.
    body = "# Goal\n\n## Final Verification\n\nEverything local.\n"
    report: dict = {}

    parsed = DELEGATION.parse_closeout_delegation(body)
    DELEGATION.apply_closeout_delegation(report, body)

    assert parsed["mode"] == "standalone"
    assert parsed["declared"] is False
    assert "ok" not in report


def test_s13_an_explicit_standalone_with_a_trailing_clause_still_passes():
    body = "## Closeout Delegation\n\nCloseout mode: standalone (owns all proof)\n"
    report: dict = {}

    DELEGATION.apply_closeout_delegation(report, body)

    assert "ok" not in report


def test_no_checked_in_goal_artifact_is_refused_by_the_new_delegation_floors():
    # The measurement behind arming: 0 of the checked-in goal artifacts declare a
    # `## Closeout Delegation` section at all, so both floors cost this repo nothing.
    refused = []
    for path in sorted((ROOT / "charness-artifacts" / "goals").glob("*.md")):
        report: dict = {}
        DELEGATION.apply_closeout_delegation(report, path.read_text(encoding="utf-8", errors="replace"))
        if report.get("ok") is False:
            refused.append(path.name)

    assert refused == []


# --- the measurement itself ----------------------------------------------------------
# The 2026-08-01 slice-5 critique (F2) recorded an unverified measurement script as
# "the withdrawn attempts' mistake one level up", and the remedy it set was a test that
# re-runs the recorded probe against today's tree. This mirrors it.


MEASURE = _load_script_module(
    "measure_inventory_consumption_floor_under_test",
    ROOT / "scripts" / "measure_inventory_consumption_floor.py",
)
PROBE = ROOT / "charness-artifacts" / "probe" / "2026-08-01-inventory-consumption-floor.json"


def test_the_recorded_probe_still_matches_todays_tree():
    import json

    recorded = json.loads(PROBE.read_text(encoding="utf-8"))
    live = MEASURE.scan(
        ROOT,
        ROOT / "charness-artifacts" / "quality",
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json",
    )

    assert live["floor"] == recorded["floor"]
    # The numbers other prose actually leans on: D47 cites the 169 denominator and the
    # gate comment cites the label minimum of 7. Pinning only the floor let them drift.
    assert live["artifacts"] == recorded["artifacts"]
    assert live["field_mention_residuals"] == recorded["field_mention_residuals"]
    assert live["label_value_residuals"]["min"] == recorded["label_value_residuals"]["min"]
    assert live["citations_lowered_below_requirement"] == []
    assert live["label_value_residuals"]["below_floor"] == 0
    assert live["exemption_counts"]["REFUSED-uncorroborated"] == 0


def test_the_measurement_refuses_an_empty_corpus(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "quality"
    empty.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        ["measure", "--repo-root", str(tmp_path), "--corpus", str(empty)],
    )

    assert MEASURE.main() == 2
    assert "not a measurement" in capsys.readouterr().err


def test_the_measurement_floor_is_overridable_without_editing_the_gate():
    # The docstring's own rule is that a threshold is defended by a number that can be
    # re-run; the counterfactual floor was not re-runnable until `--floor` existed.
    corpus = ROOT / "charness-artifacts" / "quality"
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"

    low = MEASURE.scan(ROOT, corpus, fields, 5)
    high = MEASURE.scan(ROOT, corpus, fields, 20)

    assert low["floor"] == 5 and high["floor"] == 20
    assert len(high["citations_lowered_below_requirement"]) > len(
        low["citations_lowered_below_requirement"]
    )


def test_the_measurement_reports_a_corpus_outside_the_repo_without_crashing(tmp_path):
    # `relative_to` was the false-RED class this slice removed from the validator, and the
    # measurement shipped in the same slice reproduced it at two call sites.
    corpus = tmp_path / "elsewhere"
    corpus.mkdir()
    (corpus / "a.md").write_text("# Q\n\nDate: 2026-08-01\n\n## Commands Run\n\n- none\n", encoding="utf-8")

    report = MEASURE.scan(
        ROOT, corpus,
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json",
    )

    assert report["artifacts"] == 1


def test_s12_a_resolved_item_is_not_refused_for_a_word_in_its_reason():
    # `skipped:` and `verified:` are resolutions, and their REASONS are exactly where
    # "blocked" / "pending" / "awaiting" appear. Checking the negation first refused them
    # — the same token-for-sentence move S12 names, pointed the other way.
    for item in (
        "live provider proof — skipped: blocked on an upstream outage, tracked in issue #501",
        "pushed-ci — verified: the pending-work queue is now empty",
        "issue-closed — verified: no longer blocked, closed 2026-07-30",
    ):
        assert DELEGATION._item_resolved(item) is True, item


def test_the_gate_reports_an_unparsable_date_line_instead_of_crashing(tmp_path):
    # `Date: 2026-13-45` matches the digit shape and is not a date; raising there was the
    # false-RED class `_display_path` was added to remove.
    repo, artifact = _write_repo(tmp_path, _artifact(_FAILING_BODY, date="2026-13-45"), git=True)

    result = _run(repo, artifact)

    assert "Traceback" not in result.stderr
    assert result.returncode == 1


def test_an_em_dashed_stub_does_not_land_on_the_floor():
    # Only ASCII hyphens were stripped before the phrase test, so `— none found` scored
    # exactly the floor while `none found` scored 0. This repo writes `—` routinely.
    assert INVENTORY.residual_chars(" — none found", "") == 0


def test_a_failed_git_status_does_not_read_as_a_clean_tree(monkeypatch, tmp_path):
    # Every other channel returns `unavailable` on failure; this one fell through to the
    # log branch, so an `index.lock` turned a dirty artifact back into "Corroborated".
    repo, _ = _write_repo(tmp_path, _artifact(_FAILING_BODY), git=True)

    def _fake(root, *args):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 128, "", "fatal: index.lock")
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)

    monkeypatch.setattr(INVENTORY, "_git", _fake)

    assert INVENTORY.commit_state(repo, repo / "artifact.md") == ("unavailable", None)


# --- lines the armed changed-line gate named as uncovered ----------------------------
# Each of these was written because `prepush_focused_changed_line_coverage.py
# --refuse-unestablished` over this goal's own committed range listed the exact
# `path:line` below. That is the flag earning its cost: a green over an unestablished
# range would have proved nothing about any of them.


def test_commit_state_reports_unavailable_when_git_cannot_run(monkeypatch, tmp_path):
    # `validate_inventory_consumption.py:179-180` — the OSError arm.
    def _boom(*args, **kwargs):
        raise OSError("no git binary")

    monkeypatch.setattr(INVENTORY.subprocess, "run", _boom)

    assert INVENTORY.commit_state(tmp_path, tmp_path / "a.md") == ("unavailable", None)


def test_commit_state_survives_an_unparsable_head_date(monkeypatch, tmp_path):
    # `:204-205` — git answered with something that is not a date.
    calls = []

    def _fake(root, *args):
        calls.append(args)
        if args[0] == "log" and "--" not in args:
            return subprocess.CompletedProcess(args, 0, "not-a-date\n", "")
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 0, "2020-01-02\n", "")

    monkeypatch.setattr(INVENTORY, "_git", _fake)

    assert INVENTORY.commit_state(tmp_path, tmp_path / "a.md") == ("dated", INVENTORY.date(2020, 1, 2))


def test_commit_state_reports_unavailable_when_the_path_log_fails(monkeypatch, tmp_path):
    # `:221` — git works for HEAD and refuses the pathspec (a submodule path, say).
    def _fake(root, *args):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 0, "", "")
        if "--" in args:
            return subprocess.CompletedProcess(args, 128, "", "fatal: bad pathspec")
        return subprocess.CompletedProcess(args, 0, "2026-08-01\n", "")

    monkeypatch.setattr(INVENTORY, "_git", _fake)

    assert INVENTORY.commit_state(tmp_path, tmp_path / "a.md") == ("unavailable", None)


def test_commit_state_reports_uncommitted_for_a_clean_but_never_committed_path(monkeypatch, tmp_path):
    # `:225` — the arm round 1 found: git exits 0 with EMPTY stdout for a file it has
    # never seen, which the first cut collapsed into "git cannot answer".
    def _fake(root, *args):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 0, "", "")
        if "--" in args:
            return subprocess.CompletedProcess(args, 0, "", "")
        return subprocess.CompletedProcess(args, 0, "2026-08-01\n", "")

    monkeypatch.setattr(INVENTORY, "_git", _fake)

    assert INVENTORY.commit_state(tmp_path, tmp_path / "a.md") == (
        "uncommitted", INVENTORY.date(2026, 8, 1),
    )


def test_commit_state_reports_unavailable_for_an_unparsable_path_date(monkeypatch, tmp_path):
    # `:228-229`.
    def _fake(root, *args):
        if args[0] == "status":
            return subprocess.CompletedProcess(args, 0, "", "")
        if "--" in args:
            return subprocess.CompletedProcess(args, 0, "garbage\n", "")
        return subprocess.CompletedProcess(args, 0, "2026-08-01\n", "")

    monkeypatch.setattr(INVENTORY, "_git", _fake)

    assert INVENTORY.commit_state(tmp_path, tmp_path / "a.md") == ("unavailable", None)


def test_a_whole_repository_predating_the_contract_is_not_called_corroborated(tmp_path):
    # `:324, :331` — the arm round 2 rewrote: HEAD's date says nothing about a file git
    # has not seen, so this may not print "Corroborated".
    repo, artifact = _write_repo(
        tmp_path, _artifact(_FAILING_BODY, date="2020-01-01"), git=True,
        commit_date="2020-01-02T12:00:00 +0000",
    )
    fresh = repo / "fresh.md"
    fresh.write_text(_artifact(_FAILING_BODY, date="2020-01-01"), encoding="utf-8")

    result = _run(repo, fresh)

    assert result.returncode == 0
    assert "NOT CORROBORATED" in result.stdout
    assert "Corroborated:" not in result.stdout


def test_the_floor_measurement_human_output_and_exit_code(tmp_path, monkeypatch, capsys):
    # `measure_inventory_consumption_floor.py:202-221` — the whole human-render path and
    # the exit expression, none of which the earlier tests reached.
    corpus = tmp_path / "quality"
    corpus.mkdir()
    (corpus / "a.md").write_text(
        _artifact("- The inventory reported `scope_status=complete` across 41 skills."),
        encoding="utf-8",
    )
    measure = _load_script_module(
        "measure_inventory_consumption_floor_cli",
        ROOT / "scripts" / "measure_inventory_consumption_floor.py",
    )
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"
    monkeypatch.setattr("sys.argv", [
        "measure", "--repo-root", str(tmp_path), "--corpus", str(corpus),
        "--consumer-fields-path", str(fields),
    ])

    code = measure.main()
    out = capsys.readouterr().out

    assert code in (0, 1)
    assert "exemption states:" in out
    assert "label-value residuals:" in out
    assert "citations the floor drops below their requirement:" in out


def test_the_floor_measurement_emits_json(tmp_path, monkeypatch, capsys):
    # `:203-204`.
    corpus = tmp_path / "quality"
    corpus.mkdir()
    (corpus / "a.md").write_text(_artifact("- nothing cited."), encoding="utf-8")
    measure = _load_script_module(
        "measure_inventory_consumption_floor_json",
        ROOT / "scripts" / "measure_inventory_consumption_floor.py",
    )
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"
    monkeypatch.setattr("sys.argv", [
        "measure", "--repo-root", str(tmp_path), "--corpus", str(corpus),
        "--consumer-fields-path", str(fields), "--json",
    ])

    assert measure.main() == 0
    assert json.loads(capsys.readouterr().out)["artifacts"] == 1
