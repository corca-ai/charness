from __future__ import annotations

import importlib.util
from pathlib import Path

from .support import ROOT, run_script


def test_check_skill_contracts_rejects_missing_required_snippet(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    handoff_skill_dir = repo / "skills" / "public" / "handoff"
    handoff_skill_dir.mkdir(parents=True)

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_test_module", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for rel_path in module.REPRESENTATIVE_CONTRACTS:
        if rel_path == "skills/public/handoff/SKILL.md":
            continue
        target = repo / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((ROOT / rel_path).read_text(encoding="utf-8"), encoding="utf-8")

    (handoff_skill_dir / "SKILL.md").write_text(
        "---\nname: handoff\ndescription: \"demo\"\n---\n\n# Handoff\n",
        encoding="utf-8",
    )

    result = run_script("scripts/check_skill_contracts.py", "--repo-root", str(repo))
    assert result.returncode == 1
    assert "missing required core contract snippet" in result.stderr


def test_check_skill_contracts_allows_reference_level_package_contract(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: \"demo\"\n---\n\n# Demo\n\nCore promise.\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "details.md").write_text(
        "# Details\n\nReference-level package promise.\n",
        encoding="utf-8",
    )

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_reference_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    module.validate_package_contract(skill_path, ("Reference-level package promise.",))


def test_check_skill_contracts_uses_declared_active_package_sources(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: \"demo\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "active.md").write_text(
        "# Active\n\nReference-level active promise.\n",
        encoding="utf-8",
    )
    (skill_dir / "scripts" / "active.py").write_text(
        "SCRIPT_PROMISE = 'script-level active promise'\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "orphan.md").write_text(
        "# Orphan\n\nOrphan promise should not satisfy this active-source contract.\n",
        encoding="utf-8",
    )

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_active_sources_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PACKAGE_CONTRACT_SOURCE_PATHS["skills/public/demo/SKILL.md"] = (
        "references/active.md",
        "scripts/active.py",
    )

    module.validate_package_contract(
        skill_path,
        ("Reference-level active promise.", "script-level active promise"),
    )
    try:
        module.validate_package_contract(skill_path, ("Orphan promise should not satisfy",))
    except module.ValidationError as exc:
        assert "missing required package contract snippet" in str(exc)
    else:
        raise AssertionError("expected active-source package contract to ignore orphan references")

    module.PACKAGE_CONTRACT_SOURCE_PATHS["skills/public/demo/SKILL.md"] = ("scripts/missing.py",)
    try:
        module.validate_package_contract(skill_path, ("script-level active promise",))
    except module.ValidationError as exc:
        assert "missing package contract source" in str(exc)
    else:
        raise AssertionError("expected missing active package source to fail")


def test_check_skill_contracts_keeps_core_contract_in_skill_body(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references").mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: \"demo\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "details.md").write_text(
        "# Details\n\nCore-only promise.\n",
        encoding="utf-8",
    )

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_core_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        module.validate_core_contract(skill_path, ("Core-only promise.",))
    except module.ValidationError as exc:
        assert "missing required core contract snippet" in str(exc)
    else:
        raise AssertionError("expected core-only contract to fail when it only appears in references")


def test_check_skill_contracts_forbidden_snippets_fail_in_skill_body(tmp_path: Path) -> None:
    skill_path = tmp_path / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: \"demo\"\n---\n\n# Demo\n\nForbidden promise.\n",
        encoding="utf-8",
    )

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_forbidden_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        module.validate_forbidden_snippets(skill_path, ("Forbidden promise.",))
    except module.ValidationError as exc:
        assert "forbidden contract snippet" in str(exc)
    else:
        raise AssertionError("expected forbidden snippet to fail when it appears in the skill body")


def test_check_skill_contracts_ignores_non_text_reference_artifacts(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    skill_dir = repo / "skills" / "public" / "demo"
    (skill_dir / "references" / "__pycache__").mkdir(parents=True)
    skill_path = skill_dir / "SKILL.md"
    skill_path.write_text(
        "---\nname: demo\ndescription: \"demo\"\n---\n\n# Demo\n",
        encoding="utf-8",
    )
    (skill_dir / "references" / "__pycache__" / "details.pyc").write_bytes(
        b"Reference-level package promise."
    )

    module_path = ROOT / "scripts" / "check_skill_contracts.py"
    spec = importlib.util.spec_from_file_location("check_skill_contracts_non_text_test", module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    try:
        module.validate_package_contract(skill_path, ("Reference-level package promise.",))
    except module.ValidationError as exc:
        assert "missing required package contract snippet" in str(exc)
    else:
        raise AssertionError("expected non-text reference artifact to be ignored")
