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
    assert report["packaged_validator_count"] == 133
    assert report["consumer_facing_count"] == 14
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


def _valid_header() -> dict[str, object]:
    return {
        "schema_version": 1,
        "package_root": "plugins/charness",
        "candidate_patterns": list(catalog_check.EXPECTED_CANDIDATE_PATTERNS),
        "scanner_exclusions": [
            {
                "path": catalog_check.EXPECTED_SCANNER_EXCLUSIONS[0],
                "reason": "fixed scanner owner",
            }
        ],
        "consumer_contract": {
            "source": "packaged",
            "selection_field": "consumer_facing",
            "no_substitute": "use packaged validator",
        },
        "validators": [],
    }


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.update(schema_version=2), "schema_version"),
        (lambda value: value.update(package_root="other"), "package_root"),
        (lambda value: value.update(candidate_patterns=["**/check_*.py"]), "fixed scanner scope"),
        (lambda value: value.update(scanner_exclusions=None), "scanner_exclusions"),
        (
            lambda value: value.update(
                scanner_exclusions=[
                    {"path": catalog_check.EXPECTED_SCANNER_EXCLUSIONS[0], "reason": "x"},
                    "not a mapping",
                ]
            ),
            r"scanner_exclusions\[2\]",
        ),
        (
            lambda value: value.update(
                scanner_exclusions=[
                    {
                        "path": catalog_check.EXPECTED_SCANNER_EXCLUSIONS[0],
                        "reason": "",
                    }
                ]
            ),
            "reason",
        ),
        (lambda value: value.update(consumer_contract=None), "consumer_contract"),
        (
            lambda value: value.update(
                consumer_contract={
                    "source": "consumer",
                    "selection_field": "x",
                    "no_substitute": "y",
                }
            ),
            "source.*packaged",
        ),
        (
            lambda value: value.update(
                consumer_contract={"source": "packaged", "selection_field": "", "no_substitute": "y"}
            ),
            "selection_field",
        ),
        (lambda value: value.update(validators=None), "validators"),
    ],
)
def test_header_rejects_each_untrusted_shape(mutate, message: str) -> None:
    header = _valid_header()
    mutate(header)

    with pytest.raises(catalog_check.CatalogError, match=message):
        catalog_check._validate_catalog_header(header, Path("catalog.yaml"), "plugins/charness")


def test_loader_and_discovery_failures_are_attributed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(catalog_check.CatalogError, match="packaged plugin root is missing"):
        catalog_check.discover_packaged_validators(tmp_path / "missing")

    with pytest.raises(catalog_check.CatalogError, match="catalog is missing"):
        catalog_check._load_catalog(tmp_path / "missing.yaml")

    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("placeholder", encoding="utf-8")
    for failure in (OSError("read failed"), ValueError("bad yaml"), TypeError("wrong yaml")):
        monkeypatch.setattr(catalog_check, "load_yaml_file", lambda _path, failure=failure: (_ for _ in ()).throw(failure))
        with pytest.raises(catalog_check.CatalogError, match="could not read catalog"):
            catalog_check._load_catalog(catalog_path)

    monkeypatch.setattr(catalog_check, "load_yaml_file", lambda _path: ["not a mapping"])
    with pytest.raises(catalog_check.CatalogError, match="top level must be a mapping"):
        catalog_check._load_catalog(catalog_path)


@pytest.mark.parametrize(
    ("entry", "message"),
    [
        ([], "must be a mapping"),
        ({"path": "../escape"}, "normalized relative POSIX"),
        ({"path": "scripts/check_demo.py", "consumer_facing": False, "decision": "unknown", "reason": "x"}, "decision"),
        ({"path": "scripts/check_demo.py", "consumer_facing": True, "decision": "publish", "reason": "x"}, "purpose"),
    ],
)
def test_entry_validation_rejects_untrusted_shapes(entry, message: str) -> None:
    with pytest.raises(catalog_check.CatalogError, match=message):
        catalog_check._validate_entry(
            entry,
            index=1,
            catalog_path=Path("catalog.yaml"),
            discovered={"scripts/check_demo.py"},
            declared={},
        )
