from __future__ import annotations

import os
import time
from pathlib import Path

from scripts.mutation import manage_mutation_reports as reports


def _file(path: Path, *, age_days: int, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    stamp = time.time() - age_days * 86400
    os.utime(path, (stamp, stamp))
    return path


def test_main_absent_report_root_is_empty_and_execute_is_noop(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    import yaml

    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: set())

    assert reports.main(["--repo-root", str(tmp_path)]) == 0
    dry_run = yaml.safe_load(capsys.readouterr().out)
    assert dry_run["report_root_exists"] is False
    assert dry_run["report_root_device"] is None
    assert dry_run["report_root_inode"] is None
    assert dry_run["records"] == []
    assert dry_run["candidate_count"] == 0
    assert not (tmp_path / "reports" / "mutation").exists()

    assert reports.main(
        [
            "--repo-root",
            str(tmp_path),
            "--execute",
            "--confirm-candidate-set-sha256",
            dry_run["candidate_set_sha256"],
        ]
    ) == 0
    executed = yaml.safe_load(capsys.readouterr().out)
    assert executed["executed"] is True
    assert executed["removed"] == []
    assert not (tmp_path / "reports" / "mutation").exists()


def test_inventory_classifies_managed_fresh_and_old_unmanaged(
    tmp_path: Path, monkeypatch
) -> None:
    report_root = tmp_path / "reports" / "mutation"
    managed = _file(report_root / "test-coverage.json", age_days=90)
    old = _file(report_root / "old-probe.json", age_days=60, text="old-data")
    fresh = _file(report_root / "fresh-probe.json", age_days=1)
    directory = report_root / "probe-dir"
    directory.mkdir()
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: {managed.resolve()})

    payload = reports.inventory(tmp_path, older_than_days=30)
    records = {record["path"]: record for record in payload["records"]}

    assert records["reports/mutation/test-coverage.json"]["managed"] is True
    assert records["reports/mutation/test-coverage.json"]["prune_candidate"] is False
    assert records["reports/mutation/old-probe.json"]["prune_candidate"] is True
    assert records["reports/mutation/fresh-probe.json"]["prune_candidate"] is False
    assert records["reports/mutation/probe-dir"]["kind"] == "directory"
    assert records["reports/mutation/probe-dir"]["prune_candidate"] is False
    assert payload["candidate_count"] == 1
    assert payload["candidate_bytes"] == len("old-data")
    assert old.is_file() and fresh.is_file()


def test_execute_prune_removes_only_the_rendered_candidate(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports" / "mutation"
    managed = _file(report_root / "summary.md", age_days=90)
    candidate = _file(report_root / "old-probe.json", age_days=60)
    fresh = _file(report_root / "fresh-probe.json", age_days=1)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: {managed.resolve()})
    payload = reports.inventory(tmp_path, older_than_days=30)

    removed = reports.execute_prune(
        tmp_path,
        payload,
        confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
    )

    assert removed == ["reports/mutation/old-probe.json"]
    assert not candidate.exists()
    assert managed.is_file() and fresh.is_file()


def test_execute_refuses_stale_or_unconfirmed_candidate_set(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports" / "mutation"
    first = _file(report_root / "first-old-probe.json", age_days=60)
    candidate = _file(report_root / "second-old-probe.json", age_days=60)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: set())
    payload = reports.inventory(tmp_path, older_than_days=30)

    try:
        reports.execute_prune(tmp_path, payload, confirmed_candidate_set_sha256="wrong")
    except SystemExit as exc:
        assert "confirmation mismatch" in str(exc)
    else:
        raise AssertionError("expected candidate-set confirmation refusal")

    candidate.write_text("changed", encoding="utf-8")
    try:
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
        )
    except SystemExit as exc:
        assert "changed after inventory" in str(exc)
    else:
        raise AssertionError("expected changed-candidate refusal")

    assert candidate.is_file()
    assert first.is_file()


def test_execute_refuses_candidate_replaced_by_symlink_without_deleting_target(
    tmp_path: Path, monkeypatch
) -> None:
    report_root = tmp_path / "reports" / "mutation"
    candidate = _file(report_root / "old-probe.json", age_days=60)
    managed = _file(report_root / "summary.md", age_days=60)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: {managed.resolve()})
    payload = reports.inventory(tmp_path, older_than_days=30)
    candidate.unlink()
    candidate.symlink_to(managed.name)

    try:
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
        )
    except SystemExit as exc:
        assert "changed after inventory" in str(exc)
    else:
        raise AssertionError("expected candidate symlink refusal")

    assert candidate.is_symlink()
    assert managed.is_file()


def test_execute_refuses_replaced_report_root(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports" / "mutation"
    candidate = _file(report_root / "old-probe.json", age_days=60)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: set())
    payload = reports.inventory(tmp_path, older_than_days=30)
    saved_root = tmp_path / "reports" / "mutation-saved"
    report_root.rename(saved_root)
    outside = tmp_path / "outside"
    outside.mkdir()
    external = _file(outside / candidate.name, age_days=60)
    report_root.symlink_to(outside, target_is_directory=True)

    try:
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
        )
    except SystemExit as exc:
        assert "report root changed after inventory" in str(exc)
    else:
        raise AssertionError("expected replaced-root refusal")

    assert (saved_root / candidate.name).is_file()
    assert external.is_file()


def test_execute_rechecks_candidate_immediately_before_each_unlink(
    tmp_path: Path, monkeypatch
) -> None:
    report_root = tmp_path / "reports" / "mutation"
    first = _file(report_root / "first-old.json", age_days=60)
    second = _file(report_root / "second-old.json", age_days=60)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: set())
    payload = reports.inventory(tmp_path, older_than_days=30)
    original = reports._validate_candidate
    validations: dict[str, int] = {}

    def mutate_before_second_unlink(root_fd, name, path, record, current_managed):
        validations[name] = validations.get(name, 0) + 1
        if name == second.name and validations[name] == 2:
            second.write_text("changed after full preflight", encoding="utf-8")
        return original(root_fd, name, path, record, current_managed)

    monkeypatch.setattr(reports, "_validate_candidate", mutate_before_second_unlink)
    try:
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
        )
    except SystemExit as exc:
        assert "changed after inventory" in str(exc)
    else:
        raise AssertionError("expected immediate pre-unlink refusal")

    assert not first.exists()
    assert second.is_file()


def test_execute_rechecks_managed_set_before_any_delete(tmp_path: Path, monkeypatch) -> None:
    report_root = tmp_path / "reports" / "mutation"
    candidate = _file(report_root / "old-probe.json", age_days=60)
    calls = 0

    def changing_managed(repo_root):
        nonlocal calls
        calls += 1
        return set() if calls == 1 else {candidate.resolve()}

    monkeypatch.setattr(reports, "managed_paths", changing_managed)
    payload = reports.inventory(tmp_path, older_than_days=30)

    try:
        reports.execute_prune(
            tmp_path,
            payload,
            confirmed_candidate_set_sha256=payload["candidate_set_sha256"],
        )
    except SystemExit as exc:
        assert "became managed after inventory" in str(exc)
    else:
        raise AssertionError("expected newly-managed refusal")

    assert candidate.is_file()


def test_adapter_declared_report_paths_are_managed(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(
        reports,
        "load_quality_adapter_strict",
        lambda repo_root: {
            "valid": True,
            "data": {
                "mutation_testing": {"report_paths": {"log": "reports/mutation/custom.log"}},
                "changed_line_mutation_gate": {"coverage_json": "reports/mutation/custom-coverage.json"},
            },
        },
    )

    managed = reports.managed_paths(tmp_path)

    assert (tmp_path / "reports/mutation/custom.log").resolve() in managed
    coverage = (tmp_path / "reports/mutation/custom-coverage.json").resolve()
    assert coverage in managed
    assert coverage.with_name("custom-coverage.json.fingerprint") in managed
    assert coverage.with_name("custom-coverage.json.changed-line.fingerprint") in managed
    assert (tmp_path / "reports/mutation/sample-coverage.json").resolve() in managed
    assert (tmp_path / "reports/mutation/stryker-js.html").resolve() in managed


def test_main_dry_run_confirmation_and_execute_are_operator_visible(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    import yaml

    report_root = tmp_path / "reports" / "mutation"
    candidate = _file(report_root / "old-probe.json", age_days=60)
    monkeypatch.setattr(reports, "managed_paths", lambda repo_root: set())

    assert reports.main(["--repo-root", str(tmp_path), "--older-than-days", "30"]) == 0
    dry_run = yaml.safe_load(capsys.readouterr().out)
    assert dry_run["executed"] is False and dry_run["removed"] == []
    assert candidate.is_file()

    try:
        reports.main(["--repo-root", str(tmp_path), "--older-than-days", "30", "--execute"])
    except SystemExit as exc:
        assert "requires --confirm-candidate-set-sha256" in str(exc)
    else:
        raise AssertionError("expected missing-confirmation refusal")
    assert candidate.is_file()

    assert reports.main(
        [
            "--repo-root",
            str(tmp_path),
            "--older-than-days",
            "30",
            "--execute",
            "--confirm-candidate-set-sha256",
            dry_run["candidate_set_sha256"],
        ]
    ) == 0
    executed = yaml.safe_load(capsys.readouterr().out)
    assert executed["executed"] is True
    assert executed["removed"] == ["reports/mutation/old-probe.json"]
    assert not candidate.exists()
