from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_consumer_validator_catalog as catalog_check

ROOT = Path(__file__).resolve().parents[1]


def _fixture_repo(tmp_path: Path, *, candidates: tuple[str, ...] = ("scripts/check_demo.py",)) -> Path:
    repo = tmp_path / "repo"
    package_root = repo / "plugins" / "charness"
    for relative in candidates:
        path = package_root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    return repo


def _entry(path: str, *, consumer_facing: bool = False) -> dict[str, object]:
    entry: dict[str, object] = {
        "path": path,
        "consumer_facing": consumer_facing,
        "decision": "publish" if consumer_facing else "exclude",
        "reason": "an explicit fixture decision",
    }
    if consumer_facing:
        entry["purpose"] = "validates a consumer-authored artifact"
        entry["invocation"] = f"python3 <plugin-root>/{path}"
    return entry


def _write_catalog(repo: Path, entries: list[dict[str, object]]) -> Path:
    path = repo / catalog_check.DEFAULT_CATALOG_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "schema_version: 1",
                "package_root: plugins/charness",
                "candidate_patterns:",
                "  - '**/check_*.py'",
                "  - '**/validate_*.py'",
                "scanner_exclusions:",
                "  - path: scripts/check_consumer_validator_catalog.py",
                "    reason: the checker is the fixed source-side scanner and is not a product validator",
                "consumer_contract:",
                "  source: packaged",
                "  selection_field: consumer_facing",
                "  no_substitute: use the packaged validator instead of a consumer-specific substitute",
                "validators:",
                *[
                    f"  - path: {entry['path']}\n"
                    f"    consumer_facing: {str(entry['consumer_facing']).lower()}\n"
                    f"    decision: {entry['decision']}\n"
                    f"    reason: {entry['reason']}"
                    + (
                        f"\n    purpose: {entry['purpose']}\n"
                        f"    invocation: '{entry['invocation']}'"
                        if entry["consumer_facing"]
                        else ""
                    )
                    for entry in entries
                ],
                "",
            ]
        ),
        encoding="utf-8",
    )
    return path


def test_live_catalog_has_a_decision_for_every_packaged_candidate() -> None:
    report = catalog_check.validate_catalog(ROOT)

    assert report["status"] == "pass"
    assert report["packaged_validator_count"] == report["decision_count"]
    assert report["packaged_validator_count"] == 132
    assert report["consumer_facing_count"] == 13
    assert "scripts/validate_handoff_artifact.py" in report["consumer_facing_validators"]
    assert "scripts/validate_adapters.py" not in report["consumer_facing_validators"]


def test_new_packaged_validator_cannot_stay_silent(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path, candidates=("scripts/check_demo.py", "skills/demo/validate_new.py"))
    _write_catalog(repo, [_entry("scripts/check_demo.py")])

    with pytest.raises(catalog_check.CatalogError, match="missing an explicit catalog decision"):
        catalog_check.validate_catalog(repo)


def test_catalog_rejects_a_non_packaged_or_duplicate_entry(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    _write_catalog(repo, [_entry("scripts/check_demo.py"), _entry("scripts/check_demo.py")])

    with pytest.raises(catalog_check.CatalogError, match="duplicate validator path"):
        catalog_check.validate_catalog(repo)

    _write_catalog(repo, [_entry("scripts/check_demo.py"), _entry("scripts/validate_missing.py")])
    with pytest.raises(catalog_check.CatalogError, match="not a packaged check_/validate_ script"):
        catalog_check.validate_catalog(repo)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("consumer_facing", None, "consumer_facing.*explicit boolean"),
        ("decision", "publish", "disagrees"),
        ("reason", "", "reason.*non-empty string"),
    ],
)
def test_each_catalog_decision_has_an_explicit_shape(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py")
    entry[field] = value
    _write_catalog(repo, [entry])

    with pytest.raises(catalog_check.CatalogError, match=message):
        catalog_check.validate_catalog(repo)


def test_consumer_entry_must_explain_the_packaged_invocation(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    entry["invocation"] = "python3 scripts/check_demo.py"
    _write_catalog(repo, [entry])

    with pytest.raises(catalog_check.CatalogError, match="invocation.*packaged path"):
        catalog_check.validate_catalog(repo)


def test_catalog_cannot_shrink_the_scanner_scope(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    path = _write_catalog(repo, [_entry("scripts/check_demo.py")])
    text = path.read_text(encoding="utf-8").replace("'**/validate_*.py'", "'scripts/check_*.py'")
    path.write_text(text, encoding="utf-8")

    with pytest.raises(catalog_check.CatalogError, match="fixed scanner scope"):
        catalog_check.validate_catalog(repo)


def test_catalog_must_explain_the_self_scanner_exclusion(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    path = _write_catalog(repo, [_entry("scripts/check_demo.py")])
    text = path.read_text(encoding="utf-8").replace(
        "  - path: scripts/check_consumer_validator_catalog.py\n"
        "    reason: the checker is the fixed source-side scanner and is not a product validator\n",
        "",
    )
    path.write_text(text, encoding="utf-8")

    with pytest.raises(catalog_check.CatalogError, match="scanner_exclusions"):
        catalog_check.validate_catalog(repo)


def test_report_lists_only_explicit_consumer_facing_paths(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path, candidates=("scripts/check_demo.py", "scripts/validate_demo.py"))
    _write_catalog(repo, [_entry("scripts/check_demo.py"), _entry("scripts/validate_demo.py", consumer_facing=True)])

    report = catalog_check.validate_catalog(repo)

    assert report["consumer_facing_validators"] == ["scripts/validate_demo.py"]
    assert report["excluded_count"] == 1
