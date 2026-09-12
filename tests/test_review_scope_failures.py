from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.review.reviewed_input_identity import build_reviewed_input_identity
from tests.quality_gates.repo_shapes import install_committed_repo
from tests.script_main import load_script_module

ROOT = Path(__file__).resolve().parents[1]

ADAPTER = load_script_module(
    "review_scope_failures_adapter",
    ROOT / "scripts/review/critique_adapter_lib.py",
)
SCOPE = load_script_module(
    "review_scope_failures_scope",
    ROOT / "scripts/review/critique_followup_scope.py",
)
PACKET = load_script_module(
    "review_scope_failures_packet",
    ROOT / "scripts/review/critique_packet_lib.py",
)
PRODUCER = load_script_module(
    "review_scope_failures_producer",
    ROOT / "scripts/review/render_critique_section_changed_surfaces.py",
)
VERIFICATION = load_script_module(
    "review_scope_failures_verification",
    ROOT / "scripts/review/reviewed_input_verification.py",
)
CONSUMER = load_script_module(
    "review_scope_failures_consumer",
    ROOT / "skills/public/critique/scripts/followup_scope_consumer.py",
)


class ScopeError(ValueError):
    def __init__(self, code: str, message: str, *, details: dict | None = None) -> None:
        self.code = code
        self.details = details or {}
        super().__init__(message)


def _scope_error(code: str, message: str, *, details: dict | None = None) -> Exception:
    return ScopeError(code, message, details=details)


def _scope_adapter(declarations: object) -> dict[str, object]:
    return {"data": {"follow_up_scope": declarations}}


def _manifest(*paths: str) -> str:
    return "Exact reviewed-path manifest:\n" + "\n".join(f"- {path}" for path in paths) + "\n\n"


def test_adapter_rejects_malformed_follow_up_scope_declarations() -> None:
    cases = (
        ({"follow_up_scope": {}}, "follow_up_scope must be a list"),
        ({"follow_up_scope": ["selected"]}, "follow_up_scope[0] must be a mapping"),
        (
            {
                "follow_up_scope": [
                    {
                        "section_id": "files",
                        "mode": "selected-paths",
                        "binding": "paths",
                        "path_binding": "wrong",
                    }
                ]
            },
            "path_binding must be `exact-path-manifest`",
        ),
        (
            {
                "follow_up_scope": [
                    {"section_id": "files", "mode": "unknown", "binding": "paths"}
                ]
            },
            "mode must be one of: selected-paths, static",
        ),
        (
            {
                "follow_up_scope": [
                    {"section_id": "files", "mode": "static", "binding": "static"},
                    {"section_id": "files", "mode": "static", "binding": "static"},
                ]
            },
            "duplicates `files`",
        ),
    )

    for data, expected in cases:
        _validated, errors, _warnings = ADAPTER.validate_adapter_data(
            {"version": 1, **data}, ROOT
        )
        assert any(expected in error for error in errors), errors


def test_adapter_keeps_only_valid_follow_up_scope_entries() -> None:
    validated, errors, warnings = ADAPTER.validate_adapter_data(
        {
            "version": 1,
            "follow_up_scope": [
                {
                    "section_id": "files",
                    "mode": "selected-paths",
                    "binding": "CHARNESS_CRITIQUE_REVIEWED_PATHS",
                    "path_binding": "exact-path-manifest",
                },
                {
                    "section_id": "notes",
                    "mode": "static",
                    "binding": "adapter-static-content",
                },
            ],
        },
        ROOT,
    )

    assert errors == []
    assert warnings == []
    assert validated["follow_up_scope"] == [
        {
            "section_id": "files",
            "mode": "selected-paths",
            "binding": "CHARNESS_CRITIQUE_REVIEWED_PATHS",
            "path_binding": "exact-path-manifest",
        },
        {
            "section_id": "notes",
            "mode": "static",
            "binding": "adapter-static-content",
            "path_binding": None,
        },
    ]


def test_adapter_drops_a_follow_up_entry_with_missing_binding() -> None:
    validated, errors, _warnings = ADAPTER.validate_adapter_data(
        {
            "version": 1,
            "follow_up_scope": [{"section_id": "files", "mode": "selected-paths"}],
        },
        ROOT,
    )

    assert errors == []
    assert validated.get("follow_up_scope") == []


def test_adapter_rejects_schema_failure_paths_used_by_follow_up_configs() -> None:
    validated, errors, warnings = ADAPTER.validate_adapter_data(
        {
            "version": 1,
            "packet_sections": [
                None,
                {"title": "missing id", "content_kind": "static", "content": "x"},
                {"id": "script", "title": "wrong payload", "content_kind": "script", "content": "x"},
                {"id": "command", "title": "wrong kind", "content_kind": "static", "command": "x"},
                {"id": "empty", "title": "empty", "content_kind": "static"},
                {"id": "bad-content", "title": "bad", "content_kind": "static", "content": 3},
            ],
            "reviewer_tiers": {
                "unmapped": "not a mapping",
                "unknown": {"model": "m"},
                "high-leverage": {"unknown": "field", "model": 3},
            },
            "reviewer_runner": {
                "mode": "unknown",
                "backend": "unknown",
                "timeout_seconds": 0,
                "extra": "field",
            },
        },
        ROOT,
    )

    assert validated["packet_sections"]
    assert warnings and "not a known reviewer tier" in warnings[0]
    expected_fragments = (
        "packet_sections[0] must be a mapping",
        "packet_sections[1].id is required",
        "content_kind=script requires `command`",
        "content_kind=static requires `content` or `content_path`",
        "must declare exactly one",
        "content must be a string or list of strings",
        "reviewer_tiers.unmapped must be a mapping",
        "unknown is not a valid reviewer-tier field",
        "reviewer_runner.extra is not a valid runner field",
        "timeout_seconds must be a positive integer",
        "mode must be one of: file-backed-worker, typed-subagent",
        "backend must be one of: codex_exec, claude_p, host-defaulted",
    )
    for fragment in expected_fragments:
        assert any(fragment in error for error in errors), (fragment, errors)


def test_scope_receipt_accepts_exact_selected_paths_and_static_sections() -> None:
    receipt = SCOPE.follow_up_scope_receipt(
        adapter=_scope_adapter(
            [
                {
                    "section_id": "files",
                    "mode": "selected-paths",
                    "binding": "paths",
                    "path_binding": "exact-path-manifest",
                },
                {"section_id": "notes", "mode": "static", "binding": "notes"},
            ]
        ),
        sections=[
            {"id": "files", "content": _manifest("b.py", "a.py  (DELETED — explain)" )},
            {"id": "notes", "content": "Prior evidence is not approval."},
        ],
        selected_paths=["b.py", "a.py", "a.py"],
        error=_scope_error,
    )

    assert receipt["status"] == "verified"
    assert receipt["selected_paths"] == ["a.py", "b.py"]
    assert receipt["sections"][0]["path_check"] == "exact-manifest"
    assert receipt["sections"][0]["selected_path_count"] == 2
    assert receipt["sections"][0]["path_set_sha256"] == hashlib.sha256(b"a.py\nb.py").hexdigest()
    assert receipt["sections"][1]["path_check"] == "not-applicable"
    assert receipt["sections"][1]["path_set_sha256"] is None


@pytest.mark.parametrize(
    ("adapter", "sections", "selected_paths", "code", "message"),
    (
        ({"data": {"follow_up_scope": {}}}, [], [], "follow-up-scope-unbound", "must be a list"),
        (
            _scope_adapter([{"section_id": "other", "mode": "static", "binding": "x"}]),
            [{"id": "files", "content": "x"}],
            [],
            "follow-up-scope-unbound",
            "declare every packet section",
        ),
        (
            _scope_adapter([{"section_id": "files", "mode": "broken", "binding": "x"}]),
            [{"id": "files", "content": "x"}],
            [],
            "follow-up-scope-unbound",
            "mode is invalid",
        ),
        (
            _scope_adapter([{"section_id": "files", "mode": "selected-paths", "binding": "x"}]),
            [{"id": "files", "content": _manifest("a.py")}],
            ["a.py"],
            "follow-up-producer-out-of-scope",
            "no exact path binding",
        ),
        (
            _scope_adapter(
                [
                    {
                        "section_id": "files",
                        "mode": "selected-paths",
                        "binding": "x",
                        "path_binding": "exact-path-manifest",
                    }
                ]
            ),
            [{"id": "files", "content": "no manifest\n"}],
            ["a.py"],
            "follow-up-producer-out-of-scope",
            "manifest is not exact",
        ),
        (
            _scope_adapter(
                [
                    {
                        "section_id": "files",
                        "mode": "selected-paths",
                        "binding": "x",
                        "path_binding": "exact-path-manifest",
                    }
                ]
            ),
            [{"id": "files", "content": "Exact reviewed-path manifest:\nnot a list\n"}],
            ["a.py"],
            "follow-up-producer-out-of-scope",
            "manifest is not exact",
        ),
        (
            _scope_adapter(
                [
                    {
                        "section_id": "files",
                        "mode": "selected-paths",
                        "binding": "x",
                        "path_binding": "exact-path-manifest",
                    }
                ]
            ),
            [{"id": "files", "content": _manifest("other.py")}],
            ["a.py"],
            "follow-up-producer-out-of-scope",
            "manifest is not exact",
        ),
    ),
)
def test_scope_receipt_refuses_unbound_or_inexact_producer_scope(
    adapter: dict[str, object],
    sections: list[dict[str, object]],
    selected_paths: list[str],
    code: str,
    message: str,
) -> None:
    with pytest.raises(ScopeError, match=message) as raised:
        SCOPE.follow_up_scope_receipt(
            adapter=adapter,
            sections=sections,
            selected_paths=selected_paths,
            error=_scope_error,
        )
    assert raised.value.code == code


def test_packet_builder_delegates_scope_validation() -> None:
    sections = [{"id": "files", "content": _manifest("a.py")}]
    receipt = PACKET.follow_up_scope_receipt(
        adapter=_scope_adapter(
            [
                {
                    "section_id": "files",
                    "mode": "selected-paths",
                    "binding": "paths",
                    "path_binding": "exact-path-manifest",
                }
            ]
        ),
        sections=sections,
        selected_paths=["a.py"],
    )
    assert receipt["kind"] == "charness.follow_up_scope_receipt.v1"


def test_packet_producer_and_static_input_failures_are_preserved(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict[str, object]] = []

    def successful_phase(command, **kwargs):
        calls.append({"command": command, **kwargs})
        return SimpleNamespace(returncode=0, timed_out=False, stdout="body", stderr="")

    monkeypatch.setattr(PACKET, "run_monitored_phase", successful_phase)
    assert PACKET._run_command(
        "python3 producer.py", repo_root=tmp_path, changed_ref="HEAD", changed_ref_env_var="BOUND_REF"
    ) == ("body", [], True)
    assert calls[0]["env"]["BOUND_REF"] == "HEAD"

    monkeypatch.setattr(
        PACKET,
        "run_monitored_phase",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=7, timed_out=False, stdout="partial", stderr="producer failed"
        ),
    )
    assert PACKET._run_command("producer", repo_root=tmp_path) == (
        "partial",
        ["exit code 7", "producer failed"],
        False,
    )
    monkeypatch.setattr(
        PACKET,
        "run_monitored_phase",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=0, timed_out=True, stdout="", stderr=""
        ),
    )
    assert PACKET._run_command("producer", repo_root=tmp_path) == (
        "",
        ["command timed out after 60s"],
        False,
    )
    monkeypatch.setattr(
        PACKET,
        "run_monitored_phase",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(FileNotFoundError("missing")),
    )
    content, errors, ok = PACKET._run_command("missing", repo_root=tmp_path)
    assert content == "" and not ok and errors == ["command not found: missing"]

    assert PACKET._resolve_static({}, repo_root=tmp_path) == (
        "",
        ["static section missing content/content_path"],
        False,
    )
    assert PACKET._resolve_static({"content_path": "../outside"}, repo_root=tmp_path)[2] is False
    assert PACKET._resolve_static({"content_path": "missing.txt"}, repo_root=tmp_path)[2] is False
    (tmp_path / "body.txt").write_text("static body\n", encoding="utf-8")
    assert PACKET._resolve_static({"content_path": "body.txt"}, repo_root=tmp_path) == (
        "static body\n",
        [],
        True,
    )


def test_packet_render_records_follow_up_context_and_section_errors() -> None:
    base = {
        "kind": PACKET.PACKET_KIND,
        "version": 1,
        "repo": "demo",
        "generated_at": "2026-09-12T00:00:00Z",
        "prepared_for": "follow-up",
        "changed_ref": None,
        "adapter_path": None,
        "section_count": 1,
        "ok": False,
        "sections": [
            {
                "id": "files",
                "title": "Files",
                "content_kind": "script",
                "producer": "producer",
                "content": "",
                "ok": False,
                "errors": ["producer failed"],
            }
        ],
        "follow_up": {"selected_paths": ["a.py"]},
    }
    without_scope = PACKET.render_markdown(base)
    assert "## Follow-up Context" in without_scope
    assert "## Follow-up Producer Scope" not in without_scope
    assert "- **Errors**:" in without_scope
    assert "  - producer failed" in without_scope
    base["follow_up_scope"] = {"status": "verified"}
    with_scope = PACKET.render_markdown(base)
    assert "## Follow-up Producer Scope" in with_scope
    without_followup = dict(base)
    without_followup.pop("follow_up")
    assert "## Follow-up Context" not in PACKET.render_markdown(without_followup)


def test_runtime_bootstrap_inserts_repo_for_standalone_script_loads(monkeypatch) -> None:
    reduced_path = [entry for entry in sys.path if entry != str(ROOT)]
    monkeypatch.setattr(sys, "path", reduced_path)
    ADAPTER._load_repo_runtime_bootstrap()
    PACKET._load_repo_runtime_bootstrap()
    VERIFICATION._load_repo_runtime_bootstrap()
    assert str(ROOT) in sys.path


@pytest.mark.parametrize(
    ("raw", "expected"),
    (
        (None, None),
        ("not json", []),
        (json.dumps({"paths": ["a.py", 3, ""]}), []),
        (json.dumps(["b.py", "a.py", "a.py"]), ["a.py", "b.py"]),
    ),
)
def test_changed_surface_declared_paths_are_fail_closed_and_canonical(
    monkeypatch: pytest.MonkeyPatch, raw: str | None, expected: list[str] | None
) -> None:
    if raw is None:
        monkeypatch.delenv("CHARNESS_CRITIQUE_REVIEWED_PATHS", raising=False)
    else:
        monkeypatch.setenv("CHARNESS_CRITIQUE_REVIEWED_PATHS", raw)
    assert PRODUCER._declared_review_paths() == expected


def test_changed_surface_renderer_marks_narrow_scope_and_no_owner(monkeypatch, capsys, tmp_path: Path) -> None:
    payload = {
        "changed_paths": ["a.py"],
        "deleted_paths": set(),
        "matched_surfaces": [],
        "sync_commands": [],
        "changed_ref": None,
        "narrowed": True,
    }
    assert "Bound review paths for working tree" in PRODUCER._render_paths(payload)[0]
    assert "- (no surfaces matched the changed paths)" in PRODUCER._render_owners(payload)
    assert PRODUCER._render_sync({"sync_commands": []}) == []

    monkeypatch.setattr(PRODUCER, "load_surfaces", lambda _root: {})
    monkeypatch.setattr(
        PRODUCER,
        "collect_working_tree_snapshot",
        lambda _root: SimpleNamespace(changed_paths=["a.py", "b.py"], deleted_paths={"b.py"}),
    )
    monkeypatch.setattr(
        PRODUCER,
        "match_surfaces",
        lambda _surfaces, paths: {
            "changed_paths": list(paths),
            "matched_surfaces": [],
            "sync_commands": [],
        },
    )
    monkeypatch.setenv("CHARNESS_CRITIQUE_REVIEWED_PATHS", json.dumps(["a.py"]))
    monkeypatch.setattr(sys, "argv", ["render", "--repo-root", str(tmp_path)])
    assert PRODUCER.main() == 0
    output = capsys.readouterr().out
    assert "Bound review paths for working tree: (narrow follow-up scope)" in output
    assert "- a.py" in output
    assert "- b.py" not in output


def test_changed_surface_rendering_keeps_ref_and_empty_scope_prose_distinct() -> None:
    assert PRODUCER._render_paths(
        {
            "changed_paths": ["a.py"],
            "changed_ref": "HEAD^..HEAD",
            "deleted_paths": set(),
            "narrowed": True,
        }
    )[0].startswith("Bound review paths for ref `HEAD^..HEAD`")
    assert PRODUCER._render_paths(
        {
            "changed_paths": ["a.py"],
            "changed_ref": "HEAD^..HEAD",
            "deleted_paths": set(),
        }
    )[0] == "Changed paths for ref `HEAD^..HEAD`:"
    assert PRODUCER._render_paths(
        {"changed_paths": ["a.py"], "changed_ref": None, "deleted_paths": set()}
    )[0] == "Changed paths for working tree:"
    assert "- (none — changed ref produced no changed paths)" in PRODUCER._render_paths(
        {"changed_paths": [], "changed_ref": "HEAD", "deleted_paths": set()}
    )
    assert "- (none — clean working tree)" in PRODUCER._render_paths(
        {"changed_paths": [], "changed_ref": None, "deleted_paths": set()}
    )
    owner_lines = PRODUCER._render_owners(
        {
            "matched_surfaces": [
                {
                    "surface_id": "docs",
                    "description": "Markdown",
                    "matched_source_paths": ["docs/*.md"],
                    "matched_derived_paths": ["site/index.html"],
                    "sync_commands": ["sync docs"],
                    "verify_commands": ["check docs"],
                }
            ]
        }
    )
    assert "source matches: docs/*.md" in "\n".join(owner_lines)
    assert "derived matches: site/index.html" in "\n".join(owner_lines)
    assert "sync: sync docs" in "\n".join(owner_lines)
    assert "verify: check docs" in "\n".join(owner_lines)
    assert PRODUCER._render_sync({"sync_commands": ["sync docs"]}) == [
        "Planned sync commands before validators:",
        "- sync docs",
    ]


def test_changed_surface_renderer_uses_ref_snapshot_injected_in_process(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    monkeypatch.setattr(PRODUCER, "load_surfaces", lambda _root: {})
    monkeypatch.setattr(
        PRODUCER,
        "collect_changed_and_deleted_paths_for_ref",
        lambda _root, ref: (["ref.py"], {"ref.py"}),
    )
    monkeypatch.setattr(
        PRODUCER,
        "match_surfaces",
        lambda _surfaces, paths: {
            "changed_paths": list(paths),
            "matched_surfaces": [],
            "sync_commands": [],
        },
    )
    monkeypatch.setattr(sys, "argv", ["render", "--repo-root", str(tmp_path), "--changed-ref", "HEAD"])
    assert PRODUCER.main() == 0
    output = capsys.readouterr().out
    assert "- ref.py  (DELETED" in output

def test_changed_surface_renderer_returns_typed_failure_for_surface_lookup(
    monkeypatch, capsys, tmp_path: Path
) -> None:
    def fail(_root):
        raise PRODUCER.SurfaceError("surfaces file is invalid")

    monkeypatch.setattr(PRODUCER, "load_surfaces", fail)
    monkeypatch.setattr(sys, "argv", ["render", "--repo-root", str(tmp_path)])
    assert PRODUCER.main() == 1
    assert "surfaces lookup failed: surfaces file is invalid" in capsys.readouterr().out


def test_semantic_carrier_verifier_rejects_wrong_size_hash_and_identity_frame() -> None:
    content = b"captured bytes\n"
    carrier_sha = hashlib.sha256(content).hexdigest()
    working_hash = hashlib.sha256(b"file\0-\0" + content).hexdigest()
    base = {"carrier_sha256": carrier_sha, "content_sha256": working_hash, "size_bytes": len(content)}
    identity = {"substrate_mode": VERIFICATION.SUBSTRATE_WORKING_TREE}

    wrong_size = dict(base, size_bytes=len(content) + 1)
    assert VERIFICATION.verify_semantic_carrier_entry(identity, wrong_size, content) == (
        False,
        "carrier bytes do not match recorded size",
    )
    assert VERIFICATION.verify_semantic_carrier_entry(
        identity, dict(base, content_sha256="invalid"), content
    ) == (False, "semantic carrier content hash is invalid")
    assert VERIFICATION.verify_semantic_carrier_entry(
        identity, dict(base, content_sha256=hashlib.sha256(b"other").hexdigest()), content
    ) == (False, "carrier bytes do not match the recorded identity hash")
    assert VERIFICATION.verify_semantic_carrier_entry(
        {"substrate_mode": VERIFICATION.SUBSTRATE_COMMITTED_REF},
        dict(base, content_sha256=carrier_sha),
        content,
    ) == (True, "verified")
    assert VERIFICATION.verify_semantic_carrier_entry(
        identity,
        dict(base, content_sha256=carrier_sha, disposition="deleted-preimage"),
        content,
    ) == (True, "verified")


@pytest.mark.parametrize("raised", (VERIFICATION.ReviewedInputError("code", "failure"), TypeError("bad shape")))
def test_identity_verifier_reports_reconstruction_failures(monkeypatch, tmp_path: Path, raised: Exception) -> None:
    identity = {
        "status": "captured",
        "algorithm": VERIFICATION.ALGORITHM,
        "reviewed_paths": ["a.py"],
        "substrate_mode": VERIFICATION.SUBSTRATE_WORKING_TREE,
        "mode": VERIFICATION.SUBSTRATE_WORKING_TREE,
    }

    def fail(**_kwargs):
        raise raised

    monkeypatch.setattr(VERIFICATION._identity, "build_reviewed_input_identity", fail)
    ok, reason = VERIFICATION.verify_reviewed_input_identity(tmp_path, identity)
    assert not ok
    assert (reason == "code: failure") if isinstance(raised, VERIFICATION.ReviewedInputError) else reason == "cannot reconstruct reviewed input identity: bad shape"


def test_recorded_identity_verifier_rejects_shape_tampering_and_accepts_valid_record(
    tmp_path: Path,
) -> None:
    repo = install_committed_repo(tmp_path / "repo", {"a.py": "value = 1\n"})
    identity = build_reviewed_input_identity(repo_root=repo, reviewed_paths=["a.py"])
    assert VERIFICATION.verify_recorded_reviewed_input_identity(identity) == (True, "recorded")

    cases = (
        (dict(identity, status="unavailable"), "reviewed input identity was not captured"),
        (dict(identity, algorithm="wrong"), "must use `sha256-v2`"),
        (dict(identity, reviewed_paths=[]), "declared reviewed inputs cover zero paths"),
        (dict(identity, reviewed_content=[]), "content paths do not match reviewed_paths"),
        (dict(identity, mode="wrong"), "invalid or missing substrate mode"),
        (dict(identity, changed_ref="HEAD"), "substrate mode does not match changed_ref"),
        (
            dict(identity, reviewed_content=[dict(identity["reviewed_content"][0], content_sha256="x")]),
            "contains a null or invalid content hash",
        ),
        (dict(identity, reviewed_patch_sha256="x"), "contains a null or invalid reviewed_patch_sha256"),
        (dict(identity, identity_sha256="0" * 64), "self-digest does not match its recorded fields"),
    )
    for tampered, expected in cases:
        ok, reason = VERIFICATION.verify_recorded_reviewed_input_identity(tampered)
        assert not ok and expected in reason, (tampered, reason)


def test_artifact_binding_uses_canonical_layout_fallback_without_git(tmp_path: Path) -> None:
    artifact = tmp_path / "repo/charness-artifacts/critique/review.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("review", encoding="utf-8")
    ok, reason = VERIFICATION.verify_artifact_binding(
        artifact,
        {"packet path": "missing.json", "packet sha256": "0" * 64, "identity sha256": "0" * 64},
        expected_kind="charness.critique_prepare_packet",
    )
    assert not ok
    assert reason == "reviewed packet does not exist: missing.json"


class ConsumerSupport:
    class RunReviewError(ValueError):
        def __init__(self, code: str, message: str, *, details: dict | None = None) -> None:
            self.code = code
            self.details = details or {}
            super().__init__(message)


def _consumer_packet(*, receipt: dict | None = None, content: str | None = None) -> dict:
    section_content = content if content is not None else _manifest("a.py")
    return {
        "follow_up": {"source": "prior"},
        "follow_up_scope": receipt
        if receipt is not None
        else {
            "status": "verified",
            "selected_paths": ["a.py"],
            "sections": [
                {
                    "section_id": "files",
                    "mode": "selected-paths",
                    "path_binding": "exact-path-manifest",
                    "path_set_sha256": hashlib.sha256(b"a.py").hexdigest(),
                    "status": "verified",
                }
            ],
        },
        "sections": [{"id": "files", "content": section_content}],
    }


def test_consumer_scope_check_accepts_a_verified_exact_manifest() -> None:
    CONSUMER.refuse_if_unbound(ConsumerSupport, _consumer_packet(), ["a.py"])


def test_consumer_scope_check_skips_static_sections_and_parses_manifest_edges() -> None:
    packet = _consumer_packet()
    packet["sections"].append({"id": "notes", "content": "not path-bearing"})
    packet["follow_up_scope"]["sections"].append(
        {"section_id": "notes", "mode": "static", "status": "verified"}
    )
    CONSUMER.refuse_if_unbound(ConsumerSupport, packet, ["a.py"])
    assert CONSUMER._manifest_paths("missing manifest") is None
    assert CONSUMER._manifest_paths("Exact reviewed-path manifest:\n\n") == []


@pytest.mark.parametrize(
    ("packet", "code", "message"),
    (
        (_consumer_packet(receipt=None) | {"follow_up_scope": None}, "follow-up-scope-unbound", "no verified"),
        (
            _consumer_packet(receipt={"status": "verified", "selected_paths": ["b.py"], "sections": []}),
            "follow-up-scope-mismatch",
            "does not match",
        ),
        (
            _consumer_packet(
                receipt={
                    "status": "verified",
                    "selected_paths": ["a.py"],
                    "sections": [{"section_id": "other", "status": "verified"}],
                }
            ),
            "follow-up-scope-unbound",
            "every packet section",
        ),
        (
            _consumer_packet(
                receipt={
                    "status": "verified",
                    "selected_paths": ["a.py"],
                    "sections": [{"section_id": "files", "status": "verified", "mode": "selected-paths"}],
                }
            ),
            "follow-up-producer-out-of-scope",
            "no exact path binding",
        ),
        (
            _consumer_packet(
                receipt={
                    "status": "verified",
                    "selected_paths": ["a.py"],
                    "sections": [
                        {
                            "section_id": "files",
                            "status": "verified",
                            "mode": "selected-paths",
                            "path_binding": "exact-path-manifest",
                            "path_set_sha256": hashlib.sha256(b"a.py").hexdigest(),
                        }
                    ],
                },
                content="Exact reviewed-path manifest:\nwrong\n",
            ),
            "follow-up-producer-out-of-scope",
            "manifest is not exact",
        ),
        (
            _consumer_packet(
                receipt={
                    "status": "verified",
                    "selected_paths": ["a.py"],
                    "sections": [
                        {
                            "section_id": "files",
                            "status": "verified",
                            "mode": "selected-paths",
                            "path_binding": "exact-path-manifest",
                            "path_set_sha256": "0" * 64,
                        }
                    ],
                }
            ),
            "follow-up-scope-mismatch",
            "path digest does not match",
        ),
    ),
)
def test_consumer_scope_check_refuses_unproven_receipts(packet: dict, code: str, message: str) -> None:
    with pytest.raises(ConsumerSupport.RunReviewError, match=message) as raised:
        CONSUMER.refuse_if_unbound(ConsumerSupport, packet, ["a.py"])
    assert raised.value.code == code
