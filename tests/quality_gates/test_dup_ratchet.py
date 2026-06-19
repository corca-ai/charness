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

import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from .support import ROOT, run_script

SCRIPTS = ROOT / "skills" / "public" / "quality" / "scripts"
CHECK_SCRIPT = SCRIPTS / "check_dup_ratchet.py"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{name}_inproc", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lib = _load("dup_ratchet_lib")
nose_report = _load("nose_report_lib")
# check_dup_ratchet is loaded in-process (not only via subprocess) so its CLI/run
# branches attribute coverage — the #393 subprocess-only-attribution class. The
# subprocess SC5 tests below still prove the real process contract (argv, exit codes,
# stdout); these in-process drives prove the same branches under coverage.
check = _load("check_dup_ratchet")


def _run_inproc(repo: Path, *cli: str) -> dict:
    """Drive check_dup_ratchet.run() in-process (mirrors main()'s repo_root.resolve())."""
    args = check.parse_args(["--repo-root", str(repo), *cli])
    return check.run(args.repo_root.resolve(), args)


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
# Gate baseline + overlay readers
# --------------------------------------------------------------------------- #
def test_build_and_load_gate_baseline_roundtrip() -> None:
    baseline = lib.build_gate_baseline(["b", "a", "a", ""])
    assert baseline["code_family_ids"] == ["a", "b"]  # sorted, deduped, empties dropped
    assert baseline["schemaVersion"] == lib.GATE_BASELINE_SCHEMA_VERSION
    assert lib.validate_gate_baseline(baseline) == []
    assert lib.load_gate_baseline_ids(baseline) == {"a", "b"}


def test_load_gate_baseline_ids_none_on_malformed() -> None:
    assert lib.load_gate_baseline_ids(None) is None
    assert lib.load_gate_baseline_ids({"code_family_ids": "nope"}) is None
    assert lib.load_gate_baseline_ids([1, 2]) is None


def test_validate_gate_baseline_flags_bad_schema_and_ids() -> None:
    errors = lib.validate_gate_baseline({"schemaVersion": "wrong", "code_family_ids": ["", 5]})
    joined = " ".join(errors)
    assert "schemaVersion" in joined and "code_family_ids[0]" in joined


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
# SC4 (git seams) — real git fixture: resolve_anchor / ancestor / stagnation
# --------------------------------------------------------------------------- #
def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "user.email=t@t", "-c", "user.name=t", *args],
        cwd=repo, check=True, capture_output=True, text=True,
    )


def test_git_seams_anchor_stagnation_and_reset(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init")
    overlay = repo / "q" / "dup-review.json"
    overlay.parent.mkdir(parents=True)
    overlay.write_text("{}\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "seed overlay")
    anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()

    for index in range(3):
        _git(repo, "commit", "--allow-empty", "-m", f"work {index}")

    assert lib.resolve_anchor(repo, "q/dup-review.json") == anchor
    assert lib.anchor_is_ancestor(repo, anchor) is True
    assert lib.stagnation_commits(repo, anchor) == 3

    # Editing the overlay (a review) advances the anchor and resets the clock.
    overlay.write_text('{"reviewed": 1}\n', encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "lower the ceiling")
    new_anchor = _git(repo, "rev-parse", "HEAD").stdout.strip()
    assert lib.resolve_anchor(repo, "q/dup-review.json") == new_anchor
    assert lib.stagnation_commits(repo, new_anchor) == 0


def test_git_seams_orphan_and_missing(tmp_path: Path) -> None:
    repo = tmp_path / "r"
    repo.mkdir()
    _git(repo, "init")
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "init")
    # A bogus/orphaned anchor is not an ancestor, and stagnation is unknowable.
    assert lib.anchor_is_ancestor(repo, "0" * 40) is False
    assert lib.stagnation_commits(repo, "0" * 40) is None
    assert lib.anchor_is_ancestor(repo, None) is False
    # A path never committed has no anchor.
    assert lib.resolve_anchor(repo, "q/never.json") is None


# --------------------------------------------------------------------------- #
# SC6 — family_summary emits family_id (the code arm's identity)
# --------------------------------------------------------------------------- #
def test_family_summary_emits_family_id() -> None:
    assert nose_report.family_summary({"family_id": "abc123"})["family_id"] == "abc123"


# --------------------------------------------------------------------------- #
# SC5 — CLI end-to-end on a consumer-style fixture (no charness internals)
# --------------------------------------------------------------------------- #
def _write_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")
    return path


def _code_inventory(path: Path, family_ids: list[str]) -> Path:
    return _write_json(path, {"status": "findings", "families": [{"family_id": fid} for fid in family_ids]})


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
    _write_json(repo / "q" / "dup-review.json", {
        "schemaVersion": "charness.quality.dup_review.v1",
        "fixable_ceiling": fixable_ceiling, "entries": entries,
    })
    _write_json(repo / "q" / "dup-ratchet-baseline.json", {
        "schemaVersion": "charness.quality.dup_ratchet_baseline.v1",
        "code_family_ids": list(baseline_ids),
    })
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
    return run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo),
        "--code-inventory", str(code_json), "--doc-inventory", str(doc_json),
        "--json", *(extra or []), cwd=ROOT,
    )


def _verdict(result: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(result.stdout)


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
    assert _verdict(result)["status"] == "degraded"


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
        "--doc-inventory", str(doc_json), "--json", cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    verdict = _verdict(result)
    assert verdict["status"] == "degraded"
    assert any("0 families" in reason for reason in verdict["degraded_reasons"])


def test_cli_write_baseline_from_injected_inventory(tmp_path: Path) -> None:
    repo = _consumer_repo(tmp_path, baseline_ids=("old",))
    code_json = _code_inventory(tmp_path / "code.json", ["a", "b", "a"])
    result = run_script(
        str(CHECK_SCRIPT), "--repo-root", str(repo), "--code-inventory", str(code_json),
        "--write-baseline", "--json", cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert written["code_family_ids"] == ["a", "b"]
    assert lib.validate_gate_baseline(written) == []


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
        json.dumps({"schemaVersion": "WRONG", "code_family_ids": ["known1"]}), encoding="utf-8",
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
    assert preserved["code_family_ids"] == ["old1", "old2", "old3"]  # unchanged


def test_inproc_C_large_delta_with_confirm_rebaselines(tmp_path: Path) -> None:
    # C: the deliberate-re-baseline case (e.g. a nose version swing) proceeds with the
    # named confirm flag.
    repo = _consumer_repo(tmp_path, baseline_ids=("old1", "old2", "old3"))
    code_json = _code_inventory(tmp_path / "code.json", ["n1", "n2", "n3", "n4"])
    report = _run_inproc(repo, "--code-inventory", str(code_json), "--write-baseline",
                         "--baseline-delta-threshold", "2", "--confirm-baseline-delta")
    assert report["ok"] is True and report["status"] == "baseline-written"
    written = json.loads((repo / "q" / "dup-ratchet-baseline.json").read_text(encoding="utf-8"))
    assert written["code_family_ids"] == ["n1", "n2", "n3", "n4"]
