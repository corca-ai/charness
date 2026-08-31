from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.quality_gates.git_fixture_support import init_git_repo
from tests.quality_gates.repo_shapes import install_committed_repo

from .support import ROOT, _load_script_module

LIFECYCLE = _load_script_module(
    "quality_declaration_path_resolution_under_test",
    ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py",
)
LIFECYCLE_PATH = ROOT / "skills/public/quality/scripts/quality_declaration_lifecycle.py"
APPLICABILITY = _load_script_module(
    "quality_catalog_gate_applicability_under_test",
    ROOT / "skills/public/quality/scripts/quality_catalog_gate_applicability.py",
)


def test_an_unparseable_command_is_kept_rather_than_declared_unavailable(tmp_path: Path) -> None:
    """A command `shlex` cannot split names no path this check can judge.

    The direction of the fallback is the decision: `_catalog_gate_path` returns `None`, so
    the gate stays APPLICABLE. Reporting it unavailable instead would let one unbalanced
    quote in a catalog entry silently retire a gate that a shell may still run, which is
    the failure this whole module is a guard against -- an unenforceable bar reading as
    protection. Kept-and-visible is the recoverable half of that trade.
    """
    gate = {"id": "unbalanced", "command": './run-quality.sh --mode "full', "run_when": "repo-native command"}

    applicable, unavailable = APPLICABILITY.applicable_catalog_gates(tmp_path, {}, [gate])

    assert unavailable == []
    assert applicable == [gate]
    assert APPLICABILITY._catalog_gate_path('./x "unterminated') is None


def _declared_paths(repo: Path, *declarations: str) -> list[dict[str, object]]:
    return LIFECYCLE._declared_skill_paths(
        repo, {"skill_ergonomics_skill_paths": list(declarations)}
    )


def test_repo_module_bootstraps_repo_import_path_and_fails_loudly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root_text = str(ROOT)
    monkeypatch.setattr(
        LIFECYCLE.sys, "path", [entry for entry in sys.path if entry != root_text]
    )

    module = LIFECYCLE._repo_module("scripts.adapter_lib")

    assert module.__name__ == "scripts.adapter_lib"
    assert LIFECYCLE.sys.path[0] == root_text
    with pytest.raises(ImportError, match="not found from quality skill runtime"):
        LIFECYCLE._repo_module("scripts.quality_module_that_does_not_exist")


def test_declaration_lifecycle_loads_when_importlib_util_was_not_preloaded() -> None:
    source = LIFECYCLE_PATH.read_text(encoding="utf-8")
    program = "\n".join(
        [
            "import importlib",
            "assert not hasattr(importlib, 'util')",
            f"namespace = {{'__file__': {str(LIFECYCLE_PATH)!r}, '__name__': 'isolated_lifecycle'}}",
            f"exec(compile({source!r}, {str(LIFECYCLE_PATH)!r}, 'exec'), namespace)",
        ]
    )

    result = subprocess.run(
        [sys.executable, "-S", "-c", program],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_preset_reconciliation_distinguishes_applied_missing_and_metadata_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    presets = repo / "presets"
    presets.mkdir(parents=True)
    (presets / "strict.md").write_text(
        "---\nname: strict\ndescription: \"Strict reconciliation fixture.\"\npreset_kind: sample-vocabulary\ninstall_scope: maintainer\nreconciliation:\n  required_adapter_commands:\n    - python3 -m pytest\n    - ruff check .\n---\n# strict\n\n## Intended Use\n\nTest fixture.\n",
        encoding="utf-8",
    )
    (presets / "metadata.md").write_text(
        "---\nname: metadata\ndescription: \"Metadata fixture.\"\npreset_kind: sample-vocabulary\ninstall_scope: maintainer\n---\n# metadata\n\n## Intended Use\n\nTest fixture.\n",
        encoding="utf-8",
    )
    modules = {
        "scripts.validate_presets": LIFECYCLE._repo_module("scripts.validate_presets"),
        "scripts.quality_bootstrap_detect": SimpleNamespace(detect_preset_lineage=lambda _repo: ["strict"]),
    }
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)

    rows, gaps = LIFECYCLE._preset_rows(
        repo,
        {
            "preset_lineage": ["strict", "metadata", "missing"],
            "gate_commands": ["python3 -m pytest", "ruff check ."],
        },
    )

    assert rows == [
        {
            "preset": "strict",
            "declaration_state": "declared",
            "repo_signal_detected": True,
            "required_adapter_commands": ["python3 -m pytest", "ruff check ."],
            "missing_adapter_commands": [],
            "reconciliation_state": "reconciled",
        },
        {
            "preset": "metadata",
            "declaration_state": "declared",
            "repo_signal_detected": False,
            "reconciliation_state": "metadata-only",
            "reconciliation_reason": "preset declares no reconciliation prescription",
        },
        {
            "preset": "missing",
            "declaration_state": "declared",
            "repo_signal_detected": False,
            "reconciliation_state": "metadata-only",
            "reconciliation_reason": "no local machine-readable preset prescription",
        },
    ]
    assert gaps == []

    rows, gaps = LIFECYCLE._preset_rows(repo, {"preset_lineage": ["strict"], "gate_commands": []})

    assert rows[0]["reconciliation_state"] == "missing"
    assert rows[0]["missing_adapter_commands"] == ["python3 -m pytest", "ruff check ."]
    assert gaps == [
        {
            "kind": "preset_requirement_missing",
            "detail": "strict: declare adapter command: python3 -m pytest",
        },
        {"kind": "preset_requirement_missing", "detail": "strict: declare adapter command: ruff check ."},
    ]


def test_preset_contract_refuses_malformed_frontmatter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    presets = repo / "presets"
    presets.mkdir(parents=True)
    validator = LIFECYCLE._repo_module("scripts.validate_presets")
    monkeypatch.setattr(
        LIFECYCLE,
        "_repo_module",
        lambda name: validator
        if name == "scripts.validate_presets"
        else SimpleNamespace(detect_preset_lineage=lambda _repo: []),
    )
    prefix = (
        "---\nname: strict\ndescription: \"Strict fixture.\"\npreset_kind: sample-vocabulary\n"
        "install_scope: maintainer\nreconciliation:\n  required_adapter_commands:\n    - pytest\n"
    )
    for frontmatter in ("---not-a-fence", "---not-a-fence\nname: malformed\n"):
        (presets / "strict.md").write_text(prefix + frontmatter, encoding="utf-8")
        assert LIFECYCLE._preset_contract(repo, "strict")["state"] == "unavailable"


def test_preset_contract_accepts_crlf_and_refuses_external_symlink(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "app"
    presets = repo / "presets"
    presets.mkdir(parents=True)
    (presets / "crlf.md").write_bytes(b"---\r\nname: crlf\r\ndescription: \"CRLF fixture.\"\r\npreset_kind: sample-vocabulary\r\ninstall_scope: maintainer\r\nreconciliation:\r\n  required_adapter_commands:\r\n    - pytest\r\n---\r\n# crlf\r\n\r\n## Intended Use\r\n\r\nTest fixture.\r\n")
    outside = tmp_path / "outside.md"
    outside.write_text("---\nname: external\ndescription: \"External fixture.\"\npreset_kind: sample-vocabulary\ninstall_scope: maintainer\nreconciliation:\n  required_adapter_commands:\n    - pytest\n---\n# external\n\n## Intended Use\n\nTest fixture.\n", encoding="utf-8")
    (presets / "external.md").symlink_to(outside)
    validator = LIFECYCLE._repo_module("scripts.validate_presets")
    monkeypatch.setattr(LIFECYCLE, "_repo_module", lambda name: validator if name == "scripts.validate_presets" else SimpleNamespace(detect_preset_lineage=lambda _repo: []))

    assert LIFECYCLE._preset_contract(repo, "crlf")["state"] == "prescribed"
    assert LIFECYCLE._preset_contract(repo, "external")["state"] == "unavailable"
    assert LIFECYCLE._preset_contract(repo, "../external")["state"] == "unavailable"


def test_preset_contract_refuses_a_presets_directory_symlink(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "app"
    outside_presets = tmp_path / "outside-presets"
    outside_presets.mkdir()
    (outside_presets / "strict.md").write_text(
        "---\nname: strict\ndescription: \"Strict fixture.\"\npreset_kind: sample-vocabulary\ninstall_scope: maintainer\nreconciliation:\n  required_adapter_commands:\n    - pytest\n---\n# strict\n\n## Intended Use\n\nTest fixture.\n",
        encoding="utf-8",
    )
    repo.mkdir()
    (repo / "presets").symlink_to(outside_presets, target_is_directory=True)
    validator = LIFECYCLE._repo_module("scripts.validate_presets")
    monkeypatch.setattr(LIFECYCLE, "_repo_module", lambda name: validator if name == "scripts.validate_presets" else SimpleNamespace(detect_preset_lineage=lambda _repo: []))

    contract = LIFECYCLE._preset_contract(repo, "strict")

    assert contract == {"state": "unavailable", "reason": "presets/strict.md must resolve inside presets/"}


def test_declaration_lifecycle_refuses_when_adjacent_catalog_is_not_loadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        LIFECYCLE.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None
    )

    with pytest.raises(ImportError, match="quality_catalog_gate_applicability.py not loadable beside"):
        LIFECYCLE._load_catalog_applicability()


def test_declaration_lifecycle_refuses_when_adjacent_preset_helper_is_not_loadable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        LIFECYCLE.importlib.util, "spec_from_file_location", lambda *_args, **_kwargs: None
    )

    with pytest.raises(ImportError, match="quality_preset_reconciliation.py not loadable beside"):
        LIFECYCLE._load_preset_reconciliation()


def test_preset_reconciliation_reports_unavailable_contract_shapes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    presets = repo / "presets"
    presets.mkdir(parents=True)
    strict = presets / "strict.md"
    strict.write_text("fixture", encoding="utf-8")
    validator = SimpleNamespace(
        re=__import__("re"), PRESET_NAME_RE=r"[a-z]+",
        ValidationError=ValueError,
        validate_preset=lambda _path: {"reconciliation": "wrong-shape"},
    )
    modules = {
        "scripts.validate_presets": validator,
        "scripts.quality_bootstrap_detect": SimpleNamespace(detect_preset_lineage=lambda _repo: ["strict"]),
    }
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)

    contract = LIFECYCLE._preset_contract(repo, "strict")
    assert contract == {"state": "unavailable", "reason": "reconciliation must be a mapping"}

    validator.validate_preset = lambda _path: {"reconciliation": {"required_adapter_commands": []}}
    contract = LIFECYCLE._preset_contract(repo, "strict")
    assert contract["state"] == "unavailable"
    assert "non-empty string list" in contract["reason"]

    monkeypatch.setattr(
        LIFECYCLE._PRESET_RECONCILIATION,
        "preset_contract",
        lambda *_args: {"state": "unavailable", "reason": "forced unavailable"},
    )
    rows, gaps = LIFECYCLE._preset_rows(repo, {"preset_lineage": ["strict"]})
    assert rows[0]["reconciliation_state"] == "unavailable"
    assert gaps == [{"kind": "preset_reconciliation_unavailable", "detail": "strict: forced unavailable"}]


def test_preset_contract_reports_a_resolve_oserror(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo = tmp_path / "app"
    preset = repo / "presets" / "strict.md"
    preset.parent.mkdir(parents=True)
    preset.write_text("fixture", encoding="utf-8")
    validator = SimpleNamespace(re=__import__("re"), PRESET_NAME_RE=r"[a-z]+", ValidationError=ValueError)
    monkeypatch.setattr(LIFECYCLE, "_repo_module", lambda _name: validator)
    original = Path.resolve

    def fail_preset(path: Path, *args, **kwargs):
        if path == preset:
            raise OSError("forced resolve failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "resolve", fail_preset)
    assert LIFECYCLE._preset_contract(repo, "strict") == {
        "state": "unavailable", "reason": "could not resolve presets/strict.md"
    }


def test_declaration_helpers_skip_non_values_without_creating_routes(
    tmp_path: Path,
) -> None:
    command_rows, packets = LIFECYCLE._declared_commands(
        {"gate_commands": [None, "", "python3 -m pytest"]}, []
    )
    repo = tmp_path / "app"
    repo.mkdir()

    path_rows = LIFECYCLE._declared_skill_paths(
        repo, {"skill_ergonomics_skill_paths": [None, ""]}
    )

    assert [row["command"] for row in command_rows] == ["python3 -m pytest"]
    assert len(packets) == 1
    assert path_rows == []


def test_declared_paths_report_uninterpretable_patterns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()

    def fail_listing(_repo: Path, _patterns: tuple[str, ...]):
        raise ValueError("bad pattern")

    monkeypatch.setattr(
        LIFECYCLE._REPO_FILE_LISTING, "iter_matching_repo_files", fail_listing
    )

    row = _declared_paths(repo, "skills/*/SKILL.md")[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["declaration_error"] == "path pattern could not be interpreted"


def test_declared_paths_skip_non_skills_and_count_unresolvable_candidates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    readme = repo / "README.md"
    readme.write_text("# app\n", encoding="utf-8")

    class UnresolvableSkill:
        name = "SKILL.md"

        @staticmethod
        def is_file() -> bool:
            return True

        @staticmethod
        def resolve() -> Path:
            raise OSError("unreadable target")

    monkeypatch.setattr(
        LIFECYCLE._REPO_FILE_LISTING,
        "iter_matching_repo_files",
        lambda _repo, _patterns: [readme, UnresolvableSkill()],
    )

    row = _declared_paths(repo, "**/*")[0]

    assert row["target_state"] == "unreachable"
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1


def test_declaration_lifecycle_treats_non_mapping_yaml_as_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modules = {
        "scripts.quality_adapter_lib": SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {
                "found": True,
                "valid": True,
                "path": str(tmp_path / ".agents" / "quality-adapter.yaml"),
                "errors": [],
                "warnings": [],
            }
        ),
        "scripts.adapter_lib": SimpleNamespace(load_yaml_file=lambda _path: []),
        "scripts.quality_bootstrap_detect": SimpleNamespace(
            detect_preset_lineage=lambda _repo: []
        ),
    }
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)

    report, packets = LIFECYCLE.build_declaration_lifecycle(
        tmp_path, skills=[], catalog_gates=[]
    )

    assert report["status"] == "configured"
    assert report["commands"] == []
    assert report["surfaces"] == []
    assert report["declared_skill_paths"] == []
    assert packets == []


def test_declaration_lifecycle_keeps_catalog_gates_when_no_adapter_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modules = {
        "scripts.quality_adapter_lib": SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {
                "found": False,
                "valid": True,
                "path": None,
                "errors": [],
                "warnings": [],
            }
        ),
        "scripts.adapter_lib": SimpleNamespace(load_yaml_file=lambda _path: {}),
        "scripts.quality_bootstrap_detect": SimpleNamespace(
            detect_preset_lineage=lambda _repo: []
        ),
    }
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)
    catalog_gates = [{"id": "repo-native", "command": "./scripts/run-quality.sh"}]

    report, packets = LIFECYCLE.build_declaration_lifecycle(
        tmp_path, skills=[], catalog_gates=catalog_gates
    )

    assert report["status"] == "not-configured"
    assert report["unavailable_catalog_gates"] == []
    assert report["gaps"] == []
    assert packets == []


def test_declaration_lifecycle_reports_unavailable_catalog_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    modules = {
        "scripts.quality_adapter_lib": SimpleNamespace(
            load_quality_adapter_permissive=lambda _repo: {
                "found": True,
                "valid": True,
                "path": str(tmp_path / ".agents" / "quality-adapter.yaml"),
                "errors": [],
                "warnings": [],
            }
        ),
        "scripts.adapter_lib": SimpleNamespace(load_yaml_file=lambda _path: {}),
        "scripts.quality_bootstrap_detect": SimpleNamespace(
            detect_preset_lineage=lambda _repo: []
        ),
    }
    unavailable = {"id": "repo-native", "reason": "runner is absent"}
    monkeypatch.setattr(LIFECYCLE, "_repo_module", modules.__getitem__)
    monkeypatch.setattr(
        LIFECYCLE._CATALOG_APPLICABILITY,
        "applicable_catalog_gates",
        lambda _repo, _raw, _gates: ([], [unavailable]),
    )

    report, packets = LIFECYCLE.build_declaration_lifecycle(
        tmp_path, skills=[], catalog_gates=[{"id": "repo-native"}]
    )

    assert report["unavailable_catalog_gates"] == [unavailable]
    assert report["gaps"] == [
        {"kind": "catalog_gate_unavailable", "detail": "repo-native: runner is absent"}
    ]
    assert packets == []


def test_declared_paths_do_not_resolve_ignored_repo_skills_or_support_symlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = install_committed_repo(tmp_path / "app", {".gitignore": "ignored/\n"})
    ignored_skill = repo / "ignored" / "private" / "SKILL.md"
    ignored_skill.parent.mkdir(parents=True)
    ignored_skill.write_text("# ignored\n", encoding="utf-8")

    rows = _declared_paths(
        repo, "ignored/*/SKILL.md", "ignored/private/SKILL.md"
    )

    assert rows == [
        {
            "declaration": "ignored/*/SKILL.md",
            "target_state": "unreachable",
            "resolved_paths": [],
            "routing_state": "routed",
            "packet_id": "skill-ergonomics",
        },
        {
            "declaration": "ignored/private/SKILL.md",
            "target_state": "unreachable",
            "resolved_paths": [],
            "routing_state": "routed",
            "packet_id": "skill-ergonomics",
        },
    ]

    support = tmp_path / "support"
    alias = support / "alias"
    alias.mkdir(parents=True)
    (alias / "SKILL.md").symlink_to(ignored_skill)
    init_git_repo(support)
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))
    row = _declared_paths(repo, "skills/support/alias/SKILL.md")[0]
    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1
    assert "target_scope" not in row


def test_declared_paths_refuse_out_of_repo_declarations(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    outside = tmp_path / "outside" / "nested"
    outside.mkdir(parents=True)
    (outside / "SKILL.md").write_text("# outside\n", encoding="utf-8")

    rows = _declared_paths(
        repo, "../outside/SKILL.md", "../outside/*/SKILL.md", "/tmp/outside/SKILL.md"
    )
    assert len(rows) == 3
    for row in rows:
        assert row["target_state"] == "unreachable"
        assert row["resolved_paths"] == []
        assert "repo-relative" in row["declaration_error"]


def test_declared_paths_virtualize_configured_external_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    support = tmp_path / "support"
    skill = support / "feedback" / "SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("# Feedback\n", encoding="utf-8")
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))

    row = _declared_paths(repo, "skills/support/feedback/SKILL.md")[0]

    assert row["target_state"] == "resolved"
    assert row["resolved_paths"] == ["skills/support/feedback/SKILL.md"]
    assert row["target_scope"] == "configured-external-support"
    assert str(tmp_path) not in str(row)


def test_declared_paths_do_not_resolve_ignored_external_support(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    support = install_committed_repo(tmp_path / "support", {".gitignore": "private/\n"})
    ignored_skill = support / "private" / "SKILL.md"
    ignored_skill.parent.mkdir(parents=True)
    ignored_skill.write_text("# ignored\n", encoding="utf-8")
    monkeypatch.setenv("CHARNESS_SUPPORT_DIR", str(support))

    rows = _declared_paths(
        repo, "skills/support/private/SKILL.md", "skills/support/*/SKILL.md"
    )
    assert len(rows) == 2
    for row in rows:
        assert row["target_state"] == "unreachable"
        assert row["resolved_paths"] == []
        assert row["routing_state"] == "routed"


def test_declared_paths_refuse_repo_symlink_escape(tmp_path: Path) -> None:
    repo = tmp_path / "app"
    repo.mkdir()
    outside_skill = tmp_path / "outside" / "SKILL.md"
    outside_skill.parent.mkdir()
    outside_skill.write_text("# outside\n", encoding="utf-8")
    alias = repo / "alias"
    alias.mkdir()
    (alias / "SKILL.md").symlink_to(outside_skill)

    row = _declared_paths(repo, "alias/SKILL.md")[0]

    assert row["target_state"] == "unreachable"
    assert row["resolved_paths"] == []
    assert row["routing_state"] == "partial"
    assert row["excluded_match_count"] == 1
