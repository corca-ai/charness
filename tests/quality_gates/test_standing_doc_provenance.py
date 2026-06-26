from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from .support import ROOT, run_script

SCRIPT = "skills/public/quality/scripts/check_standing_doc_provenance.py"


def _load_checker() -> ModuleType:
    module_path = ROOT / SCRIPT
    spec = importlib.util.spec_from_file_location("tests.quality_gates.check_standing_doc_provenance", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CHECKER = _load_checker()


def _run(repo: Path) -> dict[str, object]:
    return CHECKER.run(repo.resolve())


def _returncode(payload: dict[str, object]) -> int:
    return 0 if payload["ok"] else 1


def _write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _seed_repo(tmp_path: Path, *, adapter_block: list[str]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".agents").mkdir(parents=True)
    (repo / ".agents" / "quality-adapter.yaml").write_text(
        "\n".join(
            [
                "version: 1",
                "repo: testrepo",
                "output_dir: charness-artifacts/quality",
                *adapter_block,
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return repo


STANDARD_BLOCK = [
    "standing_doc_provenance:",
    "  standing_docs:",
    "    - docs/conventions/*.md",
    "  tracking_allowlist:",
    "    - docs/conventions/tracking-ledger.md",
    "  inline_allow_marker: provenance-allow",
]


def test_flags_dated_and_multiref_standing_doc_lines(tmp_path: Path) -> None:
    """AC1: a standing-doc rule line with a date or >=2 issue refs is flagged."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        [
            "# Operating Rules",
            "",
            "Sync the mirror before validators (added 2026-05-01 after the regression).",
            "Prefer deleting drift; see #257 and #260 for the precedent.",
        ],
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    flagged_lines = {finding["line"] for finding in payload["findings"]}
    assert flagged_lines == {3, 4}
    heuristics = {h for finding in payload["findings"] for h in finding["heuristics"]}
    assert "standing_doc_date" in heuristics
    assert "standing_doc_multiple_issue_refs" in heuristics
    assert all(
        finding["path"] == "docs/conventions/operating-rules.md" for finding in payload["findings"]
    )


def test_allowlisted_tracking_doc_is_silent(tmp_path: Path) -> None:
    """AC2: a tracking doc in tracking_allowlist is not scanned even with dates/refs."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "tracking-ledger.md",
        [
            "# Tracking Ledger",
            "",
            "Follow-up 2026-06-01: #321 and #322 still open.",
        ],
    )
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["ok"] is True
    assert payload["findings"] == []
    assert "docs/conventions/tracking-ledger.md" not in payload["scanned"]


def test_single_load_bearing_trailing_ref_is_silent(tmp_path: Path) -> None:
    """AC3: a single load-bearing trailing (#NNN) with no date does not flag."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "load-bearing.md",
        [
            "# Load Bearing",
            "",
            "Sync the mirror before validators; the pre-commit gate blocks the split (#257).",
        ],
    )
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["ok"] is True
    assert payload["findings"] == []
    assert "docs/conventions/load-bearing.md" in payload["scanned"]


def test_mixed_corpus_flags_only_the_standing_doc(tmp_path: Path) -> None:
    """AC1+AC2+AC3 together: only the standing rule doc is flagged."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        ["# Rules", "", "Added 2026-05-01 after the mirror regression."],
    )
    _write(
        repo / "docs" / "conventions" / "tracking-ledger.md",
        ["# Ledger", "", "2026-06-01: #321 / #322 open."],
    )
    _write(
        repo / "docs" / "conventions" / "load-bearing.md",
        ["# LB", "", "The pre-commit gate blocks the staged/unstaged split (#257)."],
    )
    payload = _run(repo)
    assert _returncode(payload) == 1
    flagged_paths = {finding["path"] for finding in payload["findings"]}
    assert flagged_paths == {"docs/conventions/operating-rules.md"}
    assert set(payload["scanned"]) == {
        "docs/conventions/load-bearing.md",
        "docs/conventions/operating-rules.md",
    }


def test_inert_when_no_standing_docs_configured(tmp_path: Path) -> None:
    """AC4: empty standing_docs makes the check inert (stack-neutral default)."""
    repo = _seed_repo(
        tmp_path,
        adapter_block=["standing_doc_provenance:", "  standing_docs: []"],
    )
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        ["# Rules", "", "Added 2026-05-01 after the regression."],
    )
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["inert"] is True
    assert payload["findings"] == []

    assert "inert" in CHECKER._render_plain(payload)


def test_no_adapter_block_defaults_inert(tmp_path: Path) -> None:
    """No standing_doc_provenance block at all defaults to inert."""
    repo = _seed_repo(tmp_path, adapter_block=[])
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["inert"] is True


def test_fenced_and_inline_marked_lines_are_skipped(tmp_path: Path) -> None:
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        [
            "# Rules",
            "",
            "```text",
            "smell example: added 2026-05-01 after #257 and #260",
            "```",
            "A genuinely load-bearing dated fact stays here. 2026-05-15 <!-- provenance-allow -->",
        ],
    )
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["findings"] == []
    assert "docs/conventions/operating-rules.md" in payload["scanned"]


def test_sanctioned_placements_are_not_flagged(tmp_path: Path) -> None:
    """The check must not over-fire on the placements the policy *prescribes*:
    a date inside a record-layer link / raw record path, and refs/dates inside
    inline-code examples. Only free-prose diary noise flags."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        [
            "# Rules",
            "",
            "Background: [the retro](../../charness-artifacts/retro/2026-05-01-mirror.md).",
            "Background: charness-artifacts/retro/2026-06-07-producer-rerun-waste.md explains it.",
            "Banned anchors look like `#310`, `owner/repo#5`; a dated `2026-06-05 lesson` too.",
            "The pre-commit gate blocks the staged/unstaged split (#257).",
        ],
    )
    payload = _run(repo)
    assert _returncode(payload) == 0
    assert payload["findings"] == []


def test_stacked_refs_in_link_text_still_flag(tmp_path: Path) -> None:
    """Masking removes link *targets*, not link *text* — stacked refs in the
    visible text are diary noise and must still flag."""
    repo = _seed_repo(tmp_path, adapter_block=STANDARD_BLOCK)
    _write(
        repo / "docs" / "conventions" / "operating-rules.md",
        [
            "# Rules",
            "",
            "Contract for [#230 + #229](../../x.md) self-substitution.",
        ],
    )
    payload = _run(repo)
    assert _returncode(payload) == 1
    assert payload["findings"][0]["heuristics"] == ["standing_doc_multiple_issue_refs"]


def test_invalid_adapter_block_fails_with_error(tmp_path: Path) -> None:
    repo = _seed_repo(
        tmp_path,
        adapter_block=["standing_doc_provenance: not-a-mapping"],
    )
    result = run_script(SCRIPT, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["adapter_errors"]
    assert "standing_doc_provenance must be a mapping" in payload["adapter_errors"][0]
