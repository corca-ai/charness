"""Composed behavior coverage for mixed issue closeout carriers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
import yaml

from tests.quality_gates.issue_closeout_support import (
    bug_closeout_body,
    load_verify_module,
)
from tests.quality_gates.seeding_support import load_module
from tests.quality_gates.support import ROOT, run_script
from tests.quality_gates.test_issue_closeout_commit_msg_hook import _run as run_commit_hook
from tests.quality_gates.test_issue_worker_carrier import (
    _rebind_worker_packet,
    _worker_delivered_artifact,
)
from tests.quality_gates.test_prepush_close_keyword_guard import _finding as prepush_finding

REPO = "corca-ai/charness"
NUMBERS = [42, 43]
TARGETS = [f"{REPO}#42", f"{REPO}#43"]
OBSERVATIONS = [
    {
        "target": f"{REPO}#42",
        "verdict": "pass",
        "summary": "bug behavior was observed through its regression check",
        "evidence": ["bug-regression-observation-42"],
    },
    {
        "target": f"{REPO}#43",
        "verdict": "pass",
        "summary": "feature behavior was observed through its acceptance check",
        "evidence": ["feature-acceptance-observation-43"],
    },
]
MISSING = object()


def _bundle_body() -> str:
    return "\n\n".join(
        [
            bug_closeout_body(
                close_line="Closes #42, #43.",
                critique_line="Critique #42 #43: res-42.md",
                behavior_line=(
                    "Behavior #42: bug regression test observed the corrected carrier path.\n"
                    "Behavior #43: feature acceptance test observed the new bundled path."
                ),
                probe_line=None,
            ),
            "Classification #42: bug",
            "Classification #43: feature",
            "Boundary: the feature remains within the bundled closeout consumer.",
            "Resolution brief: preserve one scoped packet and result for both targets.",
            "Implementation: added exact target and observation validation.",
        ]
    )


def _bundle_artifact(
    repo_root: Path,
    *,
    packet_targets: object = TARGETS,
    result_observations: object = OBSERVATIONS,
) -> Path:
    """Extend the existing single-target worker fixture into one bound bundle."""
    artifact = _worker_delivered_artifact(repo_root)
    packet_path = repo_root / "packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    if packet_targets is MISSING:
        packet.pop("prepared_targets", None)
    else:
        packet["prepared_targets"] = list(packet_targets)  # type: ignore[arg-type]
    packet_path.write_text(json.dumps(packet, separators=(",", ":")), encoding="utf-8")

    result_path = repo_root / "worker-result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    if result_observations is MISSING:
        result.pop("target_observations", None)
    elif result_observations is None:
        result["target_observations"] = None
    else:
        result["target_observations"] = [
            dict(observation) for observation in result_observations  # type: ignore[union-attr]
        ]
    result_path.write_text(json.dumps(result, separators=(",", ":")), encoding="utf-8")
    receipt_path = repo_root / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt["output_size"] = result_path.stat().st_size
    receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")

    # This helper rebinds every packet/result/receipt/ledger/report identity after
    # the semantic mutation, so a passing case proves the actual delivery join.
    _rebind_worker_packet(artifact, f"{REPO}#42 resolution-critique")
    packet_identity = hashlib.sha256(packet_path.read_bytes()).hexdigest()
    result_identity = hashlib.sha256(result_path.read_bytes()).hexdigest()
    ledger_path = repo_root / "ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    for event in ledger["attempts"][0].get("history", []):
        event["packet_identity"] = packet_identity
        if event.get("state") == "findings-received":
            event["findings_identity"] = result_identity
    ledger_path.write_text(json.dumps(ledger, separators=(",", ":")), encoding="utf-8")
    artifact.write_text(
        artifact.read_text(encoding="utf-8").replace(
            "Critique of the #42 resolution.",
            "Critique of the #42 and #43 resolutions.",
        ),
        encoding="utf-8",
    )
    return artifact


def _write_body(repo_root: Path, body: str) -> Path:
    path = repo_root / "bundle-closeout.md"
    path.write_text(body, encoding="utf-8")
    return path


@pytest.mark.boundary_contract(reason="Both public closeout subcommands execute in-process with identical carrier inputs.")
def _public_closeout_results(repo_root: Path, body_file: Path):
    args = (
        "--repo-root", str(repo_root), "--repo", REPO,
        "--number", "42", "--number", "43", "--body-file", str(body_file),
        "--carrier", "pr-body",
    )
    return (
        run_script("skills/public/issue/scripts/issue_tool.py", "verify-closeout", *args),
        run_script("skills/public/issue/scripts/issue_tool.py", "validate-closeout-draft", *args),
    )


def _verify(verifier, repo_root: Path, body_file: Path, **kwargs):
    return verifier.verify_closeout(
        repo_root=repo_root,
        repo=REPO,
        numbers=NUMBERS,
        carrier="pr-body",
        backend={"id": "gh"},
        body_file=body_file,
        **kwargs,
    )


def _assert_two_group_success(result: dict) -> None:
    assert result["ok"] is True
    assert result["classification"] is None
    assert {int(number): value for number, value in result["classifications"].items()} == {42: "bug", 43: "feature"}
    assert set(result["classification_reports"]) == {"bug", "feature"}
    assert result["classification_reports"]["bug"]["numbers"] == [42]
    assert result["classification_reports"]["feature"]["numbers"] == [43]
    assert result["classification_reports"]["bug"]["missing_fields"] == []
    assert result["classification_reports"]["feature"]["missing_fields"] == []
    assert result["classification_reports"]["bug"]["behavioral_verdict"]["missing"] == []
    assert result["classification_reports"]["feature"]["behavioral_verdict"]["missing"] == []
    checks = result["resolution_critique_check"]["checks"]
    assert len(checks) == 1
    assert checks[0]["target"] == "#42 #43"
    assert checks[0]["numbers"] == [42, 43]
    assert checks[0]["fresh_eye_observer"]["carrier_verified"] is True


def test_mixed_bundle_does_not_gain_singleton_behavior_shorthand(tmp_path: Path) -> None:
    _bundle_artifact(tmp_path)
    body = "\n".join(
        line for line in _bundle_body().splitlines() if not line.startswith("Behavior #")
    ) + "\nBehavior: only the bug regression was observed.\n"
    result = _verify(load_verify_module(), tmp_path, _write_body(tmp_path, body))
    assert result["ok"] is False
    for group, number in (("bug", 42), ("feature", 43)):
        assert result["classification_reports"][group]["behavioral_verdict"]["missing"] == [number]
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")
    assert run_commit_hook(tmp_path, message).returncode != 0
    assert prepush_finding(tmp_path, body, {})["ok"] is False


def test_mixed_hotl_keeps_full_invocation_shorthand_rules(tmp_path: Path) -> None:
    _bundle_artifact(tmp_path)
    verifier = load_verify_module()
    body = _bundle_body() + "\nHOTL: untyped singleton-only entry\n"
    result = _verify(verifier, tmp_path, _write_body(tmp_path, body))
    assert result["ok"] is True
    assert all(not group["hotl_dispositions"]["applies"] for group in result["classification_reports"].values())
    body = body.replace("HOTL:", "HOTL #42:")
    result = _verify(verifier, tmp_path, _write_body(tmp_path, body))
    assert result["ok"] is False
    assert result["classification_reports"]["bug"]["hotl_dispositions"]["ok"] is False
    assert result["classification_reports"]["feature"]["hotl_dispositions"]["applies"] is False


@pytest.mark.parametrize("target", ["foreign/repo#42 foreign/repo#43", "garbage#42 #43"])
@pytest.mark.boundary_contract(reason="Exercise the public closeout CLI refusal contract through the in-process script runner.")
def test_bundle_refuses_foreign_or_malformed_citation(tmp_path: Path, target: str) -> None:
    _bundle_artifact(tmp_path)
    body = _bundle_body().replace("Critique #42 #43:", f"Critique {target}:")
    body_file = _write_body(tmp_path, body)
    assert _verify(load_verify_module(), tmp_path, body_file)["ok"] is False
    for result in _public_closeout_results(tmp_path, body_file):
        assert result.returncode != 0
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")
    assert run_commit_hook(tmp_path, message).returncode != 0
    assert prepush_finding(tmp_path, body, {})["ok"] is False


@pytest.mark.boundary_contract(reason="Observe one delivered bundle through both public CLI commands and hook consumers; CLI execution is in-process.")
def test_one_delivered_mixed_bundle_reaches_every_closeout_consumer(tmp_path: Path) -> None:
    artifact = _bundle_artifact(tmp_path)
    body = _bundle_body()
    body_file = _write_body(tmp_path, body)
    verifier = load_verify_module()

    standalone = _verify(verifier, tmp_path, body_file)
    _assert_two_group_success(standalone)

    draft_module = load_module(
        "issue_validate_closeout_draft_bundled_test",
        ROOT / "skills/public/issue/scripts/issue_validate_closeout_draft.py",
    )
    draft = draft_module.validate_closeout_draft(
        verifier=verifier,
        repo_root=tmp_path,
        repo=REPO,
        numbers=NUMBERS,
        classification=None,
        body_file=body_file,
        backend={"id": "gh"},
        carrier="pr-body",
    )
    _assert_two_group_success(draft)
    assert draft["status"] == "draft_verified"

    for cli in _public_closeout_results(tmp_path, body_file):
        assert cli.returncode == 0, cli.stderr
        _assert_two_group_success(yaml.safe_load(cli.stdout))

    issue_artifact = tmp_path / "charness-artifacts/issue/bundle-closeout.md"
    issue_artifact.parent.mkdir(parents=True)
    issue_artifact.write_text(body, encoding="utf-8")
    message = tmp_path / "message.txt"
    message.write_text(body, encoding="utf-8")

    commit_result = run_commit_hook(tmp_path, message)
    assert commit_result.returncode == 0, commit_result.stderr
    commit_payload = commit_result.payload
    assert commit_payload["status"] == "verified"
    commit_report = commit_payload["reports"][0]
    assert commit_report["numbers"] == NUMBERS
    assert commit_report["classifications"] == {42: "bug", 43: "feature"}
    assert commit_report["missing_fields"] == []

    prepush = prepush_finding(
        tmp_path,
        body,
        {"charness-artifacts/issue/bundle-closeout.md": body},
    )
    assert prepush is not None
    assert prepush["ok"] is True
    prepush_report = prepush["reports"][0]
    assert prepush_report["numbers"] == NUMBERS
    assert prepush_report["classifications"] == {42: "bug", 43: "feature"}
    assert prepush_report["missing_fields"] == []
    assert artifact.is_file()

    # A previously paused brief becomes a close carrier when the commit closes
    # its targets; the pause-only provenance exemption must not swallow floors.
    paused_body = body + "\n\nAutonomous vs pause: paused\n"
    issue_artifact.write_text(paused_body, encoding="utf-8")
    resumed = run_commit_hook(tmp_path, message)
    assert resumed.returncode == 0, resumed.stderr
    assert resumed.payload["reports"][0]["classifications"] == {42: "bug", 43: "feature"}


@pytest.mark.parametrize("packet_targets", [MISSING, TARGETS])
def test_nullable_observations_mean_absent_only_for_a_legacy_packet(
    tmp_path: Path, packet_targets: object,
) -> None:
    _bundle_artifact(tmp_path, packet_targets=packet_targets, result_observations=None)
    body_file = _write_body(tmp_path, _bundle_body())
    verifier = load_verify_module()
    result = _verify(verifier, tmp_path, body_file)
    assert result["ok"] is False  # neither legacy nor unobserved packets cover a bundle
    if packet_targets is MISSING:
        from tests.quality_gates.test_issue_worker_carrier import _load_resolution_critique

        check = {"satisfied": [{"name": "resolution_critique", "via": "evidence", "path": str(tmp_path / "res-42.md")}]}
        observed = _load_resolution_critique()._observer_disposition(
            tmp_path, check, expected_issue_numbers=[42], expected_repository=REPO,
        )
        assert observed["carrier_verified"] is True


@pytest.mark.parametrize(
    "mutation",
    [
        "packet-omitted",
        "packet-extra",
        "packet-duplicate",
        "packet-foreign",
        "result-omitted",
        "result-extra",
        "result-duplicate",
        "result-foreign",
    ],
)
def test_structured_worker_membership_refuses_each_exact_set_mutation(
    tmp_path: Path, mutation: str
) -> None:
    packet_targets = TARGETS
    result_observations = OBSERVATIONS
    if mutation == "packet-omitted":
        packet_targets = MISSING  # type: ignore[assignment]
    elif mutation == "packet-extra":
        packet_targets = [*TARGETS, f"{REPO}#44"]
    elif mutation == "packet-duplicate":
        packet_targets = [TARGETS[0], TARGETS[0], TARGETS[1]]
    elif mutation == "packet-foreign":
        packet_targets = [TARGETS[0], "other-org/other-repo#43"]
    elif mutation == "result-omitted":
        result_observations = MISSING  # type: ignore[assignment]
    elif mutation == "result-extra":
        result_observations = [
            *OBSERVATIONS,
            {
                "target": f"{REPO}#44",
                "verdict": "pass",
                "summary": "uninvoked observation",
                "evidence": ["foreign-observation"],
            },
        ]
    elif mutation == "result-duplicate":
        result_observations = [OBSERVATIONS[0], dict(OBSERVATIONS[0])]
    elif mutation == "result-foreign":
        result_observations = [OBSERVATIONS[0], {**OBSERVATIONS[1], "target": "other-org/other-repo#43"}]
    else:  # pragma: no cover - the parameter list is the test's input contract
        raise AssertionError(mutation)

    _bundle_artifact(
        tmp_path,
        packet_targets=packet_targets,
        result_observations=result_observations,
    )
    result = _verify(load_verify_module(), tmp_path, _write_body(tmp_path, _bundle_body()))

    assert result["ok"] is False
    check = result["resolution_critique_check"]
    assert check["ok"] is False
    observer = check["checks"][0]["fresh_eye_observer"]
    assert observer["carrier_verified"] is False
    assert observer["carrier_reason"]


def test_nonpassing_target_observation_cannot_be_consumed_as_worker_approval(
    tmp_path: Path,
) -> None:
    observations = [dict(observation) for observation in OBSERVATIONS]
    observations[1]["verdict"] = "block"
    _bundle_artifact(tmp_path, result_observations=observations)

    result = _verify(load_verify_module(), tmp_path, _write_body(tmp_path, _bundle_body()))

    assert result["ok"] is False
    observer = result["resolution_critique_check"]["checks"][0]["fresh_eye_observer"]
    assert observer["carrier_verified"] is False
    assert "passing verdict" in observer["carrier_reason"]


@pytest.mark.parametrize("mutation", ["partial", "global-mixed", "duplicate-target"])
def test_targeted_classification_authority_must_be_complete_and_unambiguous(
    tmp_path: Path, mutation: str
) -> None:
    body = _bundle_body()
    if mutation == "partial":
        body = body.replace("Classification #43: feature\n\n", "")
    elif mutation == "global-mixed":
        body += "\n\nClassification: feature\n"
    elif mutation == "duplicate-target":
        body += "\n\nClassification #42: feature\n"
    else:  # pragma: no cover
        raise AssertionError(mutation)

    with pytest.raises(RuntimeError, match="classification"):
        _verify(load_verify_module(), tmp_path, _write_body(tmp_path, body))


def test_supplied_partial_classification_map_refuses_before_floor_evaluation(tmp_path: Path) -> None:
    with pytest.raises(RuntimeError, match="complete issue"):
        _verify(
            load_verify_module(),
            tmp_path,
            _write_body(tmp_path, _bundle_body()),
            classifications={42: "bug"},
        )


def test_targeted_classifications_cannot_accept_an_explicit_scalar_conflict(
    tmp_path: Path,
) -> None:
    with pytest.raises(RuntimeError, match="mixed with scalar"):
        _verify(
            load_verify_module(),
            tmp_path,
            _write_body(tmp_path, _bundle_body()),
            classification="bug",
        )


@pytest.mark.parametrize("classification,field,number", [("feature", "boundary", 43), ("bug", "root cause", 42)])
@pytest.mark.boundary_contract(reason="The public CLI must refuse each missing group floor; exercise its exit contract in-process alongside hooks.")
def test_each_group_keeps_its_own_ledger_floor(
    tmp_path: Path, classification: str, field: str, number: int,
) -> None:
    _bundle_artifact(tmp_path)
    body = "\n".join(line for line in _bundle_body().splitlines() if not line.lower().startswith(field + ":"))
    body_file = _write_body(tmp_path, body)
    result = _verify(load_verify_module(), tmp_path, body_file)

    assert result["ok"] is False
    other = "bug" if classification == "feature" else "feature"
    assert result["classification_reports"][other]["missing_fields"] == []
    missing = field.replace(" ", "_")
    assert result["classification_reports"][classification]["missing_fields"] == [missing]
    assert f"#{number}:{missing}" in result["missing_fields"]
    for cli in _public_closeout_results(tmp_path, body_file):
        assert cli.returncode != 0, cli.stdout
        assert yaml.safe_load(cli.stdout)["ok"] is False
    artifact = tmp_path / "charness-artifacts/issue/bundle-closeout.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(body)
    assert run_commit_hook(tmp_path, body_file).returncode != 0
    prepush = prepush_finding(tmp_path, body, {str(artifact.relative_to(tmp_path)): body})
    assert prepush is not None and prepush["ok"] is False
    artifact.write_text(body + "\n\nAutonomous vs pause: paused\n")
    assert run_commit_hook(tmp_path, body_file).returncode != 0


@pytest.mark.parametrize("consumer", ["commit-msg", "pre-push"])
@pytest.mark.parametrize("extra", ["Classification #42: feature", "Classification: feature"])
def test_artifact_classification_conflicts_cannot_be_erased_by_hook_projection(
    tmp_path: Path, consumer: str, extra: str,
) -> None:
    _bundle_artifact(tmp_path)
    body = _bundle_body() + "\n\n" + extra + "\n"
    artifact = tmp_path / "charness-artifacts/issue/bundle-closeout.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text(body)
    message = tmp_path / "message.txt"
    message.write_text(body)
    try:
        if consumer == "commit-msg":
            result = run_commit_hook(tmp_path, message)
            assert result.returncode != 0, result.stdout
        else:
            result = prepush_finding(tmp_path, body, {str(artifact.relative_to(tmp_path)): body})
            assert result is not None and result["ok"] is False, result
    except RuntimeError as exc:
        assert "classification" in str(exc).lower()
