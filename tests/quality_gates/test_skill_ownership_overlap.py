from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import yaml

from runtime_bootstrap import import_repo_module
from tests.quality_gates.support import ROOT, run_script

SCRIPT = "scripts/gates/check_skill_ownership_overlap.py"
_ownership_overlap = import_repo_module(ROOT / SCRIPT, "scripts.gates.check_skill_ownership_overlap")


def run_ownership_overlap(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_skill_ownership_overlap.py", *args])
    returncode = _ownership_overlap.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def test_current_repo_passes_with_seeded_allowlist() -> None:
    result = run_script(SCRIPT, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["findings"] == []
    assert payload["scanned_skills"] >= 1
    assert payload["allowlist_size"] >= 1


def test_unallowlisted_cross_namespace_artifact_write_fails(tmp_path: Path, monkeypatch, capsys) -> None:
    skills_dir = tmp_path / "skills" / "public"
    rogue = skills_dir / "rogue"
    rogue.mkdir(parents=True)
    (rogue / "SKILL.md").write_text(
        "---\nname: rogue\ndescription: \"rogue\"\n---\n\n"
        "# Rogue\n\nWrites into `<repo-root>/charness-artifacts/quality/latest.md`.\n",
        encoding="utf-8",
    )
    other = skills_dir / "neighbor"
    other.mkdir()
    (other / "SKILL.md").write_text(
        "---\nname: neighbor\ndescription: \"n\"\n---\n\n# Neighbor\n\nstays in own namespace.\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()

    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    findings = payload["findings"]
    assert len(findings) == 1
    finding = findings[0]
    assert finding["skill"] == "rogue"
    assert finding["kind"] == "artifact"
    assert finding["owner"] == "quality"
    assert finding["allowlist_entry"] == "rogue:artifact:quality:<reason>"


def test_allowlist_entry_silences_finding(tmp_path: Path, monkeypatch, capsys) -> None:
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "demo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "# Demo\n\nReads from `<repo-root>/charness-artifacts/release/latest.md`.\n",
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir()
    (scripts_dir / "check_skill_ownership_overlap.allowlist.txt").write_text(
        "demo:artifact:release:read-only cite\n", encoding="utf-8"
    )

    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["findings"] == []
    assert payload["allowlist_size"] == 1


def test_unallowlisted_adapter_namespace_mention_fails(tmp_path: Path, monkeypatch, capsys) -> None:
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "stub"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "# Stub\n\nReads `<repo-root>/.agents/quality-adapter.yaml`.\n",
        encoding="utf-8",
    )
    (tmp_path / "scripts").mkdir()

    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 2, result.stdout
    payload = yaml.safe_load(result.stdout)
    finding = payload["findings"][0]
    assert finding["kind"] == "adapter"
    assert finding["owner"] == "quality"


# --- stale-waiver advisory -----------------------------------------------------------
#
# The allowlist could only grow: it was reviewed on the way in and silent on the way out,
# so two entries described boundary decisions the code had already stopped making while
# the gate counted 27 and printed ok. The repo had already decided the right posture and
# built it for the OTHER allowlist -- "a waiver that is no longer needed is surfaced as a
# stale-allowlist advisory, never silently dropped" -- so this is scope, not a new rule.


def _seed(tmp_path: Path, allowlist_lines: list[str]) -> Path:
    """A minimal repo whose scanner produces exactly one real overlap."""
    skill = tmp_path / "skills" / "public" / "alpha"
    (skill / "scripts").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "See `.agents/beta-adapter.yaml` for the boundary.\n", encoding="utf-8"
    )
    (tmp_path / "skills" / "public" / "beta").mkdir(parents=True)
    (tmp_path / "scripts").mkdir(exist_ok=True)
    (tmp_path / _ownership_overlap.ALLOWLIST_PATH).write_text(
        "".join(f"{line}\n" for line in allowlist_lines), encoding="utf-8"
    )
    return tmp_path


def test_a_waiver_nobody_consumed_is_reported_as_stale(monkeypatch, capsys, tmp_path: Path) -> None:
    """The escape: a waiver for an overlap the scanner no longer produces.

    Its `<reason>` keeps asserting a coupling in the present tense, and a later session
    reading the allowlist as documentation -- which the required reason field invites --
    preserves a boundary that is not there.
    """
    _seed(tmp_path, [
        "alpha:adapter:beta:real -- alpha reads beta's adapter",
        "alpha:artifact:gamma:this overlap no longer exists",
    ])
    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 0, result.stdout
    payload = yaml.safe_load(result.stdout)
    # The consumed waiver must NOT be reported; a stale advisory that fires on live
    # entries is noise, and noise is how an advisory stops being read.
    assert [row["entry"] for row in payload["stale_allowlist"]] == ["alpha:artifact:gamma"]
    # The hedge the deleted renderer carried alongside each stale row: without it a
    # flagged waiver reads as a delete instruction rather than a re-check request.
    assert "re-check the entry's reason before deleting" in payload["stale_allowlist_advisory"]


def test_a_fully_consumed_allowlist_reports_no_stale_entries(monkeypatch, capsys, tmp_path: Path) -> None:
    _seed(tmp_path, ["alpha:adapter:beta:real -- alpha reads beta's adapter"])
    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["stale_allowlist"] == []
    # No stale rows means no advisory: an advisory that fires on a clean run is
    # the noise that trains a reader to skip it.
    assert "stale_allowlist_advisory" not in payload


def test_the_checked_in_allowlist_has_no_stale_entries() -> None:
    """Pinned against the live tree: this is the state the fix established, and a waiver
    going stale again should be visible as a failing pin rather than a line nobody reads.
    """
    result = run_script(SCRIPT, "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr
    stale = yaml.safe_load(result.stdout)["stale_allowlist"]
    assert stale == [], (
        "allowlist entries no longer produced by the scan: "
        f"{[e['entry'] for e in stale]}. Re-check each reason, then delete the entry — "
        "the scan reads only top-level .py/.md under each skill, so confirm the mention "
        "is really gone rather than merely out of scan scope."
    )


def test_scan_reports_scanned_files_and_uncovered_breakdown(tmp_path: Path) -> None:
    """Every run sizes what the non-recursive .py/.md scan cannot reach, as a NUMBER,
    broken down by why: nested, wrong suffix at the top level, or anywhere else under
    the skill root besides SKILL.md.
    """
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "alpha"
    (skill / "scripts" / "templates").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Alpha\n\nNo overlap here.\n", encoding="utf-8")
    (skill / "scripts" / "run.py").write_text("# scanned top-level .py\n", encoding="utf-8")
    (skill / "scripts" / "config.yaml").write_text("key: value\n", encoding="utf-8")
    (skill / "scripts" / "templates" / "nested.py").write_text(
        "# nested, never opened by the non-recursive walk\n", encoding="utf-8"
    )
    (skill / "README.md").write_text("# root file other than SKILL.md\n", encoding="utf-8")
    # references/ as well as scripts/. A first cut exercised only scripts/, and a
    # fresh-eye round showed the obvious mutant survived it: narrowing the bucket
    # condition to ("scripts",) reclassifies every references/ file the scan DOES read
    # into `skill_root_other`, so scanned files get counted as uncovered -- real
    # double-counting -- with the whole suite green.
    (skill / "references" / "deep").mkdir(parents=True)
    (skill / "references" / "notes.md").write_text("# scanned top-level .md\n", encoding="utf-8")
    (skill / "references" / "deep" / "buried.md").write_text("# nested\n", encoding="utf-8")
    # And the build-artifact exclusion, which was itself untested while being the
    # single highest-impact line in the walk.
    (skill / "scripts" / "__pycache__").mkdir()
    (skill / "scripts" / "__pycache__" / "run.cpython-310.pyc").write_bytes(b"\x00")

    result = _ownership_overlap.scan(tmp_path, set())

    assert result["scanned_files"] == 3  # SKILL.md + scripts/run.py + references/notes.md
    uncovered = result["uncovered"]
    assert uncovered["non_py_md_top_level"] == 1  # scripts/config.yaml
    # scripts/templates/nested.py + references/deep/buried.md
    assert uncovered["nested_under_scripts_or_references"] == 2
    assert uncovered["skill_root_other"] == 1  # README.md
    assert uncovered["total"] == 4
    # Reported, and deliberately NOT in `total` -- otherwise the headline number would
    # move with whether bytecode happens to be on disk.
    assert uncovered["excluded_build_artifacts"] == 1
    # Additive only: none of the extra files introduced any finding.
    assert result["findings"] == []


def test_uncovered_count_does_not_change_verdict_on_a_real_blind_spot(tmp_path: Path) -> None:
    """A real cross-namespace mention hidden in the scan's own blind spot still passes ok --
    sizing the gap must not itself start judging what's inside it (constraint: additive
    only, never a new verdict/exit code/refusal).
    """
    skills_dir = tmp_path / "skills" / "public"
    skill = skills_dir / "alpha"
    (skill / "scripts" / "templates").mkdir(parents=True)
    (skill / "SKILL.md").write_text("# Alpha\n", encoding="utf-8")
    (skill / "scripts" / "templates" / "hidden.yaml").write_text(
        "writes charness-artifacts/quality/latest.md\n", encoding="utf-8"
    )
    (skills_dir / "quality").mkdir(parents=True)

    result = _ownership_overlap.scan(tmp_path, set())

    assert result["findings"] == []
    assert result["uncovered"]["total"] >= 1
    assert result["uncovered"]["nested_under_scripts_or_references"] >= 1


def test_empty_tree_reports_zero_scanned_files_and_zero_uncovered(tmp_path: Path) -> None:
    (tmp_path / "scripts").mkdir(parents=True)

    result = _ownership_overlap.scan(tmp_path, set())

    assert result["scanned_files"] == 0
    assert result["uncovered"] == {
        "nested_under_scripts_or_references": 0,
        "non_py_md_top_level": 0,
        "skill_root_other": 0,
        "excluded_build_artifacts": 0,
        "total": 0,
    }


def test_the_published_payload_carries_the_malformed_lines_and_the_gap_list(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    """Both fields are asserted on the PAYLOAD, not on the functions that build them.

    `malformed_allowlist_lines` is the only place a dropped-and-already-stale waiver
    surfaces, and the release record says so in the sentence carrying its bump
    argument — yet nothing read the emitted key, so deleting the `main()` line that
    publishes it left the suite green and that sentence false.

    `did_not_judge`'s PUBLISH arm was likewise unpinned: only the withhold was
    asserted, so a regression restoring the conditional emission this release removed
    would have been caught by nothing. Both sibling gates pin their publish arm.
    """
    repo = _seed(tmp_path, ["alpha:adapter:beta:a real reason", "broken-entry"])
    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(repo))
    payload = yaml.safe_load(result.stdout)

    assert payload["malformed_allowlist_lines"] == [2], payload
    assert payload["allowlist_size"] == 1
    assert payload["did_not_judge"], "a run that read a file must name what it did not judge"
    assert any("cannot reach" in entry for entry in payload["did_not_judge"])


def test_a_reasonless_waiver_is_dropped_rather_than_honoured(tmp_path: Path) -> None:
    """The `<reason>` field the format declares and the comment calls REQUIRED.

    `len(parts) < 3` accepted a bare `alpha:adapter:beta`, so the field that makes a
    waiver reviewable was optional in fact — an unenforced REQUIRED in a comment. A
    reasonless entry silenced a real finding AND was consumed, so it never surfaced as
    stale either. Dropping it fails toward noticing: the mention comes back as a
    violation.
    """
    repo = _seed(tmp_path, ["alpha:adapter:beta"])
    allowlist, malformed = _ownership_overlap.parse_allowlist(repo / _ownership_overlap.ALLOWLIST_PATH)
    assert allowlist == set()
    assert malformed, "a dropped entry must be reported, not vanish"
    assert _ownership_overlap.scan(repo, allowlist)["findings"], (
        "a reasonless waiver must not silence the finding"
    )

    # The placeholder the gate's own remediation string suggests is not a reason.
    repo = _seed(tmp_path / "placeholder", ["alpha:adapter:beta:<reason>"])
    allowlist, malformed = _ownership_overlap.parse_allowlist(repo / _ownership_overlap.ALLOWLIST_PATH)
    assert allowlist == set() and malformed

    # Control: the same entry WITH a real reason is honoured and reported clean.
    repo = _seed(tmp_path / "reasoned", ["alpha:adapter:beta:documented boundary"])
    allowlist, malformed = _ownership_overlap.parse_allowlist(repo / _ownership_overlap.ALLOWLIST_PATH)
    assert allowlist == {("alpha", "adapter", "beta")}
    assert malformed == []
    assert _ownership_overlap.scan(repo, allowlist)["findings"] == []


def test_a_dropped_waiver_whose_overlap_is_gone_still_surfaces(tmp_path: Path, capsys) -> None:
    """The arm where "it resurfaces as a violation" is FALSE, and nothing else fires.

    A malformed entry is not in the allowlist, so the stale arm -- which only walks the
    allowlist -- can never report it. If its overlap still exists the mention returns as
    a violation and you notice. If the overlap is GONE there is no finding, no stale
    row, and `allowlist_size` is merely one smaller than the file's entry count: total
    silence, in the gate whose stale advisory exists to stop exactly that.

    So the parser reports its own drops rather than the comment asserting a
    fails-toward-noticing property that holds on only one of the two arms.
    """
    # Deliberately NOT `_seed`: that fixture plants a live overlap of its own, which
    # would supply the very finding this test needs to be absent.
    skill = tmp_path / "skills" / "public" / "solo"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("Mentions nobody else's namespace.\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / _ownership_overlap.ALLOWLIST_PATH).write_text(
        "ghost:adapter:nobody\n", encoding="utf-8"
    )

    allowlist, malformed = _ownership_overlap.parse_allowlist(tmp_path / _ownership_overlap.ALLOWLIST_PATH)
    result = _ownership_overlap.scan(tmp_path, allowlist)

    assert result["findings"] == [], "the overlap is gone, so nothing resurfaces"
    assert result["stale_allowlist"] == [], "and the stale arm cannot see a dropped entry"
    assert malformed == [1], "which leaves the parser's own report as the only signal"


def test_every_walk_that_read_no_file_withholds_its_gap_list(tmp_path: Path) -> None:
    """Existing is not walking, and walking is not reading.

    An ABSENT `skills/public/` returned early and withheld `did_not_judge`. A PRESENT
    but empty one fell through to the normal return, publishing gap entries for a walk
    that read no file -- the "empty gap list reads as full coverage" shape this gate
    exists to remove, on the path where it is emptiest.

    The first fix keyed on `skill_count == 0`, and a second review round showed that
    missed one level in: a skill DIRECTORY with nothing readable inside increments the
    count while reading nothing. Third case below. The invariant this asserts is about
    FILES READ, so the code is keyed on `scanned_files` to match -- the assertion
    message used to state a universal the code only held for two of the three.
    """
    absent = tmp_path / "absent"
    (absent / "scripts").mkdir(parents=True)
    empty_root = tmp_path / "empty_root"
    (empty_root / "skills" / "public").mkdir(parents=True)
    empty_skill = tmp_path / "empty_skill"
    (empty_skill / "skills" / "public" / "beta").mkdir(parents=True)
    # A skill directory that reads as nothing but CONTAINS something: no SKILL.md, so
    # `scanned_files` is 0, while one unreachable file really is sitting there.
    unreadable = tmp_path / "unreadable"
    nested = unreadable / "skills" / "public" / "alpha" / "scripts" / "templates"
    nested.mkdir(parents=True)
    (nested / "hidden.yaml").write_text(
        "# writes charness-artifacts/quality/latest.md\n", encoding="utf-8"
    )

    results = [
        _ownership_overlap.scan(path, set())
        for path in (absent, empty_root, empty_skill, unreadable)
    ]

    for result in results:
        assert result["scanned_files"] == 0
        assert "did_not_judge" not in result, (
            "a walk that read no file must not name gaps it never looked for"
        )
        assert result["stale_allowlist"] == []

    # The withhold covers what a read would have established. It must NOT zero the
    # counts a walk DID establish: the first cut returned a hardcoded empty `uncovered`,
    # so this tree reported `total: 0` with a live cross-namespace mention sitting in an
    # unreachable file. Removing an over-claim of judgment by adding an under-claim of
    # gap is the same defect one field over.
    assert results[3]["uncovered"]["total"] == 1, results[3]["uncovered"]
    assert results[3]["uncovered"]["nested_under_scripts_or_references"] == 1
    assert results[3]["scanned_skills"] == 1

    # Genuinely-empty trees still report zero, because zero is the truth there.
    for result in results[:3]:
        assert result["uncovered"]["total"] == 0

    # The walked and unwalked payloads must not drift in SHAPE. Both route through
    # `_uncovered_payload`; a separate all-zero literal for the unwalked path was a
    # second source of truth for a key set and a sum rule the code owns once.
    walked = _ownership_overlap.scan(_seed(tmp_path / "walked", []), set())
    assert walked["scanned_files"] > 0, "fixture must actually walk for this to compare"
    assert set(walked["uncovered"]) == set(results[3]["uncovered"])

    # `excluded_build_artifacts` stays OUT of `total` on the unwalked path too. The
    # fixtures above carry no build artifacts, so nothing there would catch a
    # `_uncovered_payload` that started summing it.
    artifacts = tmp_path / "artifacts"
    pyc = artifacts / "skills" / "public" / "gamma" / "scripts" / "__pycache__"
    pyc.mkdir(parents=True)
    (pyc / "x.cpython-311.pyc").write_bytes(b"\x00")
    result = _ownership_overlap.scan(artifacts, set())
    assert result["scanned_files"] == 0
    assert result["uncovered"]["excluded_build_artifacts"] == 1
    assert result["uncovered"]["total"] == 0, (
        "build artifacts are reported beside the content buckets, never summed into them"
    )

    # The ignore rule reaches the `skills/public/` level too. `_uncovered_counts` tests
    # segments relative to the skill directory, so the skill's OWN name escapes it: a
    # build-artifact directory sitting where a skill goes was counted as a skill, and
    # its files landed in a content bucket and were summed into `uncovered.total`.
    # Latent on this repo, shipping in an exported gate.
    at_skill_level = tmp_path / "at_skill_level"
    cache = at_skill_level / "skills" / "public" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "stale.cpython-311.pyc").write_bytes(b"\x00")
    result = _ownership_overlap.scan(at_skill_level, set())
    assert result["scanned_skills"] == 0, "a build-artifact directory is not a skill"
    assert result["uncovered"]["total"] == 0, (
        "and its contents must not be summed into the content total"
    )


def test_current_repo_reports_positive_scanned_files_and_uncovered(monkeypatch, capsys) -> None:
    """Pinned against the live tree: the measured gap (skills/public/setup/scripts/templates/)
    must show up as a positive nested count on every run, not just in the one-off measurement.
    """
    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(ROOT))

    assert result.returncode == 0, result.stdout + result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["scanned_files"] >= 1
    assert isinstance(payload["uncovered"]["total"], int)
    assert payload["uncovered"]["nested_under_scripts_or_references"] >= 1


def test_a_tree_with_no_public_skills_claims_no_staleness(monkeypatch, capsys, tmp_path: Path) -> None:
    """It reports zero stale entries because it SCANNED nothing, not because it checked.

    Worth pinning rather than leaving implicit: "no stale entries" after measuring
    nothing is the same declaration-without-a-reader shape this issue is about. The
    empty answer is the right one -- an unrun scan cannot call a waiver dead, and
    listing every one would be pure noise -- but the payload must still report
    `scanned_skills: 0` so the reader can tell an empty scan from a clean one.
    """
    (tmp_path / "scripts").mkdir(parents=True)
    (tmp_path / _ownership_overlap.ALLOWLIST_PATH).write_text(
        "alpha:adapter:beta:a waiver nothing can consume here\n", encoding="utf-8"
    )
    result = run_ownership_overlap(monkeypatch, capsys, "--repo-root", str(tmp_path))

    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["stale_allowlist"] == []
    assert "stale_allowlist_advisory" not in payload
    # `0 skills` used to be the ok line's own words; `scanned_skills` is what lets a
    # reader still tell an EMPTY scan from a clean one.
    assert payload["scanned_skills"] == 0
    assert payload["status"] == "ok"
