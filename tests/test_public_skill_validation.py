from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import suggest_public_skill_validation as _suggest_public_skill_validation
from scripts import validate_public_skill_validation as _validate_public_skill_validation
from scripts.public_skill_validation_lib import ValidationError, load_policy, validate_policy
from scripts.suggest_public_skill_validation import _format_human, build_report
from scripts.validate_public_skill_validation import validate_adapter_requirement

ROOT = Path(__file__).resolve().parents[1]


def run_module_main(module, monkeypatch, capsys, *args: str) -> SimpleNamespace:
    monkeypatch.setattr(sys, "argv", [f"{module.__name__.rsplit('.', 1)[-1]}.py", *args])
    try:
        returncode = module.main()
    except _validate_public_skill_validation.ValidationError as exc:
        print(
            f"{exc}\nRun `python3 scripts/suggest_public_skill_validation.py --repo-root .` for bucket choices.",
            file=sys.stderr,
        )
        returncode = 1
    except SystemExit as exc:
        returncode = exc.code if isinstance(exc.code, int) else 1
    captured = capsys.readouterr()
    return SimpleNamespace(returncode=returncode, stdout=captured.out, stderr=captured.err)


def with_fallback_policy(policy: dict[str, object]) -> dict[str, object]:
    updated = json.loads(json.dumps(policy))
    updated.setdefault(
        "fallback_policy",
        {
            "allow": [],
            "visible": [],
            "block": [],
        },
    )
    return updated


def seed_repo(tmp_path: Path, *, policy: dict[str, object]) -> Path:
    repo = tmp_path / "repo"
    docs_dir = repo / "docs"
    public_root = repo / "skills" / "public"
    docs_dir.mkdir(parents=True)
    public_root.mkdir(parents=True)
    (docs_dir / "public-skill-validation.json").write_text(
        json.dumps(with_fallback_policy(policy), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return repo


def seed_skill(repo: Path, skill_id: str, *, adapter: bool) -> None:
    skill_dir = repo / "skills" / "public" / skill_id
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "\n".join(
            [
                "---",
                f"name: {skill_id}",
                'description: "Demo skill."',
                "---",
                "",
                "# Demo",
                "",
                "## References",
                "",
                "- `references/demo.md`",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    references_dir = skill_dir / "references"
    references_dir.mkdir()
    (references_dir / "demo.md").write_text("# Demo\n", encoding="utf-8")
    if adapter:
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "adapter.example.yaml", skill_dir / "adapter.example.yaml")
        scripts_dir = skill_dir / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "resolve_adapter.py", scripts_dir / "resolve_adapter.py")
        shutil.copy2(ROOT / "skills" / "public" / "handoff" / "scripts" / "init_adapter.py", scripts_dir / "init_adapter.py")


def assert_validation_error(repo: Path, *fragments: str) -> None:
    with pytest.raises(ValidationError) as excinfo:
        validate_policy(load_policy(repo), repo)
    message = str(excinfo.value)
    for fragment in fragments:
        assert fragment in message


def test_validate_public_skill_validation_requires_full_partition(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    assert_validation_error(
        repo,
        "does not classify every public skill",
        "`demo-b`",
        "`tiers.smoke-only`",
        "`tiers.hitl-recommended`",
        "`tiers.evaluator-required`",
    )


def test_validate_public_skill_validation_reports_missing_adapter_requirement_bucket(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a", "demo-b"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a", "demo-b"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    assert_validation_error(
        repo,
        "adapter_requirements does not classify every public skill",
        "`demo-b`",
        "`adapter_requirements.required`",
        "`adapter_requirements.adapter-free`",
    )


def test_validate_public_skill_validation_requires_adapter_contract_for_required_skill(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=False)

    policy = validate_policy(load_policy(repo), repo)
    with pytest.raises(ValidationError, match="adapter-required skill is missing `adapter.example.yaml`"):
        for skill_id in policy["adapter_requirements"]["required"]:
            validate_adapter_requirement(repo, skill_id, required=True)


def test_validate_public_skill_validation_rejects_adapter_helpers_for_adapter_free_skill(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": [],
                "adapter-free": ["demo-a"],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)

    policy = validate_policy(load_policy(repo), repo)
    with pytest.raises(ValidationError, match="adapter-free skill should not ship `adapter.example.yaml`"):
        for skill_id in policy["adapter_requirements"]["adapter-free"]:
            validate_adapter_requirement(repo, skill_id, required=False)


def test_validate_public_skill_validation_ignores_orphan_skill_dir_without_skill_md(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    orphan = repo / "skills" / "public" / "demo-removed" / "scripts" / "__pycache__"
    orphan.mkdir(parents=True)
    (orphan / "stale.cpython-310.pyc").write_bytes(b"\x00")

    policy = validate_policy(load_policy(repo), repo)
    for skill_id in policy["adapter_requirements"]["required"]:
        validate_adapter_requirement(repo, skill_id, required=True)


def test_suggest_public_skill_validation_reports_missing_bucket_choices(tmp_path: Path) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    payload = build_report(repo)
    assert payload["missing_tiers"] == ["demo-b"]
    assert payload["missing_adapter_requirements"] == ["demo-b"]
    assert payload["missing_fallback_policy"] == ["demo-b"]
    assert payload["suggestions"] == [
        {
            "skill_id": "demo-b",
            "missing_fields": {
                "tiers": True,
                "adapter_requirements": True,
                "fallback_policy": True,
            },
            "choose_one_of": {
                "tiers": [
                    "tiers.smoke-only",
                    "tiers.hitl-recommended",
                    "tiers.evaluator-required",
                ],
                "adapter_requirements": [
                    "adapter_requirements.required",
                    "adapter_requirements.adapter-free",
                ],
                "fallback_policy": [
                    "fallback_policy.allow",
                    "fallback_policy.visible",
                    "fallback_policy.block",
                ],
            },
        }
    ]

    human = _format_human(payload)
    assert "`demo-b`" in human
    assert "`tiers.hitl-recommended`" in human
    assert "`adapter_requirements.adapter-free`" in human
    assert "`fallback_policy.visible`" in human


def test_validate_public_skill_validation_cli_reports_guidance(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    result = run_module_main(_validate_public_skill_validation, monkeypatch, capsys, "--repo-root", str(repo))
    assert result.returncode == 1
    assert "does not classify every public skill" in result.stderr
    assert "suggest_public_skill_validation.py" in result.stderr


def test_suggest_public_skill_validation_cli_emits_json(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = seed_repo(
        tmp_path,
        policy={
            "schema_version": 1,
            "tiers": {
                "smoke-only": [],
                "hitl-recommended": ["demo-a"],
                "evaluator-required": [],
            },
            "adapter_requirements": {
                "required": ["demo-a"],
                "adapter-free": [],
            },
            "fallback_policy": {
                "allow": ["demo-a"],
                "visible": [],
                "block": [],
            },
        },
    )
    seed_skill(repo, "demo-a", adapter=True)
    seed_skill(repo, "demo-b", adapter=False)

    result = run_module_main(_suggest_public_skill_validation, monkeypatch, capsys, "--repo-root", str(repo), "--json")
    assert result.returncode == 1
    assert json.loads(result.stdout)["suggestions"][0]["skill_id"] == "demo-b"
