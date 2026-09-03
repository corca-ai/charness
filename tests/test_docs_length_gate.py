"""The docs-length gate: a page over its word budget is red, recorded pages only shrink."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

import pytest

from scripts.gates import check_docs_length as gate
from tests.quality_gates.support import ROOT


def _words(count: int) -> str:
    return " ".join(f"w{i}" for i in range(count)) + "\n"


def _seed(tmp_path: Path, body: str, *, baseline: dict[str, int] | None = None) -> Path:
    repo = tmp_path / "repo"
    (repo / "docs").mkdir(parents=True)
    (repo / "docs" / "probe.md").write_text(body, encoding="utf-8")
    if baseline is not None:
        record = repo / gate.DEFAULT_BASELINE_REL
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text(
            json.dumps(
                {
                    "schema": gate.BASELINE_SCHEMA,
                    "budget": gate.WORD_BUDGET,
                    "pages": baseline,
                    "total": sum(baseline.values()),
                }
            ),
            encoding="utf-8",
        )
    return repo


def test_an_over_budget_page_not_in_the_record_is_red(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, _words(gate.WORD_BUDGET + 1), baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 1
    err = capsys.readouterr().err
    assert f"docs/probe.md: {gate.WORD_BUDGET + 1} words, budget {gate.WORD_BUDGET}" in err
    assert "split the page along one owning question" in err
    assert "move dated evidence to charness-artifacts/" in err
    assert "fold prose into a table" in err


def test_a_page_at_the_budget_passes(tmp_path: Path) -> None:
    repo = _seed(tmp_path, _words(gate.WORD_BUDGET), baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_a_recorded_page_at_its_count_passes_and_one_more_word_fails(
    tmp_path: Path, capsys
) -> None:
    over = gate.WORD_BUDGET + 40
    repo = _seed(tmp_path, _words(over), baseline={"docs/probe.md": over})
    assert gate.main(["--repo-root", str(repo)]) == 0
    (repo / "docs" / "probe.md").write_text(_words(over + 1), encoding="utf-8")
    assert gate.main(["--repo-root", str(repo)]) == 1
    assert f"docs/probe.md: {over + 1} words, recorded {over}" in capsys.readouterr().err


def test_a_shrunk_page_prompts_to_lower_the_record(tmp_path: Path, capsys) -> None:
    over = gate.WORD_BUDGET + 40
    repo = _seed(tmp_path, _words(over - 10), baseline={"docs/probe.md": over})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert f"docs/probe.md: {over - 10} < recorded {over}; lower the record" in (
        capsys.readouterr().err
    )


def test_a_recorded_page_now_under_budget_prompts_to_drop_it(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, _words(12), baseline={"docs/probe.md": gate.WORD_BUDGET + 40})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "docs/probe.md: 12 words is under budget" in capsys.readouterr().err


def test_a_gone_page_prompts_to_drop_it(tmp_path: Path, capsys) -> None:
    repo = _seed(tmp_path, _words(12), baseline={"docs/gone.md": gate.WORD_BUDGET + 40})
    assert gate.main(["--repo-root", str(repo)]) == 0
    assert "docs/gone.md: page gone" in capsys.readouterr().err


def test_the_writer_refuses_to_raise_a_recorded_count(tmp_path: Path) -> None:
    over = gate.WORD_BUDGET + 40
    repo = _seed(tmp_path, _words(over + 5), baseline={"docs/probe.md": over})
    with pytest.raises(SystemExit, match="refusing to raise the docs-length baseline"):
        gate.main(["--repo-root", str(repo), "--write-baseline"])


def test_the_writer_refuses_a_new_over_budget_page_once_a_record_exists(tmp_path: Path) -> None:
    repo = _seed(tmp_path, _words(gate.WORD_BUDGET + 1), baseline={"docs/other.md": 2000})
    (repo / "docs" / "other.md").write_text(_words(2000), encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing to raise the docs-length baseline"):
        gate.main(["--repo-root", str(repo), "--write-baseline"])


def test_writing_the_record_lowers_it_and_the_written_record_reads_back(
    tmp_path: Path, capsys
) -> None:
    over = gate.WORD_BUDGET + 40
    repo = _seed(tmp_path, _words(over - 10), baseline={"docs/probe.md": over})
    assert gate.main(["--repo-root", str(repo), "--write-baseline"]) == 0
    assert "Wrote docs-length baseline: 1 page(s) over budget" in capsys.readouterr().out
    assert gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL) == {"docs/probe.md": over - 10}
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_fenced_code_is_not_counted() -> None:
    prose = "one two three\n"
    fenced = "```bash\n" + _words(5000) + "```\n"
    tilde = "~~~\n" + _words(5000) + "~~~\n"
    assert gate.word_count(prose + fenced + prose + tilde) == 6
    assert gate.word_count("```\n" + _words(5000)) == 0  # an unclosed fence runs to the end


def test_a_fenced_transcript_keeps_a_page_green(tmp_path: Path) -> None:
    body = _words(10) + "```\n" + _words(gate.WORD_BUDGET * 2) + "```\n"
    repo = _seed(tmp_path, body, baseline={})
    assert gate.main(["--repo-root", str(repo)]) == 0


def test_empty_universe_is_a_refusal(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text(_words(3000), encoding="utf-8")
    with pytest.raises(SystemExit, match="refusing empty matched universe"):
        gate.main(["--repo-root", str(tmp_path)])


@pytest.mark.parametrize(
    "payload, message",
    [
        ({"schema": "other", "pages": {}}, "not a charness.docs-length-baseline/v1 record"),
        ({"schema": gate.BASELINE_SCHEMA, "pages": {"docs/x.md": 0}}, "positive word counts"),
        ({"schema": gate.BASELINE_SCHEMA, "pages": ["docs/x.md"]}, "positive word counts"),
    ],
)
def test_a_malformed_record_is_refused(tmp_path: Path, payload: dict, message: str) -> None:
    repo = _seed(tmp_path, _words(3))
    record = repo / gate.DEFAULT_BASELINE_REL
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(SystemExit, match=message):
        gate.main(["--repo-root", str(repo)])


def test_live_repo_has_no_page_above_its_record() -> None:
    counts = gate.measure(ROOT, require_git=True)
    assert counts
    failures, _prompts = gate.judge(counts, gate.load_baseline(ROOT / gate.DEFAULT_BASELINE_REL))
    assert failures == []


def test_the_module_main_guard_executes(tmp_path: Path, monkeypatch) -> None:
    repo = _seed(tmp_path, _words(3), baseline={})
    monkeypatch.setattr(sys, "argv", ["check_docs_length.py", "--repo-root", str(repo)])
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_path(str(ROOT / "scripts/gates/check_docs_length.py"), run_name="__main__")
    assert excinfo.value.code == 0


def test_the_bootstrap_shim_adds_the_repo_root_once_and_an_absent_record_reads_absent(
    tmp_path: Path, monkeypatch
) -> None:
    """The two lines the changed-line proof named: the shim's insert arm and the empty record.

    The shim runs at import, when the root is already on ``sys.path`` under the
    standing runner, so its insert arm is reached only when the root is absent.
    An absent record is the state before the first ``--write-baseline``; it must
    read as absent (None, judged as empty), not as a refusal, or a fresh consumer
    repo could never run the gate.
    """
    root = str(ROOT)
    monkeypatch.setattr(sys, "path", [entry for entry in sys.path if entry != root])
    gate._load_repo_runtime_bootstrap()
    assert sys.path[0] == root
    gate._load_repo_runtime_bootstrap()
    assert sys.path.count(root) == 1
    assert gate.load_baseline(tmp_path / "absent.json") is None
    assert gate.judge({"docs/a.md": 1}, gate.load_baseline(tmp_path / "absent.json") or {}) == ([], [])


def test_the_writer_refuses_a_new_over_budget_page_when_the_record_is_empty(tmp_path: Path) -> None:
    """A record whose map reached zero is a ratchet at zero, not an absent record:
    the writer must not re-found it from whatever is over budget now."""
    repo = _seed(tmp_path, _words(gate.WORD_BUDGET + 1), baseline={})
    with pytest.raises(SystemExit, match="refusing to raise the docs-length baseline"):
        gate.main(["--repo-root", str(repo), "--write-baseline"])
    assert gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL) == {}


def test_an_absent_record_is_founded_from_the_tree(tmp_path: Path) -> None:
    repo = _seed(tmp_path, _words(gate.WORD_BUDGET + 1), baseline=None)
    assert gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL) is None
    assert gate.main(["--repo-root", str(repo), "--write-baseline"]) == 0
    assert gate.load_baseline(repo / gate.DEFAULT_BASELINE_REL) == {"docs/probe.md": gate.WORD_BUDGET + 1}
