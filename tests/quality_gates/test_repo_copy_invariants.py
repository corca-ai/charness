from __future__ import annotations

import ast
import re
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

from runtime_bootstrap import import_repo_module
from tests import repo_copy
from tools import check_coverage

from .support import ROOT, run_script

_repo_copy_invariants = import_repo_module(
    ROOT / "scripts/gates/check_test_repo_copy_invariants.py",
    "scripts.gates.check_test_repo_copy_invariants",
)


def run_repo_copy_invariants(monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", ["check_test_repo_copy_invariants.py", *args])
    returncode = _repo_copy_invariants.main()
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


REQUIRED_VOLATILE_COPY_EXCLUDES = {
    ".charness",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "__pycache__",
    ".coverage",
    ".venv",
    "charness-artifacts",
    "node_modules",
    "reports",
}


def test_test_repo_copy_ignore_lives_in_canonical_module() -> None:
    result = run_script("scripts/gates/check_test_repo_copy_invariants.py", "--repo-root", str(ROOT))
    assert result.returncode == 0, result.stderr


def test_repo_copy_excludes_volatile_artifact_roots() -> None:
    assert REQUIRED_VOLATILE_COPY_EXCLUDES <= set(repo_copy.REPO_COPY_EXCLUDE_NAMES)


def test_coverage_copy_excludes_volatile_artifact_roots() -> None:
    assert REQUIRED_VOLATILE_COPY_EXCLUDES <= set(check_coverage.COPY_IGNORE_NAMES)


def test_repo_copy_ignore_drops_generated_reports(tmp_path: Path) -> None:
    source = tmp_path / "source"
    payload = source / "reports" / "mutation" / "large-run.log"
    payload.parent.mkdir(parents=True)
    payload.write_text("large generated report\n", encoding="utf-8")
    (source / "README.md").write_text("# source\n", encoding="utf-8")

    target = tmp_path / "target"
    shutil.copytree(source, target, ignore=repo_copy.REPO_COPY_IGNORE)

    assert (target / "README.md").is_file()
    assert not (target / "reports").exists()


def test_coverage_copy_ignore_drops_generated_reports(tmp_path: Path) -> None:
    source = tmp_path / "coverage-source"
    payload = source / "reports" / "mutation" / "large-run.log"
    payload.parent.mkdir(parents=True)
    payload.write_text("large generated report\n", encoding="utf-8")
    (source / "scripts").mkdir()
    (source / "scripts" / "demo.py").write_text("print('ok')\n", encoding="utf-8")

    target = tmp_path / "coverage-target"
    shutil.copytree(source, target, ignore=check_coverage.COPY_IGNORE)

    assert (target / "scripts" / "demo.py").is_file()
    assert not (target / "reports").exists()


def test_check_test_repo_copy_invariants_flags_inline_ignore(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text(
        "import shutil\nREPO_COPY_IGNORE = shutil.ignore_patterns('.git')\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_drift.py").write_text(
        "import shutil\nROOT = '/repo'\n"
        "DRIFT_IGNORE = shutil.ignore_patterns('.git', 'node_modules')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "shutil.ignore_patterns" in result.stderr


def test_check_test_repo_copy_invariants_flags_inline_copytree_root(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_drift.py").write_text(
        "import shutil\nfrom pathlib import Path\nROOT = Path('/repo')\n"
        "def make(tmp): shutil.copytree(ROOT, tmp / 'repo')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "tests/test_drift.py" in result.stderr
    assert "clone_seeded_charness_repo" in result.stderr or "shutil.copytree" in result.stderr


def test_a_copy_heavy_fixture_wrapper_does_not_hide_the_cost(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """One hop used to defeat this gate entirely.

    The check enumerated `COPY_HEAVY_FIXTURES` and `COPY_HEAVY_HELPERS` and looked for
    them only inside `test_` bodies. A module-local fixture that wrapped the helper named
    neither, so the test named nothing listed and the call sat outside a test body.
    `tests/quality_gates/test_gate_summary_names_failures.py` did exactly that and was the
    most expensive copy-heavy test in the standing lane -- 7.3s of SETUP, five tests --
    while this gate reported clean over it. The wrapper is two hops deep here because a
    wrapper can wrap a wrapper.
    """

    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_wrapped.py").write_text(
        "import pytest\n"
        "@pytest.fixture\n"
        "def base(tmp_path, seeded_charness_git_repo):\n"
        "    return clone_seeded_charness_repo(tmp_path, seeded_charness_git_repo)\n"
        "@pytest.fixture\n"
        "def wrapped(base):\n"
        "    return base\n"
        "def test_wrapped(wrapped):\n"
        "    assert wrapped\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_wrapped.py::test_wrapped" in result.stderr
    assert "wrapped" in result.stderr


def test_a_test_that_reaches_nothing_copy_heavy_stays_clean(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The negative control for the transitive rule: reachability, not name-similarity.

    Without this, widening the check to module-local functions could flag every fixture
    in a file that happens to contain one copy-heavy test, and the suite would still be
    green.
    """

    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_cheap.py").write_text(
        "import pytest\n"
        "@pytest.fixture\n"
        "def cheap(tmp_path):\n"
        "    return tmp_path\n"
        "def test_cheap(cheap):\n"
        "    assert cheap\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_flags_unmarked_copy_heavy_test(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "def test_copy(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_copy_heavy.py::test_copy" in result.stderr
    assert "pytest.mark.release_only" in result.stderr


def test_check_test_repo_copy_invariants_accepts_release_only_copy_heavy_test(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "import pytest\n\n"
        "@pytest.mark.release_only\n"
        "def test_copy(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_recorded_standing_copy_heavy_test_is_exempt_from_the_marker_rule_only(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """A test-level exemption, scoped to one test's marker requirement.

    `ALLOWED_FILES` was the alternative and is the wrong tool: it skips a file
    from ALL FOUR checks, so exempting one marker would have disarmed the
    ignore-patterns, copytree-ROOT, and real-checkout-write rules over every test
    in that file, permanently.
    """
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "def test_recorded(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n\n"
        "def test_unrecorded(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        _repo_copy_invariants,
        "STANDING_COPY_HEAVY_TESTS",
        {"tests/test_copy_heavy.py::test_recorded": "+0.4s measured"},
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    # The recorded one passes; its unrecorded sibling in the SAME FILE still fails.
    assert result.returncode == 1
    assert "::test_recorded" not in result.stderr
    assert "tests/test_copy_heavy.py::test_unrecorded" in result.stderr
    assert "STANDING_COPY_HEAVY_TESTS" in result.stderr


def test_a_recorded_standing_test_still_obeys_the_other_three_checks(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    """The exemption must not become a file-level pass by another name."""
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "import shutil\n"
        "from pathlib import Path\n\n"
        "ROOT = Path('/repo')\n"
        "IGNORE = shutil.ignore_patterns('.git')\n\n"
        "def test_recorded(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n"
        "    shutil.copytree(ROOT, tmp_path / 'repo')\n"
        "    (ROOT / 'x.txt').write_text('mutating the real checkout')\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        _repo_copy_invariants,
        "STANDING_COPY_HEAVY_TESTS",
        {"tests/test_copy_heavy.py::test_recorded": "+0.4s measured"},
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    # All three of the other checks still fire on the exempted test's file.
    assert "defines shutil.ignore_patterns" in result.stderr
    assert "shutil.copytree(ROOT, ...)" in result.stderr
    assert any("write_text" in line or "ROOT" in line for line in result.stderr.splitlines())
    # ...and the marker rule stays exempted, so the exemption is scoped, not broad.
    assert "pytest.mark.release_only" not in result.stderr


def test_the_recorded_standing_test_exists_and_is_still_copy_heavy() -> None:
    """An entry that outlives its test becomes a silent hole.

    Judged with the GATE'S OWN per-function predicate, not a per-file regex. A
    review round caught the weaker version: `COPY_HEAVY_TOKEN_RE.search(source)`
    scans the whole file and is satisfied by the `from tests.repo_copy import
    clone_seeded_charness_repo` line alone, so a test rewritten to use a light
    fixture would keep its exemption with nothing red -- and a later re-heavying
    of that name would then be exempt without a measured cost.
    """
    for entry, cost in _repo_copy_invariants.STANDING_COPY_HEAVY_TESTS.items():
        rel_path, separator, test_name = entry.partition("::")
        assert separator and test_name, f"entry must be `path::test_name`: {entry}"
        assert (ROOT / rel_path).is_file(), entry
        tree = ast.parse((ROOT / rel_path).read_text(encoding="utf-8"), filename=rel_path)
        node = next(
            (
                item
                for item in ast.walk(tree)
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
                and item.name == test_name
            ),
            None,
        )
        assert node is not None, f"{entry} names no such test"
        # The same predicate the gate exempts on, so "still copy-heavy" cannot
        # drift away from what the gate means by copy-heavy.
        assert _repo_copy_invariants._copy_heavy_reason(node) is not None, entry
        # "MEASURED and recorded" made machine-checkable: a comment can be deleted
        # with nothing red, a required value cannot.
        assert re.search(r"\d", cost) and re.search(r"\b(s|ms|sec|second)", cost), entry


def test_the_standing_exemption_membership_is_pinned() -> None:
    """A second entry must be argued in a gate test, not only in the gate.

    The recorded bar ("observes something no standing gate otherwise observes,
    and the cost is measured") is prose that nothing executes, so without this
    the next entry costs one string and no review.
    """
    assert set(_repo_copy_invariants.STANDING_COPY_HEAVY_TESTS) == {
        "tests/control_plane/test_integrations_validation.py"
        "::test_tool_doctor_cli_returns_nonzero_for_blocking_disposition"
    }


def test_check_test_repo_copy_invariants_flags_real_repo_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_shared_write.py").write_text(
        "from pathlib import Path\n"
        "ROOT = Path(__file__).resolve().parents[1]\n"
        "def test_write():\n"
        "    target = ROOT / 'charness-artifacts' / 'temporary.md'\n"
        "    target.write_text('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_shared_write.py:5" in result.stderr
    assert "mutates a path derived from the real repository root" in result.stderr
    assert "tmp_path or an isolated repo" in result.stderr


def test_check_test_repo_copy_invariants_flags_import_time_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_import_write.py").write_text(
        "from .support import ROOT\n(ROOT / 'temporary.txt').touch()\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "module import mutates" in result.stderr


def test_check_test_repo_copy_invariants_flags_aliased_root_path_open(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_alias_write.py").write_text(
        "from pathlib import Path\n"
        "from .support import ROOT as checkout\n"
        "def test_write():\n"
        "    target = Path(checkout).joinpath('temporary.txt')\n"
        "    with target.open(mode='w') as stream:\n"
        "        stream.write('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "Path.open(mode='w')" in result.stderr


def test_check_test_repo_copy_invariants_flags_annotated_root_builtin_open(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_builtin_open.py").write_text(
        "from pathlib import Path\n"
        "from .support import ROOT\n"
        "def test_write():\n"
        "    target: Path = ROOT / 'temporary.txt'\n"
        "    with open(target, 'w') as stream:\n"
        "        stream.write('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "open(mode='w')" in result.stderr


def test_check_test_repo_copy_invariants_flags_class_style_root_write(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_class_write.py").write_text(
        "from .support import ROOT\n"
        "class TestSharedState:\n"
        "    def test_write(self):\n"
        "        (ROOT / 'temporary.txt').write_text('transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "`test_write` mutates" in result.stderr


def test_check_test_repo_copy_invariants_tracks_module_aliases_and_async_writes(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_alias_chain.py").write_text(
        "from pathlib import Path\n"
        "REPO_ROOT = Path(__file__).resolve().parents[1]\n"
        "checkout = REPO_ROOT.absolute()\n"
        "class TestSharedState:\n"
        "    async def test_write(self):\n"
        "        target: Path = Path(checkout).joinpath('scratch').resolve()\n"
        "        target.mkdir()\n"
        "        target.write_bytes(b'transient')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "tests/test_alias_chain.py" in result.stderr
    assert "`test_write` mutates" in result.stderr
    assert "`mkdir`" in result.stderr
    assert "`write_bytes`" in result.stderr


def test_check_test_repo_copy_invariants_accepts_module_release_only_marker(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_copy_heavy.py").write_text(
        "import pytest\n"
        "pytestmark = (pytest.mark.release_only,)\n"
        "def test_copy(tmp_path, seeded_charness_repo):\n"
        "    clone_seeded_charness_repo(tmp_path, seeded_charness_repo)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_accepts_non_checkout_root_name(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_local_root.py").write_text(
        "from pathlib import Path\n"
        "ROOT = Path('/tmp/test-output')\n"
        "def test_write():\n"
        "    (ROOT / 'result.txt').write_text('isolated')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_accepts_tmp_write_and_root_read(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_isolated.py").write_text(
        "from .support import ROOT\n"
        "def test_isolated(tmp_path):\n"
        "    source = (ROOT / 'AGENTS.md').read_text()\n"
        "    (tmp_path / 'AGENTS.md').write_text(source)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_cached_quality_runner_seed_is_read_only(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_seed_write.py").write_text(
        "def test_write(seeded_quality_runner_repo):\n"
        "    target = seeded_quality_runner_repo / 'scripts' / 'run-quality.sh'\n"
        "    target.write_text('contaminated')\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 1
    assert "mutates cached read-only fixture" in result.stderr
    assert "Clone the seed into tmp_path first" in result.stderr


def test_cached_quality_runner_seed_may_be_read_then_cloned(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_seed_clone.py").write_text(
        "def test_clone(tmp_path, seeded_quality_runner_repo):\n"
        "    source = (seeded_quality_runner_repo / 'README.md').read_text()\n"
        "    (tmp_path / 'README.md').write_text(source)\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr


def test_check_test_repo_copy_invariants_skips_ast_for_irrelevant_files(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "fake-charness"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "tests" / "repo_copy.py").write_text("", encoding="utf-8")
    (repo / "tests" / "test_irrelevant.py").write_text(
        "def not_valid_python(:\n",
        encoding="utf-8",
    )

    result = run_repo_copy_invariants(monkeypatch, capsys, "--repo-root", str(repo))

    assert result.returncode == 0, result.stderr
