from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

from scripts.review.reviewed_input_identity import build_reviewed_input_identity
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_main import load_script_module, run_loaded_script_main
from tests.test_review_followup import _prior_review

ROOT = Path(__file__).resolve().parents[1]
FOLLOWUP = load_script_module(
    "review_followup_failures_main",
    ROOT / "skills/public/critique/scripts/review_followup.py",
)
SELECTION = FOLLOWUP.SELECTION
CONTEXT = FOLLOWUP.CONTEXT
PROVENANCE = FOLLOWUP.PROVENANCE
PREPARE = load_script_module(
    "review_followup_failures_prepare",
    ROOT / "skills/public/critique/scripts/prepare_packet.py",
)


class SelectionError(ValueError):
    def __init__(self, code: str, message: str, *, details: dict | None = None) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def _selection_error(code: str, message: str, *, details: dict | None = None) -> Exception:
    return SelectionError(code, message, details=details)


def _identity(paths: list[str], *, mode: str = "working-tree") -> dict[str, object]:
    return {
        "status": "captured",
        "reviewed_paths": paths,
        "reviewed_content": [
            {"path": path, "content_sha256": f"old-{path}"} for path in paths
        ],
        "substrate_mode": mode,
        "mode": mode,
        "changed_ref": "HEAD" if mode == "committed-ref" else None,
        "identity_sha256": "prior-identity",
    }


def test_followup_path_and_source_inputs_fail_closed(tmp_path: Path) -> None:
    with pytest.raises(FOLLOWUP.FollowupError, match="repository-relative"):
        FOLLOWUP._relative_safe(tmp_path, "../outside.json", label="source")
    with pytest.raises(FOLLOWUP.FollowupError, match="must not be a symlink"):
        link = tmp_path / "link.json"
        link.symlink_to(tmp_path / "target.json")
        FOLLOWUP._relative_safe(tmp_path, "link.json", label="source")
    outside = tmp_path.parent / "outside"
    outside.mkdir()
    (tmp_path / "escape").symlink_to(outside, target_is_directory=True)
    with pytest.raises(FOLLOWUP.FollowupError, match="resolves outside"):
        FOLLOWUP._relative_safe(tmp_path, "escape/missing.json", label="source")

    bad = tmp_path / "bad.json"
    bad.write_text("not json", encoding="utf-8")
    with pytest.raises(FOLLOWUP.FollowupError, match="not readable"):
        FOLLOWUP._load_mapping(bad)
    bad.write_text("[1, 2]", encoding="utf-8")
    with pytest.raises(FOLLOWUP.FollowupError, match="must contain a mapping"):
        FOLLOWUP._load_mapping(bad)
    single = tmp_path / "single.json"
    single.write_text("{}", encoding="utf-8")
    assert FOLLOWUP._source_path(tmp_path, "single.json") == single

    carrier_dir = tmp_path / "attempt"
    carrier_dir.mkdir()
    (carrier_dir / "result.json").write_text("{}", encoding="utf-8")
    assert FOLLOWUP._source_path(tmp_path, "attempt").name == "result.json"
    (carrier_dir / "partial-result.json").write_text("{}", encoding="utf-8")
    assert FOLLOWUP._source_path(tmp_path, "attempt").name == "partial-result.json"
    (carrier_dir / "partial-result.json").unlink()
    (carrier_dir / "result.json").unlink()
    (carrier_dir / "worker-report.yaml").write_text("{}", encoding="utf-8")
    assert FOLLOWUP._source_path(tmp_path, "attempt").name == "worker-report.yaml"
    (carrier_dir / "worker-report.yaml").unlink()
    with pytest.raises(FOLLOWUP.FollowupError, match="no reusable review carrier"):
        FOLLOWUP._source_path(tmp_path, "attempt")
    with pytest.raises(FOLLOWUP.FollowupError, match="does not exist"):
        FOLLOWUP._source_path(tmp_path, "missing.json")


def test_followup_context_helpers_preserve_only_bounded_prior_evidence() -> None:
    assert CONTEXT.clip({"value": "x"}, 100) == '{"value": "x"}'
    assert CONTEXT.clip("x" * 30, 20).endswith("…[truncated]")
    findings, omitted, truncated = CONTEXT.compact_findings(
        [None, {"summary": "short"}, *({"id": f"F-{i}"} for i in range(70))]
    )
    assert len(findings) == CONTEXT.MAX_FINDINGS
    assert findings[0]["id"] == "finding-2"
    assert omitted == [f"F-{i}" for i in range(63, 70)]
    assert truncated is False
    assert CONTEXT.compact_findings("not a list") == ([], [], False)
    assert CONTEXT._collapse_path_arrays([{"nested": [1, 2]}]) == [{"nested": [1, 2]}]
    small = {"selection": "changed-prior-inputs"}
    assert CONTEXT.bound_context(small, _selection_error) is small

    first_stage = {
        "prior_findings": [{"id": "F-1", "summary": "x" * 30000, "action": "y" * 30000}],
    }
    assert len(CONTEXT.context_bytes(CONTEXT.bound_context(first_stage, _selection_error))) <= CONTEXT.MAX_CONTEXT_BYTES

    path_heavy = {"selected_paths": [f"src/{i:05d}-long-name.py" for i in range(10000)]}
    bounded = CONTEXT.bound_context(path_heavy, _selection_error)
    assert bounded["selected_paths"]["summarized"] is True
    assert len(CONTEXT.context_bytes(bounded)) <= CONTEXT.MAX_CONTEXT_BYTES

    id_heavy = {
        "prior_findings": [{"id": "x" * 1000, "summary": "summary"} for _ in range(64)]
    }
    bounded = CONTEXT.bound_context(id_heavy, _selection_error)
    assert bounded["prior_findings_omitted"] > 0
    assert len(CONTEXT.context_bytes(bounded)) <= CONTEXT.MAX_CONTEXT_BYTES

    with pytest.raises(SelectionError, match="hard byte bound"):
        CONTEXT.bound_context({"approval_rule": "x" * 30000}, _selection_error)


def test_final_followup_identity_is_size_bound() -> None:
    context = {"kind": "charness.review_followup_context.v1", "selected_paths": ["a.py"]}
    identity = {"identity_sha256": "a" * 64, "reviewed_paths": ["a.py"]}
    bound = CONTEXT.bind_final_identity(context, identity, FOLLOWUP.FollowupError)
    assert bound["final_selected_path_count"] == 1
    assert bound["context_size_bytes"] == len(CONTEXT.context_bytes(bound))
    with pytest.raises(FOLLOWUP.FollowupError, match="hard byte bound"):
        CONTEXT.bind_final_identity(
            {"approval_rule": "x" * (CONTEXT.MAX_CONTEXT_BYTES + 1)},
            identity,
            FOLLOWUP.FollowupError,
        )


def test_selection_covers_explicit_delta_and_committed_ref_rules() -> None:
    prior = _identity(["a.py", "b.py"])

    def current(**_kwargs):
        return {
            "status": "captured",
            "reviewed_content": [
                {"path": "a.py", "content_sha256": "new-a"},
                {"path": "b.py", "content_sha256": "old-b.py"},
            ],
            "identity_sha256": "comparison",
        }

    paths, label, comparison, receipt = SELECTION.select_paths(
        repo_root=Path("."),
        identity=prior,
        prior_paths=["a.py", "b.py"],
        explicit_paths=["b.py", "new.py"],
        prior_mode="working-tree",
        current_mode="working-tree",
        changed_ref=None,
        build_identity=current,
        prior_binding={"status": "verified"},
        error=_selection_error,
    )
    assert paths == ["b.py", "new.py"]
    assert label == "explicit-with-selection-receipt"
    assert comparison["changed_prior_paths"] == ["a.py"]
    assert comparison["unchanged_selected_paths"] == ["b.py"]
    assert comparison["omitted_changed_prior_paths"] == ["a.py"]
    assert receipt["new_paths"] == ["new.py"]

    committed = _identity(["a.py"], mode="committed-ref")
    paths, _label, comparison, receipt = SELECTION.select_paths(
        repo_root=Path("."),
        identity=committed,
        prior_paths=["a.py"],
        explicit_paths=["new.py"],
        prior_mode="committed-ref",
        current_mode="committed-ref",
        changed_ref="HEAD^",
        build_identity=lambda **_: pytest.fail("different refs must not compare"),
        prior_binding={"status": "verified"},
        error=_selection_error,
    )
    assert paths == ["new.py"]
    assert comparison["comparison_ref"] == {"prior": "HEAD", "current": "HEAD^"}
    assert "differs" in receipt["rationale"]


def test_selection_covers_implicit_delta_and_rejects_unlike_substrates() -> None:
    assert SELECTION._content_index({}) == {}
    prior = _identity(["a.py"])
    current = {
        "status": "captured",
        "reviewed_content": [{"path": "a.py", "content_sha256": "new"}],
        "identity_sha256": "comparison",
    }
    paths, label, comparison, receipt = SELECTION.select_paths(
        repo_root=Path("."),
        identity=prior,
        prior_paths=["a.py"],
        explicit_paths=None,
        prior_mode="working-tree",
        current_mode="working-tree",
        changed_ref=None,
        build_identity=lambda **_kwargs: current,
        prior_binding={"status": "verified"},
        error=_selection_error,
    )
    assert paths == ["a.py"] and label == "changed-prior-inputs"
    assert comparison["changed_paths"] == 1
    assert receipt["selected_changed_prior_paths"] == ["a.py"]

    committed = _identity(["a.py"], mode="committed-ref")
    paths, _label, _comparison, _receipt = SELECTION.select_paths(
        repo_root=Path("."),
        identity=committed,
        prior_paths=["a.py"],
        explicit_paths=None,
        prior_mode="committed-ref",
        current_mode="committed-ref",
        changed_ref="HEAD",
        build_identity=lambda **_kwargs: {
            "status": "captured",
            "reviewed_content": [{"path": "a.py", "content_sha256": "new"}],
            "identity_sha256": "committed-comparison",
        },
        prior_binding={"status": "verified"},
        error=_selection_error,
    )
    assert paths == ["a.py"]

    with pytest.raises(SelectionError, match="different review substrate") as raised:
        SELECTION.select_paths(
            repo_root=Path("."),
            identity=prior,
            prior_paths=["a.py"],
            explicit_paths=None,
            prior_mode="working-tree",
            current_mode="committed-ref",
            changed_ref="HEAD",
            build_identity=lambda **_kwargs: current,
            prior_binding={"status": "verified"},
            error=_selection_error,
        )
    assert raised.value.code == "follow-up-paths-required"


@pytest.mark.parametrize(
    ("kwargs", "code", "message"),
    (
        (
            {"prior_mode": "committed-ref", "current_mode": "working-tree", "explicit_paths": ["a.py"]},
            "follow-up-substrate-mismatch",
            "different review substrates",
        ),
        (
            {"prior_mode": None, "current_mode": "working-tree", "explicit_paths": ["a.py"]},
            None,
            None,
        ),
        (
            {"prior_mode": "working-tree", "current_mode": "working-tree", "explicit_paths": None},
            "follow-up-paths-required",
            "no reconstructable",
        ),
        (
            {"prior_mode": "committed-ref", "current_mode": "committed-ref", "explicit_paths": None},
            "follow-up-ref-mismatch",
            "same pinned ref",
        ),
    ),
)
def test_selection_refuses_unsafe_implicit_or_mismatched_substrates(
    kwargs: dict[str, object], code: str | None, message: str | None
) -> None:
    identity = _identity(["a.py"], mode=str(kwargs["prior_mode"]) if kwargs["prior_mode"] else "working-tree")
    if kwargs["prior_mode"] is None:
        identity["reviewed_content"] = None
    if kwargs["explicit_paths"] is None and kwargs["prior_mode"] == "working-tree":
        identity["reviewed_content"] = None
    if kwargs["prior_mode"] == "committed-ref":
        identity["changed_ref"] = "HEAD"
    selection_kwargs = {
        "repo_root": Path("."),
        "identity": identity,
        "prior_paths": ["a.py"] if kwargs["prior_mode"] is not None else [],
        "explicit_paths": kwargs["explicit_paths"],
        "prior_mode": kwargs["prior_mode"],
        "current_mode": kwargs["current_mode"],
        "changed_ref": "HEAD^" if kwargs["prior_mode"] == "committed-ref" else None,
        "build_identity": lambda **_: {"status": "captured", "reviewed_content": []},
        "prior_binding": {"status": "verified"},
        "error": _selection_error,
    }
    if code is None:
        paths, label, comparison, receipt = SELECTION.select_paths(**selection_kwargs)
        assert paths == ["a.py"] and label == "explicit-with-selection-receipt"
        assert comparison is None and "not approval" in receipt["rationale"]
        return
    with pytest.raises(SelectionError, match=message) as raised:
        SELECTION.select_paths(**selection_kwargs)
    assert raised.value.code == code


@pytest.mark.parametrize(
    ("explicit", "status", "code", "message"),
    (
        (True, "exception", "follow-up-delta-unavailable", "git failed"),
        (True, "unavailable", "follow-up-delta-unavailable", "could not be captured"),
        (False, "exception", "follow-up-delta-unavailable", "git failed"),
        (False, "unavailable", "follow-up-delta-unavailable", "could not be captured"),
        (False, "same", "follow-up-no-delta", "no previously reviewed input changed"),
    ),
)
def test_selection_reports_delta_capture_failures(
    explicit: bool, status: str, code: str, message: str
) -> None:
    identity = _identity(["a.py"])
    current = {"status": "captured", "reviewed_content": identity["reviewed_content"]}
    if status == "unavailable":
        current["status"] = "unavailable"
    elif status == "same":
        current["identity_sha256"] = "same"

    def build(**_kwargs):
        if status == "exception":
            raise KeyError("git failed")
        return current

    with pytest.raises(SelectionError, match=message) as raised:
        SELECTION.select_paths(
            repo_root=Path("."),
            identity=identity,
            prior_paths=["a.py"],
            explicit_paths=["a.py"] if explicit else None,
            prior_mode="working-tree",
            current_mode="working-tree",
            changed_ref=None,
            build_identity=build,
            prior_binding={"status": "verified"},
            error=_selection_error,
        )
    assert raised.value.code == code


def _provenance_fixture(tmp_path: Path) -> dict[str, object]:
    repo = install_committed_repo(tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"})
    source_value, source = _prior_review(repo)
    packet_path = repo / "charness-artifacts/critique/prior-packet.json"
    return {
        "repo": repo,
        "source": source,
        "source_value": source_value,
        "raw": json.loads(source.read_text(encoding="utf-8")),
        "plan_path": source.parent / "run-plan.json",
        "plan": json.loads((source.parent / "run-plan.json").read_text(encoding="utf-8")),
        "manifest_path": source.parent / "attempt-manifest.json",
        "manifest": json.loads((source.parent / "attempt-manifest.json").read_text(encoding="utf-8")),
        "receipt_path": source.parent / "receipt.json",
        "receipt": json.loads((source.parent / "receipt.json").read_text(encoding="utf-8")),
        "report_path": source.parent / "worker-report.yaml",
        "report": json.loads((source.parent / "worker-report.yaml").read_text(encoding="utf-8")),
        "delivery_path": source.parent / "delivery.json",
        "delivery": json.loads((source.parent / "delivery.json").read_text(encoding="utf-8")),
        "packet": json.loads(packet_path.read_text(encoding="utf-8")),
    }


def _verify_provenance(case: dict[str, object]) -> dict[str, object]:
    packet = case["packet"]
    return PROVENANCE.verify_result_carrier(
        root=case["repo"],
        source=case["source"],
        raw=case["raw"],
        plan=case["plan"],
        identity=packet["reviewed_input_identity"],
        load_mapping=FOLLOWUP._load_mapping,
        sha256=FOLLOWUP._sha256,
        error=FOLLOWUP.FollowupError,
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _mutate_result_projection(case: dict[str, object]) -> None:
    result_path = case["repo"] / "charness-artifacts/critique/workers/prior/result.json"
    result = json.loads(result_path.read_text(encoding="utf-8"))
    result["verdict"] = "pass"
    _write_json(result_path, result)


def _mutate_backend_content(case: dict[str, object], backend: Path) -> None:
    content = b"{}\n"
    backend.write_bytes(content)
    case["manifest"]["logs"]["backend.stdout"].update(
        bytes=len(content), sha256=hashlib.sha256(content).hexdigest()
    )


def test_provenance_rejects_missing_and_mismatched_identity_chain(tmp_path: Path) -> None:
    mutations = (
        ("missing chain", lambda c: c["manifest_path"].unlink(), "missing the retained attempt provenance"),
        ("attempt", lambda c: c["manifest"].pop("attempt_id"), "has no attempt_id"),
        ("plan", lambda c: c["plan"].pop("packet_sha256"), "no packet/input identities"),
        ("identity", lambda c: c["packet"]["reviewed_input_identity"].update(identity_sha256="wrong"), "not bound to the run plan"),
        ("raw", lambda c: c["raw"].update(packet_sha256="wrong"), "do not match the retained run plan"),
    )
    for name, mutate, message in mutations:
        case = _provenance_fixture(tmp_path / name)
        mutate(case)
        for key in ("manifest", "plan"):
            if isinstance(case[key], dict) and case[f"{key}_path"].exists():
                _write_json(case[f"{key}_path"], case[key])
        with pytest.raises(FOLLOWUP.FollowupError, match=message):
            _verify_provenance(case)


@pytest.mark.parametrize(
    ("kind", "message"),
    (
        ("descriptor-path", "not the partial-result carrier"),
        ("descriptor-bytes", "bytes do not match the retained attempt descriptor"),
        ("manifest-file", "does not expose the supplied result carrier"),
        ("unsafe-source", "no safe retained backend source"),
        ("unlisted-source", "not exposed by the attempt manifest"),
        ("log-missing", "has no retained log descriptor"),
        ("backend-size", "backend source byte count changed"),
        ("backend-digest", "backend source digest changed"),
        ("backend-content", "not present in its retained backend source"),
        ("projection", "not a projection of the receipt-bound result carrier"),
        ("report-receipt", "report receipt path is not retained"),
        ("report-ledger", "report delivery path is not retained"),
        ("producer", "not bound to its result file"),
        ("result-output", "not bound to its result file"),
        ("result-digest", "digest is not bound by receipt/report"),
        ("delivery", "does not bind the result attempt"),
        ("identity-name", "identity does not match the attempt"),
        ("backend-path", "backend source path is not repository-relative"),
    ),
)
def test_provenance_rejects_tampered_or_unbound_carriers(
    tmp_path: Path, kind: str, message: str
) -> None:
    case = _provenance_fixture(tmp_path / kind)
    manifest = case["manifest"]
    receipt = case["receipt"]
    report = case["report"]
    delivery = case["delivery"]
    backend = case["repo"] / manifest["logs"]["backend.stdout"]["path"]
    mutations = {
        "descriptor-path": lambda: manifest["partial_result"].update(path="other.json"),
        "descriptor-bytes": lambda: manifest["partial_result"].update(
            bytes=manifest["partial_result"]["bytes"] + 1
        ),
        "manifest-file": lambda: manifest["files"].pop("partial-result.json"),
        "unsafe-source": lambda: manifest["partial_result"].update(source="../outside.log"),
        "unlisted-source": lambda: manifest["files"].pop("backend.stdout"),
        "log-missing": lambda: manifest.update(logs={}),
        "backend-size": lambda: backend.write_bytes(backend.read_bytes() + b"x"),
        "backend-digest": lambda: backend.write_bytes(b"x" + backend.read_bytes()[1:]),
        "backend-content": lambda: _mutate_backend_content(case, backend),
        "projection": lambda: _mutate_result_projection(case),
        "report-receipt": lambda: report.update(receipt_path="wrong.json"),
        "report-ledger": lambda: report.update(ledger_path="wrong.json"),
        "producer": lambda: report.pop("producer_binding"),
        "result-output": lambda: report["producer_binding"].update(output_file="other.json"),
        "result-digest": lambda: receipt.update(output_sha256="wrong"),
        "delivery": lambda: delivery["attempts"][0].update(packet_identity="wrong"),
        "identity-name": lambda: manifest.update(attempt_id="other"),
        "backend-path": lambda: manifest["partial_result"].update(
            source="./charness-artifacts/critique/workers/prior/backend.stdout"
        ),
    }
    mutations[kind]()
    for key, path in (("manifest", case["manifest_path"]), ("receipt", case["receipt_path"]), ("report", case["report_path"]), ("delivery", case["delivery_path"])):
        if isinstance(case[key], dict):
            _write_json(path, case[key])
    with pytest.raises(FOLLOWUP.FollowupError, match=message):
        _verify_provenance(case)


def test_provenance_handles_partial_only_carriers_and_safe_source_parsing(tmp_path: Path) -> None:
    case = _provenance_fixture(tmp_path / "valid")
    assert PROVENANCE._retained_source(case["repo"], "missing") is None
    assert PROVENANCE._retained_source(case["repo"], None) is None
    assert PROVENANCE._retained_source(case["repo"], "../outside") is None
    outside = case["repo"].parent / "outside"
    outside.mkdir()
    (case["repo"] / "escape").symlink_to(outside, target_is_directory=True)
    assert PROVENANCE._retained_source(case["repo"], "escape/backend.stdout") is None
    assert PROVENANCE._json_objects(b"prefix {bad\n {\"ok\": 1}") == [{"ok": 1}]

    result_path = case["repo"] / "charness-artifacts/critique/workers/prior/result.json"
    result_path.unlink()
    source = case["source"]
    case["receipt"]["retained_partial_output"] = {
        "path": source.relative_to(case["repo"]).as_posix(),
        "bytes": source.stat().st_size,
        "sha256": FOLLOWUP._sha256(source),
    }
    _write_json(case["receipt_path"], case["receipt"])
    assert _verify_provenance(case)["result_sha256"] is None
    case = _provenance_fixture(tmp_path / "invalid")
    result_path = case["repo"] / "charness-artifacts/critique/workers/prior/result.json"
    result_path.unlink()
    case["receipt"]["retained_partial_output"] = {"path": "wrong", "bytes": 0, "sha256": "wrong"}
    _write_json(case["receipt_path"], case["receipt"])
    with pytest.raises(FOLLOWUP.FollowupError, match="does not match the receipt-bound retained descriptor"):
        _verify_provenance(case)

    case = _provenance_fixture(tmp_path / "missing-descriptor")
    (case["repo"] / "charness-artifacts/critique/workers/prior/result.json").unlink()
    _write_json(case["receipt_path"], case["receipt"])
    with pytest.raises(FOLLOWUP.FollowupError, match="no receipt-bound retained descriptor"):
        _verify_provenance(case)

    case = _provenance_fixture(tmp_path / "report-binding")
    result_path = case["repo"] / "charness-artifacts/critique/workers/prior/result.json"
    result_path.unlink()
    source = case["source"]
    case["receipt"]["retained_partial_output"] = {
        "path": source.relative_to(case["repo"]).as_posix(),
        "bytes": source.stat().st_size,
        "sha256": FOLLOWUP._sha256(source),
    }
    case["report"]["producer_binding"]["output_file"] = "wrong.json"
    _write_json(case["receipt_path"], case["receipt"])
    _write_json(case["report_path"], case["report"])
    with pytest.raises(FOLLOWUP.FollowupError, match="do not share the producer output binding"):
        _verify_provenance(case)


def test_build_followup_reuses_a_valid_carrier_and_binds_the_new_identity(tmp_path: Path) -> None:
    repo = install_committed_repo(tmp_path / "repo", {"a.py": "VALUE = 1\n", "b.py": "VALUE = 2\n"})
    source_value, _source = _prior_review(repo)
    (repo / "a.py").write_text("VALUE = 3\n", encoding="utf-8")
    paths, context = FOLLOWUP.build_followup(
        repo_root=repo,
        source_value=source_value,
        explicit_paths=None,
        build_identity=build_reviewed_input_identity,
    )
    assert paths == ["a.py"]
    assert context["selection"] == "changed-prior-inputs"
    final = FOLLOWUP.bind_final_identity(context, {"identity_sha256": "new", "reviewed_paths": paths})
    assert final["final_reviewed_input_identity_sha256"] == "new"


def test_followup_binding_and_context_reuse_refuse_missing_or_invalid_prior_state(tmp_path: Path) -> None:
    assert FOLLOWUP._result_payload({"reviewer_result": {"verdict": "block"}})["verdict"] == "block"
    assert FOLLOWUP._result_payload({"other": "value"})["other"] == "value"
    assert FOLLOWUP._verify_prior_packet_binding(
        root=tmp_path,
        source=tmp_path / "result.json",
        raw={},
        plan={},
        packet=None,
        packet_path=None,
    )["status"] == "unavailable"
    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    with pytest.raises(FOLLOWUP.FollowupError, match="does not exist"):
        FOLLOWUP.build_followup(
            repo_root=tmp_path,
            source_value="missing.json",
            explicit_paths=None,
            build_identity=lambda **_: {},
        )


def test_prepare_packet_runner_restores_scope_environment_and_emits_refusals(monkeypatch, tmp_path: Path) -> None:
    adapter = {"valid": True, "path": ".agents/critique-adapter.yaml", "data": {"packet_sections": [{"id": "files"}], "output_dir": "out"}}
    monkeypatch.setattr(PREPARE, "load_adapter", lambda _root: adapter)
    monkeypatch.setattr(PREPARE, "adapter_has_sections", lambda _adapter: True)
    captured: list[str | None] = []

    def build(**_kwargs):
        captured.append(os.environ.get("CHARNESS_CRITIQUE_REVIEWED_PATHS"))
        return {"built": True}

    monkeypatch.setattr(PREPARE, "build_packet", build)
    monkeypatch.setenv("CHARNESS_CRITIQUE_REVIEWED_PATHS", "prior")
    assert PREPARE._build_packet(
        adapter=adapter,
        repo_root=tmp_path,
        prepared_for="test",
        changed_ref=None,
        substrate_mode="working-tree",
        reviewed_paths=["a.py"],
        excluded_paths=[],
        excluded_prefixes=[],
        prepared_targets=None,
    ) == {"built": True}
    assert json.loads(captured[0]) == ["a.py"]
    assert os.environ["CHARNESS_CRITIQUE_REVIEWED_PATHS"] == "prior"

    def followup_failure(**_kwargs):
        raise PREPARE._followup.FollowupError("prior-review-missing", "carrier unavailable")

    monkeypatch.setattr(PREPARE._followup, "build_followup", followup_failure)
    result = run_loaded_script_main(
        "prepare_packet.py", PREPARE, "--repo-root", str(tmp_path), "--follow-up-from", "missing.json"
    )
    assert result.returncode == 1
    assert "prior-review-missing" in result.stdout
    assert not (tmp_path / "out").exists()


def _prepare_main_with_followup(monkeypatch, tmp_path: Path, *, bind_error: bool = False, scope_error: bool = False):
    adapter = {"valid": True, "path": ".agents/critique-adapter.yaml", "data": {"packet_sections": [{"id": "files"}], "output_dir": "out"}}
    monkeypatch.setattr(PREPARE, "load_adapter", lambda _root: adapter)
    monkeypatch.setattr(PREPARE, "adapter_has_sections", lambda _adapter: True)
    monkeypatch.setattr(PREPARE._followup, "build_followup", lambda **_kwargs: (["a.py"], {"prior": True}))
    if bind_error:
        monkeypatch.setattr(
            PREPARE._followup,
            "bind_final_identity",
            lambda *_args: (_ for _ in ()).throw(PREPARE._followup.FollowupError("context-too-large", "too large")),
        )
    else:
        monkeypatch.setattr(PREPARE._followup, "bind_final_identity", lambda context, _identity: context)
    packet = {
        "kind": PREPARE._critique_packet_lib.PACKET_KIND,
        "section_count": 1,
        "ok": True,
        "changed_ref": None,
        "adapter_path": ".agents/critique-adapter.yaml",
        "substrate_mode": "working-tree",
        "reviewed_input_identity": {"identity_sha256": "a" * 64, "reviewed_paths": ["a.py"]},
        "sections": [{"id": "files", "content": _manifest_for_prepare(["a.py"]), "ok": True}],
    }
    monkeypatch.setattr(PREPARE, "_build_packet", lambda **_kwargs: packet)
    if scope_error:
        monkeypatch.setattr(
            PREPARE,
            "follow_up_scope_receipt",
            lambda **_kwargs: (_ for _ in ()).throw(PREPARE.ReviewedInputError("scope", "scope missing")),
        )
    else:
        monkeypatch.setattr(PREPARE, "follow_up_scope_receipt", lambda **_kwargs: {"status": "verified"})
    monkeypatch.setattr(PREPARE, "write_packet", lambda packet, *, output_dir, slug: _write_prepare_files(output_dir, slug, packet))
    return run_loaded_script_main("prepare_packet.py", PREPARE, "--repo-root", str(tmp_path), "--slug", "case", "--follow-up-from", "prior.json")


def _manifest_for_prepare(paths: list[str]) -> str:
    return "Exact reviewed-path manifest:\n" + "\n".join(f"- {path}" for path in paths) + "\n"


def _write_prepare_files(output_dir: Path, slug: str, packet: dict) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"{slug}-packet.json"
    md_path = output_dir / f"{slug}-packet.md"
    json_path.write_text(json.dumps(packet), encoding="utf-8")
    md_path.write_text("packet", encoding="utf-8")
    return json_path, md_path


@pytest.mark.parametrize(
    ("bind_error", "scope_error", "code", "message"),
    (
        (True, False, "context-too-large", "too large"),
        (False, True, "scope", "scope missing"),
    ),
)
def test_prepare_packet_followup_refusals_are_structured(
    monkeypatch, tmp_path: Path, bind_error: bool, scope_error: bool, code: str, message: str
) -> None:
    result = _prepare_main_with_followup(
        monkeypatch, tmp_path, bind_error=bind_error, scope_error=scope_error
    )
    assert result.returncode == 1
    assert code in result.stdout
    assert message in result.stdout
    assert not (tmp_path / "out/case-packet.json").exists()
