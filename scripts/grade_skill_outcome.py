#!/usr/bin/env python3

"""Evidence-based OUTCOME grader for charness skill captures: did the run actually
accomplish the work, judged against per-eval discriminating assertions + cited
evidence — not the routing/coverage PROXY the current cautilus modes score.

This is the missing OUTCOME layer (methodology spec
`charness-artifacts/spec/2026-06-23-skill-claim-fidelity-doc-philosophy.md`
§ "Evaluation Ownership + the Outcome Gap"). Both current cautilus modes score
ROUTING/coverage; neither GRADES the produced artifact for correctness with
discriminating assertions. An efficiency number is trustworthy only alongside an
outcome check — a leaner token/time number can just mean the variant did LESS, so
this grader is what makes the A/B efficiency comparison trustworthy.

Ownership (fixed by the spec): the grader is HOST-SIDE, not cautilus. cautilus is a
deterministic scorer and must NOT host the LLM judge (LLM/agent surfaces are
not enabled by repo policy). This runner borrows skill-creator's GRADING pattern
(assertions + LLM judge over transcript + outputs), execution-agnostic, NOT its
subagent executor (which breaks spawn-heavy skills).

What it grades: a per-run EVIDENCE BUNDLE (the `preserved/<arm>__<n>/` dir the A/B
harness already writes, or any dir with the same shape):
  observed.v1.json     required — the distilled packet (summary, metrics, outcome)
  trace-digest.jsonl   optional — per-call trace (tool name + args digest)
  outputs/             optional — produced artifact files (the preservation
                       follow-up; deterministic file checks resolve here)
  transcript.txt       optional — captured transcript text (transcript checks)

Assertion kinds:
  deterministic — mechanically checkable here, offline, no spend (summary_contains,
                  trace_tool_used, output_file_exists, output_file_contains,
                  transcript_contains). This already grades real outcome facts.
  judge         — subjective; routed to an injectable judge seam. The live judge is
                  a real token spend (ask-before-run): `--grade` evaluates
                  deterministic assertions for free and SKIPS judge-kind unless
                  `--judge-cmd` is given. The judge command is the portable seam
                  (could be `claude -p`, a script, …), not a hardcoded provider.

Self-tested instruments (`--selftest`, offline, no API): like the A/B harness, prove
the grader ranks a known-GOOD output (satisfies the assertions) strictly above a
known-BAD one before trusting any verdict — a grader you can't trust is worse than
none. Mirrors `run_skill_efficiency_ab.py --selftest`.

Advisory, never a gate: this emits no pass/fail commit verdict and gates nothing; it
produces per-assertion PASS/FAIL + evidence + a weighted pass_rate, and a human
reads it. The correctness FLOOR stays owned by the claim matcher + cautilus.
floor-addition-restraint: advisory measurement only, no new blocking floor added.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from runtime_bootstrap import repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

# Verdict vocabulary. "skipped" is a real outcome (judge not run / unknown check),
# distinct from "fail", and is excluded from the pass_rate denominator so a deferred
# judge does not silently depress the score.
PASS, FAIL, SKIPPED, ERROR = "pass", "fail", "skipped", "error"

DETERMINISTIC_CHECK_TYPES = (
    "summary_contains",
    "trace_tool_used",
    "output_file_exists",
    "output_file_contains",
    "output_glob",
    "transcript_contains",
)


# --- assertion set (data) -------------------------------------------------------


def validate_assertion_set(obj: object) -> list[str]:
    """Return a list of human-readable problems (empty = valid). Kept pure so the
    CLI and the tests share one definition of a well-formed assertion set."""
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["assertion set must be a JSON object"]
    if not isinstance(obj.get("evalId"), str) or not obj["evalId"].strip():
        errors.append("evalId must be a non-empty string")
    assertions = obj.get("assertions")
    if not isinstance(assertions, list) or not assertions:
        return errors + ["assertions must be a non-empty list"]
    seen_ids: set[str] = set()
    for index, assertion in enumerate(assertions):
        where = f"assertions[{index}]"
        if not isinstance(assertion, dict):
            errors.append(f"{where} must be an object")
            continue
        aid = assertion.get("id")
        if not isinstance(aid, str) or not aid.strip():
            errors.append(f"{where}.id must be a non-empty string")
        elif aid in seen_ids:
            errors.append(f"{where}.id duplicate: {aid!r}")
        else:
            seen_ids.add(aid)
        if not isinstance(assertion.get("statement"), str) or not assertion["statement"].strip():
            errors.append(f"{where}.statement must be a non-empty string")
        kind = assertion.get("kind")
        if kind not in ("deterministic", "judge"):
            errors.append(f"{where}.kind must be 'deterministic' or 'judge'")
        weight = assertion.get("weight", 1)
        if not isinstance(weight, (int, float)) or isinstance(weight, bool) or weight <= 0:
            errors.append(f"{where}.weight must be a positive number")
        if kind == "deterministic":
            errors.extend(_validate_check(assertion.get("check"), where))
        elif kind == "judge" and "check" in assertion:
            errors.append(f"{where} is judge-kind but carries a deterministic check")
    return errors


def _validate_check(check: object, where: str) -> list[str]:
    if not isinstance(check, dict):
        return [f"{where}.check must be an object for a deterministic assertion"]
    ctype = check.get("type")
    if ctype not in DETERMINISTIC_CHECK_TYPES:
        return [f"{where}.check.type must be one of {DETERMINISTIC_CHECK_TYPES}"]
    needs_value = {"summary_contains", "output_file_contains", "transcript_contains"}
    needs_path = {"output_file_exists", "output_file_contains"}
    problems = []
    if "negate" in check and not isinstance(check["negate"], bool):
        problems.append(f"{where}.check.negate must be a boolean")
    if ctype in needs_value and not isinstance(check.get("value"), str):
        problems.append(f"{where}.check.value must be a string for {ctype}")
    elif check.get("regex") and ctype in needs_value:
        # A `regex: true` value is compiled at grade time; catch a malformed pattern
        # at the authoring boundary instead of crashing a live grade mid-run.
        try:
            re.compile(check["value"])
        except re.error as exc:
            problems.append(f"{where}.check.value is an invalid regex: {exc}")
    if ctype in needs_path and not isinstance(check.get("path"), str):
        problems.append(f"{where}.check.path must be a string for {ctype}")
    if ctype == "trace_tool_used" and not isinstance(check.get("name"), str):
        problems.append(f"{where}.check.name must be a string for trace_tool_used")
    if ctype == "output_glob" and not isinstance(check.get("pattern"), str):
        problems.append(f"{where}.check.pattern must be a string for output_glob")
    return problems


def load_assertion_set(path: Path) -> dict:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = validate_assertion_set(obj)
    if errors:
        raise ValueError(f"invalid assertion set {path}:\n  - " + "\n  - ".join(errors))
    return obj


# --- evidence bundle ------------------------------------------------------------


class Bundle:
    """A captured run's evidence sources, read once. Missing optional sources are
    empty, never an error — a deterministic check over an absent source simply
    fails (with evidence saying so), which is the honest outcome."""

    def __init__(self, summary: str, trace: list[dict], outputs_dir: Path | None, transcript: str):
        self.summary = summary
        self.trace = trace
        self.outputs_dir = outputs_dir
        self.transcript = transcript

    @property
    def judge_context(self) -> str:
        """The text a judge sees: the observed summary, a compact trace rendering,
        the assistant transcript (what the run PRESENTED), and excerpts of the
        produced output files (what it MADE). Every section is bounded so a huge run
        cannot blow the judge prompt — the judge grades the work, not the whole log."""
        lines = [f"{r.get('name')}: {r.get('args', '')}" for r in self.trace[:80]]
        parts = [f"SUMMARY:\n{self.summary}", "TRACE:\n" + "\n".join(lines)]
        if self.transcript:
            parts.append("TRANSCRIPT (assistant text, truncated):\n" + self.transcript[:8000])
        excerpts = self._output_excerpts()
        if excerpts:
            parts.append("PRODUCED OUTPUTS (truncated):\n" + excerpts)
        # Strip NUL bytes: a binary output excerpt (valid UTF-8 U+0000 survives errors=
        # "replace") would otherwise reach a judge that passes the context as a subprocess
        # argument and crash it with `embedded null byte`. Defensive — preserve_outputs
        # already drops binary files, but a tracked binary output could still carry one.
        return "\n\n".join(parts).replace("\x00", "")

    def _output_excerpts(self, max_files: int = 20, per_file: int = 8000, total_budget: int = 40000) -> str:
        # per_file must fit a full produced artifact's SUBSTANCE, not just its head:
        # a debug artifact caps at ~180 lines (~7KB) and its load-bearing sections
        # (Detection Gap / Sibling Search / Prevention) sit at the BOTTOM, so a small
        # window (the old 500 chars) truncated them and forced false-negative judge
        # verdicts on exactly the substance the assertion set exists to grade. The
        # total_budget bounds a pathological many-file run so the judge prompt is
        # still capped — the judge grades the work, not the whole log.
        if self.outputs_dir is None:
            return ""
        blocks: list[str] = []
        used = 0
        for path in sorted(self.outputs_dir.rglob("*")):
            if not path.is_file() or path.name == "outputs-manifest.json":
                continue
            rel = path.relative_to(self.outputs_dir)
            excerpt = path.read_text(encoding="utf-8", errors="replace")[:per_file]
            blocks.append(f"--- {rel} ---\n{excerpt}")
            used += len(excerpt)
            if len(blocks) >= max_files or used >= total_budget:
                break
        return "\n".join(blocks)


def load_bundle(bundle_dir: Path) -> Bundle:
    bundle_dir = Path(bundle_dir)
    observed_path = bundle_dir / "observed.v1.json"
    if not observed_path.is_file():
        raise FileNotFoundError(f"evidence bundle missing observed.v1.json: {bundle_dir}")
    packet = json.loads(observed_path.read_text(encoding="utf-8"))
    evaluation = (packet.get("evaluations") or [{}])[0]
    summary = evaluation.get("summary") or ""

    trace: list[dict] = []
    trace_path = bundle_dir / "trace-digest.jsonl"
    if trace_path.is_file():
        for line in trace_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(record, dict):
                    trace.append(record)

    outputs_dir = bundle_dir / "outputs"
    outputs_dir = outputs_dir if outputs_dir.is_dir() else None

    transcript = ""
    transcript_path = bundle_dir / "transcript.txt"
    if transcript_path.is_file():
        transcript = transcript_path.read_text(encoding="utf-8", errors="replace")

    return Bundle(summary, trace, outputs_dir, transcript)


# --- deterministic checks (pure) ------------------------------------------------


def _matches(haystack: str, value: str, regex: bool) -> bool:
    return bool(re.search(value, haystack)) if regex else value in haystack


def eval_deterministic(check: dict, bundle: Bundle) -> tuple[str, str]:
    """Return (verdict, evidence), applying an optional `negate` flip. `negate` lets
    an assertion express a reliable ABSENCE signal — e.g. PASS iff the observed
    summary does NOT report a required fragment as missing. That reads the
    authoritative cross-tool claim-matcher verdict instead of re-grepping the trace,
    which the digest truncates (~160 chars) and which misses shell-opened refs (a
    `sed`/`cat` open is invisible to a `trace_tool_used name=Read` check)."""
    verdict, evidence = _eval_check(check, bundle)
    if check.get("negate") and verdict in (PASS, FAIL):
        return (FAIL if verdict == PASS else PASS), f"[negated] {evidence}"
    return verdict, evidence


def _eval_check(check: dict, bundle: Bundle) -> tuple[str, str]:
    ctype = check["type"]
    regex = bool(check.get("regex"))
    if ctype == "summary_contains":
        value = check["value"]
        hit = _matches(bundle.summary, value, regex)
        return (PASS if hit else FAIL, f"summary {'matched' if hit else 'lacked'} {value!r}")
    if ctype == "trace_tool_used":
        name = check["name"]
        args_sub = check.get("args_contains")
        min_count = int(check.get("min_count", 1))
        hits = [
            r for r in bundle.trace
            if r.get("name") == name and (args_sub is None or args_sub in str(r.get("args", "")))
        ]
        ok = len(hits) >= min_count
        detail = f"{name}" + (f" args~{args_sub!r}" if args_sub else "")
        return (PASS if ok else FAIL, f"trace had {len(hits)} {detail} call(s) (need >={min_count})")
    if ctype == "output_file_exists":
        if bundle.outputs_dir is None:
            return FAIL, "no outputs/ dir in bundle (output preservation not yet wired)"
        target = bundle.outputs_dir / check["path"]
        return (PASS, f"output {check['path']} present") if target.is_file() else (FAIL, f"output {check['path']} missing")
    if ctype == "output_file_contains":
        if bundle.outputs_dir is None:
            return FAIL, "no outputs/ dir in bundle (output preservation not yet wired)"
        target = bundle.outputs_dir / check["path"]
        if not target.is_file():
            return FAIL, f"output {check['path']} missing"
        text = target.read_text(encoding="utf-8", errors="replace")
        hit = _matches(text, check["value"], regex)
        return (PASS if hit else FAIL, f"output {check['path']} {'matched' if hit else 'lacked'} {check['value']!r}")
    if ctype == "output_glob":
        if bundle.outputs_dir is None:
            return FAIL, "no outputs/ dir in bundle (output preservation not yet wired)"
        matches = [p for p in bundle.outputs_dir.rglob(check["pattern"]) if p.is_file()]
        return (PASS, f"{len(matches)} output(s) match {check['pattern']!r}") if matches \
            else (FAIL, f"no output matches {check['pattern']!r} under outputs/")
    if ctype == "transcript_contains":
        if not bundle.transcript:
            return FAIL, "no transcript.txt in bundle"
        hit = _matches(bundle.transcript, check["value"], regex)
        return (PASS if hit else FAIL, f"transcript {'matched' if hit else 'lacked'} {check['value']!r}")
    return ERROR, f"unknown check type {ctype!r}"  # pragma: no cover - guarded by validate


# --- grading + aggregation (pure) -----------------------------------------------


def grade(assertion_set: dict, bundle: Bundle, judge_fn=None) -> dict:
    """Grade every assertion, returning per-assertion verdict + evidence and a
    weighted pass_rate. `judge_fn(statement, context) -> (verdict, evidence)` is the
    injection seam: None means judge-kind assertions are SKIPPED (the free,
    ask-before-run-respecting default)."""
    rows: list[dict] = []
    for assertion in assertion_set["assertions"]:
        kind = assertion["kind"]
        weight = assertion.get("weight", 1)
        if kind == "deterministic":
            verdict, evidence = eval_deterministic(assertion["check"], bundle)
        elif judge_fn is None:
            verdict, evidence = SKIPPED, "judge not run (no --judge-cmd; live judge is ask-before-run spend)"
        else:
            verdict, evidence = judge_fn(assertion["statement"], bundle.judge_context)
        rows.append({
            "id": assertion["id"],
            "kind": kind,
            "statement": assertion["statement"],
            "weight": weight,
            "verdict": verdict,
            "evidence": evidence,
        })
    return {"evalId": assertion_set["evalId"], "assertions": rows, **_aggregate(rows)}


def _aggregate(rows: list[dict]) -> dict:
    """Weighted pass_rate over SCORED rows only (pass/fail); skipped/error are
    excluded from the denominator and reported separately."""
    scored = [r for r in rows if r["verdict"] in (PASS, FAIL)]
    denom = sum(r["weight"] for r in scored)
    passed_weight = sum(r["weight"] for r in scored if r["verdict"] == PASS)
    return {
        "n": len(rows),
        "scored": len(scored),
        "passed": sum(1 for r in scored if r["verdict"] == PASS),
        "skipped": sum(1 for r in rows if r["verdict"] == SKIPPED),
        "errors": sum(1 for r in rows if r["verdict"] == ERROR),
        "pass_rate": round(passed_weight / denom, 3) if denom else None,
    }


def build_report(result: dict) -> str:
    lines = [
        f"# Outcome grade — {result['evalId']}",
        "",
        "Advisory outcome grade (NOT a pass/fail commit verdict). Per-assertion "
        "verdict + cited evidence; weighted pass_rate over scored rows only.",
        "",
        f"- scored {result['passed']}/{result['scored']} "
        f"(pass_rate {result['pass_rate'] if result['pass_rate'] is not None else 'n/a'}); "
        f"skipped {result['skipped']}, errors {result['errors']}, total {result['n']}.",
        "",
        "| id | kind | verdict | statement | evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in result["assertions"]:
        statement = row["statement"].replace("|", "\\|")
        evidence = str(row["evidence"]).replace("|", "\\|")
        lines.append(f"| {row['id']} | {row['kind']} | {row['verdict']} | {statement} | {evidence} |")
    lines += [
        "",
        "## Honest caveats",
        "",
        "- Deterministic checks grade mechanical facts; judge-kind rows are SKIPPED "
        "unless a live judge (`--judge-cmd`, ask-before-run spend) ran.",
        "- `trace_tool_used` args matching is best-effort: the trace digest truncates "
        "`args` (~160 chars), so a long command can undercount.",
        "- `output_file_*` checks resolve against the bundle `outputs/` dir, which the "
        "A/B runner now preserves; a bundle captured before that (no `outputs/`) fails "
        "those checks with that explicit evidence.",
        "",
    ]
    return "\n".join(lines)


# --- judge seam (live = ask-before-run spend) -----------------------------------


def judge_via_command(judge_cmd: str, timeout_sec: int):
    """Build a judge_fn that shells to `judge_cmd`, feeding it a JSON payload on
    stdin and reading a JSON `{"verdict": "pass"|"fail", "evidence": "..."}` from
    stdout. The command is the portable seam (the repo can point it at `claude -p`
    with a strict-JSON prompt, or any scorer); invoking it is the real token spend."""

    def _judge(statement: str, context: str) -> tuple[str, str]:
        payload = json.dumps({"statement": statement, "context": context})
        try:
            proc = subprocess.run(
                judge_cmd, shell=True, input=payload,
                capture_output=True, text=True, timeout=timeout_sec, check=False,
            )
        except subprocess.TimeoutExpired:
            return ERROR, f"judge command timed out after {timeout_sec}s"
        if proc.returncode != 0:
            return ERROR, f"judge command failed (rc={proc.returncode}): {proc.stderr[-300:]}"
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            return ERROR, f"judge command did not emit JSON: {proc.stdout[-300:]}"
        verdict = out.get("verdict")
        if verdict not in (PASS, FAIL):
            return ERROR, f"judge verdict must be pass/fail, got {verdict!r}"
        return verdict, str(out.get("evidence", ""))

    return _judge


# --- self-test: synthetic good vs bad bundle, real grader -----------------------


_SELFTEST_ASSERTIONS = {
    "evalId": "grader-selftest",
    "assertions": [
        {"id": "summary-marker", "kind": "deterministic",
         "statement": "The summary records the expected outcome marker.",
         "check": {"type": "summary_contains", "value": "OUTCOME_OK"}},
        {"id": "opened-floor", "kind": "deterministic",
         "statement": "The run opened the briefed reference.",
         "check": {"type": "trace_tool_used", "name": "Read", "args_contains": "floor.md"}},
        {"id": "produced-output", "kind": "deterministic",
         "statement": "The run produced the expected artifact.",
         "check": {"type": "output_file_exists", "path": "result.md"}},
        {"id": "subjective-quality", "kind": "judge",
         "statement": "The artifact is correct and complete.", "weight": 2},
    ],
}


def _write_bundle(bundle_dir: Path, *, summary: str, trace: list[dict], output: str | None) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    packet = {"evaluations": [{"summary": summary, "outcome": "passed", "metrics": {}}]}
    (bundle_dir / "observed.v1.json").write_text(json.dumps(packet), encoding="utf-8")
    (bundle_dir / "trace-digest.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in trace), encoding="utf-8")
    if output is not None:
        outputs = bundle_dir / "outputs"
        outputs.mkdir(exist_ok=True)
        (outputs / "result.md").write_text(output, encoding="utf-8")


# A single deterministic oracle judge: pass iff the bundle context carries the
# sentinel. The GOOD bundle's summary carries it; the BAD one's does not — so ONE
# judge produces pass on good and fail on bad, proving the seam + aggregation
# end-to-end (mirrors the A/B selftest running the REAL extractor over both trees).
def _oracle_judge(statement: str, context: str) -> tuple[str, str]:
    ok = "OUTCOME_OK" in context
    return (PASS if ok else FAIL, f"oracle saw sentinel={ok}")


def selftest() -> int:
    """Prove the grader ranks a known-GOOD output strictly above a known-BAD one.
    Refuse (exit 1) if it does not — a grader you can't trust is worse than none."""
    with tempfile.TemporaryDirectory(prefix="charness-grader-selftest-") as tmp:
        root = Path(tmp)
        _write_bundle(
            root / "good",
            summary="Execution of /x: OUTCOME_OK, the work was done.",
            trace=[{"name": "Read", "args": "/repo/skills/x/references/floor.md"}],
            output="# result\nthe artifact\n",
        )
        _write_bundle(
            root / "bad",
            summary="Execution of /x: stalled early, nothing produced.",
            trace=[{"name": "Bash", "args": "ls"}],
            output=None,
        )
        good = grade(_SELFTEST_ASSERTIONS, load_bundle(root / "good"), _oracle_judge)
        bad = grade(_SELFTEST_ASSERTIONS, load_bundle(root / "bad"), _oracle_judge)
    print(f"  good pass_rate={good['pass_rate']} ({good['passed']}/{good['scored']})")
    print(f"  bad  pass_rate={bad['pass_rate']} ({bad['passed']}/{bad['scored']})")
    good_rate = good["pass_rate"] if good["pass_rate"] is not None else -1.0
    bad_rate = bad["pass_rate"] if bad["pass_rate"] is not None else -1.0
    if not (good_rate == 1.0 and bad_rate == 0.0 and good_rate > bad_rate):
        print(
            "SELFTEST FAILED: grader did not rank known-good (expect 1.0) strictly "
            f"above known-bad (expect 0.0); got good={good_rate} bad={bad_rate}. "
            "Grader not trustworthy.",
            file=sys.stderr,
        )
        return 1
    print("SELFTEST PASSED: grader ranks the known-good output above the known-bad one.")
    return 0


# --- CLI ------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Evidence-based outcome grader for charness skill captures (advisory; never gates).")
    parser.add_argument("--selftest", action="store_true",
                        help="Offline: prove the grader ranks known-good above known-bad (no API).")
    parser.add_argument("--grade", type=Path, metavar="BUNDLE_DIR",
                        help="Grade an evidence bundle dir (preserved/<arm>__<n>/ shape).")
    parser.add_argument("--assertions", type=Path, help="Path to the per-eval assertion set JSON.")
    parser.add_argument("--judge-cmd", type=str, default=None,
                        help="Shell command for the live judge (ask-before-run SPEND). "
                             "Reads a JSON payload on stdin, emits {verdict,evidence} JSON. "
                             "Omit to SKIP judge-kind assertions (free, offline).")
    parser.add_argument("--judge-timeout-sec", type=int, default=300)
    parser.add_argument("--output", type=Path, help="Write the markdown report here (also printed).")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.grade is not None:
        if args.assertions is None:
            parser.error("--grade requires --assertions")
        # Gate live grading on the offline self-test, exactly like the A/B harness
        # gates its live matrix: a grader that can't rank good>bad must never
        # produce a verdict we'd trust. Cheap (no API) and fail-closed.
        print("running grader self-test before grading...", file=sys.stderr)
        if selftest() != 0:
            print("refusing --grade: grader self-test failed.", file=sys.stderr)
            return 1
        assertion_set = load_assertion_set(args.assertions)
        bundle = load_bundle(args.grade)
        judge_fn = judge_via_command(args.judge_cmd, args.judge_timeout_sec) if args.judge_cmd else None
        result = grade(assertion_set, bundle, judge_fn)
        report = build_report(result)
        if args.output:
            args.output.write_text(report + "\n", encoding="utf-8")
        print(report)
        return 0
    parser.error("one of --selftest or --grade is required")


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
