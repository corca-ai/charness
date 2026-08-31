"""Sweep rows S9 and S10: what the audited content says about itself is not proof.

Two surfaces, one shape. An artifact's own `Date:` line decided whether its floor ran.
A field name's presence stood in for engaging with the field.

Each test names the pre-repair verdict it pins against, observed in the parent on
2026-08-01 before any repair was written.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from .support import ROOT, _load_script_module, run_script

INVENTORY = _load_script_module(
    "validate_inventory_consumption_under_test",
    ROOT / "scripts" / "validate_inventory_consumption.py",
)
_CITED = "`python3 skills/public/quality/scripts/inventory_skill_ergonomics.py --repo-root .`"


def _artifact(body: str, date: str = "2026-08-01") -> str:
    return f"# Quality Review\n\nDate: {date}\n\n## Findings\n\n{body}\n\n## Commands Run\n\n- {_CITED}\n"


def _write_repo(tmp_path: Path, text: str, *, git: bool, commit_date: str | None = None) -> tuple[Path, Path]:
    from .repo_shapes import install_committed_repo

    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"
    files = {
        "fields.json": fields.read_text(encoding="utf-8"),
        "artifact.md": text,
    }
    repo = tmp_path / "repo"
    if git:
        install_committed_repo(repo, files, author_date=commit_date)
    else:
        repo.mkdir()
        (repo / "fields.json").write_text(files["fields.json"], encoding="utf-8")
        (repo / "artifact.md").write_text(text, encoding="utf-8")
    return repo, repo / "artifact.md"


def _run(repo: Path, artifact: Path) -> subprocess.CompletedProcess:
    return run_script(
        "scripts/validate_inventory_consumption.py",
        "--repo-root",
        str(repo),
        "--artifact-path",
        str(artifact),
        "--consumer-fields-path",
        str(repo / "fields.json"),
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


# --- the measurement itself ----------------------------------------------------------
# The dated probe records the 2026-08-01 measurement. The live test below owns
# today's rule-sensitive invariants; valid additions to a growing corpus do not
# rewrite historical evidence merely to satisfy an equality check.


MEASURE = _load_script_module(
    "measure_inventory_consumption_floor_under_test",
    ROOT / "scripts" / "measure_inventory_consumption_floor.py",
)
PROBE = ROOT / "charness-artifacts" / "probe" / "2026-08-01-inventory-consumption-floor.json"


@pytest.mark.slow_corpus
def test_the_current_corpus_preserves_the_recorded_floor_and_live_safety():
    import json

    recorded = json.loads(PROBE.read_text(encoding="utf-8"))
    live = MEASURE.scan(
        ROOT,
        ROOT / "charness-artifacts" / "quality",
        ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json",
    )

    assert MEASURE.safety_defects(live, expected_floor=recorded["floor"]) == []
    assert live["field_mention_residuals"]["count"] > 0
    assert live["label_value_residuals"]["count"] > 0


def test_each_live_inventory_safety_invariant_has_a_negative_control():
    import copy

    report = {
        "floor": 5,
        "artifacts": 1,
        "field_mention_residuals": {"count": 1},
        "label_value_residuals": {"count": 1, "below_floor": 0},
        "citations_lowered_below_requirement": [],
        "exemption_counts": {"REFUSED-uncorroborated": 0},
    }
    cases = (
        (("floor",), 6, "floor-changed"),
        (("artifacts",), 0, "empty-artifact-corpus"),
        (("citations_lowered_below_requirement",), [{"path": "x"}], "required-citation-lowered"),
        (("label_value_residuals", "below_floor"), 1, "label-value-below-floor"),
        (("exemption_counts", "REFUSED-uncorroborated"), 1, "uncorroborated-exemption-refused"),
    )
    for path, value, expected in cases:
        changed = copy.deepcopy(report)
        target = changed
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        defects = MEASURE.safety_defects(changed, expected_floor=5)
        assert expected in defects, expected


def test_the_measurement_refuses_an_empty_corpus(tmp_path, monkeypatch, capsys):
    empty = tmp_path / "quality"
    empty.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        ["measure", "--repo-root", str(tmp_path), "--corpus", str(empty)],
    )

    assert MEASURE.main() == 2
    assert "not a measurement" in capsys.readouterr().err


@pytest.mark.slow_corpus
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


# --- lines the release-final changed-line gate named as uncovered --------------------
# Each of these was written because the release proof listed the exact `path:line`
# below. That is the proof earning its cost: a green over an unestablished range
# would have proved nothing about any of them.


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


def test_the_floor_measurement_payload_and_exit_code(tmp_path, monkeypatch, capsys):
    # `measure_inventory_consumption_floor.py`'s emit path and the exit expression,
    # none of which the earlier tests reached. The prose render is gone, so the
    # sections it labelled are asserted as the payload keys they came from.
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
    payload = yaml.safe_load(capsys.readouterr().out)

    assert code in (0, 1)
    assert payload["artifacts"] == 1
    assert payload["corpus"]
    assert payload["floor"]
    assert "exemption_counts" in payload
    assert "label_value_residuals" in payload
    assert "field_mention_residuals" in payload
    assert "citations_lowered_below_requirement" in payload


def test_the_floor_measurement_emits_a_structured_payload(tmp_path, monkeypatch, capsys):
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
        "--consumer-fields-path", str(fields),
    ])

    assert measure.main() == 0
    assert yaml.safe_load(capsys.readouterr().out)["artifacts"] == 1


def test_the_floor_measurement_names_a_citation_it_lowers(tmp_path, monkeypatch, capsys):
    # `measure_inventory_consumption_floor.py` — the per-entry detail the
    # lowered-citations list carries, which needs a corpus where the floor actually
    # drops a citation below its requirement.
    corpus = tmp_path / "quality"
    corpus.mkdir()
    (corpus / "a.md").write_text(
        _artifact(
            "- `scope_status=complete` and `finding_status=clean` across the run."
        ),
        encoding="utf-8",
    )
    measure = _load_script_module(
        "measure_inventory_consumption_floor_lowered",
        ROOT / "scripts" / "measure_inventory_consumption_floor.py",
    )
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"
    monkeypatch.setattr("sys.argv", [
        "measure", "--repo-root", str(tmp_path), "--corpus", str(corpus),
        "--consumer-fields-path", str(fields), "--floor", "400",
    ])

    assert measure.main() == 1
    payload = yaml.safe_load(capsys.readouterr().out)
    lowered = payload["citations_lowered_below_requirement"]
    assert len(lowered) == 1
    # The entry has to NAME the citation it lowered; a bare count would say a
    # citation was dropped without saying which one.
    assert "inventory_skill_ergonomics.py" in lowered[0]["inventory"]
    assert lowered[0]["lost_to_the_floor"]


def test_the_floor_measurement_runs_as_a_script(tmp_path):
    # the `__main__` guard, reachable only through a subprocess invocation.
    corpus = tmp_path / "quality"
    corpus.mkdir()
    (corpus / "a.md").write_text(_artifact("- nothing cited."), encoding="utf-8")
    fields = ROOT / "skills" / "public" / "quality" / "references" / "inventory-consumer-fields.json"

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "measure_inventory_consumption_floor.py"),
         "--repo-root", str(tmp_path), "--corpus", str(corpus),
         "--consumer-fields-path", str(fields)],
        capture_output=True, text=True,
    )

    assert result.returncode == 0
    assert yaml.safe_load(result.stdout)["artifacts"] == 1
