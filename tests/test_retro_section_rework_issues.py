from __future__ import annotations

import subprocess
from datetime import date
from pathlib import Path

from scripts.retro_debug import render_retro_section_rework_issues as producer_module


def test_parse_causing_skills_variants() -> None:
    assert producer_module.parse_causing_skills("Causing skill: achieve") == ["achieve"]
    assert producer_module.parse_causing_skills("**Causing skill:** `issue`, `debug`") == [
        "issue",
        "debug",
    ]
    assert producer_module.parse_causing_skills("- causing skill: one, one, two") == ["one", "two"]
    assert producer_module.parse_causing_skills(
        "text\nCausing skill: first\nCausing skill: second"
    ) == ["first"]
    assert producer_module.parse_causing_skills("No attribution") == []


def test_parse_causing_skills_drops_prose_annotation() -> None:
    # The first live instance, #773, verbatim: a parenthetical and a full stop
    # rendered as a third skill row before this was handled.
    line = "Causing skill: achieve, issue (goal-run provider operations)."
    assert producer_module.parse_causing_skills(line) == ["achieve", "issue"]
    assert producer_module.parse_causing_skills("Causing skill: `retro` (packet read); ") == [
        "retro"
    ]


def _runner(payload: object, code: int = 0, stderr: str = ""):
    def run(command, **kwargs):
        return subprocess.CompletedProcess(command, code, payload, stderr)

    return run


def _issue(number: int, created: str, body: str, title: str = "Title") -> dict[str, object]:
    return {
        "number": number,
        "title": title,
        "url": f"https://github.com/o/r/issues/{number}",
        "state": "OPEN",
        "createdAt": created,
        "closedAt": None,
        "body": body,
    }


def test_window_boundary_and_rendering(capsys) -> None:
    payload = [
        _issue(773, "2026-08-03T00:00:00Z", "Causing skill: achieve, issue", "Goal Run binding"),
        _issue(772, "2026-08-02T23:59:59Z", "Causing skill: debug"),
    ]
    assert (
        producer_module.main(
            ["--repo-root", ".", "--since", "2026-08-03"],
            runner=_runner(__import__("json").dumps(payload)),
        )
        == 0
    )
    output = capsys.readouterr().out
    assert "(1 issue(s))" in output
    assert "| achieve | 1 |\n| issue | 1 |" in output
    assert "Counts are per attribution" in output
    assert "#773 Goal Run binding (OPEN, 2026-08-03; achieve, issue)" in output
    assert "https://github.com/o/r/issues/773" in output
    assert "#772" not in output


def test_empty_window_and_failure_outputs(capsys) -> None:
    producer_module.main(["--since", "2026-08-03"], runner=_runner("[]"))
    output = capsys.readouterr().out
    assert "(0 issue(s))" in output
    assert "- (none — no `rework` issues since 2026-08-03)" in output

    assert producer_module.main(runner=_runner("", 1, "  gh failed\n")) == 0
    assert capsys.readouterr().out.startswith("Rework issues UNAVAILABLE: exit code 1: gh failed")

    assert producer_module.main(runner=_runner("", 127, "")) == 0
    assert "Rework issues UNAVAILABLE: exit code 127" in capsys.readouterr().out


def test_malformed_json_is_unavailable(capsys) -> None:
    assert producer_module.main(runner=_runner("not json")) == 0
    assert capsys.readouterr().out.startswith(
        "Rework issues UNAVAILABLE: exit code 0: malformed JSON"
    )


def test_main_command_repo_option_and_defaults(capsys, tmp_path: Path) -> None:
    calls: list[list[str]] = []

    def runner(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "[]", "")

    producer_module.main(["--repo-root", str(tmp_path)], runner=runner, today=date(2026, 9, 2))
    producer_module.main(
        ["--repo-root", str(tmp_path), "--repo", "o/r", "--label", "rework"],
        runner=runner,
        today=date(2026, 9, 2),
    )
    assert calls[0][:5] == ["gh", "issue", "list", "--label", "rework"]
    assert "--repo" not in calls[0]
    assert calls[1][-2:] == ["--repo", "o/r"]
    assert "--limit" in calls[0] and "200" in calls[0]
    assert "2026-08-03" in capsys.readouterr().out
