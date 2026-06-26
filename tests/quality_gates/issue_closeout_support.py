from __future__ import annotations

import importlib.util
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
    subprocess.run(["git", "config", "user.name", "Codex Test"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.email", "codex-test@example.com"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )
    (repo / "README.md").write_text("# Test\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True, capture_output=True, text=True)
    command = ["git", "commit", "-m", "Resolve issue"]
    for paragraph in body.split("\n\n"):
        command.extend(["-m", paragraph])
    subprocess.run(command, cwd=repo, check=True, capture_output=True, text=True)


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
    if hotl_line is not None:
        parts.append(hotl_line)
    return "\n\n".join(parts)
