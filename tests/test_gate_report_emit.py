"""Pin the emit convention in scripts/gate_report_emit.py (#457 surviving mutants).

Five of the six mutants that survived the #457 mutation run were in
`emit_findings_report`, because the module had no tests at all: mutants flipping
`ensure_ascii`, flipping `sort_keys`, and changing `indent=2` all produced output
nobody asserted on.

Each formatting argument is a real contract, not decoration:

- `ensure_ascii=False` keeps Korean/CJK findings readable instead of `\\uXXXX` soup.
- `sort_keys=True` makes two runs diffable, which is the whole point of a machine
  report.
- `indent=2` is the repo's committed-JSON convention, so an emitted payload can be
  pasted into a checked-in artifact without reformatting.
- the stream split keeps a green run's stdout quotable.

So each assertion below names the behavior the mutant would have broken.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import gate_report_emit  # noqa: E402


def _render(report: dict[str, object]) -> str:
    return f"rendered {len(report['findings'])} finding(s)"


# --- stream routing ---------------------------------------------------------


def test_findings_go_to_stderr_so_a_green_stdout_stays_quotable(capsys) -> None:
    report = {"findings": [{"detail": "x"}]}
    gate_report_emit.emit_findings_report(report, as_json=False, render=_render)
    captured = capsys.readouterr()
    assert captured.err.strip() == "rendered 1 finding(s)"
    assert captured.out == ""


def test_a_clean_report_goes_to_stdout(capsys) -> None:
    report: dict[str, object] = {"findings": []}
    gate_report_emit.emit_findings_report(report, as_json=False, render=_render)
    captured = capsys.readouterr()
    assert captured.out.strip() == "rendered 0 finding(s)"
    assert captured.err == ""


def test_findings_stream_selects_by_findings_presence() -> None:
    assert gate_report_emit.findings_stream({"findings": [1]}) is sys.stderr
    assert gate_report_emit.findings_stream({"findings": []}) is sys.stdout


# --- json payload formatting ------------------------------------------------


def test_json_mode_emits_the_payload_verbatim_and_parseable(capsys) -> None:
    report = {"findings": [{"detail": "x"}], "status": "blocked"}
    gate_report_emit.emit_findings_report(report, as_json=True, render=_render)
    assert json.loads(capsys.readouterr().err) == report


def test_json_keeps_non_ascii_literal(capsys) -> None:
    """`ensure_ascii=False`: a Korean finding must stay readable to a human.

    Kills the ensure_ascii flip: with `True` this emits `\\uXXXX` escapes.
    """
    report = {"findings": [{"detail": "한글 finding"}]}
    gate_report_emit.emit_findings_report(report, as_json=True, render=_render)
    raw = capsys.readouterr().err
    assert "한글 finding" in raw
    assert "\\u" not in raw


def test_json_sorts_keys_so_two_runs_are_diffable(capsys) -> None:
    """`sort_keys=True`: kills the sort_keys flip.

    Insertion order here is deliberately reverse-alphabetical, so unsorted output
    would put `zebra` before `alpha`.
    """
    report = {"zebra": 1, "findings": [], "alpha": 2}
    gate_report_emit.emit_findings_report(report, as_json=True, render=_render)
    raw = capsys.readouterr().out
    keys = [line.split('"')[1] for line in raw.splitlines() if line.startswith("  \"")]
    assert keys == sorted(keys)
    assert keys == ["alpha", "findings", "zebra"]


def test_json_uses_a_two_space_indent(capsys) -> None:
    """`indent=2`: kills the NumberReplacer mutants on the indent argument."""
    report = {"findings": [], "status": "ok"}
    gate_report_emit.emit_findings_report(report, as_json=True, render=_render)
    raw = capsys.readouterr().out
    top_level = [line for line in raw.splitlines() if line.startswith(" ") and '"' in line]
    assert top_level, "expected indented keys in the payload"
    for line in top_level:
        indent = len(line) - len(line.lstrip(" "))
        assert indent % 2 == 0, f"indent {indent} is not a multiple of 2: {line!r}"
    assert any(line.startswith('  "') and not line.startswith('   ') for line in top_level)


def test_json_output_ends_with_exactly_one_newline(capsys) -> None:
    """The trailing newline is what makes the payload safe to pipe."""
    report: dict[str, object] = {"findings": []}
    gate_report_emit.emit_findings_report(report, as_json=True, render=_render)
    raw = capsys.readouterr().out
    assert raw.endswith("\n")
    assert not raw.endswith("\n\n")


def test_render_is_not_called_in_json_mode(capsys) -> None:
    """`--json` emits the payload verbatim, so the text renderer must not run."""
    calls: list[int] = []

    def counting_render(report: dict[str, object]) -> str:
        calls.append(1)
        return "should not appear"

    gate_report_emit.emit_findings_report(
        {"findings": []}, as_json=True, render=counting_render
    )
    assert calls == []
    assert "should not appear" not in capsys.readouterr().out
