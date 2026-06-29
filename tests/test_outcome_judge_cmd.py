from __future__ import annotations

import json
import subprocess
from pathlib import Path

from tests.script_loader import load_script_module

ROOT = Path(__file__).resolve().parents[1]
j = load_script_module("outcome_judge_cmd_under_test", ROOT / "scripts" / "outcome_judge_cmd.py")


def _claude(stdout: str = "", rc: int = 0, stderr: str = ""):
    return lambda _prompt, _timeout: subprocess.CompletedProcess("claude", rc, stdout=stdout, stderr=stderr)


def _envelope(result_text: str) -> str:
    # Mirrors `claude -p --output-format json`: model text under .result.
    return json.dumps({"type": "result", "result": result_text})


def test_judge_parses_pass_verdict() -> None:
    claude = _claude(_envelope(json.dumps({"verdict": "pass", "evidence": "chunk shape present"})))
    code, out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert code == 0 and err is None
    assert json.loads(out) == {"verdict": "pass", "evidence": "chunk shape present"}


def test_judge_tolerates_prose_and_code_fence() -> None:
    fenced = "Sure, here is my verdict:\n```json\n{\"verdict\": \"fail\", \"evidence\": \"no dispositions\"}\n```"
    code, out, _ = j.judge({"statement": "s", "context": "c"}, 10, claude=_claude(_envelope(fenced)))
    assert code == 0 and json.loads(out)["verdict"] == "fail"


def test_judge_fails_closed_on_claude_error() -> None:
    code, out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=_claude(rc=1, stderr="boom"))
    assert code == 1 and out is None and "claude -p failed" in err


def test_judge_fails_closed_on_unparseable_verdict() -> None:
    code, out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=_claude(_envelope("I cannot decide.")))
    assert code == 1 and out is None and "no parseable pass/fail verdict" in err


def test_judge_rejects_non_passfail_value() -> None:
    claude = _claude(_envelope(json.dumps({"verdict": "maybe", "evidence": "x"})))
    code, _out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert code == 1 and "no parseable pass/fail verdict" in err


def test_judge_handles_timeout() -> None:
    def boom(_prompt, _timeout):
        raise subprocess.TimeoutExpired("claude", 10)
    code, _out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=boom)
    assert code == 1 and "timed out" in err


def test_judge_truncates_evidence() -> None:
    claude = _claude(_envelope(json.dumps({"verdict": "pass", "evidence": "z" * 500})))
    _code, out, _ = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert len(json.loads(out)["evidence"]) == 300


def test_judge_reads_bare_result_when_envelope_not_json() -> None:
    # If stdout is not the json envelope, fall back to treating it as the result text.
    claude = _claude(json.dumps({"verdict": "pass", "evidence": "ok"}))
    code, out, _ = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert code == 0 and json.loads(out)["verdict"] == "pass"


def test_judge_does_not_crash_on_non_string_result() -> None:
    # A non-string envelope `result` (JSON null) must be a clean ERROR, never a crash.
    claude = _claude(json.dumps({"type": "result", "result": None}))
    code, out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert code == 1 and out is None and "no parseable pass/fail verdict" in err


def test_judge_does_not_crash_on_non_dict_envelope() -> None:
    claude = _claude(json.dumps([1, 2, 3]))  # envelope is a list, not a dict
    code, _out, err = j.judge({"statement": "s", "context": "c"}, 10, claude=claude)
    assert code == 1 and "no parseable pass/fail verdict" in err


def test_extract_verdict_tolerates_braces_before_and_after() -> None:
    # The greedy-regex bug: a brace before OR after the verdict object must not lose it.
    text = 'reasoning {not: json} then\n{"verdict": "fail", "evidence": "no disposition"}\nthanks! {bye}'
    assert j._extract_verdict_json(text) == {"verdict": "fail", "evidence": "no disposition"}


def test_extract_verdict_handles_brace_inside_evidence_string() -> None:
    # A brace inside a JSON string value must not mis-balance the scan.
    text = '{"verdict": "pass", "evidence": "presented chunk {1} with disposition"}'
    assert j._extract_verdict_json(text)["evidence"] == "presented chunk {1} with disposition"


def test_extract_verdict_prefers_last_passfail_object() -> None:
    text = '{"note": "draft"} {"verdict": "pass", "evidence": "ok"}'
    assert j._extract_verdict_json(text)["verdict"] == "pass"
    assert j._extract_verdict_json(None) is None  # non-string -> None, no crash
