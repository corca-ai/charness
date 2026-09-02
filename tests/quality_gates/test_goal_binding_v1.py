from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "skills/public/achieve/scripts/goal_binding.py"
SUPPORT_SCRIPT = ROOT / "skills/public/achieve/scripts/goal_binding_support.py"
OBSERVATION_SCRIPT = ROOT / "skills/public/issue/scripts/issue_tracker_observation.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


binding = _load_module(SCRIPT, "goal_binding_v1")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _parent(number: int = 724) -> dict[str, object]:
    return {
        "repo": "corca-ai/charness",
        "number": number,
        "url": f"https://github.com/corca-ai/charness/issues/{number}",
    }


def _reused(
    *,
    key: str = "provider",
    number: int = 726,
    state: str = "OPEN",
    policy: str = "managed-addendum",
    body_sha256: str | None = _sha("provider addendum\n"),
) -> dict[str, object]:
    return {
        "key": key,
        "intent": "reuse",
        "issue": {
            "repo": "corca-ai/charness",
            "number": number,
            "url": f"https://github.com/corca-ai/charness/issues/{number}",
        },
        "dependencies": [],
        "rank": 1,
        "body_policy": policy,
        "body_sha256": body_sha256,
        "observed": {
            "state": state,
            "title_sha256": _sha(f"title-{key}"),
            "body_sha256": _sha(f"old-{key}-body"),
        },
    }


def _created(
    *, key: str = "binding", dependencies: list[str] | None = None, rank: int = 2
) -> dict[str, object]:
    return {
        "key": key,
        "intent": "create",
        "issue": None,
        "dependencies": dependencies or [],
        "rank": rank,
        "body_policy": "managed",
        "body_sha256": _sha(f"{key} body\n"),
        "observed": None,
    }


def _fixture(tmp_path: Path, *, write: bool = True) -> tuple[Path, Path, dict[str, object]]:
    draft = tmp_path / "charness-artifacts/goals/demo.md"
    draft.parent.mkdir(parents=True)
    draft.write_text("# approved draft\n", encoding="utf-8")
    payload = binding.build_binding(
        draft_path="charness-artifacts/goals/demo.md",
        draft_sha256=binding.sha256_file(draft),
        briefing_sha256=_sha("briefing"),
        approval_response="승인",
        approval_session_id="session-1",
        approval_observed_at="2026-08-26T09:00:00+09:00",
        parent=_parent(),
        approved_work_items=[_reused(), _created(dependencies=["provider"])],
    )
    path = draft.with_suffix(".binding.json")
    if write:
        path.write_bytes(binding.canonical_json_bytes(payload))
    return draft, path, payload


def _strict_validate(draft: Path, path: Path, payload: dict[str, object]):
    return binding.validate_binding(
        draft.parents[2],
        path,
        expected_parent=payload["parent"],
        expected_draft_path=draft,
        expected_draft_sha256=payload["draft"]["sha256"],
        expected_binding_sha256=binding.sha256_file(path),
    )


def _refresh_graph_digest(payload: dict[str, object]) -> None:
    payload["approved_work_items_sha256"] = binding.sha256_bytes(
        binding.canonical_json_bytes(payload["approved_work_items"])
    )


def test_identical_semantics_are_canonical_and_strictly_hash_bound(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)
    reordered = binding.build_binding(
        draft_path=payload["draft"]["path"],
        draft_sha256=payload["draft"]["sha256"],
        briefing_sha256=payload["approval"]["briefing_sha256"],
        approval_response=payload["approval"]["response"],
        approval_session_id=payload["approval"]["session_id"],
        approval_observed_at=payload["approval"]["observed_at"],
        parent=payload["parent"],
        approved_work_items=list(reversed(payload["approved_work_items"])),
    )

    assert binding.canonical_json_bytes(payload) == binding.canonical_json_bytes(reordered)
    result = _strict_validate(draft, path, payload)
    assert result["ok"] is True
    assert result["authority"] == "parent-bound"
    assert result["binding_sha256"] == binding.sha256_file(path)
    assert result["approved_work_item_count"] == 2


def test_structural_validation_is_explicitly_not_authority(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)

    structural = binding.validate_structural_binding(tmp_path, path)
    assert structural["authority"] == "structural-only"
    with pytest.raises(binding.BindingError, match="parent-unverified"):
        binding.validate_binding(tmp_path, path)

    assert _strict_validate(draft, path, payload)["authority"] == "parent-bound"


def test_draft_change_after_binding_is_reported_not_refused(tmp_path: Path) -> None:
    """The binding keeps the approval-time hash as identity; an amended draft is visible, not fatal."""
    draft, path, payload = _fixture(tmp_path)
    assert _strict_validate(draft, path, payload)["draft_amended"] is False
    draft.write_text("# changed draft\n", encoding="utf-8")

    result = _strict_validate(draft, path, payload)
    assert result["draft_amended"] is True
    assert result["draft_sha256"] == payload["draft"]["sha256"]
    assert result["draft_current_sha256"] != payload["draft"]["sha256"]


def test_binding_state_fields_are_not_allowed(tmp_path: Path) -> None:
    _, path, _ = _fixture(tmp_path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["status"] = "active"
    path.write_bytes(binding.canonical_json_bytes(payload))

    with pytest.raises(binding.BindingError, match="state-field-forbidden"):
        binding.validate_structural_binding(tmp_path, path)


def test_unknown_schema_and_noncanonical_bytes_refuse(tmp_path: Path) -> None:
    _, path, payload = _fixture(tmp_path)
    payload["kind"] = "charness.goal-binding/v2"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="schema-unknown"):
        binding.validate_structural_binding(tmp_path, path)

    _, path, _ = _fixture(tmp_path / "noncanonical")
    raw = path.read_bytes()
    path.write_bytes(raw[:-1])
    with pytest.raises(binding.BindingError, match="binding-hash-mismatch"):
        binding.validate_structural_binding(tmp_path / "noncanonical", path)


def test_parent_mismatch_and_internal_graph_digest_mismatch_are_independent(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)
    mutated = copy.deepcopy(payload)
    mutated["parent"] = _parent(725)
    path.write_bytes(binding.canonical_json_bytes(mutated))
    with pytest.raises(binding.BindingError, match="parent-mismatch"):
        binding.validate_structural_binding(tmp_path, path, expected_parent=payload["parent"])

    _, path, payload = _fixture(tmp_path / "graph")
    payload["approved_work_items"][0]["body_sha256"] = _sha("changed body")
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="graph-digest-mismatch"):
        binding.validate_structural_binding(tmp_path / "graph", path)


@pytest.mark.parametrize(
    ("intent", "state", "policy", "body_sha256"),
    [
        ("reuse", "OPEN", "preserve-closed-evidence", None),
        ("reuse", "CLOSED", "managed", _sha("managed")),
        ("create", None, "preserve-closed-evidence", None),
    ],
)
def test_create_reuse_preserve_matrix_rejects_impossible_states(
    tmp_path: Path,
    intent: str,
    state: str | None,
    policy: str,
    body_sha256: str | None,
) -> None:
    draft, path, payload = _fixture(tmp_path)
    item = next(item for item in payload["approved_work_items"] if item["key"] == "provider")
    if intent == "create":
        item = payload["approved_work_items"][0]
        item["intent"] = "create"
        item["issue"] = None
        item["observed"] = None
    else:
        item["observed"]["state"] = state
    item["body_policy"] = policy
    item["body_sha256"] = body_sha256
    _refresh_graph_digest(payload)
    path.write_bytes(binding.canonical_json_bytes(payload))

    with pytest.raises(binding.BindingError, match="body-policy-invalid"):
        binding.validate_structural_binding(tmp_path, path)

    if intent == "reuse" and state == "CLOSED":
        item["body_policy"] = "preserve-closed-evidence"
        item["body_sha256"] = None
        _refresh_graph_digest(payload)
        path.write_bytes(binding.canonical_json_bytes(payload))
        assert binding.validate_structural_binding(tmp_path, path)["ok"] is True


@pytest.mark.parametrize(
    ("field", "value"),
    [("intent", []), ("body_policy", {}), ("observed_state", [])],
)
def test_malformed_enum_shapes_are_typed_refusals(
    tmp_path: Path, field: str, value: object
) -> None:
    _, path, payload = _fixture(tmp_path)
    item = next(item for item in payload["approved_work_items"] if item["key"] == "provider")
    if field == "observed_state":
        item["observed"]["state"] = value
    else:
        item[field] = value
    _refresh_graph_digest(payload)
    path.write_bytes(binding.canonical_json_bytes(payload))

    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path, path)
    expected_code = "body-policy-invalid" if field == "body_policy" else "schema-invalid"
    assert exc_info.value.code == expected_code


def test_dependency_cycles_and_identity_collisions_are_rejected(tmp_path: Path) -> None:
    common = {
        "draft_path": "charness-artifacts/goals/demo.md",
        "draft_sha256": _sha("draft"),
        "briefing_sha256": _sha("briefing"),
        "approval_response": "승인",
        "approval_session_id": "session-1",
        "approval_observed_at": "2026-08-26T09:00:00+09:00",
        "parent": _parent(),
    }
    with pytest.raises(binding.BindingError, match="dependency-cycle"):
        binding.build_binding(
            **common,
            approved_work_items=[
                _created(key="a", dependencies=["b"], rank=1),
                _created(key="b", dependencies=["a"], rank=1),
            ],
        )

    with pytest.raises(binding.BindingError, match="graph-identity-collision"):
        binding.build_binding(
            **common,
            approved_work_items=[
                _reused(key="a", number=726),
                _reused(key="b", number=726),
            ],
        )


def test_dependency_rank_must_be_strictly_after_dependency() -> None:
    common = {
        "draft_path": "charness-artifacts/goals/demo.md",
        "draft_sha256": _sha("draft"),
        "briefing_sha256": _sha("briefing"),
        "approval_response": "승인",
        "approval_session_id": "session-1",
        "approval_observed_at": "2026-08-26T09:00:00+09:00",
        "parent": _parent(),
    }
    with pytest.raises(binding.BindingError) as exc_info:
        binding.build_binding(
            **common,
            approved_work_items=[
                _created(key="a", dependencies=["b"], rank=1),
                _created(key="b", rank=1),
            ],
        )
    assert exc_info.value.code == "dependency-rank-invalid"


@pytest.mark.parametrize("repo", ["org/repo?x", "org/repo#x", "org:repo", "org/repo name"])
def test_noncanonical_repository_slugs_are_rejected(repo: str) -> None:
    with pytest.raises(binding.BindingError) as exc_info:
        binding.build_binding(
            draft_path="charness-artifacts/goals/demo.md",
            draft_sha256=_sha("draft"),
            briefing_sha256=_sha("briefing"),
            approval_response="승인",
            approval_session_id="session-1",
            approval_observed_at="2026-08-26T09:00:00+09:00",
            parent={"repo": repo, "number": 724, "url": f"https://github.com/{repo}/issues/724"},
            approved_work_items=[_created()],
        )
    assert exc_info.value.code == "schema-invalid"


@pytest.mark.parametrize("url_suffix", ["?x=1", "#fragment", ";params"])
def test_parent_url_query_fragment_or_params_are_rejected(tmp_path: Path, url_suffix: str) -> None:
    _, path, payload = _fixture(tmp_path)
    payload["parent"]["url"] += url_suffix
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path, path)
    assert exc_info.value.code == "parent-mismatch"


def test_path_escape_missing_wrong_pairing_and_symlink_paths_refuse(tmp_path: Path) -> None:
    _, path, payload = _fixture(tmp_path)
    payload["draft"]["path"] = "../outside.md"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="path-invalid"):
        binding.validate_structural_binding(tmp_path, path)

    _, path, payload = _fixture(tmp_path / "missing")
    payload["draft"]["path"] = "charness-artifacts/goals/missing.md"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="draft-missing"):
        binding.validate_structural_binding(tmp_path / "missing", path)

    _, path, payload = _fixture(tmp_path / "wrong-suffix")
    payload["draft"]["path"] = "charness-artifacts/goals/demo.txt"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="path-invalid"):
        binding.validate_structural_binding(tmp_path / "wrong-suffix", path)

    _, original, payload = _fixture(tmp_path / "wrong-pair")
    wrong = original.with_name("other.json")
    wrong.write_bytes(original.read_bytes())
    with pytest.raises(binding.BindingError, match="path-invalid"):
        binding.validate_structural_binding(tmp_path / "wrong-pair", wrong)

    outside = tmp_path / "outside.md"
    outside.write_text("outside\n", encoding="utf-8")
    _, path, payload = _fixture(tmp_path / "absolute")
    payload["draft"]["path"] = str(outside)
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="path-invalid"):
        binding.validate_structural_binding(tmp_path / "absolute", path)

    _, path, payload = _fixture(tmp_path / "in-repo-absolute")
    payload["draft"]["path"] = str(
        (tmp_path / "in-repo-absolute" / "charness-artifacts/goals/demo.md").resolve()
    )
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path / "in-repo-absolute", path)
    assert exc_info.value.code == "path-invalid"

    _, path, payload = _fixture(tmp_path / "nul")
    payload["draft"]["path"] = "charness-artifacts/goals/de\x00mo.md"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path / "nul", path)
    assert exc_info.value.code == "path-invalid"

    symlink_root = tmp_path / "symlink"
    symlink_root.mkdir()
    symlink_target = symlink_root / "target.md"
    symlink_target.write_text("target\n", encoding="utf-8")
    symlink_draft = symlink_root / "draft.md"
    try:
        symlink_draft.symlink_to(symlink_target)
    except OSError:
        pytest.skip("symlinks are unavailable")
    _, path, payload = _fixture(symlink_root / "fixture")
    payload["draft"]["path"] = "draft.md"
    payload["draft"]["sha256"] = binding.sha256_file(symlink_target)
    path = symlink_root / "fixture.binding.json"
    path.write_bytes(binding.canonical_json_bytes(payload))
    with pytest.raises(binding.BindingError, match="path-invalid"):
        binding.validate_structural_binding(symlink_root, path)


def test_strict_external_binding_hash_rejects_edited_and_rehashed_core(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)
    original_hash = binding.sha256_file(path)
    payload["approval"]["response"] = "edited approval"
    path.write_bytes(binding.canonical_json_bytes(payload))

    assert binding.validate_structural_binding(tmp_path, path)["ok"] is True
    with pytest.raises(binding.BindingError, match="binding-hash-mismatch"):
        binding.validate_binding(
            tmp_path,
            path,
            expected_parent=payload["parent"],
            expected_draft_path=draft,
            expected_draft_sha256=payload["draft"]["sha256"],
            expected_binding_sha256=original_hash,
        )


def test_writer_requires_authority_and_uses_deterministic_atomic_create(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path, write=False)
    with pytest.raises(binding.BindingError, match="parent-unverified"):
        binding.write_immutable_binding(path, payload, repo_root=tmp_path)
    assert not path.exists()

    digest = binding.write_immutable_binding(
        path,
        payload,
        repo_root=tmp_path,
        expected_parent=payload["parent"],
        expected_draft_path=draft,
        expected_draft_sha256=payload["draft"]["sha256"],
    )
    assert digest == binding.sha256_file(path)
    assert _strict_validate(draft, path, payload)["binding_sha256"] == digest
    assert not list(path.parent.glob(f".{path.name}.*.tmp"))
    with pytest.raises(binding.BindingError, match="binding-frozen"):
        binding.write_immutable_binding(
            path,
            payload,
            repo_root=draft.parents[2],
            expected_parent=payload["parent"],
            expected_draft_path=draft,
            expected_draft_sha256=payload["draft"]["sha256"],
        )

    draft, original, payload = _fixture(tmp_path / "wrong-writer", write=False)
    wrong = original.with_name("wrong.json")
    with pytest.raises(binding.BindingError) as exc_info:
        binding.write_immutable_binding(
            wrong,
            payload,
            repo_root=draft.parents[2],
            expected_parent=payload["parent"],
            expected_draft_path=draft,
            expected_draft_sha256=payload["draft"]["sha256"],
        )
    assert exc_info.value.code == "path-invalid"


def test_missing_inputs_and_read_failures_have_exact_typed_codes(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)
    path.unlink()
    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path, path)
    assert exc_info.value.code == "binding-missing"

    draft, path, payload = _fixture(tmp_path / "draft-missing")
    draft.unlink()
    with pytest.raises(binding.BindingError) as exc_info:
        binding.validate_structural_binding(tmp_path / "draft-missing", path)
    assert exc_info.value.code == "draft-missing"

    draft, path, payload = _fixture(tmp_path / "read-race")
    original = binding.sha256_file

    def fail_read(_: Path) -> str:
        raise OSError("simulated disappearance")

    binding.sha256_file = fail_read
    try:
        with pytest.raises(binding.BindingError) as exc_info:
            binding.validate_structural_binding(tmp_path / "read-race", path)
        assert exc_info.value.code == "draft-missing"
    finally:
        binding.sha256_file = original


def test_competing_writers_have_one_winner_and_no_partial_target(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path, write=False)

    def attempt() -> str:
        try:
            binding.write_immutable_binding(
                path,
                payload,
                repo_root=tmp_path,
                expected_parent=payload["parent"],
                expected_draft_path=draft,
                expected_draft_sha256=payload["draft"]["sha256"],
            )
        except binding.BindingError as exc:
            return exc.code
        return "ok"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda _: attempt(), range(2)))
    assert sorted(outcomes) == ["binding-frozen", "ok"]
    assert (
        binding.canonical_json_bytes(json.loads(path.read_text(encoding="utf-8")))
        == path.read_bytes()
    )


def test_provider_observation_consumes_validator_returned_hash(tmp_path: Path) -> None:
    draft, path, payload = _fixture(tmp_path)
    result = _strict_validate(draft, path, payload)
    observations = _load_module(OBSERVATION_SCRIPT, "issue_tracker_observation_v1")
    started = observations.begin(
        repo_root=tmp_path,
        observation_dir=tmp_path / "observations",
        attempt_id="binding-handoff",
        draft_sha256=result["draft_sha256"],
        binding_sha256=result["binding_sha256"],
        repo="corca-ai/charness",
        parent_number=724,
        operation="binding-readback",
        target={"work_item_key": "binding"},
        submitted_body_sha256=None,
        backend={"id": "gh", "binary": "gh"},
    )
    assert started["payload"]["binding_sha256"] == result["binding_sha256"]


@pytest.mark.boundary_contract(
    reason="env-scrubbed export self-sufficiency: a clean interpreter validates source and exported bindings"
)
def test_clean_process_validates_frozen_pair_and_export_matches_source(
    tmp_path: Path, exported_plugin_tree: Path
) -> None:
    draft, path, payload = _fixture(tmp_path)
    plugin_script = exported_plugin_tree / "skills" / "achieve" / "scripts" / "goal_binding.py"
    plugin_support_script = (
        exported_plugin_tree / "skills" / "achieve" / "scripts" / "goal_binding_support.py"
    )
    assert SCRIPT.read_bytes() == plugin_script.read_bytes()
    assert SUPPORT_SCRIPT.read_bytes() == plugin_support_script.read_bytes()

    code = """
import importlib.util
import json
import sys
from pathlib import Path
spec = importlib.util.spec_from_file_location('clean_goal_binding', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result = module.validate_binding(
    Path(sys.argv[2]), Path(sys.argv[3]),
    expected_parent=json.loads(sys.argv[4]),
    expected_draft_path=sys.argv[5],
    expected_draft_sha256=sys.argv[6],
    expected_binding_sha256=sys.argv[7],
)
assert result['authority'] == 'parent-bound'
assert result['binding_sha256'] == sys.argv[7]
"""
    for candidate in (SCRIPT, plugin_script):
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                code,
                str(candidate),
                str(tmp_path),
                str(path),
                json.dumps(payload["parent"]),
                str(draft),
                payload["draft"]["sha256"],
                binding.sha256_file(path),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        assert completed.returncode == 0, (candidate, completed.stderr)
