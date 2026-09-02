from __future__ import annotations

import runpy
import shutil
import sys
from pathlib import Path

import pytest
import yaml

from scripts import check_consumer_validator_catalog as catalog_check
from scripts import packaging_lib
from tests.quality_gates.git_fixture_support import init_git_repo
from tests.script_main import run_loaded_script_main

ROOT = Path(__file__).resolve().parents[1]


def _export_live_catalog_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "live-repo"
    source_catalog = repo / catalog_check.DEFAULT_CATALOG_REL
    source_catalog.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / catalog_check.DEFAULT_CATALOG_REL, source_catalog)
    manifest = packaging_lib.load_manifest(ROOT, "charness")
    packaging_lib.export_plugin_tree(ROOT, repo / "plugins" / "charness", manifest)
    return repo


def _fixture_repo(
    tmp_path: Path, *, candidates: tuple[str, ...] = ("scripts/check_demo.py",)
) -> Path:
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
                # Derived from the checker's own constant rather than restated, so a
                # future predicate change cannot leave this fixture asserting the old
                # scope while the tests it feeds still read as passing.
                "candidate_patterns:",
                *[f"  - '{pattern}'" for pattern in catalog_check.EXPECTED_CANDIDATE_PATTERNS],
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


def test_the_discovery_predicate_is_positional_free_and_lost_nothing(tmp_path: Path) -> None:
    """Capability-equality replay for the prefix -> token-anywhere conversion.

    The goal that made this change requires, before any enumeration becomes a
    derived property, that every entry the OLD predicate admitted is replayed
    against the new one and produces the same answer. Asserting equal capability is
    what the design north star records being wrong four times in a row; this replays
    it instead.

    The one gained path is named, not tolerated as noise: it is the live miss that
    motivated the change -- a packaged validator the issue-closeout floor invokes,
    which the prefix-only predicate never discovered, so it needed no catalog
    decision and nothing said so.
    """
    package_root = _export_live_catalog_repo(tmp_path) / "plugins" / "charness"
    old_predicate = sorted(
        path.relative_to(package_root).as_posix()
        for path in package_root.rglob("*.py")
        if path.is_file()
        and path.name.startswith(("check_", "validate_"))
        and path.relative_to(package_root).as_posix()
        not in catalog_check.EXPECTED_SCANNER_EXCLUSIONS
    )
    new_predicate = catalog_check.discover_packaged_validators(package_root)

    assert old_predicate, "replay is vacuous if the old predicate admitted nothing"
    lost = set(old_predicate) - set(new_predicate)
    assert not lost, f"capability regression: the new predicate stopped admitting {sorted(lost)}"

    # The divergence is CHARACTERISED, not pinned to a filename. A first cut asserted
    # the gained set equals one literal path — which would demand a chore edit the next
    # time someone correctly adds an infix-named validator with its decision, i.e. the
    # exact property for which the `== 134` population pin was classified
    # `recommend-removal` a slice earlier. The motivating instance belongs in the
    # docstring above; what an assertion should hold is the SHAPE of the widening.
    for path in set(new_predicate) - set(old_predicate):
        name = Path(path).name
        assert catalog_check._is_candidate_name(name)
        assert not name.startswith(("check_", "validate_")), (
            f"{path} was already admitted by the old predicate; the widening should "
            f"only add basenames carrying a token away from the front"
        )


def test_an_infix_named_validator_is_refused_where_the_old_predicate_tolerated_it(
    tmp_path: Path,
) -> None:
    """THE negative control for the conversion, and it did not exist until round 2.

    Every other planted-defect fixture in this file uses a PREFIX-form name
    (`check_demo.py`, `validate_missing.py`), which the old positional predicate
    already refused — so none of them could tell the two predicates apart. This one
    plants the defect the conversion exists to catch: an undeclared packaged module
    whose candidate token sits in the MIDDLE of the basename. Before the change it was
    silently outside the catalog; now it must be refused.

    The old-predicate arm is asserted too, so this is a verdict FLIP and not merely a
    refusal that might always have happened.
    """
    infix = "skills/demo/scripts/issue_validate_thing.py"
    repo = _fixture_repo(tmp_path, candidates=("scripts/check_demo.py", infix))
    _write_catalog(repo, [_entry("scripts/check_demo.py")])

    # The predicate that shipped before this slice would not have admitted it at all.
    assert not Path(infix).name.startswith(("check_", "validate_"))
    # The one that ships now does, so the missing decision is refused.
    assert catalog_check._is_candidate_name(Path(infix).name)
    with pytest.raises(catalog_check.CatalogError) as raised:
        catalog_check.validate_catalog(repo)
    assert "missing an explicit catalog decision" in str(raised.value)
    assert infix in str(raised.value)


def test_the_scanner_exclusion_list_is_exactly_the_checker_itself(tmp_path: Path) -> None:
    """The one detection the removed population pin uniquely owned, made explicit.

    Adding a packaged validator to `EXPECTED_SCANNER_EXCLUSIONS` and deleting its
    catalog entry is a complete, self-consistent change that SHRINKS the enforced
    population — the defect class this gate exists for, and the only one the `== 134`
    pin caught that the checker does not. Today a growing exclusion list happens to
    redden the suite because the shared fixture hardcodes the single exclusion line;
    that is incidental, and the obvious next tidy-up (deriving it, as
    `candidate_patterns` now is) would silently remove the last guard. This asserts it
    on purpose instead.
    """
    assert catalog_check.EXPECTED_SCANNER_EXCLUSIONS == (
        "scripts/check_consumer_validator_catalog.py",
    ), "the scanner may exclude only itself; a new exclusion shrinks the enforced set"


def test_the_catalog_reports_what_its_predicate_did_not_admit(tmp_path: Path) -> None:
    """A green here must not read as coverage of the whole package.

    `packaged_validator_count` counts what the predicate ADMITTED. On its own it
    reads as though every packaged module were accounted for, and a validator named
    with neither token is outside the catalog with no failure marking it. The gate
    now says so in its own output, which is the difference between a green that
    means "checked" and one that cannot tell "checked" from "never looked".
    """
    report = catalog_check.validate_catalog(_export_live_catalog_repo(tmp_path))

    assert report["packaged_module_count"] > report["packaged_validator_count"]
    assert report["uncovered_module_count"] > 0, (
        "a zero here would mean the predicate admits every packaged module; if that "
        "ever becomes true this assertion should be re-derived, not deleted"
    )
    # The NON-ZERO arm of the exclusion count, on the one tree where it is non-zero.
    # The fixture test pins it at 0 (the excluded file is absent there), and pinning
    # only that arm let `def count_scanner_exclusions(...): return 0` pass the whole
    # suite -- which is the shape of the defect that function was written to repair: a
    # published count whose wrong value nothing measured. It also silently shifts
    # `uncovered_module_count` by one, so the two are asserted together.
    assert report["scanner_excluded_count"] == len(catalog_check.EXPECTED_SCANNER_EXCLUSIONS), (
        "every declared scanner exclusion is present in this repo's packaged tree, so "
        "the measured count must equal the declared one here"
    )
    assert (
        report["packaged_module_count"]
        == report["packaged_validator_count"]
        + report["scanner_excluded_count"]
        + report["uncovered_module_count"]
    ), "the three buckets must partition the walked population exactly"
    # NOT `report["candidate_predicate"] == list(EXPECTED_CANDIDATE_PATTERNS)`. That
    # assertion was here and was removed as a tautology: the field is CONSTRUCTED from
    # that constant, so it could not fail for any value of it — the same dead-assertion
    # species this slice deleted one screen below, re-added by the same slice that
    # deleted it. A fresh-eye round caught it.
    #
    # The real risk it was hiding: `CANDIDATE_TOKENS` decides the population and
    # `EXPECTED_CANDIDATE_PATTERNS` is the operator-runnable glob the catalog restates,
    # and nothing tied them together. Publishing `**/*check*.py` (no underscore) while
    # enforcing `check_` would make the gate advertise a scope it does not apply. This
    # asserts the tie in the direction that matters: every glob's token must be one the
    # predicate actually enforces.
    for pattern in report["candidate_predicate"]:
        token = pattern.removeprefix("**/*").removesuffix("*.py")
        assert token in catalog_check.CANDIDATE_TOKENS, (
            f"published predicate {pattern!r} advertises token {token!r}, which "
            f"`_is_candidate_name` does not enforce"
        )
        assert catalog_check._is_candidate_name(f"a{token}b.py"), (
            f"a basename matching published glob {pattern!r} is not admitted"
        )
    assert len(report["candidate_predicate"]) == len(catalog_check.CANDIDATE_TOKENS)


def test_live_catalog_has_a_decision_for_every_packaged_candidate(tmp_path: Path) -> None:
    report = catalog_check.validate_catalog(_export_live_catalog_repo(tmp_path))

    assert report["status"] == "pass"
    assert "scripts/validate_adapters.py" not in report["consumer_facing_validators"]
    assert "quality-artifact" in report["consumer_validator_ids"]
    quality = next(
        entry for entry in report["consumer_validator_entries"] if entry["id"] == "quality-artifact"
    )
    assert quality["artifact_type"]
    assert quality["purpose"]
    assert quality["invocation"].startswith("python3 <plugin-root>/")


def test_new_packaged_validator_cannot_stay_silent(tmp_path: Path) -> None:
    repo = _fixture_repo(
        tmp_path, candidates=("scripts/check_demo.py", "skills/demo/validate_new.py")
    )
    _write_catalog(repo, [_entry("scripts/check_demo.py")])

    with pytest.raises(catalog_check.CatalogError, match="missing an explicit catalog decision"):
        catalog_check.validate_catalog(repo)


def test_catalog_rejects_a_non_packaged_or_duplicate_entry(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    _write_catalog(repo, [_entry("scripts/check_demo.py"), _entry("scripts/check_demo.py")])

    with pytest.raises(catalog_check.CatalogError, match="duplicate validator path"):
        catalog_check.validate_catalog(repo)

    _write_catalog(repo, [_entry("scripts/check_demo.py"), _entry("scripts/validate_missing.py")])
    # Matches the predicate-agnostic wording. The old message hardcoded
    # `check_/validate_` and kept teaching the prefix rule after the predicate stopped
    # being positional; this test pinned that stale text in place.
    with pytest.raises(catalog_check.CatalogError, match="not a packaged validator candidate"):
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
    # Target the checker's own second pattern rather than a hardcoded literal, so
    # this narrowing test cannot quietly stop narrowing anything when the predicate
    # changes — which is exactly what it did when the predicate became positional.
    text = path.read_text(encoding="utf-8").replace(
        f"'{catalog_check.EXPECTED_CANDIDATE_PATTERNS[1]}'", "'scripts/check_*.py'"
    )
    assert text != path.read_text(encoding="utf-8"), "the narrowing edit did not apply"
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
    _write_catalog(
        repo,
        [_entry("scripts/check_demo.py"), _entry("scripts/validate_demo.py", consumer_facing=True)],
    )

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
    # THE WIRED PATH for the uncovered-set report. The other assertions on these
    # fields call `validate_catalog` directly; this one goes through the CLI an
    # operator actually invokes, because the goal that added them names #586 -- a
    # check that passes its own direct-call test while never firing on the wired
    # path -- as a constraint on its own repairs.
    assert "uncovered_module_count:" in result.stdout
    assert "candidate_predicate:" in result.stdout
    # Presence was all this asserted, and presence was not enough: the count subtracted
    # a CONSTANT number of scanner exclusions from a MEASURED population, so this very
    # fixture -- one packaged module, one discovered, one declared exclusion that is not
    # in the tree -- emitted `uncovered_module_count: -1` through the wired path, and the
    # suite stayed green. A count of modules nobody looked at cannot be negative.
    payload = yaml.safe_load(result.stdout)
    assert payload["uncovered_module_count"] == 0, payload
    assert payload["scanner_excluded_count"] == 0, (
        "the declared exclusion is not in this fixture's tree, so nothing was excluded"
    )
    assert payload["uncovered_module_count"] >= 0


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


def test_script_entrypoint_calls_main_when_loaded_as_main(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _fixture_repo(tmp_path)
    _write_catalog(repo, [_entry("scripts/check_demo.py")])
    monkeypatch.setattr(
        sys,
        "argv",
        ["check_consumer_validator_catalog.py", "--repo-root", str(repo)],
    )

    with pytest.raises(SystemExit) as raised:
        runpy.run_path(
            str(ROOT / "scripts/check_consumer_validator_catalog.py"), run_name="__main__"
        )

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
                adoption_policy={
                    "declaration_path": "wrong.yaml",
                    "exactly_one_of": ["wired", "opt_out_reason"],
                }
            ),
            "adoption declaration path",
        ),
        (
            lambda value: value.update(
                adoption_policy={
                    "declaration_path": ".agents/consumer-validator-adoption.yaml",
                    "exactly_one_of": ["wired"],
                }
            ),
            "adoption policy",
        ),
        (
            lambda value: value.update(
                consumer_contract={
                    "source": "packaged",
                    "selection_field": "",
                    "no_substitute": "y",
                }
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


def test_loader_and_discovery_failures_are_attributed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(catalog_check.CatalogError, match="packaged plugin root is missing"):
        catalog_check.discover_packaged_validators(tmp_path / "missing")

    with pytest.raises(catalog_check.CatalogError, match="catalog is missing"):
        catalog_check._load_catalog(tmp_path / "missing.yaml")

    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text("placeholder", encoding="utf-8")
    for failure in (OSError("read failed"), ValueError("bad yaml"), TypeError("wrong yaml")):
        monkeypatch.setattr(
            catalog_check,
            "load_yaml_file",
            lambda _path, failure=failure: (_ for _ in ()).throw(failure),
        )
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
        (
            {
                "path": "scripts/check_demo.py",
                "consumer_facing": False,
                "decision": "unknown",
                "reason": "x",
            },
            "decision",
        ),
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


def test_consumer_entry_rejects_unstable_duplicate_and_malformed_ids() -> None:
    invalid_id = _entry("scripts/check_demo.py", consumer_facing=True)
    invalid_id["id"] = "Check_Demo"
    with pytest.raises(catalog_check.CatalogError, match="stable lower-kebab-case"):
        catalog_check._validate_entry(
            invalid_id,
            index=1,
            catalog_path=Path("catalog.yaml"),
            discovered={"scripts/check_demo.py"},
            declared={},
        )

    duplicate = _entry("scripts/check_demo.py", consumer_facing=True)
    with pytest.raises(catalog_check.CatalogError, match="duplicate validator id"):
        catalog_check._validate_entry(
            duplicate,
            index=1,
            catalog_path=Path("catalog.yaml"),
            discovered={"scripts/check_demo.py"},
            declared={"scripts/other.py": {"id": duplicate["id"]}},
        )

    malformed = _entry("scripts/check_demo.py", consumer_facing=True)
    malformed["invocation"] = "python3 <plugin-root>/scripts/check_demo.py 'unterminated"
    with pytest.raises(catalog_check.CatalogError, match="shell-tokenizable"):
        catalog_check._validate_entry(
            malformed,
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
            + (
                f"    opt_out_reason: {entry['opt_out_reason']}\n"
                if "opt_out_reason" in entry
                else ""
            )
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
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [entry])
    adoption = _write_adoption(repo, [{"id": entry["id"], "wired": True}])
    init_git_repo(repo)

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


def test_staged_adoption_reports_outside_root_and_git_errors(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    adoption = repo / catalog_check.DEFAULT_ADOPTION_REL
    adoption.parent.mkdir(parents=True)
    adoption.write_text("schema_version: 1\n", encoding="utf-8")
    outside = tmp_path / "outside" / catalog_check.DEFAULT_ADOPTION_REL

    with pytest.raises(catalog_check.CatalogError, match="inside the repo root"):
        catalog_check._require_staged_adoption(repo, outside)

    def fail_git(*_args: object, **_kwargs: object) -> object:
        raise OSError("git unavailable")

    monkeypatch.setattr(catalog_check, "run_process", fail_git)
    with pytest.raises(catalog_check.CatalogError, match="could not verify staged"):
        catalog_check._require_staged_adoption(repo, adoption)


@pytest.mark.parametrize(
    "entry",
    [
        {"id": "check-demo", "wired": True, "opt_out_reason": "both"},
        {"id": "check-demo"},
        {"id": "check-demo", "wired": False},
    ],
)
def test_adoption_rejects_ambiguous_or_false_wiring(
    tmp_path: Path, entry: dict[str, object]
) -> None:
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


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda text: text.replace("schema_version: 1", "schema_version: 2"), "schema_version"),
        (
            lambda text: text.replace(
                "catalog_id: consumer-validator-catalog", "catalog_id: other"
            ),
            "catalog_id",
        ),
        (lambda text: text.replace("validators:\n", "validators: {}\n"), "validators.*list"),
    ],
)
def test_adoption_rejects_invalid_header_shapes(tmp_path: Path, mutation, message: str) -> None:
    repo = _fixture_repo(tmp_path)
    entry = _entry("scripts/check_demo.py", consumer_facing=True)
    _write_catalog(repo, [entry])
    adoption = _write_adoption(repo, [{"id": entry["id"], "wired": True}])
    adoption.write_text(mutation(adoption.read_text(encoding="utf-8")), encoding="utf-8")

    with pytest.raises(catalog_check.CatalogError, match=message):
        catalog_check.validate_catalog(
            repo,
            adoption_path=catalog_check.DEFAULT_ADOPTION_REL,
            require_adoption=True,
        )


def test_adoption_requires_a_decision_for_every_consumer_validator(tmp_path: Path) -> None:
    repo = _fixture_repo(
        tmp_path,
        candidates=("scripts/check_demo.py", "scripts/validate_demo.py"),
    )
    entries = [
        _entry("scripts/check_demo.py", consumer_facing=True),
        _entry("scripts/validate_demo.py", consumer_facing=True),
    ]
    _write_catalog(repo, entries)
    _write_adoption(repo, [{"id": entries[0]["id"], "wired": True}])

    with pytest.raises(catalog_check.CatalogError, match="missing an adoption decision"):
        catalog_check.validate_catalog(
            repo,
            adoption_path=catalog_check.DEFAULT_ADOPTION_REL,
            require_adoption=True,
        )


@pytest.mark.parametrize(
    ("entry", "seen", "expected", "message"),
    [
        ([], set(), {"check-demo"}, "must be a mapping"),
        ({"id": "check-demo", "wired": True}, {"check-demo"}, {"check-demo"}, "duplicate"),
        ({"id": "other", "wired": True}, set(), {"check-demo"}, "not a consumer-facing"),
    ],
)
def test_adoption_entry_rejects_nonmapping_duplicate_and_unknown(
    entry, seen: set[str], expected: set[str], message: str
) -> None:
    with pytest.raises(catalog_check.CatalogError, match=message):
        catalog_check._validate_adoption_entry(
            entry,
            index=1,
            path=Path(".agents/consumer-validator-adoption.yaml"),
            expected_ids=expected,
            seen=seen,
        )
