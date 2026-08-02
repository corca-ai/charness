"""Every script path shipped skill prose tells an agent to run must resolve.

Thirteen references said `<repo-root>/scripts/<name>.py` while `<name>.py` lived
in the skill's own package, so the documented command failed in this repo and in
any consuming repo alike. Three overlapping silences in `check_doc_links.py` let
them accumulate (see the advisory's module docstring). This pins the repaired
state and pins the advisory's non-blocking posture.

Fixtures here are built from the advisory's own shipped constants and are
cross-checked against its shipped regex before use: a fixture spelled the way
the matcher wants is precisely how this class hides.
"""
from __future__ import annotations

import collections
import os
from pathlib import Path

import pytest

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


# Known shipped-layout findings, NOT repaired by the goal that added this test,
# mapped to the exact number of sites each is allowed. Counting rather than
# merely naming them means a SECOND occurrence in the same file cannot slip in
# under an existing key.
#
# `$SKILL_DIR/../../../scripts` reaches the repo root from `skills/public/<skill>`
# but overshoots the plugin root from `plugins/<pkg>/skills/<skill>`, where the
# exported scripts sit two levels up. Both call sites end in `2>/dev/null || true`,
# so the command fails silently in every installed plugin. Repointing them would
# make a currently-never-running planner start running in installed hosts -- a
# behaviour change, not a path typo, so it is filed rather than fixed here.
#
# This map is a ratchet: entries may shrink, never grow. Every entry must be the
# SAME defect class -- do not park a `package_file_wrong_prefix` finding here
# under this rationale, which is about a silently-skipped optional command.
KNOWN_SHIPPED_FINDINGS = {
    ("plugins/charness/skills/impl/SKILL.md", "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py"): 1,
    ("plugins/charness/skills/spec/SKILL.md", "$SKILL_DIR/../../../scripts/plan_risk_interrupt.py"): 1,
}


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
    assert forms["repo-root"] >= 15
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
    candidates = [row for row in shipped if row["form"] == "repo-root"]
    assert len(candidates) >= 15, "no candidates left to classify; this test proves nothing"

    broken = [row for row in candidates if row["status"] == inventory_module.BROKEN]
    assert broken == [], _describe(broken)


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


@pytest.mark.parametrize("extra_args", [(), ("--json",)])
def test_advisory_cannot_change_an_exit_code(tmp_path: Path, extra_args: tuple[str, ...]) -> None:
    """Operator decision 2026-08-02: the COMMAND never fails a run.

    The regression tests above are a gate; this script's exit code is not. Run
    against a repo that DOES have a broken reference -- a zero exit on a clean
    repo would prove nothing about the posture.
    """
    repo = _broken_reference_repo(tmp_path)
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(repo),
        *extra_args,
    )
    assert result.returncode == 0
    assert "demo_helper.py" in result.stdout


def test_advisory_declares_no_flag_that_could_fail_the_run() -> None:
    """No `--strict`-style escalation exists to be wired into a gate by habit.

    Reads the real parser rather than grepping source text, which would match
    the module docstring explaining why the flag is absent.
    """
    declared = {
        option
        for action in inventory_module.build_parser()._actions
        for option in action.option_strings
    }
    assert declared == {"-h", "--help", "--repo-root", "--json"}


def test_advisory_exits_zero_on_a_clean_repo_too(tmp_path: Path) -> None:
    (tmp_path / "skills").mkdir()
    result = run_loaded_script_main(
        "inventory_skill_script_references",
        inventory_module,
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0
