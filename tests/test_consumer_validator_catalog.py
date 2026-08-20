from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

from scripts import check_consumer_validator_catalog as catalog_check
from tests.script_main import run_loaded_script_main

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
        entry["id"] = path.rsplit("/", 1)[-1].removesuffix(".py").replace("_", "-")
        entry["artifact_type"] = "consumer-artifact"
        entry["adoption_policy"] = "wire-or-opt-out"
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
                "catalog_id: consumer-validator-catalog",
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
                "adoption_policy:",
                "  declaration_path: .agents/consumer-validator-adoption.yaml",
                "  exactly_one_of:",
                "    - wired",
                "    - opt_out_reason",
                "validators:",
                *[
                    f"  - path: {entry['path']}\n"
                    f"    consumer_facing: {str(entry['consumer_facing']).lower()}\n"
                    f"    decision: {entry['decision']}\n"
                    f"    reason: {entry['reason']}"
                    + (
                        f"\n    id: {entry['id']}\n"
                        f"    artifact_type: {entry['artifact_type']}\n"
                        f"    adoption_policy: {entry['adoption_policy']}\n"
                        f"    purpose: {entry['purpose']}\n"
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
    assert "handoff-artifact" in report["consumer_validator_ids"]
    handoff = next(
        entry for entry in report["consumer_validator_entries"] if entry["id"] == "handoff-artifact"
    )
    assert handoff["artifact_type"]
    assert handoff["purpose"]
    assert handoff["invocation"].startswith("python3 <plugin-root>/")


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

    entry["invocation"] = "python3 <plugin-root>/scripts/check_demo.py.backup"
    _write_catalog(repo, [entry])
    with pytest.raises(catalog_check.CatalogError, match="invocation.*packaged path"):
        catalog_check.validate_catalog(repo)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("id", "", "id.*non-empty string"),
        ("artifact_type", "", "artifact_type.*non-empty string"),
        ("adoption_policy", "manual", "adoption_policy.*wire-or-opt-out"),
    ],
)
def test_consumer_entry_requires_public_contract_fields(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    entry[field] = value
    _write_catalog(repo, [entry])

    with pytest.raises(catalog_check.CatalogError, match=message):
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


def test_cli_main_emits_a_structured_success_report(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    _write_catalog(repo, [_entry("scripts/check_demo.py")])

    result = run_loaded_script_main(
        "check_consumer_validator_catalog.py",
        catalog_check,
        "--repo-root",
        str(repo),
    )

    assert result.returncode == 0
    assert "status: pass" in result.stdout
    assert result.stderr == ""


def test_cli_main_reports_catalog_failure_without_traceback(tmp_path: Path) -> None:
    result = run_loaded_script_main(
        "check_consumer_validator_catalog.py",
        catalog_check,
        "--repo-root",
        str(tmp_path),
    )

    assert result.returncode == 1
    assert "status: fail" in result.stderr
    assert "catalog is missing" in result.stderr


def test_script_entrypoint_calls_main_when_loaded_as_main(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = _fixture_repo(tmp_path)
    _write_catalog(repo, [_entry("scripts/check_demo.py")])
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_consumer_validator_catalog.py", "--repo-root", str(repo)],
    )

    with pytest.raises(SystemExit) as raised:
        runpy.run_path(str(ROOT / "scripts/check_consumer_validator_catalog.py"), run_name="__main__")

    assert raised.value.code == 0


def _valid_header() -> dict[str, object]:
    return {
        "schema_version": 1,
        "catalog_id": "consumer-validator-catalog",
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
        "adoption_policy": {
            "declaration_path": ".agents/consumer-validator-adoption.yaml",
            "exactly_one_of": ["wired", "opt_out_reason"],
        },
        "validators": [],
    }


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.update(schema_version=2), "schema_version"),
        (lambda value: value.update(catalog_id="other"), "catalog_id"),
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
        (lambda value: value.update(adoption_policy=None), "adoption_policy"),
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
        (
            {
                "path": "scripts/check_demo.py",
                "consumer_facing": True,
                "decision": "publish",
                "reason": "x",
                "id": "check-demo",
                "artifact_type": "artifact",
                "adoption_policy": "wire-or-opt-out",
            },
            "purpose",
        ),
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


def _write_adoption(repo: Path, entries: list[dict[str, object]]) -> Path:
    path = repo / catalog_check.DEFAULT_ADOPTION_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "schema_version: 1\n"
        "catalog_id: consumer-validator-catalog\n"
        "validators:\n"
        + "".join(
            f"  - id: {entry['id']}\n"
            + (f"    wired: {str(entry['wired']).lower()}\n" if "wired" in entry else "")
            + (f"    opt_out_reason: {entry['opt_out_reason']}\n" if "opt_out_reason" in entry else "")
            for entry in entries
        ),
        encoding="utf-8",
    )
    return path


def test_required_adoption_declares_exactly_one_decision_for_each_consumer(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [entry])

    with pytest.raises(catalog_check.CatalogError, match="adoption declaration is missing"):
        catalog_check.validate_catalog(
            repo,
            adoption_path=catalog_check.DEFAULT_ADOPTION_REL,
            require_adoption=True,
        )

    adoption = _write_adoption(repo, [{"id": entry["id"], "wired": True}])
    report = catalog_check.validate_catalog(repo, adoption_path=adoption, require_adoption=True)
    assert report["adoption"]["status"] == "pass"
    assert report["adoption"]["wired_count"] == 1
    assert report["adoption"]["decisions"] == [{"id": entry["id"], "wired": True}]


def test_staged_adoption_requires_an_index_entry(tmp_path: Path) -> None:
    import subprocess

    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [entry])
    adoption = _write_adoption(repo, [{"id": entry["id"], "wired": True}])
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)

    with pytest.raises(catalog_check.CatalogError, match="must be staged"):
        catalog_check.validate_catalog(
            repo,
            adoption_path=adoption,
            require_adoption=True,
            require_staged_adoption=True,
        )


def test_adoption_path_cannot_be_retargeted_by_a_relative_or_named_path(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [entry])
    adoption = _write_adoption(repo, [{"id": entry["id"], "wired": True}])

    with pytest.raises(catalog_check.CatalogError, match="adoption path must"):
        catalog_check.validate_catalog(repo, adoption_path=Path("../other.yaml"))
    with pytest.raises(catalog_check.CatalogError, match="adoption path must"):
        catalog_check.validate_catalog(repo, adoption_path=adoption.with_name("other.yaml"))


@pytest.mark.parametrize(
    "entry",
    [
        {"id": "check-demo", "wired": True, "opt_out_reason": "both"},
        {"id": "check-demo"},
        {"id": "check-demo", "wired": False},
    ],
)
def test_adoption_rejects_ambiguous_or_false_wiring(tmp_path: Path, entry: dict[str, object]) -> None:
    repo = _fixture_repo(tmp_path)
    catalog_entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [catalog_entry])
    _write_adoption(repo, [entry])

    with pytest.raises(catalog_check.CatalogError, match="exactly one|must be true"):
        catalog_check.validate_catalog(
            repo,
            adoption_path=catalog_check.DEFAULT_ADOPTION_REL,
            require_adoption=True,
        )
