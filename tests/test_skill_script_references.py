"""Every script path shipped skill prose tells an agent to run must resolve.

Thirteen references said `<repo-root>/scripts/<name>.py` while `<name>.py` lived
in the skill's own package, so the documented command failed in this repo and in
any consuming repo alike. Three overlapping silences in `check_doc_links.py` let
them accumulate (see the checker's module docstring). This pins the repaired
state, and pins the gate posture: the DEFAULT mode never fails a run, `--strict`
(what `run-quality.sh` runs) does.

Fixtures here are built from the advisory's own shipped constants and are
cross-checked against its shipped regex before use: a fixture spelled the way
the matcher wants is precisely how this class hides.
"""
from __future__ import annotations

import collections
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from tests.script_main import load_script_module, run_loaded_script_main

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inventory_skill_script_references.py"

inventory_module = load_script_module("inventory_skill_script_references", SCRIPT_PATH)


def _broken_reference_repo(tmp_path: Path) -> Path:
    """A repo whose skill prose names a command that cannot run.

    The tier directory comes from the advisory's own `PORTABLE_SKILL_KINDS`, and
    the reference line is asserted to match the advisory's own
    `REPO_ROOT_SCRIPT_RE` -- if either drifts, this fails loudly instead of
    silently exercising nothing.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (tmp_path / "scripts").mkdir()

    # The file exists -- in the skill package, not at the repo root.
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")

    line = "Use `<repo-root>/scripts/demo_helper.py` to do the thing."
    assert inventory_module.REPO_ROOT_SCRIPT_RE.search(line), (
        "fixture no longer matches the advisory's shipped pattern"
    )
    (package / "SKILL.md").write_text(f"# Demo\n\n{line}\n", encoding="utf-8")
    return tmp_path


def _describe(rows) -> str:
    return "\n".join(
        f"  [{row['layout']}] {row['doc']}:{row['line']} `{row['reference']}` ({row['status']}"
        + (f", file is at {row['found_at']}" if row["found_at"] else "")
        + ")"
        for row in rows
    )


# Known shipped-layout findings, mapped to the exact number of sites each is
# allowed. Counting rather than merely naming them means a SECOND occurrence in
# the same file cannot slip in under an existing key.
#
# EMPTY, and that is the point: it held the two `plan_risk_interrupt.py` sites
# until #477 was decided, and shrank to nothing when they were repaired via the
# `$SKILL_DIR/../../shared/scripts/` shim. A ratchet may shrink, never grow.
#
# Every entry must be the SAME defect class as its rationale -- do not park a
# `package_file_wrong_prefix` finding here, which is the class the goal exists
# to keep at zero (see the dedicated test below).
KNOWN_SHIPPED_FINDINGS: dict[tuple[str, str], int] = {}


def test_no_authoring_layout_reference_fails_to_resolve() -> None:
    """The counted defect: 13 references whose file was in the skill package."""
    rows = inventory_module.classify_references(REPO_ROOT)
    authoring = [row for row in rows if row["layout"] == inventory_module.AUTHORING]
    findings = [row for row in authoring if row["status"] in inventory_module.ACTIONABLE]
    assert findings == [], "authoring-layout skill prose names unresolvable scripts:\n" + _describe(
        findings
    )
    # A vacuous pass is the failure mode that matters: an empty finding list means
    # nothing if the scan found no references at all. Floor each FORM separately --
    # an aggregate floor is dominated by `$SKILL_DIR` rows and would stay
    # satisfied while another form's population silently fell to zero.
    forms = collections.Counter(row["form"] for row in authoring)
    assert forms["skill-dir"] > 100
    # Floor the out-of-package forms TOGETHER: converting a reference between them
    # moves a row and must not trip a floor, but the combined population going to
    # zero still must.
    #
    # The combined number dropped from 15 to 11 when #478 was dispositioned: three
    # sites moved to `<authoring-repo>/`, three moved onto shared shims, and one
    # bullet was dropped. `plugin-dir` joined the sum on 2026-08-04 for exactly the
    # reason this floor is a SUM: 41 references were repaired from
    # `<authoring-repo>/` to `<plugin-dir>/` because the files ship to consumers,
    # and until the inventory learned that form they left measurement entirely --
    # a floor that cannot see a form reports its population as lost.
    assert forms["repo-root"] + forms["authoring-repo"] + forms["plugin-dir"] >= 10
    # Deliberately NOT `forms["repo-root"] > 0`. That pinned at least one live
    # `<repo-root>/scripts/` reference in real prose FOREVER, so correctly
    # converting the last one would fail the suite with a message about floors
    # rather than about the edit — a test coupling the repo's own cleanup to a
    # red build. The classifier arm is already proven to fire by the synthetic
    # fixtures below, which exercise it on a tmp tree where the population is
    # controlled instead of incidental.
    # `forms["authoring-repo"] > 0` was HERE and is deliberately gone, for the
    # reason the paragraph above gives about `repo-root`: on 2026-08-04 every live
    # `<authoring-repo>/scripts/` reference was correctly converted to
    # `<plugin-dir>/` (the files ship to consumers, so the old prefix was a false
    # claim), and the pin turned that correct edit into a red suite complaining
    # about a floor instead of about the edit. The classifier arm stays proven by
    # the synthetic fixtures below, which exercise BOTH its resolved and unresolved
    # outcomes on a tmp tree where the population is controlled rather than
    # incidental — which is the whole argument for not pinning live prose.
    # The 7 References bullets Lane A repaired, plus the pre-existing ones.
    assert forms["references-bullet"] >= 20


def test_shipped_layout_findings_never_grow() -> None:
    """The mirror is what agents actually read, and it is a different tree.

    A reference can resolve in `skills/public/<skill>` and not in
    `plugins/<pkg>/skills/<skill>`; the authoring scan alone cannot see that.
    """
    rows = inventory_module.classify_references(REPO_ROOT)
    shipped = [row for row in rows if row["layout"] == inventory_module.SHIPPED]
    findings = [row for row in shipped if row["status"] in inventory_module.ACTIONABLE]
    assert len(shipped) > 100
    observed = collections.Counter((row["doc"], row["reference"]) for row in findings)
    excess = {
        key: count
        for key, count in observed.items()
        if count > KNOWN_SHIPPED_FINDINGS.get(key, 0)
    }
    assert not excess, "new or multiplied shipped-layout reference(s) that cannot run:\n" + _describe(
        [row for row in findings if (row["doc"], row["reference"]) in excess]
    )


def test_no_shipped_reference_is_broken_because_its_file_is_in_the_package() -> None:
    """The counted class must be zero in the layout that actually ships too.

    Kept separate from the ratchet above so this class can never be parked as a
    known exception: `package_file_wrong_prefix` is exactly the defect the goal
    repaired, and the mirror is what an installed agent reads.
    """
    rows = inventory_module.classify_references(REPO_ROOT)
    shipped = [row for row in rows if row["layout"] == inventory_module.SHIPPED]
    # BROKEN can only ever be produced from a `<repo-root>/scripts/X.py` row, so
    # floor THAT population. An aggregate floor would stay green while the
    # candidate set fell to zero, and this test would pass forever without ever
    # looking at the class it is named for.
    # After #478, exactly ONE `<repo-root>/scripts/` reference remains repo-wide
    # (`rca-ledger-append.md`, where the path is an existence predicate the
    # reader evaluates and the spelling is correct). So this floor is now weak by
    # construction, and says so. The real guard against the BROKEN class is
    # `test_the_broken_class_is_detected_in_the_SHIPPED_layout_too`, which builds
    # the defect from a fixture in THIS layout instead of hoping a live instance
    # exists. (An earlier version of this comment cited the authoring-only
    # fixture, which does not cover the shipped branch at all.)
    candidates = [row for row in shipped if row["form"] == "repo-root"]
    assert len(candidates) >= 1, "no candidates left to classify; this test proves nothing"

    broken = [row for row in candidates if row["status"] == inventory_module.BROKEN]
    assert broken == [], _describe(broken)


def test_the_broken_class_is_detected_in_the_SHIPPED_layout_too(tmp_path: Path) -> None:
    """No fixture produced a shipped-layout `BROKEN` row until this one.

    The live floor above is weak by construction now that one `<repo-root>/`
    reference remains repo-wide, and the authoring-only fixture cannot stand in
    for it: the mirror is what an installed agent reads, and its classification
    path is a different branch.
    """
    package = tmp_path / "plugins" / "pkg" / "skills" / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\nUse `<repo-root>/scripts/demo_helper.py`.\n", encoding="utf-8"
    )

    rows = inventory_module.classify_references(tmp_path)
    shipped = [row for row in rows if row["layout"] == inventory_module.SHIPPED]
    assert [row["status"] for row in shipped] == [inventory_module.BROKEN]
    assert shipped[0]["found_at"].endswith("demo/scripts/demo_helper.py")


def test_repo_root_prefix_is_reported_when_the_file_is_in_the_skill_package(tmp_path: Path) -> None:
    rows = inventory_module.classify_references(_broken_reference_repo(tmp_path))
    broken = [row for row in rows if row["status"] == inventory_module.BROKEN]
    assert len(broken) == 1
    assert broken[0]["found_at"].endswith("demo/scripts/demo_helper.py")


def test_repo_root_prefix_is_allowed_for_a_real_authoring_repo_script(tmp_path: Path) -> None:
    """The placeholder is legitimate when the file really is a repo-level script.

    Without this, a check that flagged every `<repo-root>/` reference would break
    the escape hatch the prefix exists to provide.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "repo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\nRun `<repo-root>/scripts/repo_helper.py`.\n", encoding="utf-8"
    )

    rows = inventory_module.classify_references(tmp_path)
    assert [row["status"] for row in rows] == [inventory_module.AUTHORING_REPO]


def test_references_bullet_resolves_against_the_package(tmp_path: Path) -> None:
    """The form Lane A repaired 7 References bullets into must itself be pinned."""
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/demo_helper.py`\n", encoding="utf-8"
    )

    rows = inventory_module.classify_references(tmp_path)
    assert [(row["form"], row["status"]) for row in rows] == [
        ("references-bullet", inventory_module.IN_PACKAGE)
    ]


def test_prose_mention_of_a_consumer_script_is_not_a_finding(tmp_path: Path) -> None:
    """Illustrative prose must not be turned into a defect.

    `scripts/<name>.py` in prose usually names the READER's repo script, which
    exists in neither this package nor this repo. Reporting it would manufacture
    a finding -- the same failure as missing one.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text(
        "# Demo\n\nPoint it at your repo's `scripts/ci_check.py` when one exists.\n",
        encoding="utf-8",
    )

    assert inventory_module.classify_references(tmp_path) == []


def test_a_reference_escaping_the_repo_does_not_raise(tmp_path: Path) -> None:
    """`$SKILL_DIR/../../../..` can resolve outside the tree; that must not crash."""
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "repo" / "skills" / tier / "demo"
    package.mkdir(parents=True)
    outside = tmp_path / "outside.py"
    outside.write_text("print('ok')\n", encoding="utf-8")
    depth = "../" * (len(package.relative_to(tmp_path / "repo").parts) + 1)
    (package / "SKILL.md").write_text(
        f"# Demo\n\nRun `$SKILL_DIR/{depth}outside.py`.\n", encoding="utf-8"
    )

    rows = inventory_module.classify_references(tmp_path / "repo")
    assert [row["status"] for row in rows] == [inventory_module.IN_PACKAGE]
    assert rows[0]["found_at"] == outside.as_posix()


@pytest.mark.boundary_contract(
    reason="the documented command must exercise the script's __main__ dispatch"
)
def test_the_documented_command_actually_runs_as_a_command(tmp_path: Path) -> None:
    """Invoke the advisory the way its own docs tell a reader to invoke it.

    Every other test here calls `main()` in-process, which never executes the
    `if __name__ == "__main__"` entrypoint — so the *documented* invocation
    would be the one thing this file never proved. For a goal about commands
    that cannot run, that gap is the wrong one to leave open, and it is why this
    is a subprocess test rather than a `# pragma: no cover`.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/demo_helper.py`\n", encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--repo-root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert payload["denominator"]["references_scanned"] == 1
    assert payload["findings"] == []


def test_a_repo_root_reference_to_a_consumer_file_is_never_a_finding(tmp_path: Path) -> None:
    """`<repo-root>/` is the reader's tree, so absence here is not a defect.

    A skill legitimately says "point your standing gate at
    `<repo-root>/scripts/run_pre_push.py`" about a file only the consumer has.
    An earlier version called that `unresolved`, which armed the gate against
    the very escape hatch `authoring-preflight.md` documents as exempt.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (package / "SKILL.md").write_text(
        "# Demo\n\nPoint your gate at `<repo-root>/scripts/run_pre_push.py`.\n",
        encoding="utf-8",
    )

    rows = inventory_module.classify_references(tmp_path)
    assert [row["status"] for row in rows] == [inventory_module.CONSUMER_PLACEHOLDER]
    assert not [row for row in rows if row["status"] in inventory_module.ACTIONABLE]


def test_a_references_bullet_resolving_nowhere_is_still_a_finding(tmp_path: Path) -> None:
    """A `## References` bullet IS package-relative, so absence is decidable."""
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/phantom.py`\n", encoding="utf-8"
    )

    rows = inventory_module.classify_references(tmp_path)
    assert [row["status"] for row in rows] == [inventory_module.UNRESOLVED]


def test_the_authoring_marker_resolves_for_every_shipped_package_shape(tmp_path: Path) -> None:
    """`plugins/<pkg>/shared` is two deep where `skills/<x>` is three.

    A fixed `.parent.parent` is right for two shapes and silently wrong for the
    third, which made every `<authoring-repo>/` reference under `skills/shared`
    an unfixable refusal — i.e. following the tool's own printed advice broke
    the gate. The root is carried per package instead of counted backwards.
    """
    plugin = tmp_path / "plugins" / "demo"
    (plugin / "scripts").mkdir(parents=True)
    (plugin / "scripts" / "real.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "real.py").write_text("print('authoring')\n", encoding="utf-8")
    line = "`charness` ships `<authoring-repo>/scripts/real.py`.\n"
    for rel in ("skills/one", "support/two", "shared"):
        target = plugin / rel
        target.mkdir(parents=True)
        (target / "DOC.md").write_text(f"# D\n\n{line}", encoding="utf-8")

    shapes = {pkg.root.name: pkg.authoring_root for pkg in inventory_module.iter_skill_packages(tmp_path)}
    assert shapes == {"one": plugin, "two": plugin, "shared": plugin}

    rows = inventory_module.classify_references(tmp_path)
    assert len(rows) == 3
    assert {row["status"] for row in rows} == {inventory_module.AUTHORING_MARKED}


def test_the_authoring_marker_resolves_docs_and_artifacts_in_both_layouts(tmp_path: Path) -> None:
    """The placeholder covers the whole authoring tree, not only scripts/."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "design-north-star.md").write_text("# North Star\n", encoding="utf-8")
    (tmp_path / "charness-artifacts" / "spec").mkdir(parents=True)
    (tmp_path / "charness-artifacts" / "spec" / "ledger.md").write_text("# Ledger\n", encoding="utf-8")
    source_doc = _package(tmp_path, "skills/public/demo") / "SKILL.md"
    source_doc.write_text(
        "# Demo\n\n"
        "Read `<authoring-repo>/docs/design-north-star.md`.\n"
        "Read `<authoring-repo>/charness-artifacts/spec/ledger.md`.\n"
        "Read `<authoring-repo>/docs/missing.md`.\n",
        encoding="utf-8",
    )
    shipped_doc = _package(tmp_path, "plugins/demo/skills/demo") / "SKILL.md"
    shipped_doc.write_text(source_doc.read_text(encoding="utf-8"), encoding="utf-8")

    rows = [
        row
        for row in inventory_module.classify_references(tmp_path)
        if row["form"] == "authoring-repo"
    ]
    assert len(rows) == 6
    resolved = [row for row in rows if row["reference"].endswith(("design-north-star.md", "ledger.md"))]
    missing = [row for row in rows if row["reference"].endswith("missing.md")]
    assert {row["status"] for row in resolved} == {inventory_module.AUTHORING_MARKED}
    assert len(missing) == 2
    assert {row["status"] for row in missing} == {inventory_module.UNRESOLVED}


def _package(root: Path, rel: str) -> Path:
    target = root / rel
    target.mkdir(parents=True, exist_ok=True)
    return target


def test_a_file_sitting_in_plugins_is_skipped_not_treated_as_a_package(tmp_path: Path) -> None:
    """`plugins/*` globs paths, not directories.

    A stray file there (a README, a marketplace manifest, an editor artifact)
    must be skipped rather than walked as a plugin root — otherwise every
    `<authoring-repo>/` reference would resolve against a non-directory.
    """
    (tmp_path / "plugins").mkdir()
    (tmp_path / "plugins" / "marketplace.json").write_text("{}\n", encoding="utf-8")
    real = tmp_path / "plugins" / "demo" / "skills" / "one"
    real.mkdir(parents=True)
    (real / "DOC.md").write_text("# D\n", encoding="utf-8")

    roots = {pkg.root for pkg in inventory_module.iter_skill_packages(tmp_path)}
    assert roots == {real}


def test_the_counted_defect_is_caught_across_packages_not_just_within_one(tmp_path: Path) -> None:
    """`skills/shared` prose naming another package's script is the common shape.

    Checking only the REFERRING package's `scripts/` missed it entirely — the
    doc has no owning package for that file. Fixing a false positive re-opened
    this false negative in the counted class, so it is pinned separately.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    owner = _package(tmp_path, f"skills/{tier}/quality")
    (owner / "scripts").mkdir()
    (owner / "scripts" / "only_in_a_package.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    shared = _package(tmp_path, "skills/shared/references")
    (shared / "d.md").write_text(
        "# D\n\nRun `<repo-root>/scripts/only_in_a_package.py`.\n", encoding="utf-8"
    )

    findings = [
        row
        for row in inventory_module.classify_references(tmp_path)
        if row["status"] in inventory_module.ACTIONABLE
    ]
    assert len(findings) == 1
    assert findings[0]["status"] == inventory_module.BROKEN


def test_a_basename_in_both_a_package_and_the_root_is_not_refused(tmp_path: Path) -> None:
    """Ambiguous is not blockable.

    `plan_risk_interrupt.py` is BOTH `scripts/plan_risk_interrupt.py` and the
    `skills/shared/scripts/` shim, so a true sentence about the repo-level
    planner would otherwise be refused — with advice pointing at the shim, i.e.
    a refusal no correct edit can clear.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    owner = _package(tmp_path, f"skills/{tier}/quality")
    (owner / "scripts").mkdir()
    (owner / "scripts" / "twin.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "twin.py").write_text("print('ok')\n", encoding="utf-8")
    shared = _package(tmp_path, "skills/shared/references")
    (shared / "d.md").write_text("# D\n\nRun `<repo-root>/scripts/twin.py`.\n", encoding="utf-8")

    rows = inventory_module.classify_references(tmp_path)
    assert [row["status"] for row in rows] == [inventory_module.AUTHORING_REPO]


def test_no_second_output_mode_can_diverge_on_the_exit_code(tmp_path: Path) -> None:
    """The invariant behind the old `--json` hole, pinned at its root.

    Two renderings of one verdict diverged twice -- once in the findings branch,
    once in the zero-references branch -- because each computed its own exit. The
    removal of `--json` makes that class unreachable rather than merely tested:
    there is one payload, one exit code, and no selector to disagree with.
    """
    repo = _broken_reference_repo(tmp_path)
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(repo),
        "--strict",
    )
    assert result.returncode == 1
    assert yaml.safe_load(result.stdout)["refuse"] is True
    with pytest.raises(SystemExit) as excinfo:
        inventory_module.build_parser().parse_args(["--strict", "--json"])
    assert excinfo.value.code == 2


def test_strict_refuses_a_blind_scan_that_found_no_references_at_all(tmp_path: Path) -> None:
    """The blind case that lands in the zero-references branch.

    An unreadable doc that was a package's ONLY doc took the early
    `nothing was checked` return, which was an unconditional 0 — so `--strict`
    went green while the structured mode refused the same tree.
    """
    if os.geteuid() == 0:
        pytest.skip("root can read a chmod-000 file")
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = _package(tmp_path, f"skills/{tier}/demo")
    locked = package / "only.md"
    locked.write_text("nothing readable\n", encoding="utf-8")
    locked.chmod(0o000)
    try:
        result = run_loaded_script_main(
            "inventory_skill_script_references",
            inventory_module,
            "--repo-root",
            str(tmp_path),
            "--strict",
        )
    finally:
        locked.chmod(0o644)
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["verdict"] == "not-run"
    assert payload["refuse"] is True


def test_strict_refuses_when_a_doc_could_not_be_read(tmp_path: Path) -> None:
    """`--strict` must refuse on "I could not look", not only on findings."""
    if os.geteuid() == 0:
        pytest.skip("root can read a chmod-000 file")
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/demo_helper.py`\n", encoding="utf-8"
    )
    locked = package / "locked.md"
    locked.write_text("nothing to see\n", encoding="utf-8")
    locked.chmod(0o000)
    try:
        result = run_loaded_script_main(
            "inventory_skill_script_references",
            inventory_module,
            "--repo-root",
            str(tmp_path),
            "--strict",
        )
    finally:
        locked.chmod(0o644)
    assert result.returncode == 1
    assert "could not be read" in result.stdout


def test_the_structured_output_cannot_disarm_strict(tmp_path: Path) -> None:
    """The machine-readable mode is the natural one to wire into CI.

    It used to print the findings and exit 0, so the gate's own structured
    output was the one shape that could not refuse. That output is now the ONLY
    output, so the same escape would take every consumer with it.
    """
    repo = _broken_reference_repo(tmp_path)
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(repo),
        "--strict",
    )
    assert result.returncode == 1
    payload = yaml.safe_load(result.stdout)
    assert payload["findings"]
    assert payload["verdict"] == "fail"


def test_clean_output_reports_the_layout_split_and_the_unverifiable_count(tmp_path: Path) -> None:
    """The all-clear path must still disclose what it could NOT decide.

    `<repo-root>/scripts/X.py` naming a real repo script resolves against the
    CONSUMING repo once shipped, which this tree cannot inspect. Without the
    `note:`, "0 findings" would read as "every reference is fine".
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "repo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\nRun `<repo-root>/scripts/repo_helper.py`.\n", encoding="utf-8"
    )
    shipped = tmp_path / "plugins" / "pkg" / "skills" / "demo"
    shipped.mkdir(parents=True)
    (shipped / "SKILL.md").write_text(
        "# Demo\n\nRun `<repo-root>/scripts/repo_helper.py`.\n", encoding="utf-8"
    )

    result = run_loaded_script_main(
        "inventory_skill_script_references", inventory_module, "--repo-root", str(tmp_path)
    )
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["verdict"] == "ok"
    assert payload["findings"] == []
    # The layout split and the unverifiable count used to be prose; they are the
    # payload's own fields now, and the note stays because "0 findings" without it
    # reads as "every reference is fine".
    assert payload["denominator"]["by_layout"] == {"authoring": 1, "shipped": 1}
    assert any(
        "shipped reference(s) resolve only against a consuming" in note
        for note in payload["notes"]
    )


def test_advisory_says_so_when_packages_exist_but_name_no_scripts(tmp_path: Path) -> None:
    """The vacuity that survives a package-count guard.

    A repo can carry skill packages whose prose names no script path at all;
    "all 0 references resolve" would be the same false all-clear one level down.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (package / "SKILL.md").write_text("# Demo\n\nNo scripts here.\n", encoding="utf-8")

    result = run_loaded_script_main(
        "inventory_skill_script_references", inventory_module, "--repo-root", str(tmp_path)
    )
    assert result.returncode == 0
    assert "name no script paths" in result.stdout
    assert "references resolve" not in result.stdout


@pytest.mark.skipif(os.geteuid() == 0, reason="root can read a chmod-000 file")
def test_an_unreadable_doc_is_reported_rather_than_counted_as_clean(tmp_path: Path) -> None:
    """An unreadable doc hides its references; silence would read as clean."""
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/demo_helper.py`\n", encoding="utf-8"
    )
    hidden = package / "references"
    hidden.mkdir()
    unreadable = hidden / "locked.md"
    unreadable.write_text("Run `<repo-root>/scripts/demo_helper.py`.\n", encoding="utf-8")
    unreadable.chmod(0o000)
    try:
        payload = inventory_module.inventory(tmp_path)
        result = run_loaded_script_main(
            "inventory_skill_script_references", inventory_module, "--repo-root", str(tmp_path)
        )
    finally:
        unreadable.chmod(0o644)

    assert payload["denominator"]["docs_unreadable"] == [unreadable.as_posix()]
    assert result.returncode == 0
    assert "could not be read" in result.stdout


def test_advisory_says_so_when_it_scanned_nothing(tmp_path: Path) -> None:
    """A clean verdict over zero packages is the all-clear an advisory can hide behind.

    This is the normal shape in a consuming repo, where the skill packages live
    in the installed plugin rather than under the repo root.
    """
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0
    assert "nothing was checked" in result.stdout
    assert "resolve" not in result.stdout.split("nothing was checked")[0]


def test_advisory_cannot_change_an_exit_code(tmp_path: Path) -> None:
    """The DEFAULT mode never fails a run; `--strict` does.

    Kept after the promotion because the read-only inventory is still a
    supported way to run this, and its exit code must stay 0 even while holding
    findings. Run against a repo that DOES have a broken reference -- a zero
    exit on a clean repo would prove nothing about the posture.
    """
    repo = _broken_reference_repo(tmp_path)
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(repo),
    )
    assert result.returncode == 0
    payload = yaml.safe_load(result.stdout)
    assert payload["verdict"] == "warn"
    assert payload["advisories"] == []
    assert any("demo_helper.py" in finding["reference"] for finding in payload["findings"])


def test_the_option_surface_is_exactly_what_the_gate_wiring_expects() -> None:
    """Reads the real parser rather than grepping source text.

    `--strict` arrived when the operator PROMOTED this check from advisory to
    gate; before that, this test asserted the flag's absence. Pinning the whole
    surface (rather than just `--strict`'s presence) keeps a third mode from
    being added without a decision.
    """
    declared = {
        option
        for action in inventory_module.build_parser()._actions
        for option in action.option_strings
    }
    assert declared == {"-h", "--help", "--repo-root", "--strict"}


def test_strict_refuses_on_a_broken_reference_and_default_does_not(tmp_path: Path) -> None:
    """The promotion, pinned from both sides.

    Same finding set in both modes -- only the exit code differs -- so the
    read-only inventory and the gate can never disagree about what is broken.
    """
    repo = _broken_reference_repo(tmp_path)

    lenient = run_loaded_script_main(
        "inventory_skill_script_references", inventory_module, "--repo-root", str(repo)
    )
    strict = run_loaded_script_main(
        "inventory_skill_script_references", inventory_module, "--repo-root", str(repo), "--strict"
    )

    assert lenient.returncode == 0
    assert strict.returncode == 1
    lenient_payload = yaml.safe_load(lenient.stdout)
    strict_payload = yaml.safe_load(strict.stdout)
    # `WARN:`/`FAIL:` were renderer prefixes; the payload carries the same
    # distinction as `verdict`, over an identical finding set.
    assert lenient_payload["verdict"] == "warn"
    assert strict_payload["verdict"] == "fail"
    assert lenient_payload["findings"] == strict_payload["findings"]
    assert any("demo_helper.py" in finding["reference"] for finding in strict_payload["findings"])


def test_strict_passes_when_nothing_is_broken(tmp_path: Path) -> None:
    """A gate that refuses unconditionally is not a gate."""
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    (package / "scripts").mkdir(parents=True)
    (package / "scripts" / "demo_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n## References\n\n- `scripts/demo_helper.py`\n", encoding="utf-8"
    )

    result = run_loaded_script_main(
        "inventory_skill_script_references", inventory_module, "--repo-root", str(tmp_path), "--strict"
    )
    assert result.returncode == 0


def test_the_authoring_repo_marker_is_resolved_not_waved_through(tmp_path: Path) -> None:
    """The point of splitting `<authoring-repo>/` out of `<repo-root>/`.

    `<repo-root>/` means the READER's tree, so it is unverifiable here and
    exempt — which is precisely what hid 13 broken commands.
    `<authoring-repo>/` asserts the file is in THIS repo, so the assertion is
    checkable, and a wrong one is a finding rather than a silent placeholder.
    """
    tier = sorted(inventory_module.PORTABLE_SKILL_KINDS)[0]
    package = tmp_path / "skills" / tier / "demo"
    package.mkdir(parents=True)
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "real_helper.py").write_text("print('ok')\n", encoding="utf-8")
    (package / "SKILL.md").write_text(
        "# Demo\n\n"
        "`charness` ships `<authoring-repo>/scripts/real_helper.py`.\n\n"
        "`charness` also ships `<authoring-repo>/scripts/vanished.py`.\n",
        encoding="utf-8",
    )

    rows = {row["reference"]: row for row in inventory_module.classify_references(tmp_path)}
    assert rows["<authoring-repo>/scripts/real_helper.py"]["status"] == (
        inventory_module.AUTHORING_MARKED
    )
    # The one that matters: a marker claiming this repo, pointing at nothing.
    vanished = rows["<authoring-repo>/scripts/vanished.py"]
    assert vanished["status"] == inventory_module.UNRESOLVED
    assert vanished["status"] in inventory_module.ACTIONABLE


def test_advisory_exits_zero_on_a_clean_repo_too(tmp_path: Path) -> None:
    (tmp_path / "skills").mkdir()
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0


def test_a_plugin_dir_reference_is_resolved_against_the_shipped_package(tmp_path: Path) -> None:
    """The new arm, proven on a controlled tree rather than on live prose.

    `<plugin-dir>/scripts/x.py` asserts the file ships to the consumer, so it is
    checked against the generated package — not the authoring tree, which is what
    makes it a different claim from `<authoring-repo>/` rather than a synonym.
    """
    repo = tmp_path / "repo"
    package = repo / "skills" / "public" / "demo"
    (package / "references").mkdir(parents=True)
    (package / "SKILL.md").write_text("---\nname: demo\ndescription: d\n---\n\n# Demo\n", encoding="utf-8")
    (package / "references" / "note.md").write_text(
        "Run `<plugin-dir>/scripts/real.py`.\n\nAlso `<plugin-dir>/scripts/vanished.py`.\n",
        encoding="utf-8",
    )
    shipped = repo / "plugins" / "charness" / "scripts"
    shipped.mkdir(parents=True)
    (shipped / "real.py").write_text("# ships\n", encoding="utf-8")

    rows = [
        row
        for row in inventory_module.classify_references(repo)
        if row["form"] == "plugin-dir"
    ]

    by_reference = {row["reference"]: row for row in rows}
    assert by_reference["<plugin-dir>/scripts/real.py"]["status"] == inventory_module.AUTHORING_MARKED
    assert by_reference["<plugin-dir>/scripts/vanished.py"]["status"] == inventory_module.UNRESOLVED
