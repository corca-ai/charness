from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
# grade_skill_outcome.py does `from runtime_bootstrap import ...`, so scripts/ must
# be importable when the module is exec'd.
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

g = load_script_module("grade_skill_outcome_under_test", ROOT / "scripts" / "grade_skill_outcome.py")


# --- assertion set validation ---------------------------------------------------


def _valid_set() -> dict:
    return {
        "evalId": "x",
        "assertions": [
            {"id": "a", "kind": "deterministic", "statement": "s",
             "check": {"type": "summary_contains", "value": "v"}},
            {"id": "b", "kind": "judge", "statement": "s", "weight": 2},
        ],
    }


def test_validate_assertion_set_accepts_valid() -> None:
    assert g.validate_assertion_set(_valid_set()) == []


def test_validate_assertion_set_rejects_shapes() -> None:
    assert g.validate_assertion_set([]) == ["assertion set must be a JSON object"]
    assert any("evalId" in e for e in g.validate_assertion_set({"assertions": _valid_set()["assertions"]}))
    assert any("assertions must be a non-empty list" in e for e in g.validate_assertion_set({"evalId": "x", "assertions": []}))


def test_validate_assertion_set_field_errors() -> None:
    bad = {
        "evalId": "x",
        "assertions": [
            {"id": "dup", "kind": "deterministic", "statement": "s", "check": {"type": "summary_contains", "value": "v"}},
            {"id": "dup", "kind": "bogus", "statement": "", "weight": 0},  # dup id, bad kind, empty stmt, bad weight
            {"id": "j", "kind": "judge", "statement": "s", "check": {"type": "summary_contains", "value": "v"}},  # judge w/ check
            {"id": "d", "kind": "deterministic", "statement": "s", "check": {"type": "nope"}},  # bad check type
        ],
    }
    errors = " | ".join(g.validate_assertion_set(bad))
    assert "duplicate" in errors
    assert "kind must be" in errors
    assert "statement must be" in errors
    assert "weight must be a positive number" in errors
    assert "judge-kind but carries a deterministic check" in errors
    assert "check.type must be one of" in errors


def test_validate_check_requires_fields() -> None:
    # output_file_contains needs both path and value; trace_tool_used needs name.
    s = {"evalId": "x", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s", "check": {"type": "output_file_contains"}},
        {"id": "b", "kind": "deterministic", "statement": "s", "check": {"type": "trace_tool_used"}},
    ]}
    errors = " | ".join(g.validate_assertion_set(s))
    assert "check.value must be a string" in errors
    assert "check.path must be a string" in errors
    assert "check.name must be a string" in errors


def test_load_assertion_set_raises_on_invalid(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text(json.dumps({"evalId": "x", "assertions": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid assertion set"):
        g.load_assertion_set(p)


def test_load_assertion_set_loads_valid(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text(json.dumps(_valid_set()), encoding="utf-8")
    assert g.load_assertion_set(p)["evalId"] == "x"


# --- bundle loading -------------------------------------------------------------


def _make_bundle(tmp_path: Path, *, name="bundle", summary="S", trace=None, output=None, transcript=None) -> Path:
    d = tmp_path / name
    d.mkdir(exist_ok=True)
    (d / "observed.v1.json").write_text(
        json.dumps({"evaluations": [{"summary": summary, "outcome": "passed", "metrics": {}}]}), encoding="utf-8")
    if trace is not None:
        # Include a deliberately malformed line to prove load tolerates it.
        body = "".join(json.dumps(r) + "\n" for r in trace) + "{not json}\n"
        (d / "trace-digest.jsonl").write_text(body, encoding="utf-8")
    if output is not None:
        (d / "outputs").mkdir(exist_ok=True)
        (d / "outputs" / "result.md").write_text(output, encoding="utf-8")
    if transcript is not None:
        (d / "transcript.txt").write_text(transcript, encoding="utf-8")
    return d


def test_load_bundle_reads_sources(tmp_path: Path) -> None:
    d = _make_bundle(tmp_path, summary="hello", trace=[{"name": "Read", "args": "x"}], output="art", transcript="T")
    bundle = g.load_bundle(d)
    assert bundle.summary == "hello"
    assert len(bundle.trace) == 1  # malformed line dropped, not fatal
    assert bundle.outputs_dir is not None
    assert bundle.transcript == "T"
    assert "Read: x" in bundle.judge_context and "hello" in bundle.judge_context


def test_judge_context_includes_transcript_and_outputs(tmp_path: Path) -> None:
    d = _make_bundle(tmp_path, summary="S", trace=[{"name": "Read", "args": "x"}],
                     output="the produced artifact", transcript="chunk 1 was presented")
    ctx = g.load_bundle(d).judge_context
    assert "SUMMARY:" in ctx and "TRACE:" in ctx
    assert "chunk 1 was presented" in ctx  # transcript: what the run presented
    assert "the produced artifact" in ctx and "result.md" in ctx  # output excerpt + filename
    # the outputs manifest itself is not dumped as an excerpt
    (d / "outputs" / "outputs-manifest.json").write_text('{"copied":[]}', encoding="utf-8")
    assert "outputs-manifest" not in g.load_bundle(d).judge_context


def test_load_bundle_missing_observed_raises(tmp_path: Path) -> None:
    (tmp_path / "empty").mkdir()
    with pytest.raises(FileNotFoundError, match="observed.v1.json"):
        g.load_bundle(tmp_path / "empty")


def test_load_bundle_optional_sources_absent(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path))
    assert bundle.trace == [] and bundle.outputs_dir is None and bundle.transcript == ""


# --- deterministic checks -------------------------------------------------------


def test_summary_contains_plain_and_regex(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path, summary="Execution of /hitl: 5 tokens"))
    assert g.eval_deterministic({"type": "summary_contains", "value": "/hitl"}, bundle)[0] == g.PASS
    assert g.eval_deterministic({"type": "summary_contains", "value": "absent"}, bundle)[0] == g.FAIL
    assert g.eval_deterministic({"type": "summary_contains", "value": r"\d+ tokens", "regex": True}, bundle)[0] == g.PASS


def test_trace_tool_used_name_args_and_min_count(tmp_path: Path) -> None:
    trace = [{"name": "Read", "args": "a/chunk-contract.md"}, {"name": "Read", "args": "b"}, {"name": "Bash", "args": "ls"}]
    bundle = g.load_bundle(_make_bundle(tmp_path, trace=trace))
    assert g.eval_deterministic({"type": "trace_tool_used", "name": "Read"}, bundle)[0] == g.PASS
    assert g.eval_deterministic({"type": "trace_tool_used", "name": "Read", "args_contains": "chunk-contract.md"}, bundle)[0] == g.PASS
    assert g.eval_deterministic({"type": "trace_tool_used", "name": "Read", "min_count": 3}, bundle)[0] == g.FAIL
    assert g.eval_deterministic({"type": "trace_tool_used", "name": "Edit"}, bundle)[0] == g.FAIL


def test_negate_flips_pass_and_fail(tmp_path: Path) -> None:
    # negate expresses a reliable ABSENCE signal (e.g. summary does NOT report a
    # required fragment missing). It flips pass<->fail but leaves error untouched.
    bundle = g.load_bundle(_make_bundle(tmp_path, summary="missing required fragment: x.md"))
    assert g.eval_deterministic({"type": "summary_contains", "value": "missing required fragment: x.md"}, bundle)[0] == g.PASS
    flipped, evidence = g.eval_deterministic({"type": "summary_contains", "value": "missing required fragment: x.md", "negate": True}, bundle)
    assert flipped == g.FAIL and "[negated]" in evidence
    absent = g.eval_deterministic({"type": "summary_contains", "value": "absent", "negate": True}, bundle)
    assert absent[0] == g.PASS  # value absent -> raw FAIL -> negated PASS
    # negate must validate as a boolean
    bad = {"evalId": "x", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s", "check": {"type": "summary_contains", "value": "v", "negate": "yes"}}]}
    assert any("negate must be a boolean" in e for e in g.validate_assertion_set(bad))


def test_output_file_checks(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path, output="the artifact body"))
    assert g.eval_deterministic({"type": "output_file_exists", "path": "result.md"}, bundle)[0] == g.PASS
    assert g.eval_deterministic({"type": "output_file_exists", "path": "missing.md"}, bundle)[0] == g.FAIL
    assert g.eval_deterministic({"type": "output_file_contains", "path": "result.md", "value": "artifact"}, bundle)[0] == g.PASS
    assert g.eval_deterministic({"type": "output_file_contains", "path": "result.md", "value": "nope"}, bundle)[0] == g.FAIL


def test_output_glob_matches_nested(tmp_path: Path) -> None:
    d = _make_bundle(tmp_path, output="x")  # creates outputs/result.md
    nested = d / "outputs" / ".charness" / "hitl" / "runtime" / "sess1"
    nested.mkdir(parents=True)
    (nested / "queue.json").write_text("{}", encoding="utf-8")
    bundle = g.load_bundle(d)
    v, e = g.eval_deterministic({"type": "output_glob", "pattern": "**/queue.json"}, bundle)
    assert v == g.PASS and "1 output" in e
    assert g.eval_deterministic({"type": "output_glob", "pattern": "**/missing.json"}, bundle)[0] == g.FAIL
    # validation: pattern required
    bad = {"evalId": "x", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s", "check": {"type": "output_glob"}}]}
    assert any("pattern must be a string" in err for err in g.validate_assertion_set(bad))


def test_output_checks_without_outputs_dir_fail_with_evidence(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path))  # no outputs/
    verdict, evidence = g.eval_deterministic({"type": "output_file_exists", "path": "x"}, bundle)
    assert verdict == g.FAIL and "no outputs/ dir" in evidence


def test_transcript_contains(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path, transcript="approved chunk 1"))
    assert g.eval_deterministic({"type": "transcript_contains", "value": "approved"}, bundle)[0] == g.PASS
    empty = g.load_bundle(_make_bundle(tmp_path, name="empty"))
    v, e = g.eval_deterministic({"type": "transcript_contains", "value": "x"}, empty)
    assert v == g.FAIL and "no transcript" in e


# --- grading + aggregation ------------------------------------------------------


def test_grade_skips_judge_without_judge_fn(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path, summary="has v"))
    result = g.grade(_valid_set(), bundle, judge_fn=None)
    by_id = {r["id"]: r for r in result["assertions"]}
    assert by_id["a"]["verdict"] == g.PASS
    assert by_id["b"]["verdict"] == g.SKIPPED
    # skipped row excluded from the denominator -> 1/1 scored, pass_rate 1.0
    assert result["scored"] == 1 and result["pass_rate"] == 1.0 and result["skipped"] == 1


def test_grade_routes_judge_kind_to_judge_fn(tmp_path: Path) -> None:
    bundle = g.load_bundle(_make_bundle(tmp_path, summary="no marker"))
    seen = {}

    def judge(statement, context):
        seen["called"] = (statement, context)
        return g.FAIL, "judged"

    result = g.grade(_valid_set(), bundle, judge_fn=judge)
    by_id = {r["id"]: r for r in result["assertions"]}
    assert by_id["a"]["verdict"] == g.FAIL  # summary lacked "v"
    assert by_id["b"]["verdict"] == g.FAIL and by_id["b"]["evidence"] == "judged"
    assert seen["called"][0] == "s"  # statement handed to judge


def test_aggregate_weights_and_excludes_skipped_error() -> None:
    rows = [
        {"verdict": g.PASS, "weight": 2}, {"verdict": g.FAIL, "weight": 1},
        {"verdict": g.SKIPPED, "weight": 5}, {"verdict": g.ERROR, "weight": 9},
    ]
    agg = g._aggregate(rows)
    assert agg["scored"] == 2 and agg["passed"] == 1
    assert agg["pass_rate"] == round(2 / 3, 3)  # weighted: 2 of (2+1)
    assert agg["skipped"] == 1 and agg["errors"] == 1


def test_aggregate_all_skipped_is_none_not_crash() -> None:
    agg = g._aggregate([{"verdict": g.SKIPPED, "weight": 1}])
    assert agg["pass_rate"] is None and agg["scored"] == 0


def test_build_report_contents_and_pipe_escape(tmp_path: Path) -> None:
    s = {"evalId": "demo", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "has a | pipe",
         "check": {"type": "summary_contains", "value": "x"}}]}
    bundle = g.load_bundle(_make_bundle(tmp_path, summary="x here"))
    report = g.build_report(g.grade(s, bundle))
    assert "Outcome grade — demo" in report
    assert "Advisory outcome grade" in report
    assert r"has a \| pipe" in report  # pipe escaped so the markdown table is not broken
    assert "Honest caveats" in report


# --- live judge seam (monkeypatched, parity with run_one tests) ------------------


def _completed(rc: int, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess("cmd", rc, stdout=stdout, stderr=stderr)


def test_judge_via_command_parses_verdict(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g.subprocess, "run",
                        lambda *a, **k: _completed(0, stdout=json.dumps({"verdict": "pass", "evidence": "ok"})))
    verdict, evidence = g.judge_via_command("judge", 10)("stmt", "ctx")
    assert verdict == g.PASS and evidence == "ok"


def test_judge_via_command_error_paths(monkeypatch: pytest.MonkeyPatch) -> None:
    judge = g.judge_via_command("judge", 10)
    monkeypatch.setattr(g.subprocess, "run", lambda *a, **k: _completed(1, stderr="boom"))
    assert judge("s", "c")[0] == g.ERROR  # non-zero rc
    monkeypatch.setattr(g.subprocess, "run", lambda *a, **k: _completed(0, stdout="not json"))
    assert judge("s", "c")[0] == g.ERROR  # unparseable
    monkeypatch.setattr(g.subprocess, "run", lambda *a, **k: _completed(0, stdout=json.dumps({"verdict": "maybe"})))
    assert judge("s", "c")[0] == g.ERROR  # bad verdict value


def test_judge_via_command_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*a, **k):
        raise subprocess.TimeoutExpired("judge", 10)
    monkeypatch.setattr(g.subprocess, "run", boom)
    assert g.judge_via_command("judge", 10)("s", "c")[0] == g.ERROR


# --- selftest gate --------------------------------------------------------------


def test_selftest_passes() -> None:
    assert g.selftest() == 0


def test_selftest_refuses_when_grader_cannot_rank(monkeypatch: pytest.MonkeyPatch) -> None:
    # Force the grader to look broken (good no longer ranks above bad); selftest
    # must refuse (return 1) — the gate that keeps grading off untrustworthy
    # instruments, mirroring the A/B harness ranks_worse refusal.
    monkeypatch.setattr(g, "grade", lambda *a, **k: {"pass_rate": 0.5, "passed": 1, "scored": 2})
    assert g.selftest() == 1


# --- CLI ------------------------------------------------------------------------


def test_main_requires_a_mode() -> None:
    with pytest.raises(SystemExit):
        g.main([])


def test_main_dispatches_selftest(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "selftest", lambda: 0)
    assert g.main(["--selftest"]) == 0


def test_main_grade_requires_assertions(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        g.main(["--grade", str(tmp_path)])


def test_main_grade_refuses_when_selftest_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # --grade gates on the self-test and never grades on an untrustworthy grader.
    bundle = _make_bundle(tmp_path, summary="Execution of /hitl")
    assertions = tmp_path / "a.json"
    assertions.write_text(json.dumps(_valid_set()), encoding="utf-8")
    graded = {"ran": False}
    monkeypatch.setattr(g, "selftest", lambda: 1)
    monkeypatch.setattr(g, "grade", lambda *a, **k: graded.__setitem__("ran", True) or {})
    rc = g.main(["--grade", str(bundle), "--assertions", str(assertions)])
    assert rc == 1 and graded["ran"] is False


def test_shipped_hitl_assertion_set_conforms() -> None:
    # The shipped per-eval data file must parse + validate against the schema; this
    # is the only standing check of its content (the claim-fidelity validator only
    # indexes *.spec.json, not outcome-assertions.json).
    path = ROOT / "evals" / "cautilus" / "hitl-claim-fidelity" / "outcome-assertions.json"
    loaded = g.load_assertion_set(path)
    assert loaded["evalId"] == "hitl-claim-fidelity"
    assert any(a["kind"] == "judge" for a in loaded["assertions"])
    assert any(a["kind"] == "deterministic" for a in loaded["assertions"])


def test_main_grade_happy_path_writes_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(g, "selftest", lambda: 0)
    bundle = _make_bundle(tmp_path, summary="Execution of /hitl ok")
    assertions = tmp_path / "a.json"
    assertions.write_text(json.dumps({"evalId": "x", "assertions": [
        {"id": "a", "kind": "deterministic", "statement": "s", "check": {"type": "summary_contains", "value": "/hitl"}}]}),
        encoding="utf-8")
    out = tmp_path / "report.md"
    rc = g.main(["--grade", str(bundle), "--assertions", str(assertions), "--output", str(out)])
    assert rc == 0 and out.is_file() and "Outcome grade — x" in out.read_text(encoding="utf-8")
