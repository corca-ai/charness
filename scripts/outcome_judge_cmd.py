#!/usr/bin/env python3

"""Reference LIVE judge adapter for grade_skill_outcome.py's `--judge-cmd` seam.

The grader is judge-agnostic: it hands each judge-kind assertion to a shell command
as a `{"statement", "context"}` JSON payload on stdin and reads a
`{"verdict": "pass"|"fail", "evidence": "..."}` JSON back on stdout. This script is the
charness reference implementation of that command, backed by `claude -p` — so wiring
it up is the OUTCOME layer's ask-before-run LIVE token spend (one `claude -p` call per
judge-kind assertion). The grader self-tests with an injected oracle judge offline; THIS
is what makes a real verdict, and it stays a separate, swappable adapter (a different
host could point `--judge-cmd` at any other scorer) per the cautilus eval-only ownership
rule: the LLM judge lives host-side, never inside the deterministic cautilus scorer.

Fail-closed: on any claude failure or an unparseable verdict it exits non-zero with a
stderr reason, so the grader records an honest ERROR (never a silent pass/fail) for that
assertion. Usage:

  python3 scripts/grade_skill_outcome.py --grade <bundle> --assertions <set.json> \
    --judge-cmd "python3 scripts/outcome_judge_cmd.py"
"""

from __future__ import annotations

import json
import subprocess
import sys

JUDGE_PROMPT = """You are a strict, skeptical OUTCOME judge for a captured AI-agent run.
Decide whether the STATEMENT is TRUE given ONLY the EVIDENCE below (the run's summary,
tool trace, assistant transcript, and produced output files). Judge the actual produced
work, not stated intentions. Default to "fail" if the evidence does not clearly and
specifically support the statement.

Respond with ONLY a single JSON object and nothing else (no prose, no code fence):
{"verdict": "pass" or "fail", "evidence": "<=200 chars citing the specific evidence"}

STATEMENT:
%(statement)s

EVIDENCE:
%(context)s
"""


def call_claude(prompt: str, timeout_sec: int) -> subprocess.CompletedProcess:
    """Run the judge prompt through `claude -p` with structured output. Isolated as a
    seam so the parsing logic is unit-tested without a real (token-spending) call."""
    return subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json"],
        capture_output=True, text=True, timeout=timeout_sec, check=False,
    )


def _balanced_object_spans(text: str) -> list[dict]:
    """Every top-level {...} span that parses to a dict. String-aware: a brace inside a
    JSON string value does not mis-balance the scan, and braces in surrounding prose on
    either side are ignored (a non-JSON span simply fails json.loads and is discarded)."""
    objects: list[dict] = []
    i, n = 0, len(text)
    while i < n:
        if text[i] != "{":
            i += 1
            continue
        depth, in_str, esc, j = 0, False, False, i
        while j < n:
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            elif ch == '"':
                in_str = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        obj = json.loads(text[i:j + 1])
                    except json.JSONDecodeError:
                        obj = None
                    if isinstance(obj, dict):
                        objects.append(obj)
                    break
            j += 1
        i = j + 1
    return objects


def _extract_verdict_json(text: object) -> dict | None:
    """Find the verdict object, tolerating surrounding prose / a code fence / braces on
    either side. Prefers the LAST balanced {...} carrying a pass/fail verdict. Returns
    None for non-string input — a non-string envelope `result` (e.g. JSON null) is a
    clean miss (-> ERROR), never a crash."""
    if not isinstance(text, str):
        return None
    objects = _balanced_object_spans(text.strip())
    for obj in reversed(objects):
        if obj.get("verdict") in ("pass", "fail"):
            return obj
    return objects[-1] if objects else None


def judge(payload: dict, timeout_sec: int, claude=call_claude) -> tuple[int, str | None, str | None]:
    """Return (exit_code, stdout_json, stderr). exit_code != 0 (with a stderr reason)
    makes the grader mark the assertion ERROR — claude failure or an unparseable verdict
    is never silently scored as pass/fail."""
    prompt = JUDGE_PROMPT % {"statement": payload.get("statement", ""), "context": payload.get("context", "")}
    try:
        proc = claude(prompt, timeout_sec)
    except subprocess.TimeoutExpired:
        return 1, None, f"judge claude -p timed out after {timeout_sec}s"
    if proc.returncode != 0:
        return 1, None, f"judge claude -p failed (rc={proc.returncode}): {proc.stderr[-300:]}"
    # `claude -p --output-format json` wraps the model text in {"type":"result","result":...}.
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        envelope = None
    result_text = envelope.get("result", proc.stdout) if isinstance(envelope, dict) else proc.stdout
    verdict = _extract_verdict_json(result_text)
    if not verdict or verdict.get("verdict") not in ("pass", "fail"):
        return 1, None, f"judge returned no parseable pass/fail verdict: {str(result_text)[:300]}"
    out = json.dumps({"verdict": verdict["verdict"], "evidence": str(verdict.get("evidence", ""))[:300]})
    return 0, out, None


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    timeout_sec = 180
    if "--timeout-sec" in argv:
        timeout_sec = int(argv[argv.index("--timeout-sec") + 1])
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"judge adapter: stdin was not JSON: {exc}", file=sys.stderr)
        return 1
    code, out, err = judge(payload, timeout_sec)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
