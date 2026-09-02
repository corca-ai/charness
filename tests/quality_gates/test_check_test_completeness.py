from __future__ import annotations

from pathlib import Path

from scripts import check_test_completeness as checker

from .seeding_support import write_quality_adapter


def _write(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("def test_demo():\n    assert True\n", encoding="utf-8")


def _run_checker(repo: Path, targets: list[str], monkeypatch) -> int:
    monkeypatch.setattr(
        "sys.argv",
        ["check_test_completeness.py", "--repo-root", str(repo), "--", *targets],
    )
    return checker.main()


def test_check_test_completeness_accepts_directory_and_glob_targets(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    _write(repo / "tests" / "quality_gates" / "test_gate.py")
    _write(repo / "tests" / "test_top.py")
    _write(repo / "tests" / "charness_cli" / "test_cli.py")

    result = _run_checker(
        repo, ["tests/quality_gates", "tests/test_*.py", "tests/charness_cli"], monkeypatch
    )

    assert result == 0


def test_completeness_accepts_targets_expanded_from_the_adapter(
    tmp_path: Path, monkeypatch
) -> None:
    from scripts.gates_support import run_standing_pytest as runner

    repo = tmp_path / "consumer"
    _write(repo / "src" / "tests" / "test_selected.py")
    write_quality_adapter(
        repo,
        ["universes:", "  pytest_targets:", "    - src/tests/test_*.py"],
    )

    targets = runner.expand_targets(repo)

    assert targets == ["src/tests/test_selected.py"]
    assert _run_checker(repo, targets, monkeypatch) == 0


def test_check_test_completeness_reports_missing_test_files(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    repo = tmp_path / "repo"
    _write(repo / "tests" / "quality_gates" / "test_gate.py")
    _write(repo / "tests" / "integration" / "test_missing.py")

    result = _run_checker(repo, ["tests/quality_gates"], monkeypatch)

    stderr = capsys.readouterr().err
    assert result == 1
    assert "1 test file(s) not covered" in stderr
    assert "tests/integration/test_missing.py" in stderr


def test_relative_test_files_ignores_missing_targets(tmp_path: Path) -> None:
    repo = tmp_path / "repo"

    assert checker.relative_test_files(repo, repo / "tests" / "missing") == set()


def test_a_target_that_resolves_to_the_repo_root_is_refused(tmp_path: Path, monkeypatch) -> None:
    """Sweep row S6, parent-reproduced. `repo_root / ""` IS the repo root, so such a
    target made `relative_test_files` rglob the whole repo and every test file counted
    as covered — this gate reporting full completeness having established nothing.

    Blankness is not the test, because it is one spelling of the same thing: review
    found `.` and `./` collapse to the repo root too, and `.` is the most natural
    pytest target anyone would write (reachable via
    `run_standing_pytest.py --pytest-target .`). The check is on the RESOLVED path.

    The blank spelling is the shape the real caller produces: `run-quality.sh` builds
    the array with `mapfile` from `run_standing_pytest.py --print-expanded-targets`,
    and `mapfile` on empty output yields exactly one empty element."""
    repo = tmp_path / "repo"
    _write(repo / "tests" / "test_top.py")
    _write(repo / "tests" / "quality_gates" / "test_gate.py")

    for target in ("", "   ", ".", "./", str(repo)):
        assert _run_checker(repo, [target], monkeypatch) == 1, target
    # An offender alongside real targets is still a refusal: the list did not resolve.
    assert _run_checker(repo, ["tests/test_*.py", "", "tests/quality_gates"], monkeypatch) == 1

    # Falsifiable counterpart: the same targets without the offender still pass, so the
    # refusal is about the offender and not about the target set.
    assert _run_checker(repo, ["tests/test_*.py", "tests/quality_gates"], monkeypatch) == 0


def test_zero_targets_over_a_repo_that_has_tests_is_refused(tmp_path: Path, monkeypatch) -> None:
    """The hole the refusal above would otherwise route an operator into: a blank target
    exited 1 while ZERO targets exited 0, so "check the producer" could be satisfied by
    filtering the blank out of the array — and the gate went green over the same
    unestablished scope.

    A repo with no tests at all is still a legitimate skip, and both of those returns
    happen earlier."""
    with_tests = tmp_path / "with-tests"
    _write(with_tests / "tests" / "test_top.py")
    assert _run_checker(with_tests, [], monkeypatch) == 1

    no_test_root = tmp_path / "no-test-root"
    no_test_root.mkdir()
    assert _run_checker(no_test_root, [], monkeypatch) == 0

    empty_test_root = tmp_path / "empty-test-root"
    (empty_test_root / "tests").mkdir(parents=True)
    assert _run_checker(empty_test_root, [], monkeypatch) == 0


def test_repo_root_targets_reports_every_offending_position(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    assert checker.repo_root_targets(repo, ["tests", "", "docs", ".", "./"]) == [
        (2, ""),
        (4, "."),
        (5, "./"),
    ]
    assert checker.repo_root_targets(repo, ["tests", "tests/test_*.py"]) == []
    # A glob is never treated as a root target: `repo_root.glob("*")` cannot yield the
    # root itself, so a glob that happens to be `*` widens without collapsing.
    assert checker.repo_root_targets(repo, ["*"]) == []


def test_repo_root_targets_skips_a_target_whose_path_cannot_be_resolved(
    tmp_path: Path, monkeypatch
) -> None:
    """An unresolvable target is skipped, not treated as the repo root.

    This gate's whole job is to refuse a target that IS the repo root, because such a
    target makes the completeness check rglob everything and report full coverage
    having established nothing. `resolve()` can fail on the filesystem (ENAMETOOLONG,
    a broken mount, an unreadable parent). If that raise escaped, the gate would crash
    on an input it should merely pass over; if it were caught and the target counted,
    a path that could not be resolved would be reported as the repo root — a verdict
    about a path nobody ever read. Skipping is the only honest arm.
    """
    real_resolve = Path.resolve

    def resolve(self: Path, strict: bool = False) -> Path:
        if self.name == "unresolvable":
            raise OSError(36, "File name too long")
        return real_resolve(self, strict=strict) if strict else real_resolve(self)

    monkeypatch.setattr(Path, "resolve", resolve)

    offenders = checker.repo_root_targets(tmp_path, ["unresolvable", "", "tests"])

    # The empty target still resolves to the root and is still caught: the skip is
    # scoped to the unresolvable path, not a blanket bypass of the check.
    assert offenders == [(2, "")]
