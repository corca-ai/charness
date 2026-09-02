"""Pin the emit convention in scripts/core/gate_report_emit.py (#457 surviving mutants).

Five of the six mutants that survived the #457 mutation run were in
`emit_findings_report`, because the module had no tests at all: mutants flipping
`ensure_ascii`, flipping `sort_keys`, and changing `indent=2` all produced output
nobody asserted on.

The 2026-08-14 removal of `--json` made output unconditionally YAML and moved the
serializer arguments themselves into `scripts/yaml_output.render_yaml`. The
mutants those arguments carried are still live, so each one is still pinned here
-- but through the OBSERVABLE output of `emit_findings_report`, not by naming an
argument this module no longer passes. Asserting the emitted bytes is what keeps
the protection attached to the behavior when the serializer moves again.

Each property below names the behavior a mutant would break:

- non-ASCII stays literal (`ensure_ascii=False` + `allow_unicode=True`) so
  Korean/CJK findings read as text instead of `\\uXXXX` soup.
- two runs of the same report are byte-identical and emit keys in payload order
  (`sort_keys=False`), which is what makes a machine report diffable. Note this
  is the deliberate REVERSAL of the old `sort_keys=True` JSON contract: YAML
  preserves the payload's own order, so insertion order is now the stable order.
- nested blocks indent by two, the repo's committed-artifact convention, so an
  emitted payload can be pasted into a checked-in artifact without reformatting.
- the stream split keeps a green run's stdout quotable.
- there is no text-renderer branch left to select. A dead format switch on a
  shared emitter is the exact residue the migration removed, so the absence of
  one is asserted rather than assumed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

from scripts.core import gate_report_emit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


# --- stream routing ---------------------------------------------------------


def test_findings_go_to_stderr_so_a_green_stdout_stays_quotable(capsys) -> None:
    report = {"findings": [{"detail": "x"}]}
    gate_report_emit.emit_findings_report(report)
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.err) == report
    assert captured.out == ""


def test_a_clean_report_goes_to_stdout(capsys) -> None:
    report: dict[str, object] = {"findings": []}
    gate_report_emit.emit_findings_report(report)
    captured = capsys.readouterr()
    assert yaml.safe_load(captured.out) == report
    assert captured.err == ""


def test_findings_stream_selects_by_findings_presence() -> None:
    assert gate_report_emit.findings_stream({"findings": [1]}) is sys.stderr
    assert gate_report_emit.findings_stream({"findings": []}) is sys.stdout


# --- payload formatting -----------------------------------------------------


def test_the_payload_is_emitted_verbatim_and_parseable(capsys) -> None:
    report = {"findings": [{"detail": "x"}], "status": "blocked"}
    gate_report_emit.emit_findings_report(report)
    assert yaml.safe_load(capsys.readouterr().err) == report


def test_output_keeps_non_ascii_literal(capsys) -> None:
    """`ensure_ascii=False` / `allow_unicode=True`: a Korean finding stays readable.

    Kills the ensure_ascii flip: with `True` this emits `\\uXXXX` escapes.
    """
    report = {"findings": [{"detail": "한글 finding"}]}
    gate_report_emit.emit_findings_report(report)
    raw = capsys.readouterr().err
    assert "한글 finding" in raw
    assert "\\u" not in raw


def test_output_follows_payload_key_order_so_two_runs_are_diffable(capsys) -> None:
    """`sort_keys=False`: kills the sort_keys flip.

    Insertion order here is deliberately reverse-alphabetical, so a sorting
    mutant would put `alpha` before `zebra`. YAML carries the payload's own
    order, and that order is what a gate reproduces run over run.
    """
    report = {"zebra": 1, "findings": [], "alpha": 2}
    gate_report_emit.emit_findings_report(report)
    raw = capsys.readouterr().out
    keys = [line.split(":")[0] for line in raw.splitlines() if not line.startswith(" ")]
    assert keys == ["zebra", "findings", "alpha"]
    assert keys != sorted(keys), "a sorted emit would silently reorder the payload"


def test_two_emits_of_one_report_are_byte_identical(capsys) -> None:
    """Diffability is the point of the ordering contract, so assert it directly."""
    report = {"zebra": 1, "findings": [], "alpha": 2}
    gate_report_emit.emit_findings_report(report)
    first = capsys.readouterr().out
    gate_report_emit.emit_findings_report(report)
    second = capsys.readouterr().out
    assert first == second


def test_nested_blocks_use_a_two_space_indent(capsys) -> None:
    """indent=2: kills the NumberReplacer mutants on the indent argument."""
    report = {"findings": [], "detail": {"outer": {"inner": "value"}}}
    gate_report_emit.emit_findings_report(report)
    raw = capsys.readouterr().out
    indented = [line for line in raw.splitlines() if line.startswith(" ")]
    assert indented, "expected nested keys in the payload"
    for line in indented:
        indent = len(line) - len(line.lstrip(" "))
        assert indent % 2 == 0, f"indent {indent} is not a multiple of 2: {line!r}"
    assert "  outer:" in raw
    assert "    inner: value" in raw


def test_output_ends_with_exactly_one_newline(capsys) -> None:
    """The trailing newline is what makes the payload safe to pipe."""
    report: dict[str, object] = {"findings": []}
    gate_report_emit.emit_findings_report(report)
    raw = capsys.readouterr().out
    assert raw.endswith("\n")
    assert not raw.endswith("\n\n")


# --- the format switch is gone ----------------------------------------------


def test_emit_takes_the_report_alone_so_no_format_switch_can_return(capsys) -> None:
    """There is no `as_json` selector and no injectable text `render` any more.

    The old suite proved the renderer did not run in `--json` mode. The stronger
    post-migration statement is that neither branch exists to select: a caller
    that still passes the removed keywords fails loudly instead of silently
    emitting a second format.
    """
    for removed in ("as_json", "render"):
        with pytest.raises(TypeError):
            gate_report_emit.emit_findings_report({"findings": []}, **{removed: True})
    capsys.readouterr()


def test_the_module_exposes_only_the_yaml_renderer() -> None:
    assert gate_report_emit.render_yaml is not None
    for deleted in ("format_human", "render_human", "render_text", "print_text"):
        assert not hasattr(gate_report_emit, deleted), f"{deleted} came back"
