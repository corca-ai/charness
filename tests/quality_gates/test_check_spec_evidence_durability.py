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


def test_flags_gitignored_backtick_citation(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nProof: see `artifacts/eval-summary.json` for the field.\n",
        encoding="utf-8",
    )
    result = run_script(
        "scripts/check_spec_evidence_durability.py",
        "--repo-root",
        str(repo),
        real_process=True,
    )
    assert result.returncode == 1
    assert "gitignored target" in result.stderr
    assert "artifacts/eval-summary.json" in result.stderr


def test_flags_gitignored_markdown_link_citation(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nSee [eval](../../artifacts/eval-summary.json) for proof.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr


def test_passes_when_reproduction_marker_present(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRun `make eval` to refresh `artifacts/eval-summary.json` <!-- reproduction-source -->.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "citation",
    [
        pytest.param(
            "- Proof: `artifacts/eval-summary.json`\n"
            "  is reproduction-only. <!-- reproduction-source -->\n",
            id="two-space-unordered-continuation",
        ),
        pytest.param(
            "* Proof: `artifacts/eval-summary.json`\n"
            "   is reproduction-only. <!-- reproduction-source -->\n",
            id="three-space-unordered-continuation",
        ),
        pytest.param(
            "1. Proof: `artifacts/eval-summary.json`\n"
            "   is reproduction-only. <!-- reproduction-source -->\n",
            id="ordered-list-continuation",
        ),
    ],
)
def test_passes_when_marker_is_on_citation_continuation(
    tmp_path: Path,
    citation: str,
) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(f"# Demo Spec\n\n{citation}", encoding="utf-8")
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "citation",
    [
        pytest.param(
            "- Proof: `artifacts/eval-summary.json`\n<!-- reproduction-source -->\n",
            id="unindented-following-line",
        ),
        pytest.param(
            "- Proof: `artifacts/eval-summary.json`\n"
            "  1. <!-- reproduction-source -->\n",
            id="ordered-nested-item",
        ),
        pytest.param(
            "- Proof: `artifacts/eval-summary.json`\n  - <!-- reproduction-source -->\n",
            id="unordered-nested-item",
        ),
        pytest.param(
            "- Proof: `artifacts/eval-summary.json`\n  > <!-- reproduction-source -->\n",
            id="nested-block-quote",
        ),
        pytest.param(
            "<!-- reproduction-source -->\n\n"
            "Proof: see `artifacts/eval-summary.json`.\n",
            id="unrelated-preceding-line",
        ),
    ],
)
def test_marker_outside_citation_continuation_does_not_exempt(
    tmp_path: Path,
    citation: str,
) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(f"# Demo Spec\n\n{citation}", encoding="utf-8")
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "gitignored target" in result.stderr


def test_passes_when_path_is_checked_in(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    proof = repo / "charness-artifacts" / "spec" / "demo-proof.md"
    proof.write_text("# Demo Proof\n\nClaim: ok.\n", encoding="utf-8")
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nSee [proof](./demo-proof.md) for the claim.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_skips_paths_inside_fenced_code_blocks(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\n```\ncat artifacts/eval-summary.json\n```\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


@pytest.mark.slow_corpus
def test_real_repo_passes(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo_root))
    assert result.returncode == 0, result.stderr


def test_marker_matching_is_case_insensitive(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRefresh `artifacts/eval-summary.json` <!-- Reproduction-Source -->.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 0, result.stderr


def test_inline_command_with_space_is_not_flagged(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    spec = repo / "charness-artifacts" / "spec" / "demo.md"
    spec.write_text(
        "# Demo Spec\n\nRun `cat artifacts/eval-summary.json` to inspect.\n",
        encoding="utf-8",
    )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
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


def test_scope_covers_quality_release_dogfood_subdirs(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    for subdir in ("quality", "release", "dogfood", "debug", "premortem"):
        target = repo / "charness-artifacts" / subdir
        target.mkdir(parents=True, exist_ok=True)
        (target / "demo.md").write_text(
            "# Demo\n\nProof: `artifacts/eval-summary.json`.\n",
            encoding="utf-8",
        )
    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))
    assert result.returncode == 1
    for subdir in ("quality", "release", "dogfood", "debug", "premortem"):
        assert f"charness-artifacts/{subdir}/demo.md" in result.stderr


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


def test_a_new_dated_artifact_in_a_late_family_is_enforced(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "goals", "2999-01-01-demo.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1, result.stdout
    assert "charness-artifacts/goals/2999-01-01-demo.md" in result.stderr


def test_every_late_family_is_actually_wired(tmp_path: Path) -> None:
    """One assertion per family. A widening that reaches five of six directories
    is indistinguishable from one that reaches all six until the sixth is the one
    carrying the dead citation."""
    repo = _bootstrap_repo(tmp_path)
    families = ("goals", "critique", "retro", "probe", "issues", "release-review")
    for family in families:
        _late_doc(repo, family, "2999-01-01-demo.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1
    for family in families:
        assert f"charness-artifacts/{family}/2999-01-01-demo.md" in result.stderr, family


def test_a_frozen_older_record_is_counted_not_blocked(tmp_path: Path) -> None:
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "retro", "2020-01-01-demo.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "1 citation(s) to gitignored targets remain" in result.stdout


def test_the_grandfathered_debt_is_never_silent(tmp_path: Path) -> None:
    """The exclusion must arrive as a NUMBER, not as an absence.

    A gate that quietly drops part of its own scope reports the same clean line
    as one with nothing to drop, and this exclusion is deliberate debt with a date
    on it. Two docs, so the count is asserted rather than merely present.
    """
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "retro", "2020-01-01-a.md")
    _late_doc(repo, "critique", "2020-01-02-b.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "2 citation(s) to gitignored targets remain" in result.stdout
    # The POPULATION clause, not just the count. Round 1 blocked on this sentence
    # describing a set the gate did not have; asserting only the digits would have
    # passed against the wording it rejected.
    assert "whose FILENAME date precedes" in result.stdout
    assert "whatever its body says -- is enforced" in result.stdout


def test_an_undated_artifact_is_ENFORCED_not_exempt(tmp_path: Path) -> None:
    """THE fail-closed pin, and the one a revert would trip.

    The first cut exempted any doc without a leading filename date. A fresh-eye
    round measured the hole: 68 checked-in artifacts in these families carry no
    parseable date, 64 in `critique/` and `retro/`, overwhelmingly one-shot
    `*-packet.md` review artifacts -- the files carrying the MOST run-output
    citations, undated by this repo's own naming convention. So the exemption was
    not date-bounded debt that shrinks; it GREW with every new packet, opened by
    omitting a convention nothing validates, and one live violation already sat
    in it.

    `critique_enforcement_scope.observed_date` states the rule this restores:
    callers "must NOT treat `None` as fail-open by default".
    """
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "critique", "some-review-packet.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1, result.stdout
    assert "charness-artifacts/critique/some-review-packet.md" in result.stderr


def test_an_impossible_filename_date_does_not_buy_exemption(tmp_path: Path) -> None:
    """`0000-00-00-x.md` string-compares below any cutoff. Routing an unparseable
    date to `None`, and `None` to ENFORCED, closes that by construction rather
    than by enumerating bad dates."""
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "critique", "0000-00-00-my-review.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1, result.stdout
    assert "0000-00-00-my-review.md" in result.stderr


def test_a_body_date_cannot_grandfather_an_undated_filename(tmp_path: Path) -> None:
    """THE round-2 blocker pin: one author-written line must not buy an exemption.

    The first fail-closed cut delegated to `observed_date`, which is
    `max(body_date, filename_date)`. Its safety argument is CORROBORATION -- exempt
    only when both channels agree the artifact is old -- and that argument inverts
    on this corpus, which is defined by having no filename date. The body line is
    then the only channel, so `Date: 2020-01-01` in a new review packet bought a
    permanent exemption. Four checked-in docs already take their date from the body
    alone, one of them a rolling pointer file whose body date is author-maintained.
    """
    repo = _bootstrap_repo(tmp_path)
    target = repo / "charness-artifacts" / "critique"
    target.mkdir(parents=True, exist_ok=True)
    (target / "some-review-packet.md").write_text(
        "# Demo\nDate: 2020-01-01\n\nProof: `artifacts/eval-summary.json`.\n", encoding="utf-8"
    )

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1, result.stdout
    assert "some-review-packet.md" in result.stderr


def test_the_filename_decides_even_against_a_later_body_date(tmp_path: Path) -> None:
    """The filename is the ONLY grandfathering channel, so a genuinely old artifact
    stays history regardless of what its body says. Stated as a test because the
    single-channel rule is a deliberate narrowing of the repo's shared helper, not
    an oversight -- and because a future editor restoring `observed_date` here
    would reopen the blocker above."""
    repo = _bootstrap_repo(tmp_path)
    target = repo / "charness-artifacts" / "goals"
    target.mkdir(parents=True, exist_ok=True)
    (target / "2020-01-01-demo.md").write_text(
        "# Demo\nDate: 2999-01-01\n\nProof: `artifacts/eval-summary.json`.\n", encoding="utf-8"
    )

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
    assert "1 citation(s) to gitignored targets remain" in result.stdout


def test_the_excluded_count_is_reported_on_a_FAILING_run_too(tmp_path: Path) -> None:
    """A failure carries a signal about the failures and nothing about the floors
    that were off. Without this, an operator fixes the one named file, re-runs,
    and meets the excluded count only AFTER concluding the scope was complete."""
    repo = _bootstrap_repo(tmp_path)
    _late_doc(repo, "retro", "2020-01-01-old.md")
    _late_doc(repo, "goals", "2999-01-01-new.md")

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 1
    assert "2999-01-01-new.md" in result.stderr
    assert "1 citation(s) to gitignored targets remain" in result.stdout


def test_the_reproduction_marker_still_releases_a_new_artifact(tmp_path: Path) -> None:
    """The widening must not remove the escape hatch, or the only way to record a
    genuinely ephemeral reproduction source becomes lying about it."""
    repo = _bootstrap_repo(tmp_path)
    target = repo / "charness-artifacts" / "goals"
    target.mkdir(parents=True, exist_ok=True)
    (target / "2999-01-01-demo.md").write_text(
        "# Demo\n\n- Proof: `artifacts/eval-summary.json` <!-- reproduction-source -->\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check_spec_evidence_durability.py", "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
