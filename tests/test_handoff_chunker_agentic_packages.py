from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = REPO_ROOT / "skills" / "public" / "handoff" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load("chunked_routing_lib")


@pytest.fixture()
def entries(lib):
    return [
        lib.HandoffEntry(
            index=1,
            title="#101: Handoff chunker proposes issue lists",
            body="Make handoff package synthesis agentic.",
            referenced_issues=(101,),
            referenced_paths=("skills/public/handoff/scripts/chunked_routing_lib.py",),
            boundary_tokens=("skills/public/handoff/scripts/chunked_routing_lib.py",),
        ),
        lib.HandoffEntry(
            index=2,
            title="#102: Handoff tests pin live issues",
            body="Move brittle tests to synthetic fixtures.",
            referenced_issues=(102,),
            referenced_paths=("tests/test_handoff_chunker_parse.py",),
            boundary_tokens=("tests/test_handoff_chunker_parse.py",),
        ),
        lib.HandoffEntry(
            index=3,
            title="#103: Closeout rehearsal",
            body="Validate direct-commit carriers before push.",
            referenced_issues=(103,),
            boundary_tokens=("label/closeout",),
        ),
        lib.HandoffEntry(
            index=4,
            title="#104: Publication policy",
            body="Adapter-owned closeout publication defaults.",
            referenced_issues=(104,),
            boundary_tokens=("label/closeout",),
        ),
    ]


def _good_response():
    return {
        "chunks": [
            {
                "label": "handoff-fixtures",
                "source_ids": [1, 2],
                "objective_summary": "Agentic handoff packages with stable fixtures",
                "rationale": "Both sources change the handoff chunker pickup surface.",
                "downstream_unlock": "Future pickups stop presenting issue lists.",
                "excluded_source_ids": [3, 4],
                "basis_boundary_tokens": [],
            },
            {
                "label": "closeout-publication",
                "source_ids": [3, 4],
                "objective_summary": "Closeout rehearsal and publication policy",
                "rationale": "Both sources reduce publish-time closeout ambiguity.",
                "downstream_unlock": "Later issue closeout can reuse one policy path.",
                "excluded_source_ids": [1, 2],
                "basis_boundary_tokens": ["label/closeout"],
            },
        ]
    }


def test_build_chunk_proposal_packet_uses_sources_hints_and_policy(lib, entries):
    hints = lib.propose_merges(entries)
    packet = lib.build_chunk_proposal_packet(
        entries,
        merge_proposal=hints,
        policy={
            "max_package_sources": 3,
            "broad_boundary_tokens": ("label/bug",),
            "allowed_broad_boundary_tokens": (),
        },
    )

    assert packet["version"] == lib.CHUNK_PROPOSAL_PACKET_VERSION
    assert [source["source_id"] for source in packet["sources"]] == [1, 2, 3, 4]
    assert packet["policy"]["max_package_sources"] == 3
    assert packet["chunk_proposer_prompt"] == lib.CHUNK_PROPOSER_PROMPT
    assert "chunks" in packet["response_schema"]["properties"]
    assert any(hint["source_ids"] == [3, 4] for hint in packet["merge_hints"])


def test_validate_accepts_complete_agentic_packages(lib, entries):
    report = lib.validate_chunk_proposal_response(
        _good_response(),
        entries,
        policy={
            "max_package_sources": 3,
            "broad_boundary_tokens": ("label/bug",),
            "allowed_broad_boundary_tokens": (),
        },
    )
    assert report["ok"] is True, report["issues"]


def test_materialize_agentic_packages_as_merge_proposal(lib, entries):
    proposal = lib.materialize_chunk_proposal_response(_good_response(), entries)
    assert proposal.standalone == ()
    assert [candidate.label for candidate in proposal.merged] == [
        "handoff-fixtures",
        "closeout-publication",
    ]
    assert [entry.index for entry in proposal.merged[0].entries] == [1, 2]
    assert "agentic rationale:" in proposal.shared_boundary_reason["handoff-fixtures"]


@pytest.mark.parametrize(
    ("mutate", "expected"),
    [
        (lambda r: r["chunks"][0]["source_ids"].append(99), "unknown source_ids"),
        (lambda r: r["chunks"][1]["source_ids"].append(1), "duplicate source_ids"),
        (lambda r: r["chunks"][1]["source_ids"].remove(4), "missing source_ids"),
        (lambda r: r["chunks"][0].update({"rationale": "  "}), "empty `rationale`"),
        (lambda r: r["chunks"][0].update({"label": "Bad Label"}), "invalid label"),
    ],
)
def test_validate_rejects_bad_agentic_package_shapes(lib, entries, mutate, expected):
    response = _good_response()
    mutate(response)
    report = lib.validate_chunk_proposal_response(response, entries)
    assert report["ok"] is False
    assert any(expected in issue for issue in report["issues"])


def test_validate_rejects_overlarge_package(lib, entries):
    response = _good_response()
    response["chunks"] = [
        {
            "label": "too-large",
            "source_ids": [1, 2, 3, 4],
            "objective_summary": "Too broad",
            "rationale": "This bundles too much.",
            "downstream_unlock": "n/a",
            "basis_boundary_tokens": [],
        }
    ]

    report = lib.validate_chunk_proposal_response(
        response,
        entries,
        policy={
            "max_package_sources": 3,
            "broad_boundary_tokens": (),
            "allowed_broad_boundary_tokens": (),
        },
    )
    assert report["ok"] is False
    assert any("exceeds max 3" in issue for issue in report["issues"])


def test_validate_rejects_broad_label_only_package(lib, entries):
    response = _good_response()
    response["chunks"][1]["basis_boundary_tokens"] = ["label/closeout"]

    report = lib.validate_chunk_proposal_response(
        response,
        entries,
        policy={
            "max_package_sources": 3,
            "broad_boundary_tokens": ("label/closeout",),
            "allowed_broad_boundary_tokens": (),
        },
    )
    assert report["ok"] is False
    assert any("broad boundary tokens" in issue for issue in report["issues"])


def test_adapter_policy_can_allow_repo_specific_broad_label(lib, entries):
    response = _good_response()
    response["chunks"][1]["basis_boundary_tokens"] = ["label/closeout"]

    report = lib.validate_chunk_proposal_response(
        response,
        entries,
        policy={
            "max_package_sources": 3,
            "broad_boundary_tokens": ("label/closeout",),
            "allowed_broad_boundary_tokens": ("label/closeout",),
        },
    )
    assert report["ok"] is True, report["issues"]


def test_prepare_chunk_packet_cli_emits_agentic_packet(entries):
    payload = {"entries": [entry.to_dict() for entry in entries]}
    result = subprocess.run(
        ["python3", str(SCRIPTS / "prepare_chunk_packet.py"), "--input", "-"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    packet = json.loads(result.stdout)
    assert packet["version"] == 1
    assert [source["source_id"] for source in packet["sources"]] == [1, 2, 3, 4]
    assert "chunk_proposer_prompt" in packet
