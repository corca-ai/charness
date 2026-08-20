"""Focused proof for the repair-carries-its-class closeout affordance (#676)."""

from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.slice_closeout_advisories import advise_repair_parity


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _seed_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.invalid")
    _git(repo, "config", "user.name", "test")
    (repo / "README.md").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-q", "-m", "seed")
    _git(repo, "branch", "origin/main")
    return repo


def test_advisory_names_each_refusal_detector_class_in_a_real_diff(
    tmp_path: Path, capsys
) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "check_adapter.py"
    target.parent.mkdir()
    lines = (
        'raise ValueError("unsupported adapter version")',
        'raise ValueError("malformed input")',
        'raise ValueError("unhonored adapter")',
        'findings.append({"reason": "uninterpreted line"})',
        'report["status"] = False',
    )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")

    advise_repair_parity(repo, ["scripts/check_adapter.py"])

    err = capsys.readouterr().err
    assert "added refusal/detector input class candidates" in err
    for line in lines:
        assert line in err
    # The class is the exact source line; a dict key must not become a separate
    # class hint (the prior classifier returned `reason; ...`).
    assert "reason; uninterpreted line" not in err
    assert "literal no-op" in err


def test_advisory_ignores_validation_generation_cleanup_and_call_chains(
    tmp_path: Path, capsys
) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "ordinary.py"
    target.parent.mkdir()
    target.write_text(
        "\n".join(
            (
                "if value is None:",
                "    return False",
                'return [value, "probe-mutation"]',
                "except Exception:",
                "    del sys.modules[key]",
                "return next_handler(value)",
                '# docs say "unsupported" but this is not executable',
            )
        )
        + "\n",
        encoding="utf-8",
    )

    advise_repair_parity(repo, ["scripts/ordinary.py"])

    assert capsys.readouterr().err == ""


def test_advisory_is_silent_for_non_source_changed_paths(
    tmp_path: Path, capsys
) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "docs" / "check_adapter.md"
    target.parent.mkdir()
    target.write_text('raise ValueError("unsupported adapter version")\n', encoding="utf-8")

    advise_repair_parity(repo, ["docs/check_adapter.md"])

    assert capsys.readouterr().err == ""


def test_existing_closeout_consumer_runs_class_advisory_without_parity_harness(
    tmp_path: Path, capsys
) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "check_adapter.py"
    target.parent.mkdir()
    target.write_text('raise ValueError("malformed adapter")\n', encoding="utf-8")

    # The seeded consumer has no parity harness. The class advisory must still
    # run; tying it to the reviewer snapshot would recreate silent under-measurement.
    advise_repair_parity(repo, ["scripts/check_adapter.py"])

    assert "malformed adapter" in capsys.readouterr().err


def test_advisory_reports_unavailable_base_instead_of_silent_zero(tmp_path: Path, capsys) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "check_adapter.py"
    target.parent.mkdir()
    target.write_text('raise ValueError("unsupported adapter version")\n', encoding="utf-8")

    advise_repair_parity(repo, ["scripts/check_adapter.py"], base="missing-base")

    err = capsys.readouterr().err
    assert "base is unavailable" in err
    assert "UNPROVEN" in err


def test_advisory_uses_an_explicit_alternate_base(tmp_path: Path, capsys) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "check_adapter.py"
    target.parent.mkdir()
    target.write_text('raise ValueError("unsupported adapter version")\n', encoding="utf-8")

    advise_repair_parity(repo, ["scripts/check_adapter.py"], base="HEAD")

    assert "unsupported adapter version" in capsys.readouterr().err


def test_advisory_does_not_crash_on_non_mapping_harness_report(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = _seed_repo(tmp_path)
    target = repo / "scripts" / "check_adapter.py"
    target.parent.mkdir()
    target.write_text('raise ValueError("unsupported adapter version")\n', encoding="utf-8")
    harness = repo / "scripts" / "parity_harness.py"
    harness.write_text(
        'print("files: [not-a-map]\\nuncomparable: {}")\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("scripts.slice_closeout_advisories._PARITY_HARNESS", "scripts/parity_harness.py")

    advise_repair_parity(repo, ["scripts/check_adapter.py"])

    assert "malformed report" in capsys.readouterr().err
