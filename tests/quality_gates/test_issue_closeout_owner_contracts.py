"""Direct consumer contracts for closeout grammar, carrier input, and worker targets."""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.quality_gates.support import ROOT
from tests.script_loader import load_script_module


@pytest.fixture
def worker():
    return load_script_module(
        "issue_worker_targets_owner_contract",
        ROOT / "skills/public/issue/scripts/issue_worker_targets.py",
    )


@pytest.fixture
def carrier():
    return load_script_module(
        "issue_verify_closeout_carrier_owner_contract",
        ROOT / "skills/public/issue/scripts/issue_verify_closeout_carrier.py",
    )


@pytest.fixture
def issue_tool(monkeypatch: pytest.MonkeyPatch):
    tool = load_script_module(
        "issue_tool_owner_contract", ROOT / "skills/public/issue/scripts/issue_tool.py",
    )
    grammar = load_script_module(
        "issue_tool_parser_owner_contract",
        ROOT / "skills/public/issue/scripts/issue_tool_parser.py",
    )
    # Exercise the directly named owner through the real command-family wiring;
    # no command registrar, verifier constants, or handler is replaced with a fake.
    monkeypatch.setattr(tool, "PARSER", grammar)
    return tool


@pytest.mark.parametrize("command", ["verify-closeout", "validate-closeout-draft"])
@pytest.mark.parametrize("classification", [None, "bug"])
def test_real_parser_accepts_issue_owned_mixed_or_explicit_scalar_classification(
    issue_tool, command: str, classification: str | None,
) -> None:
    argv = [
        command, "--repo", "corca-ai/charness", "--number", "42", "--number", "43",
        "--carrier", "pr-body", "--body-file", "bundle.md",
    ]
    if classification is not None:
        argv += ["--classification", classification]
    args = issue_tool.build_parser().parse_args(argv)

    assert args.classification == classification
    assert args.number == [42, 43]
    assert args.body_file == Path("bundle.md")
    assert args.carrier == "pr-body"
    assert callable(args.func)
    if command == "verify-closeout":
        assert args.func is issue_tool.command_verify_closeout


@pytest.mark.parametrize("command", ["verify-closeout", "validate-closeout-draft"])
def test_real_parser_rejects_unknown_classification(issue_tool, command: str) -> None:
    with pytest.raises(SystemExit) as error:
        issue_tool.build_parser().parse_args([
            command, "--repo", "corca-ai/charness", "--number", "42",
            "--carrier", "pr-body", "--body-file", "bundle.md", "--classification", "unknown",
        ])
    assert error.value.code == 2


def test_manual_close_keeps_required_scalar_classification(issue_tool) -> None:
    argv = [
        "close-with-comment", "--repo", "corca-ai/charness",
        "--number", "42", "--body-file", "body.md",
    ]
    with pytest.raises(SystemExit) as error:
        issue_tool.build_parser().parse_args(argv)
    assert error.value.code == 2
    args = issue_tool.build_parser().parse_args(argv + ["--classification", "question"])
    assert args.classification == "question"
    assert args.func is issue_tool.command_close_with_comment


def _carrier_inputs(**overrides) -> dict:
    return {
        "numbers": [42, 43], "classification": None, "carrier": "pr-body",
        "manual_fallback_reason": None, "expect_state": None, **overrides,
    }


def test_body_only_carrier_audit_needs_neither_scalar_classification_nor_remote_state(carrier) -> None:
    assert carrier.validate_verify_inputs(**_carrier_inputs()) is None


@pytest.mark.parametrize(
    "overrides,reason",
    [
        ({"numbers": []}, "at least one --number"),
        ({"classification": "unknown"}, "unknown classification"),
        ({"carrier": "unknown"}, "unknown carrier"),
        ({"carrier": "manual-fallback"}, "requires --manual-fallback-reason"),
        ({"carrier": "manual-fallback", "manual_fallback_reason": "unknown"}, "requires --manual"),
        ({"manual_fallback_reason": "operator-directed-manual-close"}, "only valid"),
        ({"expect_state": "OPEN"}, "requires --expect-state CLOSED"),
    ],
)
def test_carrier_input_refusals_precede_body_or_backend_read(carrier, overrides: dict, reason: str) -> None:
    with pytest.raises(RuntimeError, match=reason):
        carrier.validate_verify_inputs(**_carrier_inputs(**overrides))


@pytest.mark.parametrize("classification", [None, "bug", "feature", "question", "consolidated"])
@pytest.mark.parametrize("channel", ["pr-body", "direct-commit", "manual-fallback"])
def test_valid_carrier_inputs_preserve_optional_bundle_classification(
    carrier, classification: str | None, channel: str,
) -> None:
    reason = "operator-directed-manual-close" if channel == "manual-fallback" else None
    assert carrier.validate_verify_inputs(**_carrier_inputs(
        classification=classification, carrier=channel,
        manual_fallback_reason=reason, expect_state="closed",
    )) is None


def _observation(target: str = "corca-ai/charness#42", **overrides) -> dict:
    return {
        "target": target, "verdict": "pass", "summary": "Observed the issue behavior.",
        "evidence": ["behavior observation for this target"], **overrides,
    }


def _membership(worker, **overrides) -> None:
    worker.validate_worker_target_membership(**{
        "packet": {"prepared_targets": ["corca-ai/charness#42"]},
        "result": {"target_observations": [_observation()]},
        "expected_issue_numbers": [42], "expected_repository": "corca-ai/charness",
        **overrides,
    })


@pytest.mark.parametrize(
    "overrides,reason",
    [
        ({"packet": None}, "packet and result payloads"),
        ({"packet": []}, "packet and result payloads"),
        ({"result": None}, "packet and result payloads"),
        ({"result": []}, "packet and result payloads"),
        ({"expected_issue_numbers": None}, "requires repository and issue numbers"),
        ({"expected_issue_numbers": []}, "requires repository and issue numbers"),
        ({"expected_repository": None}, "requires repository and issue numbers"),
        ({"expected_repository": " "}, "requires repository and issue numbers"),
        ({"packet": {}}, "must appear together"),
        ({"result": {}}, "must appear together"),
        ({"result": {"target_observations": None}}, "must appear together"),
    ],
)
def test_worker_membership_requires_payloads_identity_and_paired_structure(
    worker, overrides: dict, reason: str,
) -> None:
    with pytest.raises(worker.WorkerTargetError, match=reason):
        _membership(worker, **overrides)


@pytest.mark.parametrize(
    "targets,reason",
    [
        (None, "nonempty array"), ([], "nonempty array"), ("corca-ai/charness#42", "nonempty array"),
        ([42], "targets must be strings"),
        (["corca-ai/charness#42", "corca-ai/charness#42"], "duplicate targets"),
        (["#42"], "qualified owner/repo#N"),
        (["corca-ai/charness#42", "corca-ai/charness#43"], "cardinality"),
        (["foreign/repo#42"], "exactly match"),
    ],
)
def test_prepared_targets_require_an_exact_qualified_nonempty_set(worker, targets, reason: str) -> None:
    with pytest.raises(worker.WorkerTargetError, match=reason):
        _membership(worker, packet={"prepared_targets": targets})


@pytest.mark.parametrize(
    "observations,reason",
    [
        ([], "nonempty array"), ({}, "nonempty array"), (["observation"], "entries must be objects"),
        ([_observation(verdict=None)], "passing verdict"),
        ([_observation(verdict="block")], "passing verdict"),
        ([_observation(summary=None)], "nonempty summary"),
        ([_observation(summary=42)], "nonempty summary"),
        ([_observation(summary=" ")], "nonempty summary"),
        ([_observation(evidence=None)], "nonempty evidence array"),
        ([_observation(evidence=[])], "nonempty evidence array"),
        ([_observation(evidence="receipt")], "nonempty evidence array"),
        ([_observation(evidence=[None])], "nonempty evidence array"),
        ([_observation(evidence=[" "])], "nonempty evidence array"),
        ([_observation(target=None)], "targets must be strings"),
        ([_observation(target=42)], "targets must be strings"),
        ([_observation(target="#42")], "qualified owner/repo#N"),
        ([_observation(target="foreign/repo#42")], "exactly match"),
        ([_observation(), _observation()], "duplicate targets"),
        ([_observation(), _observation("corca-ai/charness#43")], "cardinality"),
    ],
)
def test_observations_require_passing_substantive_exact_target_evidence(
    worker, observations, reason: str,
) -> None:
    with pytest.raises(worker.WorkerTargetError, match=reason):
        _membership(worker, result={"target_observations": observations})


@pytest.mark.parametrize(
    "field,reason",
    [
        ("target", "targets must be strings"), ("verdict", "passing verdict"),
        ("summary", "nonempty summary"), ("evidence", "nonempty evidence array"),
    ],
)
def test_observation_field_omission_is_not_an_implicit_approval(worker, field: str, reason: str) -> None:
    observation = _observation()
    observation.pop(field)
    with pytest.raises(worker.WorkerTargetError, match=reason):
        _membership(worker, result={"target_observations": [observation]})


@pytest.mark.parametrize("result", [{}, {"target_observations": None}])
@pytest.mark.parametrize("repository", ["corca-ai/charness", "charness"])
def test_legacy_singleton_accepts_null_or_omitted_observations(worker, result: dict, repository: str) -> None:
    assert _membership(
        worker,
        packet={"prepared_for": "CORCA-AI/CHARNESS#42 resolution-critique", "repo": repository},
        result=result,
    ) is None


@pytest.mark.parametrize(
    "packet,numbers,reason",
    [
        ({"prepared_for": "corca-ai/charness#42", "repo": "charness"}, [42, 43], "only one issue"),
        ({"repo": "charness"}, [42], "prepared_for does not bind exactly"),
        ({"prepared_for": "corca-ai/charness#420", "repo": "charness"}, [42], "prepared_for does not bind exactly"),
        ({"prepared_for": "corca-ai/charness#42x", "repo": "charness"}, [42], "prepared_for does not bind exactly"),
        ({"prepared_for": "foreign/repo#42", "repo": "charness"}, [42], "prepared_for does not bind exactly"),
        ({"prepared_for": "corca-ai/charness#42"}, [42], "repo does not bind exactly"),
        ({"prepared_for": "corca-ai/charness#42", "repo": "foreign"}, [42], "repo does not bind exactly"),
    ],
)
def test_legacy_identity_never_broadens_to_a_bundle_or_prefix_collision(
    worker, packet: dict, numbers: list[int], reason: str,
) -> None:
    with pytest.raises(worker.WorkerTargetError, match=reason):
        _membership(worker, packet=packet, result={}, expected_issue_numbers=numbers)


def test_worker_target_normalization_preserves_exact_membership(worker) -> None:
    with pytest.raises(worker.WorkerTargetError, match="must be a string"):
        worker._normalize_worker_target(42)
    assert worker._normalize_worker_target(" CORCA-AI/CHARNESS#042 ") == "corca-ai/charness#42"
    assert _membership(
        worker, expected_issue_numbers=[42, 43], expected_repository=" CORCA-AI/CHARNESS ",
        packet={"prepared_targets": ["CORCA-AI/CHARNESS#042", "corca-ai/charness#43"]},
        result={"target_observations": [_observation("corca-ai/charness#43"), _observation()]},
    ) is None
