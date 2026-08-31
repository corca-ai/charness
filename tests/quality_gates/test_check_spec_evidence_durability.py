from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_spec_evidence_durability as gate

from .support import run_script


def _bootstrap_repo(tmp_path: Path) -> Path:
    from .repo_shapes import install_committed_repo

    repo = install_committed_repo(
        tmp_path / "repo",
        {".gitignore": "artifacts/\n"},
        message="init",
    )
    (repo / "charness-artifacts" / "spec").mkdir(parents=True)
    (repo / "artifacts").mkdir()
    (repo / "artifacts" / "eval-summary.json").write_text("{}\n", encoding="utf-8")
    return repo


def test_citation_grammar_is_judged_in_one_ignore_query(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec"
    (spec / "demo-proof.md").write_text("# Demo Proof\n\nClaim: ok.\n", encoding="utf-8")
    failing = {
        "backtick.md": "Proof: see `artifacts/eval-summary.json` for the field.\n",
        "link.md": "See [eval](../../artifacts/eval-summary.json) for proof.\n",
        "unindented.md": "- Proof: `artifacts/eval-summary.json`\n<!-- reproduction-source -->\n",
        "ordered-nested.md": "- Proof: `artifacts/eval-summary.json`\n  1. <!-- reproduction-source -->\n",
        "unordered-nested.md": "- Proof: `artifacts/eval-summary.json`\n  - <!-- reproduction-source -->\n",
        "blockquote.md": "- Proof: `artifacts/eval-summary.json`\n  > <!-- reproduction-source -->\n",
        "preceding.md": "<!-- reproduction-source -->\n\nProof: see `artifacts/eval-summary.json`.\n",
    }
    passing = {
        "marked.md": (
            "Run `make eval` to refresh `artifacts/eval-summary.json` "
            "<!-- reproduction-source -->.\n"
        ),
        "case.md": "Refresh `artifacts/eval-summary.json` <!-- Reproduction-Source -->.\n",
        "two-space.md": (
            "- Proof: `artifacts/eval-summary.json`\n"
            "  is reproduction-only. <!-- reproduction-source -->\n"
        ),
        "three-space.md": (
            "* Proof: `artifacts/eval-summary.json`\n"
            "   is reproduction-only. <!-- reproduction-source -->\n"
        ),
        "ordered.md": (
            "1. Proof: `artifacts/eval-summary.json`\n"
            "   is reproduction-only. <!-- reproduction-source -->\n"
        ),
        "checked-in.md": "See [proof](./demo-proof.md) for the claim.\n",
        "fenced.md": "```\ncat artifacts/eval-summary.json\n```\n",
        "inline-command.md": "Run `cat artifacts/eval-summary.json` to inspect.\n",
    }
    for name, body in {**failing, **passing}.items():
        (spec / name).write_text(f"# Demo Spec\n\n{body}", encoding="utf-8")
    extra_dirs = ("quality", "release", "dogfood", "debug", "premortem")
    for subdir in extra_dirs:
        target = repo / "charness-artifacts" / subdir
        target.mkdir(parents=True, exist_ok=True)
        (target / "demo.md").write_text(
            "# Demo\n\nProof: `artifacts/eval-summary.json`.\n", encoding="utf-8"
        )

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr
    for name in failing:
        assert name in result.stderr, name
    for name in passing:
        assert name not in result.stderr, name
    for subdir in extra_dirs:
        assert f"charness-artifacts/{subdir}/demo.md" in result.stderr


@pytest.mark.slow_corpus
def test_real_repo_passes(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo_root))
    assert result.returncode == 0, result.stderr


def test_skips_when_repo_has_no_git_directory(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    spec_dir = repo / "charness-artifacts" / "spec"
    spec_dir.mkdir(parents=True)
    (spec_dir / "demo.md").write_text(
        "# Demo Spec\n\nProof: `artifacts/eval-summary.json`.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr
    assert "no git work tree" in result.stdout


def test_main_batches_all_citation_paths_into_one_git_ignore_query(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec_dir = repo / "charness-artifacts" / "spec"
    for name in ("one.md", "two.md"):
        (spec_dir / name).write_text(
            f"# Demo\n\nProof: `artifacts/{name}.json`.\n", encoding="utf-8"
        )
    calls: list[list[Path]] = []

    def all_ignored(_root: Path, paths: list[Path]) -> set[Path]:
        calls.append(paths)
        return set(paths)

    monkeypatch.setattr(gate, "git_check_ignore", all_ignored)
    monkeypatch.setattr(
        "sys.argv", ["check_spec_evidence_durability.py", "--repo-root", str(repo)]
    )

    assert gate.main() == 1
    assert len(calls) == 1
    assert {path.name for path in calls[0]} == {"one.md.json", "two.md.json"}


# --------------------------------------------------------------------------- #
# Late-added evidence families (goals / critique / retro / probe / issues /
# release-review). These carry citations exactly like the families above and were
# simply never scanned: 70 already-evaporating citations across 2339 docs at the
# time of widening, against 0 in the families already covered.
#
# Enforcement is date-anchored because almost all 70 sit in CLOSED records from
# months back. Rewriting a frozen retro so a checker goes green is evidence
# edited to fit a gate, which is the inversion the gate exists to prevent -- so
# history is counted, and new artifacts are bound.
# --------------------------------------------------------------------------- #


def _late_doc(repo: Path, family: str, name: str) -> Path:
    target = repo / "charness-artifacts" / family
    target.mkdir(parents=True, exist_ok=True)
    doc = target / name
    doc.write_text("# Demo\n\nProof: `artifacts/eval-summary.json`.\n", encoding="utf-8")
    return doc


def test_late_family_enforcement_and_grandfathering_share_one_ignore_query(
    tmp_path: Path,
) -> None:
    repo = _bootstrap_repo(tmp_path)
    families = ("goals", "critique", "retro", "probe", "issues", "release-review")
    for family in families:
        _late_doc(repo, family, "2999-01-01-wired.md")
    _late_doc(repo, "critique", "some-review-packet.md")
    _late_doc(repo, "critique", "0000-00-00-my-review.md")
    body_dated = repo / "charness-artifacts" / "critique" / "body-dated-packet.md"
    body_dated.parent.mkdir(parents=True, exist_ok=True)
    body_dated.write_text(
        "# Demo\nDate: 2020-01-01\n\nProof: `artifacts/eval-summary.json`.\n",
        encoding="utf-8",
    )
    _late_doc(repo, "retro", "2020-01-01-old.md")
    _late_doc(repo, "critique", "2020-01-02-b.md")
    old_named = repo / "charness-artifacts" / "goals" / "2020-01-01-demo.md"
    old_named.parent.mkdir(parents=True, exist_ok=True)
    old_named.write_text(
        "# Demo\nDate: 2999-01-01\n\nProof: `artifacts/eval-summary.json`.\n",
        encoding="utf-8",
    )
    marked = repo / "charness-artifacts" / "goals" / "2999-01-01-marked.md"
    marked.write_text(
        "# Demo\n\n- Proof: `artifacts/eval-summary.json` <!-- reproduction-source -->\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    for family in families:
        assert f"charness-artifacts/{family}/2999-01-01-wired.md" in result.stderr, family
    assert "some-review-packet.md" in result.stderr
    assert "0000-00-00-my-review.md" in result.stderr
    assert "body-dated-packet.md" in result.stderr
    assert "2020-01-01-old.md" not in result.stderr
    assert "2020-01-02-b.md" not in result.stderr
    assert "2020-01-01-demo.md" not in result.stderr
    assert "2999-01-01-marked.md" not in result.stderr
    assert "3 citation(s) to gitignored targets remain" in result.stdout
    assert "whose FILENAME date precedes" in result.stdout
    assert "whatever its body says -- is enforced" in result.stdout
