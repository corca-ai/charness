"""Tests for the #358 mutation-run proof gate.

`scripts/mutation/check_mutation_run_proof.py` is the gate-shaped upgrade of the
`mutation-dispatch-no-base-sha-false-proof` durable artifact: a deterministic
refusal when a mutation workflow run is cited as proof of a claim its trigger
cannot evaluate. The classifier is pure, so the refusal matrix is pinned
without network or git state; the CLI is exercised over facts and manifests.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import yaml

from .seeding_support import load_module
from .support import ROOT, run_script

_GATE = "scripts/mutation/check_mutation_run_proof.py"


def _load_gate():
    return load_module("check_mutation_run_proof", ROOT / _GATE)


GATE = _load_gate()


# Classifier matrix --------------------------------------------------------
def test_changed_line_claim_refused_for_workflow_dispatch() -> None:
    verdict = GATE.classify_run_proof("changed-line", event="workflow_dispatch")
    assert verdict["provable"] is False
    assert verdict["class_key"] == GATE.CLASS_KEY
    assert "no base_sha" in verdict["reason"]
    assert verdict["supported_proof_paths"] == GATE.SUPPORTED_CHANGED_LINE_PROOF_PATHS


def test_changed_line_claim_refused_for_pull_request_dry_run() -> None:
    verdict = GATE.classify_run_proof("changed-line", event="pull_request")
    assert verdict["provable"] is False
    assert "dry-run" in verdict["reason"]
    # PR dry-run is mode confusion, not the dispatch/no-base-sha class.
    assert "class_key" not in verdict


def test_changed_line_claim_refused_without_base_sha_evidence() -> None:
    # A schedule run can still lack a base (no previous completed run) and an
    # event-less fact set proves nothing: refuse-by-default is the gate shape.
    for facts in ({"event": "schedule"}, {}, {"base_sha": "   "}):
        verdict = GATE.classify_run_proof("changed-line", **facts)
        assert verdict["provable"] is False, facts
        assert verdict["class_key"] == GATE.CLASS_KEY


def test_changed_line_claim_provable_with_real_base_range() -> None:
    for event in ("schedule", None):
        verdict = GATE.classify_run_proof("changed-line", event=event, base_sha="abc123")
        assert verdict["provable"] is True, event
        # base_sha alone establishes that the trigger COULD evaluate the claim,
        # never that it DID over a non-empty scope. The wording used to say
        # "live over a real base..head range", which asserted the second.
        assert verdict["range_established"] is False, event
        assert "COULD run" in verdict["reason"], event

    with_range = GATE.classify_run_proof(
        "changed-line", event="schedule", base_sha="abc123", changed_pool_files=4
    )
    assert with_range["provable"] is True
    assert with_range["range_established"] is True
    assert "live over 4 changed pool file(s)" in with_range["reason"]


def test_an_empty_changed_pool_is_not_changed_line_proof() -> None:
    """A live classifier that evaluated no file proves nothing about the fix.

    `provable` was set on `base_sha` alone, so a run whose range contained no
    pool file was a citable green. Reproduced against a real manifest shape
    before the fix.
    """
    verdict = GATE.classify_run_proof(
        "changed-line", event="schedule", base_sha="abc123", changed_pool_files=0
    )
    assert verdict["provable"] is False
    assert verdict["range_established"] is True
    assert "EMPTY changed pool" in verdict["reason"]
    assert verdict["supported_proof_paths"]


def test_score_claim_provable_for_dispatch_and_schedule_but_not_pr() -> None:
    assert GATE.classify_run_proof("score", event="workflow_dispatch")["provable"] is True
    assert GATE.classify_run_proof("score", event="schedule")["provable"] is True
    assert GATE.classify_run_proof("score", event="pull_request")["provable"] is False


def test_non_success_conclusion_refuses_every_claim() -> None:
    for claim in ("changed-line", "score"):
        verdict = GATE.classify_run_proof(
            claim, event="schedule", base_sha="abc123", conclusion="failure"
        )
        assert verdict["provable"] is False, claim
        assert "not success" in verdict["reason"]


# Manifest fact extraction --------------------------------------------------
def test_manifest_facts_from_json_and_md(tmp_path: Path) -> None:
    json_manifest = tmp_path / "sample.json"
    json_manifest.write_text(json.dumps({"base_sha": "abc123"}), encoding="utf-8")
    # An older manifest shape carries no range key: reported as not-established
    # rather than as an empty range, which would be a refusal it cannot support.
    assert GATE.facts_from_manifest(json_manifest) == {
        "base_sha": "abc123",
        "changed_pool_files": None,
    }

    json_manifest.write_text(json.dumps({"base_sha": None}), encoding="utf-8")
    assert GATE.facts_from_manifest(json_manifest) == {"base_sha": "", "changed_pool_files": None}

    json_manifest.write_text(
        json.dumps({"base_sha": "abc123", "changed_files_before_coverage": ["a.py", "b.py"]}),
        encoding="utf-8",
    )
    assert GATE.facts_from_manifest(json_manifest) == {
        "base_sha": "abc123",
        "changed_pool_files": 2,
    }

    md_manifest = tmp_path / "sample.md"
    md_manifest.write_text(
        "# Mutation Sample\n\n- Base SHA: `abc123`\n- Head SHA: `def456`\n", encoding="utf-8"
    )
    assert GATE.facts_from_manifest(md_manifest) == {
        "base_sha": "abc123",
        "changed_pool_files": None,
    }

    md_manifest.write_text(
        "# Mutation Sample\n\n- Base SHA: `abc123`\n- Changed pool files: 0\n", encoding="utf-8"
    )
    assert GATE.facts_from_manifest(md_manifest) == {"base_sha": "abc123", "changed_pool_files": 0}

    md_manifest.write_text(
        "# Mutation Sample\n\n- Base SHA: `(none)`\n- Head SHA: `def456`\n", encoding="utf-8"
    )
    assert GATE.facts_from_manifest(md_manifest) == {"base_sha": "", "changed_pool_files": None}


def test_manifest_without_base_line_is_an_error(tmp_path: Path) -> None:
    md_manifest = tmp_path / "sample.md"
    md_manifest.write_text("# Mutation Sample\n\n- Seed: `x`\n", encoding="utf-8")
    try:
        GATE.facts_from_manifest(md_manifest)
    except ValueError as error:
        assert "Base SHA" in str(error)
    else:
        raise AssertionError("expected ValueError for a manifest without a Base SHA line")


# Run-facts resolution (gh) --------------------------------------------------
def test_facts_from_run_parses_gh_payload(monkeypatch) -> None:
    def fake_run(command, **_kwargs):
        assert command[:3] == ["gh", "run", "view"]
        assert "--repo" in command and "corca-ai/charness" in command
        return subprocess_result(
            command, 0, json.dumps({"event": "workflow_dispatch", "conclusion": "success"}), ""
        )

    monkeypatch.setattr(GATE, "run_process", fake_run)
    facts = GATE.facts_from_run("123", "corca-ai/charness")
    assert facts == {"event": "workflow_dispatch", "conclusion": "success"}


def test_facts_from_run_omits_repo_flag_and_raises_on_failure(monkeypatch) -> None:
    def fake_run(command, **_kwargs):
        assert "--repo" not in command
        return subprocess_result(command, 1, "", "run not found")

    monkeypatch.setattr(GATE, "run_process", fake_run)
    try:
        GATE.facts_from_run("123", None)
    except RuntimeError as error:
        assert "run not found" in str(error)
    else:
        raise AssertionError("expected RuntimeError when gh run view fails")


def subprocess_result(
    command: list[str], returncode: int, stdout: str, stderr: str
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(command, returncode, stdout, stderr)


def test_main_run_id_branch_refuses_dispatch(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        GATE,
        "facts_from_run",
        lambda run_id, repo: {"event": "workflow_dispatch", "conclusion": "success"},
    )
    exit_code = GATE.main(["--claim", "changed-line", "--run-id", "123"])
    captured = capsys.readouterr()
    assert exit_code == 1
    assert yaml.safe_load(captured.out)["class_key"] == GATE.CLASS_KEY
    assert GATE.CLASS_KEY in captured.err


def test_main_run_id_gh_failure_is_a_diagnostic_exit(monkeypatch, capsys) -> None:
    def boom(run_id, repo):
        raise RuntimeError("gh run view failed: auth")

    monkeypatch.setattr(GATE, "facts_from_run", boom)
    exit_code = GATE.main(["--claim", "score", "--run-id", "123"])
    assert exit_code == 1
    assert "could not resolve run facts" in capsys.readouterr().err


# CLI ------------------------------------------------------------------------
def test_cli_refuses_dispatch_changed_line_claim_with_class_key() -> None:
    result = run_script(_GATE, "--claim", "changed-line", "--event", "workflow_dispatch")
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["provable"] is False
    assert payload["class_key"] == GATE.CLASS_KEY
    assert "REFUSED" in result.stderr
    assert GATE.CLASS_KEY in result.stderr
    assert "Supported changed-line proof paths" in result.stderr


def _manifest_with(changed_pool_files: int, base_sha: str = "abc123") -> Path:
    """A sampler-shaped JSON manifest carrying an explicit range size."""
    import tempfile

    path = Path(tempfile.mkdtemp()) / "sample.json"
    path.write_text(
        json.dumps(
            {
                "base_sha": base_sha,
                "changed_files_before_coverage": [
                    f"scripts/f{i}.py" for i in range(changed_pool_files)
                ],
            }
        ),
        encoding="utf-8",
    )
    return path


def test_cli_accepts_changed_line_claim_with_base_sha_but_says_what_it_did_not_check() -> None:
    """Exit 0 stays -- this is a documented path -- but it must not be SILENT.

    The assertion here used to be `result.stderr == ""`, which pinned the silent
    green: `--base-sha` alone shows the trigger could evaluate the claim and says
    nothing about what was in the range, while exit 0 is the whole signal a
    consumer reads. Whether the exit code itself should change is the contract
    question already deferred for `conclusion_established`
    (charness-artifacts/critique/2026-07-27-empty-scope-family.md F9), so this
    slice makes the gap audible rather than deciding it.
    """
    result = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--base-sha", "abc123"
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["provable"] is True
    assert payload["range_established"] is False
    assert "RANGE CONTENTS are not established" in result.stderr

    # A manifest-established range is the quiet path: nothing unestablished, so
    # nothing to warn about. Without this control the warning could fire always.
    established = run_script(
        _GATE,
        "--claim",
        "changed-line",
        "--event",
        "schedule",
        "--base-sha",
        "abc123",
        "--sample-manifest",
        str(_manifest_with(2)),
    )
    assert established.returncode == 0, established.stderr
    assert "RANGE CONTENTS" not in established.stderr
    # A manifest carries no conclusion by construction, so this path must still
    # say so. Asserting `stderr == ""` here pinned that silence -- a manifest from
    # a RED run reaches this branch identically to one from a green run.
    assert "CONCLUSION is not established" in established.stderr


def test_cli_judges_changed_line_claim_from_manifest(tmp_path: Path) -> None:
    manifest = tmp_path / "sample.md"
    manifest.write_text("- Base SHA: `(none)`\n", encoding="utf-8")
    refused = run_script(_GATE, "--claim", "changed-line", "--sample-manifest", str(manifest))
    assert refused.returncode == 1
    assert yaml.safe_load(refused.stdout)["class_key"] == GATE.CLASS_KEY

    manifest.write_text("- Base SHA: `abc123`\n", encoding="utf-8")
    provable = run_script(_GATE, "--claim", "changed-line", "--sample-manifest", str(manifest))
    assert provable.returncode == 0, provable.stderr


def test_cli_missing_manifest_fails_with_diagnostic(tmp_path: Path) -> None:
    result = run_script(
        _GATE, "--claim", "changed-line", "--sample-manifest", str(tmp_path / "absent.md")
    )
    assert result.returncode == 1
    assert "could not resolve run facts" in result.stderr


def test_the_cli_refuses_an_empty_range_manifest(tmp_path: Path) -> None:
    """End to end: the range fact was on disk the whole time.

    Every manifest the sampler writes already carried the changed-pool count;
    `facts_from_manifest` simply did not read it, so a run over an empty pool
    exited 0 with "changed-line classifier was live over a real base..head
    range" -- a citable green for a run that evaluated no file.
    """
    empty = tmp_path / "sample.json"
    empty.write_text(
        json.dumps(
            {"base_sha": "a" * 40, "changed_files_before_coverage": [], "changed_files": []}
        ),
        encoding="utf-8",
    )
    result = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(empty)
    )
    assert result.returncode == 1, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["provable"] is False
    assert "EMPTY changed pool" in payload["reason"]

    real = tmp_path / "sample2.json"
    real.write_text(
        json.dumps({"base_sha": "a" * 40, "changed_files_before_coverage": ["scripts/x.py"]}),
        encoding="utf-8",
    )
    ok = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(real)
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    assert yaml.safe_load(ok.stdout)["range_established"] is True


def test_the_markdown_manifest_carries_the_same_range_fact(tmp_path: Path) -> None:
    """Both manifest shapes must agree; the sampler writes both every run."""
    md = tmp_path / "sample.md"
    md.write_text(
        "# Mutation Sample\n\n- Base SHA: `" + "a" * 40 + "`\n- Changed pool files: 0\n",
        encoding="utf-8",
    )
    result = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(md)
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "EMPTY changed pool" in yaml.safe_load(result.stdout)["reason"]

    # Positive control on the SAME shape. Without it, a regex that matched the
    # wrong line or truncated the digits to 0 would turn every markdown manifest
    # into a universal false refusal and still pass every assertion above.
    md.write_text(
        "# Mutation Sample\n\n- Base SHA: `" + "a" * 40 + "`\n"
        "- Mutation pool files: 608\n"
        "- Changed pool files: 7\n"
        "- Changed eligible files after coverage/mutation-line filters: 3\n",
        encoding="utf-8",
    )
    ok = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(md)
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr
    payload = yaml.safe_load(ok.stdout)
    assert payload["range_established"] is True
    # 7, not 608 and not 3: the changed-pool line, not its neighbours.
    assert "live over 7 changed pool file(s)" in payload["reason"]


def test_a_manifest_cannot_lend_its_range_to_a_base_it_never_analyzed(tmp_path: Path) -> None:
    """The base comes from the flag and the COUNT from the manifest.

    So a disagreement between them would attribute the manifest's scope to a
    range it never analyzed -- this tool's own named class arriving through the
    back door. Refuse rather than pick one.
    """
    manifest = tmp_path / "sample.json"
    manifest.write_text(
        json.dumps({"base_sha": "b" * 40, "changed_files_before_coverage": ["scripts/x.py"]}),
        encoding="utf-8",
    )
    clash = run_script(
        _GATE,
        "--claim",
        "changed-line",
        "--event",
        "schedule",
        "--base-sha",
        "a" * 40,
        "--sample-manifest",
        str(manifest),
    )
    assert clash.returncode == 1, clash.stdout + clash.stderr
    assert "contradicts the manifest's own base" in clash.stderr

    # Abbreviation is not disagreement: this repo's own advice is
    # `--base-sha origin/main`, and an operator resolving that to a short sha
    # must not be refused for naming the same commit two ways.
    abbreviated = run_script(
        _GATE,
        "--claim",
        "changed-line",
        "--event",
        "schedule",
        "--base-sha",
        "b" * 12,
        "--sample-manifest",
        str(manifest),
    )
    assert abbreviated.returncode == 0, abbreviated.stdout + abbreviated.stderr
    assert yaml.safe_load(abbreviated.stdout)["range_established"] is True

    # A manifest with no base of its own cannot lend its count either.
    baseless = tmp_path / "baseless.json"
    baseless.write_text(
        json.dumps({"base_sha": "", "changed_files_before_coverage": ["scripts/x.py"]}),
        encoding="utf-8",
    )
    borrowed = run_script(
        _GATE,
        "--claim",
        "changed-line",
        "--event",
        "schedule",
        "--base-sha",
        "a" * 40,
        "--sample-manifest",
        str(baseless),
    )
    assert borrowed.returncode == 0, borrowed.stdout + borrowed.stderr
    assert yaml.safe_load(borrowed.stdout)["range_established"] is False
    assert "records no base SHA of its own" in borrowed.stderr


def test_a_gate_report_is_not_a_sample_manifest(tmp_path: Path) -> None:
    """The changed-line ARM's report also carries `base_sha`.

    Fed in here it read as a manifest, so a report that literally said
    `changed_line_proof: "refused"` returned `provable: true` -- a verdict that
    proved nothing accepted as proof of something.
    """
    report = tmp_path / "gate-report.json"
    report.write_text(
        json.dumps(
            {
                "ok": False,
                "blocking": [],
                "refused": True,
                "base_sha": "a" * 40,
                "changed_line_proof": "refused",
                "reason": "dirty worktree",
                "changed_files_before_coverage": ["scripts/x.py"],
            }
        ),
        encoding="utf-8",
    )
    result = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(report)
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "GATE REPORT" in result.stderr

    # Positive control on the same shape: a real sampler manifest carries none of
    # the marker keys and must still be accepted.
    manifest = tmp_path / "sample.json"
    manifest.write_text(
        json.dumps(
            {
                "base_sha": "a" * 40,
                "seed": "x",
                "sample": [],
                "changed_files_before_coverage": ["scripts/x.py"],
                "changed_line_uncovered_changed_files": [],
            }
        ),
        encoding="utf-8",
    )
    ok = run_script(
        _GATE, "--claim", "changed-line", "--event", "schedule", "--sample-manifest", str(manifest)
    )
    assert ok.returncode == 0, ok.stdout + ok.stderr


def test_same_commit_is_abbreviation_tolerant_but_not_credulous() -> None:
    """Prefix tolerance must not become "any two shortish strings match".

    The tool has no git access by design, so it cannot resolve `origin/main`.
    Tolerating abbreviation is the honest half; treating a ref NAME as a prefix
    match would let two genuinely different ranges pass as one.
    """
    same = GATE._same_commit
    assert same("a" * 40, "a" * 40)
    assert same("a" * 7, "a" * 40)  # abbreviated form of the same commit
    assert same("A" * 12, "a" * 40)  # case-insensitive hex
    assert not same("b" * 40, "a" * 40)  # genuinely different commits
    assert not same("a" * 6, "a" * 40)  # too short to identify a commit
    assert not same("origin/main", "a" * 40)  # a ref NAME is not a prefix
    assert not same("main", "a" * 40)
