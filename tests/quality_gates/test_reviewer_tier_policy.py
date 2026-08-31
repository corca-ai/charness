from __future__ import annotations

import yaml

from scripts.adapter_lib import load_yaml_file
from scripts.critique_adapter_lib import validate_adapter_data

from .support import ROOT, run_script

SHARED_REVIEW = ROOT / "skills" / "shared" / "references" / "fresh-eye-subagent-review.md"
CRITIQUE_DIR = ROOT / "skills" / "public" / "critique"
ADAPTER_EXAMPLE = CRITIQUE_DIR / "adapter.example.yaml"
ADAPTER_CONTRACT = CRITIQUE_DIR / "references" / "adapter-contract.md"
INIT_ADAPTER = CRITIQUE_DIR / "scripts" / "init_adapter.py"
INIT_ADAPTER_TEMPLATE = CRITIQUE_DIR / "scripts" / "templates" / "critique_adapter.yaml"
NAMED_SKILLS = ("critique", "quality", "release", "issue")
DIRECT_HIGH_LEVERAGE_REVIEW_SURFACES = (
    ROOT / "skills" / "public" / "quality" / "SKILL.md",
    ROOT / "skills" / "public" / "issue" / "references" / "causal-review.md",
)
PROVIDER_MODEL_TOKENS = ("gpt-5", "sonnet-4")


def _skill_md(skill: str) -> str:
    return (ROOT / "skills" / "public" / skill / "SKILL.md").read_text(encoding="utf-8")


def test_named_skills_reference_shared_reviewer_policy() -> None:
    for skill in NAMED_SKILLS:
        assert "fresh-eye-subagent-review.md" in _skill_md(skill), (
            f"{skill}/SKILL.md must cite the shared reviewer-tier policy"
        )


def test_portable_surfaces_do_not_hardcode_provider_models() -> None:
    surfaces = [SHARED_REVIEW.read_text(encoding="utf-8")]
    surfaces.extend(_skill_md(skill) for skill in NAMED_SKILLS)
    surfaces.extend(
        path.read_text(encoding="utf-8") for path in DIRECT_HIGH_LEVERAGE_REVIEW_SURFACES
    )
    for text in surfaces:
        for token in PROVIDER_MODEL_TOKENS:
            assert token not in text, (
                f"portable surface must not hardcode provider model `{token}`; "
                "host-specific values belong in the adapter"
            )


def test_direct_fresh_eye_reviewers_apply_high_leverage_tier() -> None:
    for path in DIRECT_HIGH_LEVERAGE_REVIEW_SURFACES:
        text = path.read_text(encoding="utf-8")
        assert "high-leverage" in text, f"{path} must name the reviewer tier"
        assert "reviewer_tiers.high-leverage" in text, (
            f"{path} must tell agents to apply host-exposed reviewer-tier fields"
        )


def test_causal_review_uses_the_shared_file_backed_delivery_contract() -> None:
    text = (ROOT / "skills" / "public" / "issue" / "references" / "causal-review.md").read_text(
        encoding="utf-8"
    )
    for marker in (
        "file-backed worker",
        "typed host subagent",
        "approval_eligible: true",
        "receipt",
        "delivery ledger",
        "same-agent local causal review",
    ):
        assert marker in text, f"causal review contract must pin `{marker}`"


def test_reviewer_tier_policy_is_host_plural() -> None:
    text = SHARED_REVIEW.read_text(encoding="utf-8")
    assert "host-plural" in text
    assert "Codex" in text and "Claude Code" in text, (
        "the reviewer-tier policy must name more than one host, not Codex-only"
    )


def test_shared_reference_keeps_delegated_fast_path() -> None:
    text = SHARED_REVIEW.read_text(encoding="utf-8")
    assert "complete that lens directly" in text
    assert "do not report `blocked` because nested subagent tools are unavailable" in text


def test_critique_adapter_validates_reviewer_tiers_example() -> None:
    raw = load_yaml_file(ADAPTER_EXAMPLE)
    data, errors, _ = validate_adapter_data(raw if isinstance(raw, dict) else {}, ROOT)
    assert errors == []
    tiers = data.get("reviewer_tiers")
    assert tiers and tiers.get("high-leverage", {}).get("model")


def test_live_critique_adapter_pins_codex_high_leverage_default() -> None:
    raw = load_yaml_file(ROOT / ".agents" / "critique-adapter.yaml")
    data, errors, _ = validate_adapter_data(raw if isinstance(raw, dict) else {}, ROOT)
    assert errors == []
    tier = data["reviewer_tiers"]["high-leverage"]
    assert tier == {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "medium",
        "service_tier": "priority",
        "fork_turns": "none",
    }
    assert data["reviewer_tiers"]["medium"] == {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "medium",
        "fork_turns": "none",
    }
    assert data["reviewer_runner"] == {
        "mode": "file-backed-worker",
        "backend": "codex_exec",
        "timeout_seconds": 900,
    }


def test_critique_init_adapter_scaffolds_reviewer_tiers(tmp_path) -> None:
    result = run_script(str(INIT_ADAPTER), "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    raw = load_yaml_file(tmp_path / ".agents" / "critique-adapter.yaml")
    data, errors, _ = validate_adapter_data(raw if isinstance(raw, dict) else {}, tmp_path)
    assert errors == []
    assert data["reviewer_tiers"]["high-leverage"]["model"] == "gpt-5.6-terra"
    assert data["reviewer_tiers"]["high-leverage"]["reasoning_effort"] == "medium"
    assert data["reviewer_tiers"]["high-leverage"]["service_tier"] == "priority"
    assert data["reviewer_tiers"]["high-leverage"]["fork_turns"] == "none"
    assert data["reviewer_tiers"]["medium"] == {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "medium",
        "fork_turns": "none",
    }


def test_critique_init_adapter_scaffold_lives_in_template_asset(tmp_path) -> None:
    result = run_script(str(INIT_ADAPTER), "--repo-root", str(tmp_path))
    assert result.returncode == 0, result.stderr
    assert (tmp_path / ".agents" / "critique-adapter.yaml").read_text(
        encoding="utf-8"
    ) == INIT_ADAPTER_TEMPLATE.read_text(encoding="utf-8")


def test_missing_critique_adapter_does_not_infer_host_specific_tier(tmp_path) -> None:
    result = run_script(
        str(CRITIQUE_DIR / "scripts" / "resolve_adapter.py"),
        "--repo-root",
        str(tmp_path),
    )
    assert result.returncode == 0, result.stderr
    payload = yaml.safe_load(result.stdout)
    assert "reviewer_tiers" not in payload["data"]


def test_adapter_example_keeps_host_plural_guidance() -> None:
    text = ADAPTER_EXAMPLE.read_text(encoding="utf-8")
    assert "Codex" in text and "Claude Code" in text, (
        "the adapter example must name both known hosts so it cannot silently regress to Codex-only"
    )


def test_critique_adapter_rejects_unknown_reviewer_tier_field() -> None:
    _, errors, _ = validate_adapter_data(
        {"reviewer_tiers": {"high-leverage": {"bogus": "x"}}}, ROOT
    )
    assert any("bogus" in error for error in errors)


def test_critique_adapter_warns_on_unknown_reviewer_tier() -> None:
    _, _, warnings = validate_adapter_data({"reviewer_tiers": {"mystery": {"model": "x"}}}, ROOT)
    assert any("mystery" in warning for warning in warnings)


def test_critique_adapter_rejects_unknown_runner_mode_and_backend() -> None:
    _, errors, _ = validate_adapter_data(
        {
            "reviewer_runner": {
                "mode": "mailbox",
                "backend": "ceal",
                "timeout_seconds": 0,
                "unexpected": "field",
            }
        },
        ROOT,
    )
    assert any("unexpected is not a valid runner field" in error for error in errors)
    assert any("reviewer_runner.mode must be one of" in error for error in errors)
    assert any("reviewer_runner.backend must be one of" in error for error in errors)
    assert any("reviewer_runner.timeout_seconds must be" in error for error in errors)


def test_critique_adapter_rejects_non_mapping_reviewer_runner() -> None:
    _, errors, _ = validate_adapter_data({"reviewer_runner": ["worker"]}, ROOT)
    assert errors == ["reviewer_runner must be a mapping"]


def test_adapter_contract_delegates_concrete_host_defaults_to_owned_assets() -> None:
    text = ADAPTER_CONTRACT.read_text(encoding="utf-8")
    for token in PROVIDER_MODEL_TOKENS:
        assert token not in text
    assert "../adapter.example.yaml" in text
    assert "../scripts/templates/critique_adapter.yaml" in text
    assert "does not prove the provider applied" in text
    assert "only when the host confirms it" in text
    assert "Codex `agent_type`" in text
