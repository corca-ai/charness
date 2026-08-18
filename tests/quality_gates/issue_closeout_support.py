from __future__ import annotations

import importlib.util
import re
import subprocess
from pathlib import Path

SCRIPT = "skills/public/issue/scripts/issue_tool.py"
VERIFY_MODULE_PATH = Path(__file__).resolve().parents[2] / "skills" / "public" / "issue" / "scripts" / "issue_verify_closeout.py"


def load_verify_module():
    spec = importlib.util.spec_from_file_location("issue_verify_closeout_test", VERIFY_MODULE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def seed_commit(repo: Path, body: str) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True, text=True)
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    command = ["git", "commit", "-m", "Resolve issue"]
    for paragraph in body.split("\n\n"):
        command.extend(["-m", paragraph])
    subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)


# Sentinel: `None` already means "omit the line", so the derive-from-close-line default
# needs a value distinguishable from it.
_DERIVE_FROM_CLOSE_LINE = object()
_ISSUE_REF = re.compile(r"#(\d+)\b")


def bug_closeout_body(
    *,
    close_line: str = "Close #42.",
    critique_line: str | None = (
        "Critique: blocked synthetic-test-harness: this test does not spawn "
        "a real resolution critique subagent"
    ),
    behavior_line: str | None = (
        "Behavior #42: behavior test tests/foo.py exercises the fixed parse path "
        "(distinct channel from CLOSED)"
    ),
    provenance_line: str | None = (
        "AI-provenance: agent-drafted via charness issue resolve; "
        "human-audited per the resolution critique"
    ),
    hotl_line: str | None = None,
    # The probe-record floor fires on any `Behavior #N:` line that CLAIMS a verification,
    # which this default body does. A synthetic fixture has no real probe behind it, so it
    # says so in the floor's own typed vocabulary rather than naming a record that does not
    # exist -- which is exactly the honest disposition the floor is built to accept.
    #
    # DERIVED from `close_line` rather than hardcoded to #42: callers that close a different
    # issue override `close_line` and `behavior_line` and would otherwise get a probe line
    # pointing at an issue this body never closes, which the floor correctly reads as the
    # obligation still unmet. Pass the string explicitly to override, or `None` to omit.
    probe_line: str | None = _DERIVE_FROM_CLOSE_LINE,
) -> str:
    parts = [
        close_line,
        "JTBD: resolve GitHub issues end-to-end.",
        "Root cause: the issue closeout carrier was prose-only.",
        "Debug artifact: charness-artifacts/debug/latest.md.",
        "Siblings: issue_tool finalization | decision: same bug, fix now | proof: static scan.",
        "Prevention: verify-closeout blocks missing carriers.",
    ]
    if critique_line is not None:
        parts.append(critique_line)
    if behavior_line is not None:
        parts.append(behavior_line)
    if provenance_line is not None:
        parts.append(provenance_line)
    if probe_line is _DERIVE_FROM_CLOSE_LINE:
        # Derived from the BEHAVIOR line first, and only then from the close line. The
        # obligation is triggered by the behavioral CLAIM, so that line is where the issue
        # numbers owing a record actually live -- and several carriers here close with a
        # keyword-free line ("Manual close comment.") whose issue number reaches the
        # verifier as an argument instead.
        #
        # ALL the numbers, not the first: a carrier closing `#42, #43` carries a
        # multi-target behavior line, and a probe line naming only `#42` leaves `#43`'s
        # claim unbacked -- which the floor correctly refuses and which reads, wrongly,
        # like the floor is broken.
        numbers = _ISSUE_REF.findall(behavior_line or "") or _ISSUE_REF.findall(close_line)
        targets = " ".join(f"#{number}" for number in numbers)
        probe_line = f"Probe record {targets}: local-only-by-contract" if numbers else None
    if probe_line is not None:
        parts.append(probe_line)
    if hotl_line is not None:
        parts.append(hotl_line)
    return "\n\n".join(parts)
