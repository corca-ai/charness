"""Item-5 slice 2: boy-scout duplicate ratchet gate (dup_ratchet_lib + check_dup_ratchet).

Covers the spec's slice-2 acceptance:

- SC1: a new fixable-eligible family blocks per surface (code via family_id diff,
  doc via signature drift).
- SC2: a family classified `intentional` is ignored.
- SC3: below the healthy floor the boy-scout arm is advisory; the hard arm still fires.
- SC4: escalation fires after K stagnant commits (injected stagnation seam + a real
  git init/--allow-empty fixture for the git seams), resets on an artifact-anchor
  advance, and anchor-not-ancestor degrades to advisory.
- SC5: adapter-driven F/K/paths are honored AND a consumer-style fixture repo (no
  charness internals) blocks on new dup while an absent block stays inert.
- SC6: family_summary() emits family_id (the slice-1 enabler the code arm keys on).

See charness-artifacts/spec/boy-scout-dup-ratchet.md (Slice 2).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from .seeding_support import load_module
from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
CHECK_SCRIPT = SCRIPTS / "check_dup_ratchet.py"


def _load(name: str):
    return load_module(f"{name}_inproc", SCRIPTS / f"{name}.py")


lib = _load("dup_ratchet_lib")
baseline_lib = _load("dup_ratchet_baseline_lib")
gitmod = _load("dup_ratchet_git")
scan = _load("dup_ratchet_scan")
nose_report = _load("nose_report_lib")
fingerprint = _load("nose_fingerprint_lib")
# check_dup_ratchet is loaded in-process (not only via subprocess) so its CLI/run
# branches attribute coverage — the #393 subprocess-only-attribution class. The
# subprocess SC5 tests below still prove the real process contract (argv, exit codes,
# stdout); these in-process drives prove the same branches under coverage.
check = _load("check_dup_ratchet")


def _run_inproc(repo: Path, *cli: str) -> dict:
    """Drive check_dup_ratchet.run() in-process (mirrors main()'s repo_root.resolve())."""
    if "--stagnation" not in cli:
        cli = (*cli, "--stagnation", "0")
    args = check.parse_args(["--repo-root", str(repo), *cli])
    return check.run(args.repo_root.resolve(), args)


def _assert_help_pairs(output: str, expected_pairs: dict[str, str]) -> None:
    """Assert each option's wrapped argparse block contains its own help text."""
    for option, fragment in expected_pairs.items():
        match = re.search(rf"^  {re.escape(option)}\b.*$", output, re.MULTILINE)
        assert match, f"missing help option: {option}"
        next_option = re.search(r"^  --[a-z][a-z-]*\b", output[match.end() :], re.MULTILINE)
        end = match.end() + next_option.start() if next_option else len(output)
        option_block = re.sub(r"\s+", " ", output[match.start() : end])
        assert fragment in option_block, f"missing help for {option}: {fragment}"


def test_check_help_describes_repo_root_and_structured_modes(capsys) -> None:
    with pytest.raises(SystemExit) as excinfo:
        check.parse_args(["--help"])

    assert excinfo.value.code == 0
    _assert_help_pairs(
        capsys.readouterr().out,
        {
            "--repo-root": "Repository root used to resolve adapter and ratchet paths.",
            "--summary": "Emit compact YAML duplicate-ratchet status and actionable findings",
            "--detail": "Emit the full duplicate-ratchet report as YAML",
        },
    )


def test_check_summary_yaml_reports_inert_gate(tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: demo\nlanguage: en\noutput_dir: charness-artifacts/quality\n",
        encoding="utf-8",
    )

    assert check.main(["--repo-root", str(repo), "--summary"]) == 0
    payload = yaml.safe_load(capsys.readouterr().out)
    assert payload["status"] == "inert"
    assert payload["ok"] is True
    # WITHHELD, not empty. An inert gate judged nothing, so publishing
    # `did_not_judge: []` would read as "I judged everything" -- the false
    # reassurance the uncovered-set fields exist to remove. Both sibling gates
    # carry this same assertion (test_docs_graph_gate, test_s6b2_changed_line_gaps);
    # this repair adopted their behaviour and, until a round-2 review said so,
    # not their proof.
    assert "did_not_judge" not in payload, (
        "an inert gate judged nothing; an empty did_not_judge reads as 'I judged everything'"
    )
    assert "scope_coverage" not in payload
    assert "scope_paths" not in payload

def _evaluate(**over):
    base = dict(
        code_family_ids=set(), gate_baseline_ids=set(), doc_drift_signatures=set(),
        intentional_code_ids=set(), intentional_doc_signatures=set(),
        fixable_ceiling=0, floor_F=0, escalation_K=3,
        stagnation=0, anchor="anchorsha", anchor_is_ancestor=True, degraded_reasons=None,
    )
    base.update(over)
    return lib.evaluate(**base)


# --------------------------------------------------------------------------- #
# SC1 — hard arm: a new fixable-eligible family blocks per surface
# --------------------------------------------------------------------------- #
def test_evaluate_new_code_family_hard_blocks() -> None:
    verdict = _evaluate(code_family_ids={"keep", "newfam"}, gate_baseline_ids={"keep"})
    assert verdict["new_code_families"] == ["newfam"]
    assert verdict["hard_block"] is True and verdict["block"] is True
    assert verdict["ok"] is False and verdict["status"] == "hard-block"


def test_evaluate_new_doc_family_hard_blocks() -> None:
    verdict = _evaluate(doc_drift_signatures={"docnew"})
    assert verdict["new_doc_families"] == ["docnew"]
    assert verdict["block"] is True and verdict["status"] == "hard-block"


def test_evaluate_known_family_in_baseline_does_not_block() -> None:
    verdict = _evaluate(code_family_ids={"keep"}, gate_baseline_ids={"keep"})
    assert verdict["new_code_families"] == [] and verdict["block"] is False
    assert verdict["status"] == "clean"


# --------------------------------------------------------------------------- #
# SC2 — intentional families are ignored by the hard arm
# --------------------------------------------------------------------------- #
def test_evaluate_intentional_code_family_ignored() -> None:
    verdict = _evaluate(
        code_family_ids={"keep", "boiler"}, gate_baseline_ids={"keep"},
        intentional_code_ids={"boiler"},
    )
    assert verdict["new_code_families"] == [] and verdict["block"] is False


def test_evaluate_intentional_doc_family_ignored() -> None:
    verdict = _evaluate(doc_drift_signatures={"sig"}, intentional_doc_signatures={"sig"})
    assert verdict["new_doc_families"] == [] and verdict["block"] is False


# --------------------------------------------------------------------------- #
# SC3 — below floor the boy-scout arm is advisory; the hard arm still fires
# --------------------------------------------------------------------------- #
def test_evaluate_below_floor_softens_escalation_even_when_stagnant() -> None:
    verdict = _evaluate(fixable_ceiling=1, floor_F=2, stagnation=999, escalation_K=1)
    assert verdict["above_floor"] is False
    assert verdict["boy_scout_block"] is False and verdict["block"] is False


def test_evaluate_hard_arm_fires_even_below_floor() -> None:
    verdict = _evaluate(
        fixable_ceiling=1, floor_F=2, code_family_ids={"new"}, gate_baseline_ids=set()
    )
    assert verdict["hard_block"] is True and verdict["block"] is True


# --------------------------------------------------------------------------- #
# SC4 — boy-scout escalation ladder (policy half; git seams below)
# --------------------------------------------------------------------------- #
def test_evaluate_escalation_fires_when_stagnant_above_floor() -> None:
    verdict = _evaluate(fixable_ceiling=2, floor_F=0, stagnation=5, escalation_K=3)
    assert verdict["above_floor"] is True
    assert verdict["boy_scout_block"] is True and verdict["block"] is True
    assert verdict["status"] == "boy-scout-escalation-block"


def test_evaluate_escalation_resets_below_K() -> None:
    verdict = _evaluate(fixable_ceiling=2, floor_F=0, stagnation=1, escalation_K=3)
    assert verdict["boy_scout_block"] is False and verdict["block"] is False
    assert verdict["status"] == "boy-scout-advisory"


def test_evaluate_anchor_not_ancestor_degrades_to_advisory() -> None:
    verdict = _evaluate(
        fixable_ceiling=2, floor_F=0, stagnation=5, escalation_K=3,
        anchor=None, anchor_is_ancestor=False,
    )
    assert verdict["block"] is False and verdict["status"] == "anchor-not-ancestor-advisory"


# --------------------------------------------------------------------------- #
# FD8 — degraded inputs are advisory, never a block (even with a "new" family)
# --------------------------------------------------------------------------- #
def test_evaluate_degraded_never_blocks() -> None:
    verdict = _evaluate(
        code_family_ids={"new"}, gate_baseline_ids=set(),
        degraded_reasons=["overlay missing"],
    )
    assert verdict["block"] is False and verdict["status"] == "degraded"
    assert verdict["degraded_reasons"] == ["overlay missing"]


# --------------------------------------------------------------------------- #
# Overlay (dup-review.json) readers. The gate-baseline schema (build/load/validate
# dup-ratchet-baseline.json) itself is covered in test_dup_ratchet_baseline.py
# (dup_ratchet_baseline_lib, split out for the test-file length cap).
# --------------------------------------------------------------------------- #
def test_overlay_intentional_only_collects_intentional() -> None:
    overlay = {"entries": [
        {"surface": "code", "id": "ci", "class": "intentional"},
        {"surface": "doc", "id": "di", "class": "intentional"},
        {"surface": "code", "id": "cf", "class": "fixable"},
        {"surface": "code", "id": "cu", "class": "unreviewed"},
    ]}
    code, doc = lib.overlay_intentional(overlay)
    assert code == {"ci"} and doc == {"di"}


def test_overlay_fixable_ceiling_reads_int_else_zero() -> None:
    assert lib.overlay_fixable_ceiling({"fixable_ceiling": 4}) == 4
    assert lib.overlay_fixable_ceiling({"fixable_ceiling": True}) == 0  # bool is not a count
    assert lib.overlay_fixable_ceiling(None) == 0


# --------------------------------------------------------------------------- #
# classify_reductions pure-function unit coverage lives in
# test_dup_ratchet_reductions.py (test-file length cap split). CLI-level
# reduction/grow/genuine-new/shrink-then-recur end-to-end tests stay below.
# --------------------------------------------------------------------------- #


# --------------------------------------------------------------------------- #
# SC4 (git seams) — real git fixture: resolve_anchor / ancestor / stagnation
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# SC6 — family_summary emits family_id AND propagates the slice-4 content
# fingerprint (so the inventory --json the overlay seed consumes carries it).
# --------------------------------------------------------------------------- #
def test_family_summary_emits_family_id_and_propagates_fingerprint() -> None:
    summary = nose_report.family_summary({"family_id": "abc123", "family_fingerprint": "ff00ff00"})
    assert summary["family_id"] == "abc123"
    assert summary["family_fingerprint"] == "ff00ff00"


# --------------------------------------------------------------------------- #
# SC5 — CLI end-to-end on a consumer-style fixture (no charness internals)
# --------------------------------------------------------------------------- #
def _write_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def _code_inventory(path: Path, family_ids: list[str]) -> Path:
    # Slice 4: the gate keys on the injected `family_fingerprint` (was `family_id`).
    # Slice D (schema v3): each family also carries `family_member_hashes` — these
    # fixtures don't exercise real membership structure, so the fingerprint doubles
    # as its own single synthetic member hash (see `_code_family` for fixtures that
    # need a real multi-hash multiset, e.g. the reduction pre-pass tests).
    return _write_json(path, {
        "status": "findings",
        "families": [{"family_fingerprint": fid, "family_member_hashes": [fid]} for fid in family_ids],
    })


def _code_family(fingerprint: str, member_hashes: list[str]) -> dict:
    """A family fixture with an explicit member-hash multiset (for the reduction
    pre-pass tests, which need real membership structure, not the single-hash
    synthetic shape `_code_inventory` uses for hard-arm identity-only tests)."""
    return {"family_fingerprint": fingerprint, "family_member_hashes": member_hashes}


def _doc_inventory(path: Path, signatures: list[str]) -> Path:
    return _write_json(path, {"status": "ok", "families": [{"signature": sig} for sig in signatures]})


def _consumer_repo(
    tmp_path: Path, *, with_block: bool = True, fixable_ceiling: int = 0,
    intentional_code: tuple[str, ...] = (), baseline_ids: tuple[str, ...] = ("known1",),
    floor_F: int = 0, escalation_K: int = 10, scope_paths: tuple[str, ...] = ("src",),
) -> Path:
    repo = tmp_path / "consumer"
    (repo / ".agents").mkdir(parents=True)
    entries = [
        {"id": fid, "surface": "code", "class": "intentional", "note": "n", "reviewed_at": "d"}
        for fid in intentional_code
    ]
    entries.extend(
        {
            "id": f"fixable-{index}",
            "surface": "code",
            "class": "fixable",
            "note": "n",
            "reviewed_at": "d",
        }
        for index in range(fixable_ceiling)
    )
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1",
        "fixable_ceiling": fixable_ceiling, "entries": entries,
    })
    _write_json(repo / "q" / "dup-ratchet-baseline.json", baseline_lib.build_gate_baseline(
        {fid: [fid] for fid in baseline_ids}
    ))
    if with_block:
        lines = [
            "version: 1", "repo: consumer", "dup_ratchet:", "  enabled: true",
            f"  floor_F: {floor_F}", f"  escalation_K: {escalation_K}",
        ]
        if scope_paths:
            lines.append("  scope_paths:")
            lines.extend(f"    - {path}" for path in scope_paths)
        else:
            lines.append("  scope_paths: []")
        lines.extend([
            "  review_artifact_path: q/dup-review.json",
            "  gate_baseline_path: q/dup-ratchet-baseline.json", "",
        ])
        adapter = "\n".join(lines)
    else:
        adapter = "version: 1\nrepo: consumer\n"
    (repo / ".agents" / "quality-adapter.yaml").write_text(adapter, encoding="utf-8")
    return repo


def _run_gate(repo: Path, tmp_path: Path, *, code_ids: list[str], doc_sigs: list[str] | None = None,
              extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    code_json = _code_inventory(tmp_path / "code.json", code_ids)
    doc_json = _doc_inventory(tmp_path / "doc.json", doc_sigs or [])
    extra_args = list(extra or [])
    if "--stagnation" not in extra_args:
        extra_args.extend(("--stagnation", "0"))
    return run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--detail", *extra_args, cwd=ROOT,
    )


def _verdict(result: subprocess.CompletedProcess[str]) -> dict:
    return yaml.safe_load(result.stdout)


def test_cli_consumer_new_code_family_blocks(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    result = _run_gate(repo, tmp_path, code_ids=["known1", "BRANDNEW"])
    assert result.returncode == 1, result.stdout + result.stderr
    assert _verdict(result)["status"] == "hard-block"


def test_cli_consumer_new_doc_family_blocks(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    result = _run_gate(repo, tmp_path, code_ids=["known1"], doc_sigs=["DOCNEW"])
    assert result.returncode == 1, result.stdout + result.stderr
    assert _verdict(result)["new_doc_families"] == ["DOCNEW"]


def test_cli_consumer_intentional_family_not_blocked(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("BRANDNEW",))
    result = _run_gate(repo, tmp_path, code_ids=["known1", "BRANDNEW"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _verdict(result)["status"] == "clean"


def test_cli_absent_block_is_inert_even_with_new_dup(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, with_block=False)
    result = _run_gate(repo, tmp_path, code_ids=["known1", "BRANDNEW"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _verdict(result)["status"] == "inert"


def test_cli_degraded_when_gate_baseline_missing(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").unlink()
    result = _run_gate(repo, tmp_path, code_ids=["known1", "BRANDNEW"])
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["status"] == "degraded"
    assert verdict["lineage_approval_eligible"] is False


def test_cli_degraded_when_review_overlay_missing_is_not_lineage_approval(
    tmp_path: Path,
) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-review.json").unlink()
    result = _run_gate(repo, tmp_path, code_ids=["known1"])
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["status"] == "degraded"
    assert verdict["lineage_readiness"]["status"] == "ready"
    assert verdict["lineage_approval_eligible"] is False
    assert any("degraded inputs" in message for message in verdict["messages"])


def test_cli_lineage_unavailability_is_not_approval_eligible(tmp_path: Path) -> None:
    """The real duplicate verdict refuses approval when lineage paths are absent."""
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), intentional_code=("known1",))
    result = _run_gate(repo, tmp_path, code_ids=["known1"])
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["lineage_readiness"]["status"] == "unavailable"
    assert verdict["lineage_approval_eligible"] is False
    assert any("REFUSAL (lineage)" in message for message in verdict["messages"])


# SC5 — adapter-driven F / K honored end-to-end
def test_cli_below_floor_advisory_honors_adapter_floor(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, fixable_ceiling=2, floor_F=3, escalation_K=1)
    result = _run_gate(repo, tmp_path, code_ids=["known1"], extra=["--stagnation", "999"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _verdict(result)["above_floor"] is False


def test_cli_escalation_block_honors_adapter_K(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, fixable_ceiling=2, floor_F=1, escalation_K=3)
    result = _run_gate(repo, tmp_path, code_ids=["known1"], extra=["--stagnation", "5"])
    assert result.returncode == 1, result.stdout + result.stderr
    assert _verdict(result)["status"] == "boy-scout-escalation-block"


def test_cli_escalation_resets_below_adapter_K(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, fixable_ceiling=2, floor_F=1, escalation_K=3)
    result = _run_gate(repo, tmp_path, code_ids=["known1"], extra=["--stagnation", "1"])
    assert result.returncode == 0, result.stdout + result.stderr
    assert _verdict(result)["status"] == "boy-scout-advisory"


@pytest.mark.skipif(
    shutil.which("nose") is None and not os.environ.get("NOSE_BIN"),
    reason="nose binary required for the real-scan empty-families guard",
)
def test_cli_empty_real_scan_with_nonempty_baseline_degrades(tmp_path: Path) -> None:
    # A real (non-injected) code scan that yields 0 families against a non-empty gate
    # baseline must degrade to advisory, never read as a silent clean pass (the
    # broken-scan / misconfigured-scope_paths false-green guard).
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    src = repo / "src"
    src.mkdir()
    (src / "only.py").write_text("def unique_fn():\n    return 42\n", encoding="utf-8")
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--doc-inventory", str(doc_json), "--detail", cwd=ROOT,
        real_process=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["status"] == "degraded"
    assert any("0 families" in reason for reason in verdict["degraded_reasons"])


@pytest.mark.skipif(
    shutil.which("nose") is None and not os.environ.get("NOSE_BIN"),
    reason="nose binary required for the family_id offset-stability characterization",
)
def test_real_nose_family_id_rotates_on_member_line_shift(tmp_path: Path) -> None:
    # Characterization for the family_id offset-rotation issue (issue 395): the gate
    # keys code newness on nose's `family_id`, which the docs once claimed was "stable
    # across sibling churn". It is NOT — the family id folds each member's LINE OFFSET,
    # so inserting lines ABOVE an unchanged duplicated span rotates the whole family id
    # even though no duplication changed and a sibling copy is byte-identical. This locks
    # that reality (the basis for the documented re-baseline-on-member-edit workflow and
    # the deferred id-rotation affordance in references/dup-ratchet.md). If a future nose
    # makes family_id position-independent this assertion flips, signalling a docs revisit.
    nose_bin = os.environ.get("NOSE_BIN") or "nose"
    scope = tmp_path / "scope"
    scope.mkdir()
    func = (
        "def compute_widget_summary(items, threshold):\n"
        "    total = 0\n"
        "    kept = []\n"
        "    for item in items:\n"
        '        value = item.get("value", 0)\n'
        "        if value is None:\n"
        "            continue\n"
        "        if value >= threshold:\n"
        "            kept.append(item)\n"
        "            total += value\n"
        "    average = total / len(kept) if kept else 0\n"
        '    return {"total": total, "kept": kept, "count": len(kept), "average": average}\n'
    )
    alpha = scope / "alpha.py"
    beta = scope / "beta.py"
    alpha.write_text("import os\n\n\n" + func, encoding="utf-8")
    beta.write_text("import sys\n\n\n" + func, encoding="utf-8")

    def family_ids() -> set[str]:
        result = subprocess.run(
            [nose_bin, "query", str(scope), "--format", "json",
             "--min-size", "24", "--min-members", "2"],
            capture_output=True, text=True, check=False,
        )
        assert result.returncode == 0, result.stderr
        return {fam["id"] for fam in yaml.safe_load(result.stdout).get("families", [])}

    before = family_ids()
    assert len(before) == 1, f"expected exactly one clone family, got {before}"

    beta_before = beta.read_text(encoding="utf-8")
    # Pure line-shift: prepend comment lines to alpha.py. alpha's function body is
    # byte-identical, beta.py is untouched, and no duplication is added or removed.
    alpha.write_text("# shift\n" * 5 + alpha.read_text(encoding="utf-8"), encoding="utf-8")
    assert beta.read_text(encoding="utf-8") == beta_before  # the sibling copy is unchanged

    after = family_ids()
    assert len(after) == 1, f"expected one clone family after the shift, got {after}"
    assert before != after, (
        "family_id did NOT rotate on a pure line-shift; nose may have become "
        "position-independent. Revisit the dup-ratchet stability caveat and the "
        "deferred id-rotation affordance."
    )


_CLONE_FUNC = (
    "def compute_widget_summary(items, threshold):\n"
    "    total = 0\n"
    "    kept = []\n"
    "    for item in items:\n"
    '        value = item.get("value", 0)\n'
    "        if value is None:\n"
    "            continue\n"
    "        if value >= threshold:\n"
    "            kept.append(item)\n"
    "            total += value\n"
    "    average = total / len(kept) if kept else 0\n"
    '    return {"total": total, "kept": kept, "count": len(kept), "average": average}\n'
)


def _clone_scope(tmp_path: Path) -> Path:
    scope = tmp_path / "scope"
    scope.mkdir()
    (scope / "alpha.py").write_text("import os\n\n\n" + _CLONE_FUNC, encoding="utf-8")
    (scope / "beta.py").write_text("import sys\n\n\n" + _CLONE_FUNC, encoding="utf-8")
    return scope


def _single_family_fingerprints(nose_bin: str, repo_root: Path) -> set:
    """Gate-side content fingerprints of the lone clone family under repo_root/scope."""
    result = subprocess.run(
        [nose_bin, "query", "scope", "--format", "json", "--min-size", "24", "--min-members", "2"],
        cwd=repo_root, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    families = yaml.safe_load(result.stdout).get("families", [])
    assert len(families) == 1, f"expected exactly one clone family, got {len(families)}"
    return {fingerprint.family_content_fingerprint(fam, repo_root) for fam in families}


@pytest.mark.skipif(
    shutil.which("nose") is None and not os.environ.get("NOSE_BIN"),
    reason="nose binary required for the gate fingerprint stability characterization",
)
def test_gate_content_fingerprint_stable_on_member_line_shift(tmp_path: Path) -> None:
    # SC1, the D30 fix: where test_real_nose_family_id_rotates... proves nose's id ROTATES
    # on a pure line-shift, this proves the GATE's content fingerprint is STABLE across the
    # same shift -> no false hard-block. The gate keys on this, not nose's id.
    nose_bin = os.environ.get("NOSE_BIN") or "nose"
    scope = _clone_scope(tmp_path)
    before = _single_family_fingerprints(nose_bin, tmp_path)
    assert None not in before  # every member span readable
    alpha = scope / "alpha.py"
    alpha.write_text("# shift\n" * 5 + alpha.read_text(encoding="utf-8"), encoding="utf-8")  # pure line-shift
    after = _single_family_fingerprints(nose_bin, tmp_path)
    assert before == after, "content fingerprint rotated on a pure line-shift (the D30 false-block)"


@pytest.mark.skipif(
    shutil.which("nose") is None and not os.environ.get("NOSE_BIN"),
    reason="nose binary required for the gate fingerprint content-sensitivity characterization",
)
def test_gate_content_fingerprint_changes_on_span_content_change(tmp_path: Path) -> None:
    # SC2: a genuine change to the duplicated span content rotates the fingerprint, so real
    # new/changed duplication is still caught (no false-negative — D30's blocking concern).
    nose_bin = os.environ.get("NOSE_BIN") or "nose"
    scope = _clone_scope(tmp_path)
    before = _single_family_fingerprints(nose_bin, tmp_path)
    for name in ("alpha.py", "beta.py"):  # change both copies so they stay one family
        path = scope / name
        path.write_text(path.read_text(encoding="utf-8").replace("total = 0", "total = 1"), encoding="utf-8")
    after = _single_family_fingerprints(nose_bin, tmp_path)
    assert before != after, "content fingerprint did NOT change on a real span edit (false-negative)"


def test_cli_write_baseline_from_injected_inventory(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    code_json = _code_inventory(tmp_path / "code.json", ["a", "b", "a"])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo), "--code-inventory", str(code_json),
        "--write-baseline", "--detail", cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"a", "b"}
    assert written["fingerprint_algo_version"] == fingerprint.FINGERPRINT_ALGO_VERSION
    assert baseline_lib.validate_gate_baseline(written) == []


# --------------------------------------------------------------------------- #
# Slice 1 hardening — F (scope_paths-empty), I (baseline integrity), C
# (--write-baseline delta guardrail). Driven in-process so the new branches in
# check_dup_ratchet attribute coverage; behaviour asserted, not literal id counts.
# --------------------------------------------------------------------------- #
def test_inproc_F_enabled_empty_scope_paths_degrades_whole_gate(tmp_path: Path) -> None:
    # F: enabled + empty scope_paths -> advisory degrade, even with a NEW family that
    # would otherwise hard-block (FD8 whole-gate degrade: never a false block, never
    # a silent clean pass).
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",), scope_paths=())
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "BRANDNEW"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["ok"] is True and report["block"] is False
    assert report["status"] == "degraded"
    assert any("scope_paths is empty" in reason for reason in report["degraded_reasons"])


def test_inproc_I_schema_invalid_baseline_degrades_advisory(tmp_path: Path) -> None:
    # I: a present, loadable baseline (valid id list) with a wrong schemaVersion still
    # surfaces an integrity advisory via validate_gate_baseline — never blocks.
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps({"schemaVersion": "WRONG",
                    "code_families": [{"fingerprint": "known1", "member_hashes": ["known1"]}]}),
        encoding="utf-8",
    )
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "BRANDNEW"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "degraded" and report["block"] is False
    assert any("integrity" in r and "schemaVersion" in r for r in report["degraded_reasons"])


def test_inproc_C_large_delta_without_confirm_refuses_and_preserves_baseline(tmp_path: Path) -> None:
    # C: a large re-baseline delta refuses (exit-1 worthy) without --confirm-baseline-delta
    # and leaves the committed baseline untouched. Never touches the gate evaluate path.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "old2", "old3"))
    code_json = _code_inventory(tmp_path / "code.json", ["n1", "n2", "n3", "n4"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline",
                         "--baseline-delta-threshold", "2")
    assert report["ok"] is False and report["status"] == "baseline-delta-unconfirmed"
    assert report["baseline_delta"] == {"added": 4, "removed": 3, "threshold": 2}
    preserved = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(preserved) == {"old1", "old2", "old3"}  # unchanged


def test_inproc_C_large_delta_with_confirm_rebaselines(tmp_path: Path) -> None:
    # C: the deliberate-re-baseline case (e.g. a nose version swing) proceeds with the
    # named confirm flag.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "old2", "old3"))
    code_json = _code_inventory(tmp_path / "code.json", ["n1", "n2", "n3", "n4"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline",
                         "--baseline-delta-threshold", "2", "--confirm-baseline-delta")
    assert report["ok"] is True and report["status"] == "baseline-written"
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"n1", "n2", "n3", "n4"}


# --------------------------------------------------------------------------- #
# Slice 2 — in-process coverage for the remaining check_dup_ratchet CLI branches
# (the #393 subprocess-only-attribution class). These drive main()/run() branches
# the subprocess SC5 tests above exercise only out-of-process; the subprocess tests
# still own the real process contract (argv, exit code, stdout), so this is
# complementary attribution, not a re-test of the same assertion.
# --------------------------------------------------------------------------- #
def test_inproc_main_json_inert_exit_0(tmp_path: Path, capsys) -> None:
    repo = _consumer_repo(tmp_path, with_block=False)
    code_json = _code_inventory(tmp_path / "code.json", ["x"])
    rc = check.main(["--repo-root", str(repo), "--code-inventory", str(code_json), "--detail"])
    payload = yaml.safe_load(capsys.readouterr().out)
    assert rc == 0 and payload["status"] == "inert"


def test_inproc_main_text_hard_block_exit_1(tmp_path: Path, capsys) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "NEWFAM"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    rc = check.main(["--repo-root", str(repo), "--code-inventory", str(code_json),
                     "--doc-inventory", str(doc_json)])  # text mode (no --json)
    out = capsys.readouterr().out
    assert rc == 1 and "FAIL (hard arm)" in out


def test_inproc_run_adapter_invalid_fails_closed(tmp_path: Path) -> None:
    repo = tmp_path / "bad"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "version: 1\nrepo: bad\ndup_ratchet:\n  enabled: notabool\n", encoding="utf-8")
    report = _run_inproc(repo)
    assert report["ok"] is False and report["status"] == "adapter-invalid"
    assert report["adapter_errors"]


def test_inproc_write_baseline_failed_on_unreadable_inventory(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    report = _run_inproc(repo, "--code-inventory", str(tmp_path / "absent.json"), "--write-baseline")
    assert report["ok"] is False and report["status"] == "write-baseline-failed"


def test_inproc_missing_overlay_and_baseline_degrade(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-review.json").unlink()
    (repo / "q" / "dup-ratchet-baseline.json").unlink()
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "NEW"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "degraded" and report["block"] is False
    reasons = " ".join(report["degraded_reasons"])
    assert "overlay missing" in reasons and "gate baseline missing" in reasons


# --------------------------------------------------------------------------- #
# Injected-payload field reads (scanner tool_version stamp, issue #391; plus the
# self-reported `status` the code arm now refuses on): the live version threads through the
# code-family helpers, stamps the baseline on write, and surfaces a skew WARNING on
# evaluate WITHOUT degrading the block. In-process so coverage attributes the lines
# (the #393 subprocess-only class — the injected-inventory branch carries the version).
# --------------------------------------------------------------------------- #
def test_payload_string_field_reads_or_empty() -> None:
    assert scan.payload_string_field('{"tool_version": "0.14.0"}', "tool_version") == "0.14.0"
    assert scan.payload_string_field('{"families": []}', "tool_version") == ""  # unstamped
    assert scan.payload_string_field("", "tool_version") == ""
    assert scan.payload_string_field(None, "tool_version") == ""
    assert scan.payload_string_field("not json{", "tool_version") == ""
    assert scan.payload_string_field('{"tool_version": 14}', "tool_version") == ""  # non-string
    assert scan.payload_string_field("[1, 2]", "tool_version") == ""  # not a dict


def test_scan_code_members_threads_live_version(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scan._inventory, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        scan._nose_report, "collect_families",
        lambda *_a, **_k: {
            "status": "findings",
            "families": [{"family_fingerprint": "x", "family_member_hashes": ["x1"]}],
            "tool_version": "0.14.0",
        },
    )
    members, spans, reason, version = scan.scan_code_members(tmp_path, ["scripts"])
    assert members == {"x": ["x1"]} and reason is None and version == "0.14.0"


def test_scan_code_members_unreadable_member_degrades_whole_gate(monkeypatch, tmp_path: Path) -> None:
    # A family with no stamped fingerprint/member hashes (unreadable member span)
    # degrades the WHOLE scan to a reason -> advisory (FD8), never a dropped family.
    monkeypatch.setattr(scan._inventory, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        scan._nose_report, "collect_families",
        lambda *_a, **_k: {
            "status": "findings",
            "families": [{"family_fingerprint": "x", "family_member_hashes": ["x1"]}, {"family_id": "noFP"}],
            "tool_version": "0.15.0",
        },
    )
    members, spans, reason, version = scan.scan_code_members(tmp_path, ["scripts"])
    assert members == {} and "unreadable member span" in reason and version == "0.15.0"


def test_scan_code_members_error_and_missing_nose_carry_version(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(scan._inventory, "resolve_nose_bin", lambda: "nose")
    monkeypatch.setattr(
        scan._nose_report, "collect_families",
        lambda *_a, **_k: {"status": "error", "stderr": "boom", "families": [], "tool_version": "0.14.0"},
    )
    members, spans, reason, version = scan.scan_code_members(tmp_path, ["scripts"])
    assert members == {} and "boom" in reason and version == "0.14.0"  # error still carries the live version
    monkeypatch.setattr(scan._inventory, "resolve_nose_bin", lambda: None)
    members, spans, reason, version = scan.scan_code_members(tmp_path, [])
    assert members == {} and "nose binary not found" in reason and version == ""


def test_code_family_members_injected_threads_version_and_unreadable(tmp_path: Path) -> None:
    inv_path = tmp_path / "c.json"
    inv_path.write_text(
        json.dumps({
            "families": [{"family_fingerprint": "a", "family_member_hashes": ["a1"]}],
            "tool_version": "0.14.0",
        }), encoding="utf-8",
    )
    args = check.parse_args(["--code-inventory", str(inv_path)])
    members, spans, reason, version = scan.code_family_members(args, tmp_path, [])
    assert members == {"a": ["a1"]} and reason is None and version == "0.14.0"
    missing = check.parse_args(["--code-inventory", str(tmp_path / "absent.json")])
    members, spans, reason, version = scan.code_family_members(missing, tmp_path, [])
    assert members == {} and "unreadable" in reason and version == ""


def test_code_family_members_injected_computes_hashes_from_locations(tmp_path: Path) -> None:
    # An injected family carrying `family_fingerprint` + `locations` but WITHOUT
    # `family_member_hashes` gets its member hashes computed from the real span
    # (mirrors the fingerprint-from-locations fallback one line above it).
    (tmp_path / "a.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    inv_path = tmp_path / "c.json"
    inv_path.write_text(
        json.dumps({"families": [{
            "family_fingerprint": "known_fp",
            "locations": [{"file": "a.py", "start": 1, "end": 2}],
        }]}),
        encoding="utf-8",
    )
    args = check.parse_args(["--code-inventory", str(inv_path)])
    members, spans, reason, version = scan.code_family_members(args, tmp_path, [])
    assert reason is None
    expected_hash = fingerprint.member_fingerprint(tmp_path, "a.py", 1, 2)
    assert members == {"known_fp": [expected_hash]}


def test_inproc_write_baseline_stamps_tool_and_algo_version(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    code_json = _write_json(
        tmp_path / "code.json",
        {"families": [_code_family("a", ["a"]), _code_family("b", ["b"])], "tool_version": "0.14.0"},
    )
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline")
    assert report["status"] == "baseline-written" and report["tool_version"] == "0.14.0"
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert written["tool_version"] == "0.14.0"
    assert written["fingerprint_algo_version"] == fingerprint.FINGERPRINT_ALGO_VERSION
    assert baseline_lib.validate_gate_baseline(written) == []


def test_inproc_version_skew_warns_without_degrading_block(tmp_path: Path) -> None:
    # Baseline minted under nose 0.13.0; the live (injected) scan is 0.14.0 and the family
    # set drifted -> "new" families. The gate STILL hard-blocks (never degrades on skew),
    # but surfaces the skew so the operator re-baselines.
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps(baseline_lib.build_gate_baseline({"known1": ["known1"]}, tool_version="0.13.0")),
        encoding="utf-8",
    )
    code_json = _write_json(
        tmp_path / "code.json",
        {"status": "findings", "tool_version": "0.14.0",
         "families": [_code_family("ROT1", ["ROT1"]), _code_family("ROT2", ["ROT2"])]},
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "hard-block" and report["block"] is True  # never degraded
    assert report["version_skew"] and "0.13.0" in report["version_skew"] and "0.14.0" in report["version_skew"]
    assert any("scanner-version skew" in m for m in report["messages"])


def test_inproc_no_version_skew_on_legacy_unstamped_baseline(tmp_path: Path) -> None:
    # The _consumer_repo baseline carries NO tool_version (legacy). A live 0.14.0 scan
    # must NOT warn (a missing stamp is "unknown", not a mismatch) and must not block.
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    code_json = _write_json(
        tmp_path / "code.json",
        {"status": "findings", "tool_version": "0.14.0", "families": [{"family_fingerprint": "known1"}]},
    )
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    # clean because 'known1' IS in the baseline (not via an empty set), and no skew on an
    # unstamped baseline.
    assert report["version_skew"] is None and report["status"] == "clean"
    assert report["new_code_families"] == []


# --------------------------------------------------------------------------- #
# CLI-level reduction pre-pass (S4-Defer-3 + S4-Defer-2 adversary) — end-to-end
# through the real gate/scoped-rebaseline commands, a real multi-hash baseline.
# --------------------------------------------------------------------------- #
def test_cli_reduction_is_advisory_not_hard_block(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=())
    # _consumer_repo's default helper only writes single-hash synthetic families;
    # this scenario needs a real multi-hash {A,A,B} family, so seed it directly.
    _write_json(repo / "q" / "dup-ratchet-baseline.json",
                baseline_lib.build_gate_baseline({"OLDFAM": ["m1", "m1", "m2"]}))
    code_json = _write_json(tmp_path / "code.json", {
        "status": "findings", "families": [_code_family("NEWFAM", ["m1", "m2"])],
    })
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["ok"] is True and report["block"] is False
    assert report["status"] == "clean"  # not "new" -- the reduction is excluded before evaluate()
    assert report["reductions"] == [{"new_fingerprint": "NEWFAM", "old_fingerprint": "OLDFAM"}]
    assert any(
        m.startswith("ADVISORY (reduction): family OLDFAM shrank to NEWFAM")
        and "--accept-rotation OLDFAM=NEWFAM" in m
        for m in report["messages"]
    )


def test_cli_genuine_new_family_not_a_reduction_hard_blocks(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=())
    _write_json(repo / "q" / "dup-ratchet-baseline.json",
                baseline_lib.build_gate_baseline({"OLDFAM": ["m1", "m2"]}))
    code_json = _write_json(tmp_path / "code.json", {
        "status": "findings", "families": [_code_family("NEWFAM", ["x1", "x2"])],
    })
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["ok"] is False and report["status"] == "hard-block"
    assert report["new_code_families"] == ["NEWFAM"]
    assert report["reductions"] == []


def test_cli_membership_grow_is_not_a_reduction_hard_blocks(tmp_path: Path) -> None:
    # baseline {A,B}, live {A,A,B} -- a SUPERSET, not a sub-multiset -- must still
    # hard-block like nose's own id would (S4-D9: membership growth is genuine
    # new/changed dup, not a reduction).
    repo = _consumer_repo(tmp_path, baseline_ids=())
    _write_json(repo / "q" / "dup-ratchet-baseline.json",
                baseline_lib.build_gate_baseline({"OLDFAM": ["m1", "m2"]}))
    code_json = _write_json(tmp_path / "code.json", {
        "status": "findings", "families": [_code_family("GROWNFAM", ["m1", "m1", "m2"])],
    })
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["ok"] is False and report["status"] == "hard-block"
    assert report["new_code_families"] == ["GROWNFAM"]
    assert report["reductions"] == []


def test_cli_shrink_then_recur_does_not_silently_reaccept(tmp_path: Path) -> None:
    # S4-Defer-2 adversary: accept a reduction via the scoped rotation path (the
    # baseline now holds only the shrunk family), then the ORIGINAL full member set
    # recurs under a DIFFERENT family identity -- it must hard-block, not silently
    # re-accepted as "known" (a residual only while a reduction advisory is ignored,
    # never while the accepted baseline already reflects the shrink).
    repo = _consumer_repo(tmp_path, baseline_ids=())
    _write_json(repo / "q" / "dup-ratchet-baseline.json",
                baseline_lib.build_gate_baseline({"OLDFAM": ["m1", "m1", "m2"]}))
    shrink_json = _write_json(tmp_path / "shrink.json", {
        "status": "findings", "families": [_code_family("NEWFAM", ["m1", "m2"])],
    })
    accept = _run_inproc(repo, "--code-inventory", str(shrink_json), "--accept-rotation", "OLDFAM=NEWFAM")
    assert accept["ok"] is True and accept["status"] == "scoped-rebaseline-written"
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert baseline_lib.load_gate_baseline_ids(written) == {"NEWFAM"}

    recur_json = _write_json(tmp_path / "recur.json", {
        "status": "findings", "families": [_code_family("RECURFAM", ["m1", "m1", "m2"])],
    })
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(recur_json), "--doc-inventory", str(doc_json))
    assert report["ok"] is False and report["status"] == "hard-block"
    assert report["new_code_families"] == ["RECURFAM"]
    assert report["reductions"] == []


# --------------------------------------------------------------------------- #
# Legacy v2-schema baseline read by v3 code -- whole gate degrades to advisory,
# NEVER blocks (the live state between Phase 1 landing and Phase 2's re-baseline).
# --------------------------------------------------------------------------- #
def test_inproc_legacy_v2_baseline_degrades_never_blocks(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("known1",))
    # Overwrite with a pre-migration v2-schema baseline (bare fingerprint list, no
    # per-family member hashes) -- load_gate_baseline_ids/members read it as None
    # (no dual-read), degrading the WHOLE gate to advisory even with a brand-new
    # family that would otherwise hard-block.
    (repo / "q" / "dup-ratchet-baseline.json").write_text(
        json.dumps({"schemaVersion": "charness.quality.dup_ratchet_baseline.v2",
                    "code_family_fingerprints": ["known1"]}),
        encoding="utf-8",
    )
    code_json = _code_inventory(tmp_path / "code.json", ["known1", "BRANDNEW"])
    doc_json = _doc_inventory(tmp_path / "doc.json", [])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--doc-inventory", str(doc_json))
    assert report["status"] == "degraded" and report["block"] is False
    assert any("gate baseline missing/unreadable" in r for r in report["degraded_reasons"])
